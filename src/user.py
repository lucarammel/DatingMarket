import random

from loguru import logger


class User:
    def __init__(self, id, gender, attractiveness_score, like_rate, swipe_limit=50):
        self.id = id
        self.gender = gender
        self.attractiveness_score = attractiveness_score
        self.like_rate = like_rate
        self.swipe_limit = swipe_limit
        self.swipes_today = 0

        self.matches = []
        self.liked_users = []
        self.seen_users = []

    def swipe(self, other_user):
        """Determines if the user swipes right (likes the other user)."""
        if self.swipes_today >= self.swipe_limit:
            logger.info(f"{self.name} has reached their daily swipe limit.")
            return False

        self.swipes_today += 1
        liked = random.random() < self.like_rate  # Decide based on like rate

        return liked

    def match(self, other_user):
        """Registers a match between two users."""
        self.matches.append(other_user)

    def reset_daily_swipes(self):
        """Resets swipe count at the start of a new day."""
        self.swipes_today = 0

    def make_all_swipes(self, other_users):
        """Makes swipes on all other users."""
        for user in other_users:
            if user.id not in self.seen_users and user.id != self.id:
                liked = self.swipe(user)
                if liked:
                    self.liked_users.append(user)
                self.seen_users.append(user.id)


class Male(User):
    def __init__(self, id, attractiveness_score, like_rate):
        super().__init__(id, "Male", attractiveness_score, like_rate)


class Female(User):
    def __init__(self, id, attractiveness_score, like_rate):
        super().__init__(id, "Female", attractiveness_score, like_rate)
