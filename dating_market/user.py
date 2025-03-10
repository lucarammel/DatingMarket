from __future__ import annotations

import random
from enum import Enum

import numpy as np
import polars as pl


class Gender(Enum):
    male = "Male"
    female = "Female"


class User:
    def __init__(self, id, gender, attractiveness_score, like_rate, swipe_limit):
        self.id = id
        self.gender = gender
        self.attractiveness_score = attractiveness_score
        self.like_rate = like_rate
        self.swipe_limit = swipe_limit
        self.swipes_today = 0

        self.matches: list[int] = []
        self.liked_users: list[int] = []
        self.seen_users: list[int] = []
        self.like_rate_history: list[float] = [self.like_rate]
        self.match_rate: float = -1
        self.match_rate_history: list[float] = []

    def __str__(self):
        return (
            "User:\n"
            f"  ID: {self.id}\n"
            f"  Gender: {self.gender.value}\n"
            f"  Attractiveness Score: {self.attractiveness_score}\n"
            f"  Like Rate: {self.like_rate:.2f}\n"
            f"  Matches: {len(self.matches)}\n"
            f"  Liked Users: {len(self.liked_users)}\n"
            f"  Seen Users: {len(self.seen_users)}"
        )

    def get_swipe_limit(self):
        if self.swipes_today >= self.swipe_limit:
            return True
        else:
            return False

    def update_like_rate(self):
        """Updates the like_rate with some randomness based on match rate"""
        if self.match_rate != -1:
            if self.match_rate >= 0.33:
                self.like_rate -= self.like_rate * abs(random.gauss(0, 0.1))
            elif self.match_rate <= 0.1:
                self.like_rate += self.like_rate * abs(random.gauss(0, 0.1))

        self.like_rate = min(max(self.like_rate, 0), 1)
        self.like_rate_history.append(self.like_rate)

    def update_match_rate(self):
        if len(self.liked_users) > 0:
            self.match_rate = len(self.matches) / len(self.liked_users)
            self.match_rate_history.append(self.match_rate)

    @staticmethod
    def compute_threshold_like_rate(like_rate, attractiveness_score):
        """Uses an log function to decrease like_rate for higher attractiveness."""
        return np.max(np.min(1 + like_rate * np.log(attractiveness_score), 1), 0)

    def match(self, user_id: int):
        """Registers a match between two users."""
        self.matches.append(user_id)

    def get_opposite_gender(self):
        if self.gender == Gender.male:
            return Gender.female
        else:
            return Gender.male

    def is_reciprocal(self, other_user: User):
        """Determines if the other user has also liked the user."""
        return self in other_user.liked_users

    def swipe(self, df_liked: pl.DataFrame, all_users: dict[int, User]):
        """Makes swipes on all other users."""
        users_liked_array = df_liked.select("id_right", "liked").to_numpy()

        other_users_idx = list(users_liked_array[:, 0])
        other_users_liked = list(users_liked_array[:, 1])

        for idx, liked in zip(other_users_idx, other_users_liked):
            if liked == 1:
                self.liked_users.append(idx)
                if self.is_reciprocal(all_users[idx]):
                    self.match(idx)
                    all_users[idx].match(self.id)


class Male(User):
    def __init__(self, id, attractiveness_score, like_rate, swipe_limit):
        super().__init__(id, Gender.male, attractiveness_score, like_rate, swipe_limit)


class Female(User):
    def __init__(self, id, attractiveness_score, like_rate, swipe_limit):
        super().__init__(id, Gender.female, attractiveness_score, like_rate, swipe_limit)
