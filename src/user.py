import random


class User:
    def __init__(self, id, gender, attractiveness_score, like_rate, swipe_limit):
        self.id = id
        self.gender = gender
        self.attractiveness_score = attractiveness_score
        self.like_rate = like_rate
        self.swipe_limit = swipe_limit
        self.swipes_today = 0

        self.matches = []
        self.liked_users = []
        self.seen_users = []

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

    def swipe(self, other_user):
        """Determines if the user swipes right (likes the other user)."""

        self.swipes_today += 1
        liked = random.random() < self.like_rate  # Decide based on like rate

        return liked

    def match(self, other_user):
        """Registers a match between two users."""
        self.matches.append(other_user)

    def reset_daily_swipes(self):
        """Resets swipe count at the start of a new day."""
        self.swipes_today = 0

    def get_opposite_gender(self):
        if self.gender == "Male":
            return Female
        else:
            return Male

    def make_all_swipes(self, other_users):
        """Makes swipes on all other users."""
        for user in other_users:
            if user.id not in self.seen_users and user.id != self.id:
                if self.get_swipe_limit():
                    break
                liked = self.swipe(user)
                if liked:
                    self.liked_users.append(user)
                self.seen_users.append(user.id)


class Male(User):
    def __init__(self, id, attractiveness_score, like_rate, swipe_limit):
        super().__init__(id, "Male", attractiveness_score, like_rate, swipe_limit)


class Female(User):
    def __init__(self, id, attractiveness_score, like_rate, swipe_limit):
        super().__init__(id, "Female", attractiveness_score, like_rate, swipe_limit)
