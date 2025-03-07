import random

import polars as pl
from loguru import logger

from .user import Female, Male, User


class Market:
    def __init__(self, n_users, male_ratio):
        self.males: list[Male] = []
        self.females: list[Female] = []
        self.users: list[User] = []

        self.day = 0
        self.n_users = n_users
        self.male_ratio = male_ratio

    def add_user(self, user: User):
        """Adds a user to the market."""
        if isinstance(user, Male):
            self.males.append(user)
        else:
            self.females.append(user)
        self.users.append(user)

    def generate_users(self, n_users: int, male_ratio: int = 0.5):
        """Generates `n_users` users with a proportion of males defined by `male_ratio`."""

        num_males = int(n_users * male_ratio)
        num_females = n_users - num_males
        logger.info(f"Generating {n_users} users with {male_ratio:.0%} of Male")

        for i in range(num_males):
            self.add_user(
                Male(
                    id=len(self.users),
                    attractiveness_score=random.gauss(0.5, 0.1),
                    like_rate=random.gauss(0.5, 0.1),
                    swipe_limit=20,
                )
            )

        for i in range(num_females):
            self.add_user(
                Female(
                    id=len(self.users),
                    attractiveness_score=random.gauss(0.5, 0.1),
                    like_rate=random.gauss(0.5, 0.1),
                    swipe_limit=20,
                )
            )

        logger.info("Users generated !")

    def run(self, days):
        """Runs the simulation for a given number of days."""
        self.generate_users(n_users=self.n_users, male_ratio=self.male_ratio)

        for _ in range(days):
            self.day += 1
            logger.info(f"📅 Day {self.day}: Users are swiping!")

            for user in self.users:
                user.reset_daily_swipes()
                all_users_by_gender = self.females if isinstance(user, Male) else self.males
                others_users_not_seen = [
                    u
                    for u in all_users_by_gender
                    if u.id not in user.seen_users and u.id != user.id
                ]

                profiles_to_present = random.sample(
                    others_users_not_seen, min(len(others_users_not_seen), user.swipe_limit)
                )

                user.make_all_swipes(profiles_to_present)

    def to_dataframe(self):
        """Exporte les utilisateurs sous forme de DataFrame (polars ou pandas)."""
        data = [
            {
                "id": user.id,
                "gender": user.gender.value,
                "attractiveness_score": user.attractiveness_score,
                "like_rate_start": user.like_rate_history[0],
                "like_rate_end": user.like_rate,
                "matches": len(user.matches),
                "match_rate": len(user.matches) / len(user.liked_users),
                "likes": len(user.liked_users),
                "likes_rate": len(user.liked_users) / len(user.seen_users),
                "seen_users": len(user.seen_users),
            }
            for user in self.users
        ]

        return pl.DataFrame(data)
