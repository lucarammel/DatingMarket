import random

import plotly.express as px
import polars as pl
from loguru import logger

from dating_market.user import Female, Male, User


class Participants:
    def __init__(self, n_users: int, male_ratio: float):
        self.n_users = n_users
        self.male_ratio = male_ratio

        self.males: list[int] = []
        self.females: list[int] = []
        self.users: dict[int, User] = {}

        self.df_users: pl.DataFrame = pl.DataFrame()

    def add_user(self, user: User):
        """Adds a user to the market."""
        if isinstance(user, Male):
            self.males.append(user.id)
        else:
            self.females.append(user.id)
        self.users[user.id] = user

    def generate_users(self):
        """Generates `n_users` users with a proportion of males defined by `male_ratio`."""

        num_males = int(self.n_users * self.male_ratio)
        num_females = self.n_users - num_males
        logger.info(f"Generating {self.n_users} users with {self.male_ratio:.0%} of Male")

        for i in range(num_males):
            self.add_user(
                Male(
                    id=len(self.users),
                    attractiveness_score=max(min(random.gauss(0.5, 0.2), 0.8), 0.2),
                    like_rate=max(min(random.gauss(0.5, 0.1), 0.8), 0.2),
                    swipe_limit=20,
                )
            )

        for i in range(num_females):
            self.add_user(
                Female(
                    id=len(self.users),
                    attractiveness_score=max(min(random.gauss(0.5, 0.2), 0.8), 0.2),
                    like_rate=max(min(random.gauss(0.5, 0.1), 0.8), 0.2),
                    swipe_limit=20,
                )
            )

        self.update_users_df()

        logger.info("Users generated !")

    def sort_users_by_attractiveness(self):
        self.females = (
            pl.DataFrame(
                [{"user": id, "attractiveness": self.users[id].match_rate} for id in self.females]
            )
            .sort(by="attractiveness", descending=True)["user"]
            .to_list()
        )

        self.males = (
            pl.DataFrame(
                [{"user": id, "attractiveness": self.users[id].match_rate} for id in self.males]
            )
            .sort(by="attractiveness", descending=True)["user"]
            .to_list()
        )

    def update_users_df(self):
        self.df_users = pl.DataFrame(
            [{"id": id, "user": self.users[id]} for id in self.users.keys()]
        )

    def run_swipes(self):
        self.update_users_df()

        for id in self.users:
            user = self.users[id]
            user.reset_daily_swipes()

            profiles_to_present = (
                self.df_users.filter(~pl.col("id").is_in(user.seen_users))
                .sample(n=user.swipe_limit)["user"]
                .to_list()
            )

            user.make_all_swipes(profiles_to_present)

        for user in self.users:
            self.users[id].update_match_rate()
            self.users[id].update_like_rate()

    def to_dataframe(self):
        """Exporte les utilisateurs sous forme de DataFrame (polars ou pandas)."""
        data = [
            {
                "id": user.id,
                "gender": user.gender.value,
                "attractiveness_score": round(user.attractiveness_score, 2),
                "like_rate_start": round(user.like_rate_history[0], 2),
                "like_rate_end": round(user.like_rate, 2),
                "increase_like_rate": round(user.like_rate - user.like_rate_history[0], 2),
                "matches": len(user.matches),
                "match_rate": round(len(user.matches) / len(user.liked_users), 2),
                "likes": len(user.liked_users),
                "seen_users": len(user.seen_users),
            }
            for user in self.users
        ]

        return pl.DataFrame(data)

    def plot_scatter(df: str, x: str, y: str, color: str, size: str, title: str, labels: dict):
        # Create scatter plot
        fig = px.scatter(
            df,
            x=x,
            y=y,
            color=color,  # Different colors for Male & Female
            size=size,
            title=title,
            labels=labels,
        )

        # Update layout for customization
        fig.update_layout(
            title_font=dict(family="Arial", size=20, color="black", weight="bold"),  # Bold title
            xaxis_title_font=dict(
                family="Arial", size=14, color="black", weight="bold"
            ),  # Bold x-axis label
            yaxis_title_font=dict(
                family="Arial", size=14, color="black", weight="bold"
            ),  # Bold y-axis label
            font=dict(
                family="Arial", size=12, color="black", weight="bold"
            ),  # Bold labels and ticks
            margin=dict(l=50, r=50, t=50, b=50),  # Add margins around the plot
            xaxis=dict(
                showgrid=True,
                zeroline=True,
                showline=True,  # Show x-axis line
                linecolor="black",  # Set the x-axis line color
            ),
            yaxis=dict(
                showgrid=True,
                zeroline=True,
                showline=True,  # Show y-axis line
                linecolor="black",  # Set the y-axis line color
                anchor="x",
            ),
            legend_title="Legend",
        )
        # fig.update_traces(marker=dict(sizemode="diameter", sizemax=20))
        fig.show()
