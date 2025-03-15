from __future__ import annotations

import random
from enum import Enum

import numpy as np


class Gender(Enum):
    male = "Male"
    female = "Female"


class User:
    def __init__(
        self, id, gender: Gender, attractiveness_score: float, like_rate: float, swipe_limit: int
    ):
        self.id = id
        self.gender = gender
        self.attractiveness_score = attractiveness_score
        self.like_rate = like_rate
        self.swipe_limit = swipe_limit
        self.swipes_today = 0

        self.matches: list[int] = []
        self.liked_users: list[int] = []
        self.seen_users: list[int] = [self.id]
        self.like_rate_history: list[float] = [self.like_rate]
        self.match_rate: float = -1
        self.match_rate_history: list[float] = []
        self.match_by_days = list[int] = []

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

    def reset_dauly(self):
        """Resets swipe count at the start of a new day."""
        self.swipes_today = 0
        self.match_today = 0

    def compute_threshold_like_rate(self, attractiveness_score):
        """Uses an log function to decrease like_rate for higher attractiveness."""
        return max(min(1 + self.like_rate * np.log(attractiveness_score), 1), 0)

    def match(self, user_id: int):
        """Registers a match between two users."""
        self.matches.append(user_id)

    def get_opposite_gender(self):
        if self.gender == Gender.male:
            return Gender.female
        else:
            return Gender.male

    def get_possible_match(self, other_user: User):
        if other_user.id in self.matches:
            return False
        if other_user.id in self.liked_users and self.id in other_user.liked_users:
            return True

    def is_reciprocal(self, other_user: User):
        """Determines if the other user has also liked the user."""
        return self in other_user.liked_users

    def add_match_by_day(self):
        self.match_today += 1

    def swipe(self, other_user: User):
        """Determines if the user swipes right (likes the other user)."""

        self.swipes_today += 1
        threshold = self.compute_threshold_like_rate(other_user.attractiveness_score)
        liked = random.random() < threshold

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
                        self.match(user_id)
                        all_users[user_id].match(self.id)

                self.seen_users.append(user_id)
        self.match_by_days.append(self.match_today)


class Male(User):
    def __init__(self, id, attractiveness_score, like_rate, swipe_limit):
        super().__init__(id, Gender.male, attractiveness_score, like_rate, swipe_limit)


class Female(User):
    def __init__(self, id, attractiveness_score, like_rate, swipe_limit):
        super().__init__(id, Gender.female, attractiveness_score, like_rate, swipe_limit)
