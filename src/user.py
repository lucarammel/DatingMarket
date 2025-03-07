from __future__ import annotations

import math
import random
from enum import Enum


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

        self.matches: list[User] = []
        self.liked_users: list[User] = []
        self.seen_users: list[User] = []
        self.like_rate_history: list[float] = [self.like_rate]
        self.match_rate: float
        self.match_rate_history: list[float] = []

    def __str__(self):
        return (
            "User:\n"
            f"  ID: {self.id}\n"
            f"  Gender: {self.gender}\n"
            f"  Attractiveness Score: {self.attractiveness_score}\n"
            f"  Like Rate: {self.like_rate:.2f}\n"
            f"  Swipes Today: {self.swipes_today}/{self.swipe_limit}\n"
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

        if self.match_rate > 0.4:
            self.like_rate -= self.like_rate * abs(random.gauss(0, 0.1))
        elif self.match_rate < 0.1:
            self.like_rate += self.like_rate * abs(random.gauss(0, 0.1))

        self.like_rate_history.append(min(self.like_rate, 1))

    def update_match_rate(self):
        self.match_rate_history.append(self.match_rate)
        self.match_rate = len(self.matches) / len(self.liked_users)

    def compute_threshold_like_rate(self, attractiveness_score):
        """Uses an log function to decrease like_rate for higher attractiveness."""
        return 1 + self.like_rate * max(math.log(attractiveness_score), -1)

    def swipe(self, other_user: User):
        """Determines if the user swipes right (likes the other user)."""

        self.swipes_today += 1
        threshold = self.compute_threshold_like_rate(other_user.attractiveness_score)
        liked = random.random() < threshold

        return liked

    def get_possible_match(self, other_user: User):
        if other_user.id in self.matches:
            return False
        if other_user.id in self.liked_users and self.id in other_user.liked_users:
            return True

    def match(self, other_user: User):
        """Registers a match between two users."""
        self.matches.append(other_user)

    def reset_daily_swipes(self):
        """Resets swipe count at the start of a new day."""
        self.swipes_today = 0

    def get_opposite_gender(self):
        if self.gender == Gender.male:
            return Female
        else:
            return Male

    def is_reciprocal(self, other_user: User):
        """Determines if the other user has also liked the user."""
        return self in other_user.liked_users

    def make_all_swipes(self, other_users: list[User]):
        """Makes swipes on all other users."""
        for user in other_users:
            if self.get_swipe_limit():
                break
            if user.id not in self.seen_users and user.id != self.id:
                liked = self.swipe(user)
                if liked:
                    self.liked_users.append(user)
                    if self.is_reciprocal(user):
                        self.match(user)
                        user.match(self)

                self.seen_users.append(user.id)

        self.update_like_rate()
        self.update_match_rate()


class Male(User):
    def __init__(self, id, attractiveness_score, like_rate, swipe_limit):
        super().__init__(id, Gender.male, attractiveness_score, like_rate, swipe_limit)


class Female(User):
    def __init__(self, id, attractiveness_score, like_rate, swipe_limit):
        super().__init__(id, Gender.female, attractiveness_score, like_rate, swipe_limit)
