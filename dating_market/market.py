from loguru import logger

from dating_market.participants import Participants


class Market:
    def __init__(self, participants: Participants):
        self.day = 0
        self.participants = participants

    def run(self, days):
        """Runs the simulation for a given number of days."""
        self.participants.generate_users(n_users=self.n_users, male_ratio=self.male_ratio)

        for _ in range(days):
            self.day += 1
            logger.info(f"📅 Day {self.day}: Users are swiping!")

            self.participants.run_swipes()
