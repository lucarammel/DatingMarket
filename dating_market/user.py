from __future__ import annotations

import random
from enum import Enum

import numpy as np


class Gender(Enum):
    """
    Enumeration representing the gender of a user.

    Attributes:
        male (str): Represents a male user.
        female (str): Represents a female user.
    """

    male = "Male"
    female = "Female"


class User:
    def __init__(
        self, id, gender: Gender, attractiveness_score: float, like_rate: float, likes_limit: int
    ):
        """
        Represents a user in the dating app, with attributes such as attractiveness score, like rate, and daily limits.

        Attributes:
            id (int): Unique identifier for the user.
            gender (Gender): Gender of the user.
            attractiveness_score (float): User's attractiveness score.
            like_rate (float): Probability of the user liking another user.
            likes_limit (int): Maximum number of likes allowed per day.
            swipe_limit (int): Maximum number of swipes per day.
            upper_likes_limit (int): Upper limit for daily likes.
            lower_likes_limit (int): Lower limit for daily likes.
            match_rate (float): Ratio of matches to liked users.
            likes_today (int): Count of likes given today.
            match_today (int): Count of matches today.
            swipes_today (int): Count of swipes today.
            matches (list[int]): List of user IDs the user has matched with.
            liked_users (list[int]): List of user IDs the user has liked.
            seen_users (list[int]): List of user IDs the user has seen.
            like_rate_history (list[float]): History of like rates.
            match_rate_history (list[float]): History of match rates.
            likes_limit_history (list[float]): History of likes limits.
            match_by_days (list[int]): Daily count of matches.
            likes_by_day (list[int]): Daily count of likes.
            swipes_by_day (list[int]): Daily count of swipes.
        """
        self.id = id
        self.gender = gender
        self.attractiveness_score = attractiveness_score
        self.like_rate = like_rate
        self.likes_limit = likes_limit
        self.swipe_limit: int = 50
        self.upper_likes_limit = likes_limit
        self.lower_likes_limit = int(likes_limit / 3)
        self.match_rate: float = -1
        self.likes_today: int = 0
        self.match_today: int = 0
        self.swipes_today: int = 0

        self.matches: list[int] = []
        self.liked_users: list[int] = []
        self.seen_users: list[int] = [self.id]

        self.like_rate_history: list[float] = []
        self.match_rate_history: list[float] = []
        self.likes_limit_history: list[float] = []

        self.match_by_days: list[int] = []
        self.likes_by_day: list[int] = []
        self.swipes_by_day: list[int] = []

    def __str__(self):
        """Returns a string representation of the user."""
        return (
            "User:\n"
            f"  ID: {self.id}\n"
            f"  Gender: {self.gender.value}\n"
            f"  Attractiveness Score: {self.attractiveness_score:.2f}\n"
            f"  Like Rate: {self.like_rate:.2f}\n"
        )

    def get_swipe_limit(self):
        """Checks if the user has reached the daily like limit."""
        if self.likes_today >= self.likes_limit:
            return True
        else:
            return False

    def update_likes_limit(self):
        """Adjusts the user's daily like limit based on the match rate."""
        if self.match_rate != -1:
            step = int(self.likes_limit * abs(random.gauss(0, 1)))
            if self.match_rate >= 0.33:
                if self.likes_limit - step >= self.lower_likes_limit:
                    self.likes_limit -= step
            elif self.match_rate <= 0.1:
                if self.likes_limit + step <= self.upper_likes_limit:
                    self.likes_limit += step

        self.likes_limit_history.append(self.likes_limit)

    def update_like_rate(self):
        """Updates the like_rate with some randomness based on match rate"""
        if self.match_rate != -1:
            increment = self.like_rate * abs(random.gauss(0, 0.1))
            if self.match_rate >= 0.33:
                self.like_rate -= increment
            elif self.match_rate <= 0.1:
                self.like_rate += increment

        self.like_rate = min(max(self.like_rate, 0), 1)
        self.like_rate_history.append(self.like_rate)

    def update_match_rate(self):
        """Updates the match rate based on past interactions."""
        if len(self.liked_users) > 0:
            self.match_rate = len(self.matches) / len(self.liked_users)
            self.match_rate_history.append(self.match_rate)

    def reset_daily(self):
        """Resets swipe, like, and match counters at the start of a new day."""
        self.likes_today = 0
        self.match_today = 0
        self.swipes_today = 0

    def compute_threshold_like_rate(self, attractiveness_score):
        """Computes an adjusted like rate based on the attractiveness score."""
        return max(min(1 + self.like_rate * np.log(attractiveness_score), 1), 0)

    def match(self, user_id: int, matched_user: User):
        """Registers a match between two users."""
        self.match_today += 1
        self.matches.append(user_id)

        matched_user.matches.append(self.id)
        matched_user.match_today += 1

    def get_opposite_gender(self):
        """Returns the opposite gender of the user."""
        if self.gender == Gender.male:
            return Gender.female
        else:
            return Gender.male

    def get_possible_match(self, other_user: User):
        """Checks if the other user can be a match."""
        if other_user.id in self.matches:
            return False
        if other_user.id in self.liked_users and self.id in other_user.liked_users:
            return True

    def is_reciprocal(self, other_user: User):
        """Determines if the other user has also liked the user."""
        return self.id in other_user.liked_users

    def swipe(self, other_user: User):
        """Determines if the user swipes right (likes the other user)."""
        self.swipes_today += 1
        threshold = self.compute_threshold_like_rate(other_user.attractiveness_score)
        liked = random.random() < threshold
        if liked:
            self.likes_today += 1
        return liked

    def make_all_swipes(self, potential_profiles: list[int], all_users: dict[str, User]):
        """Makes swipes on all other users."""
        for user_id in potential_profiles:
            if self.get_swipe_limit():
                break
            if user_id not in self.seen_users:
                liked = self.swipe(all_users[user_id])
                if liked:
                    self.liked_users.append(user_id)
                    if self.is_reciprocal(all_users[user_id]):
                        self.match(user_id, all_users[user_id])

                self.seen_users.append(user_id)

        self.match_by_days.append(self.match_today)
        self.likes_by_day.append(self.likes_today)
        self.swipes_by_day.append(self.swipes_today)


class Male(User):
    def __init__(self, id, attractiveness_score, like_rate, likes_limit):
        super().__init__(id, Gender.male, attractiveness_score, like_rate, likes_limit)


class Female(User):
    def __init__(self, id, attractiveness_score, like_rate, likes_limit):
        super().__init__(id, Gender.female, attractiveness_score, like_rate, likes_limit)
