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

        self.update_users_matrix()

        logger.info("Users generated !")

    def sort_users_by_attractiveness(self):
        self.females = self.df_users.sort(by="attractiveness_score", descending=True)[
            "id"
        ].to_list()
        self.males = self.df_users.sort(by="attractiveness_score", descending=True)["id"].to_list()

    def build_potential_profiles(self, user: User):
        gender_target = user.get_opposite_gender().value
        potential_profiles = self.df_users.filter(
            ~pl.col("id").is_in(user.seen_users), pl.col("gender") == gender_target
        )
        count = min(potential_profiles.height, user.swipe_limit)

        potential_profiles = potential_profiles.sample(n=count)["id"].to_list()

        return potential_profiles

    def update_users_matrix(self):
        males_matrix = np.zeros(shape=(len(self.males), len(self.females)))
        females_matrix = np.zeros(shape=(len(self.females), len(self.males)))

        for idx_m, value_m in enumerate(self.males):
            for idx_f, value_f in enumerate(self.females):
                males_matrix[idx_m, idx_f] = self.users[value_m].compute_threshold_like_rate(
                    self.users[value_f].attractiveness_score
                )
                females_matrix[idx_f, idx_m] = self.users[value_f].compute_threshold_like_rate(
                    self.users[value_m].attractiveness_score
                )
        self.males_matrix = pd.DataFrame(males_matrix, columns=self.females).set_index(
            np.array(self.males)
        )
        self.females_matrix = pd.DataFrame(females_matrix, columns=self.males).set_index(
            np.array(self.females)
        )

    def get_is_liked_dataframe(self, gender: Gender = Gender.male):
        if gender == Gender.male:
            df_random = pd.DataFrame(
                np.random.random(size=self.males_matrix.shape), columns=self.females
            ).set_index(np.array(self.males))
            df_is_liked = self.males_matrix < df_random
        else:
            df_random = pd.DataFrame(
                np.random.random(size=self.females_matrix.shape), columns=self.males
            ).set_index(np.array(self.females))
            df_is_liked = self.females_matrix < df_random

        return df_is_liked

    def run_swipes(self):
        self.get_users_dataframe()
        self.update_users_matrix()

        is_liked_females = self.get_is_liked_dataframe(gender=Gender.female)
        is_liked_males = self.get_is_liked_dataframe(gender=Gender.male)

        for id in self.users:
            user = self.users[id]
            potential_profiles = self.build_potential_profiles(user)

            matrix = is_liked_males if user.gender == Gender.male else is_liked_females
            user.swipe(other_users=potential_profiles, matrix=matrix, all_users=self.users)

        for id in self.users:
            self.users[id].update_match_rate()
            self.users[id].update_like_rate()

    def get_users_dataframe(self):
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

        self.df_users = pl.DataFrame(data)
        return self.df_users

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
