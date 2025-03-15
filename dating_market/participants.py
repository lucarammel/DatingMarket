import random

import numpy as np
import pandas as pd
import plotly.express as px
import polars as pl
from loguru import logger

from dating_market.user import Female, Gender, Male, User


class Participants:
    def __init__(self, n_users: int, male_ratio: float):
        self.n_users = n_users
        self.male_ratio = male_ratio

        self.males: list[int] = []
        self.females: list[int] = []
        self.users: dict[int, User] = {}

        self.males_matrix: pd.DataFrame
        self.females_matrix: pd.DataFrame

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

        logger.info("Users generated !")

    def sort_users_by_attractiveness(self):
        self.females = self.df_users.sort(by="attractiveness_score", descending=True)[
            "id"
        ].to_list()
        self.males = self.df_users.sort(by="attractiveness_score", descending=True)["id"].to_list()

    def get_potential_profiles(self, user: User):
        gender_target = user.get_opposite_gender()

        potential_profiles = self.df_users.filter(
            ~pl.col("id").is_in(user.seen_users), pl.col("gender") == gender_target.value
        )
        count = min(potential_profiles.height, user.swipe_limit)

        potential_profiles = potential_profiles.sample(n=count)["id"].to_list()

        return potential_profiles, gender_target

    def get_is_liked_data(
        self,
        user_id: int,
        potential_profiles: list[int],
        gender: Gender = Gender.male,
        gender_target: Gender = Gender.female,
    ):
        df_left = self.df_users.filter(
            pl.col("gender") == gender.value, pl.col("id") == user_id
        ).rename({"id": "id_left", "attractiveness_score": "attr_left", "like_rate": "like_left"})
        df_right = self.df_users.filter(
            pl.col("gender") == gender_target.value, pl.col("id").is_in(potential_profiles)
        ).rename(
            {"id": "id_right", "attractiveness_score": "attr_right", "like_rate": "like_right"}
        )

        df_combined = df_left.join(df_right, how="cross")
        size = df_combined.height

        df_liked = (
            df_combined.with_columns(
                (1 + pl.col("like_left") * np.log(pl.col("attr_right"))).clip(0, 1).alias("score"),
                pl.lit(np.random.rand(size)).alias("random"),
            )
            .with_columns((pl.col("random") < pl.col("score")).alias("liked"))
            .select(["id_left", "id_right", "liked"])
        )

        return df_liked

    def run_swipes(self):
        self._get_user_attractiveness_data()

        for id in self.users:
            user = self.users[id]

            potential_profiles, gender_target = self.get_potential_profiles(user)
            df_liked = self.get_is_liked_data(
                user_id=id,
                potential_profiles=potential_profiles,
                gender=user.gender,
                gender_target=gender_target,
            )
            user.swipe(df_liked=df_liked, all_users=self.users)

        for id in self.users:
            self.users[id].update_match_rate()
            self.users[id].update_like_rate()

    def _get_user_attractiveness_data(self):
        data = [
            {
                "id": u,
                "gender": self.users[u].gender.value,
                "attractiveness_score": self.users[u].attractiveness_score,
                "like_rate": self.users[u].like_rate,
            }
            for u in self.users
        ]

        self.df_users = pl.DataFrame(data)

    def get_users_data(self):
        """Exporte les utilisateurs sous forme de DataFrame (polars ou pandas)."""
        data = [
            {
                "id": u,
                "gender": self.users[u].gender.value,
                "attractiveness_score": round(self.users[u].attractiveness_score, 2),
                "like_rate_start": round(self.users[u].like_rate_history[0], 2),
                "like_rate_end": round(self.users[u].like_rate, 2),
                "increase_like_rate": round(
                    self.users[u].like_rate - self.users[u].like_rate_history[0], 2
                ),
                "matches": len(self.users[u].matches),
                "match_rate": round(self.users[u].match_rate, 2),
                "likes": len(self.users[u].liked_users),
                "seen_users": len(self.users[u].seen_users),
            }
            for u in self.users
        ]

        return pl.DataFrame(data)

    def plot_scatter(
        df: pl.DataFrame, x: str, y: str, color: str, size: str, title: str, labels: dict
    ):
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
