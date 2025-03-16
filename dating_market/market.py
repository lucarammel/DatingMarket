import polars as pl
from loguru import logger

from dating_market.participants import Participants


class Market:
    def __init__(self, n_users: int, male_ratio: float, n_days: int):
        self.n_days
        self.day = 0
        self.n_users = n_users
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

        logger.info("Market run done !")

    def get_market_data(self):
        users = self.participants.users

        data = [
            {
                "user": users[u].id,
                "matches": users[u].match_by_days,
                "likes": users[u].likes_by_day,
                "swipes": users[u].swipes_by_day,
                "like_rate": users[u].like_rate_history,
                "match_rate": users[u].match_rate_history,
            }
            for u in users
        ]

        return (
            pl.DataFrame(data, strict=False)
            .with_columns(pl.repeat([i for i in range(1, self.n_days)], self.n_users).alias("day"))
            .explode(
                "matches",
                "likes",
                "swipes",
                "like_rate",
                "match_rate",
            )
        )
