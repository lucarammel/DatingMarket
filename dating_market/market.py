import polars as pl
from loguru import logger

from dating_market.participants import Participants


class Market:
    def __init__(self, n_users: int, male_ratio: list[float] | float, n_days: int):
        self.n_days = n_days
        self.day = 0
        self.n_users = n_users
        self.male_ratio = male_ratio

        self.participants: dict[float, Participants] | Participants = (
            {male_ratio: Participants(n_users=n_users, male_ratio=male_ratio) for i in male_ratio}
            if isinstance(male_ratio, list)
            else Participants(n_users=n_users, male_ratio=male_ratio)
        )

    def get_users_data(self, nb_decimals: int = 3) -> pl.DataFrame:
        if isinstance(self.male_ratio, float):
            self.participants.get_users_data(nb_decimals=nb_decimals)
        else:
            dfs = {k: self.participants[k].get_users_data() for k in self.participants}

    def run(self):
        """Runs the simulation for a given number of days."""
        if isinstance(self.male_ratio, list):
            for k in self.participants:
                self.participants[k].generate_users()
        else:
            self.participants.generate_users()

        for _ in range(self.n_days):
            self.day += 1
            logger.info(f"📅 Day {self.day}: Users are swiping!")
            if isinstance(self.male_ratio, list):
                for k in self.participants:
                    self.participants[k].run_swipes()
            else:
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
                "likes_limit": users[u].likes_limit_history,
            }
            for u in users
        ]

        return (
            pl.DataFrame(data, strict=False)
            .with_columns(
                pl.repeat([i for i in range(1, self.n_days + 1)], self.n_users).alias("day")
            )
            .explode("day", "matches", "likes", "swipes", "like_rate", "match_rate", "likes_limit")
        )

    def plot_scatter(self, **kwargs):
        self.participants.plot_scatter(**kwargs)
