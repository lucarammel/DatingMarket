import random

import numpy as np
import polars as pl
from loguru import logger

from dating_market.user import Female, Male, User


class Participants:
    """Represents a group of users in the dating market."""

    def __init__(self, n_users: int, male_ratio: float):
        """Initializes the Participants group with a given number of users and a male ratio.

        Args:
            n_users (int): Total number of users.
            male_ratio (float): Proportion of male users in the group.
        """
        self.n_users = n_users
        self.male_ratio = male_ratio

        self.males: list[int] = []
        self.females: list[int] = []
        self.users: dict[int, User] = {}

        self.df_users: pl.DataFrame = pl.DataFrame()

    def add_user(self, user: User):
        """Adds a user to the participants list.

        Args:
            user (User): The user to be added.
        """
        if isinstance(user, Male):
            self.males.append(user.id)
        else:
            self.females.append(user.id)
        self.users[user.id] = user

    def generate_users(self):
        """Generates a specified number of users based on the male-to-female ratio."""

        num_males = int(self.n_users * self.male_ratio)
        num_females = self.n_users - num_males
        logger.info(f"Generating {self.n_users} users with {self.male_ratio:.0%} of Male")

        for i in range(num_males):
            self.add_user(
                Male(
                    id=len(self.users),
                    attractiveness_score=max(min(random.gauss(0.5, 0.2), 0.8), 0.2),
                    like_rate=max(min(random.gauss(0.5, 0.1), 0.8), 0.2),
                    likes_limit=20,
                )
            )

        for i in range(num_females):
            self.add_user(
                Female(
                    id=len(self.users),
                    attractiveness_score=max(min(random.gauss(0.5, 0.2), 0.8), 0.2),
                    like_rate=max(min(random.gauss(0.5, 0.1), 0.8), 0.2),
                    likes_limit=20,
                )
            )

        logger.success("Users generated !")

    def get_potential_profiles(self, user: User) -> list[int]:
        """Retrieves potential match profiles for a given user.

        Args:
            user (User): The user seeking potential matches.

        Returns:
            list[int]: List of user IDs representing potential matches.
        """
        gender_target = user.get_opposite_gender()

        potential_profiles = self.df_users.filter(
            ~pl.col("id").is_in(user.seen_users), pl.col("gender") == gender_target.value
        )

        potential_profiles = potential_profiles.select(pl.col("id").shuffle())["id"].to_list()

        if len(potential_profiles) > 0:
            potential_profiles = self.weighted_random_selection(
                users=potential_profiles,
                num_picks=min(user.swipe_limit, len(potential_profiles)),
                probability_ratio_between_best_and_worth=5,
            )
        return potential_profiles

    def weighted_random_selection(
        self, users: list[int], num_picks: int, probability_ratio_between_best_and_worth: int
    ):
        """Selects users randomly with weighted probabilities based on attractiveness.

        Args:
            users (list[int]): List of user IDs.
            num_picks (int): Number of users to select.
            probability_ratio_between_best_and_worth (int): Ratio influencing selection probabilities.

        Returns:
            list[int]: Selected user IDs.
        """
        n = len(users)
        weights = np.linspace(probability_ratio_between_best_and_worth, 1, n)
        weights /= weights.sum()

        selected_users = np.random.choice(users, size=num_picks, replace=False, p=weights)
        return list(selected_users)

    def run_swipes(self):
        """Simulates a full round of swiping for all users, updating match and like rates."""
        self._get_user_attractiveness_data()

        for u in self.users:
            self.users[u].reset_daily()

            profiles_to_present = self.get_potential_profiles(self.users[u])
            self.users[u].make_all_swipes(
                potential_profiles=profiles_to_present, all_users=self.users
            )

        for u in self.users:
            self.users[u].update_match_rate()
            self.users[u].update_like_rate()
            self.users[u].update_likes_limit()

    def _get_user_attractiveness_data(self):
        """Collects user attractiveness and like rate data into a DataFrame."""
        data = [
            {
                "id": u,
                "gender": self.users[u].gender.value,
                "attractiveness_score": self.users[u].attractiveness_score,
                "like_rate": self.users[u].like_rate,
            }
            for u in self.users
        ]

        self.df_users = pl.DataFrame(data)

    def get_users_data(self, nb_decimals: int = 3):
        """Exports user data as a Polars DataFrame.

        Args:
            nb_decimals (int): Number of decimal places for rounding numerical values.

        Returns:
            pl.DataFrame: DataFrame containing user statistics.
        """
        data = [
            {
                "user": u,
                "gender": self.users[u].gender.value,
                "attractiveness_score": round(self.users[u].attractiveness_score, nb_decimals),
                "like_rate_start": round(self.users[u].like_rate_history[0], nb_decimals),
                "like_rate_end": round(self.users[u].like_rate, nb_decimals),
                "like_rate_evolution": round(
                    self.users[u].like_rate - self.users[u].like_rate_history[0], nb_decimals
                ),
                "matches": len(self.users[u].matches),
                "match_rate": round(self.users[u].match_rate, nb_decimals),
                "likes": len(self.users[u].liked_users),
                "liked_by": len(self.users[u].liked_by),
                "liked_by_rate": round(
                    len(self.users[u].liked_by) / len(self.users[u].seen_by), nb_decimals
                ),
                "seen_by": len(self.users[u].seen_by),
                "seen_users": len(self.users[u].seen_users),
            }
            for u in self.users
        ]

        return pl.DataFrame(data)
