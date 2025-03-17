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
            {m: Participants(n_users=n_users, male_ratio=m) for m in male_ratio}
            if isinstance(male_ratio, list)
            else Participants(n_users=n_users, male_ratio=male_ratio)
        )

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

    def _get_market_dataframe_by_run(self, users) -> pl.DataFrame:
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

    def get_market_data(self):
        if isinstance(self.male_ratio, list):
            data: dict[int, pl.DataFrame] = {
                k: self._get_market_dataframe_by_run(self.participants[k].users).with_columns(
                    pl.lit(k).alias("male_ratio")
                )
                for k in self.participants
            }

            return pl.concat([data[k] for k in data.keys()], how="vertical")

        else:
            users = self.participants.users
            return self._get_market_dataframe_by_run(users)

    def get_users_data(self, nb_decimals: int = 3) -> pl.DataFrame:
        if isinstance(self.male_ratio, float):
            return self.participants.get_users_data(nb_decimals=nb_decimals)
        else:
            data: dict[int, pl.DataFrame] = {
                k: self.participants[k].get_users_data().with_columns(pl.lit(k).alias("male_ratio"))
                for k in self.participants
            }

            return pl.concat([data[k] for k in data.keys()], how="vertical")

    def plot_scatter(self, **kwargs):
        self.participants.plot_scatter(**kwargs)
