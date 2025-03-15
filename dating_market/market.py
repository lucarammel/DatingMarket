import polars as pl
from loguru import logger

from dating_market.participants import Participants


class Market:
    def __init__(self, n_users, male_ratio):
        self.day = 0
        self.participants = Participants(n_users=n_users, male_ratio=male_ratio)

    def get_users_data(self) -> pl.DataFrame:
        return self.participants.get_users_data()

    def run(self, days):
        """Runs the simulation for a given number of days."""
        self.participants.generate_users()

        for _ in range(days):
            self.day += 1
            logger.info(f"📅 Day {self.day}: Users are swiping!")

            self.participants.run_swipes()
