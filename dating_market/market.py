import numpy as np
import plotly.express as px
import polars as pl
from loguru import logger

from dating_market.participants import Participants
from dating_market.user import User


class Market:
    def __init__(self, n_users: int, male_ratio: list[float] | float, n_days: int):
        """
        Initializes the Market instance with the number of users, male-to-female ratio, and number of days.

        Args:
            n_users (int): The total number of users in the market.
            male_ratio (list[float] | float): The male-to-female ratio, can be a list of ratios or a single value.
            n_days (int): The number of days the market will run.
        """
        self.n_days = n_days
        self.day = 0
        self.n_users = n_users
        self.male_ratio = male_ratio

        if isinstance(self.male_ratio, list):
            self.male_ratio.sort()

        self.participants: dict[float, Participants] | Participants = (
            {m: Participants(n_users=n_users, male_ratio=m) for m in male_ratio}
            if isinstance(male_ratio, list)
            else Participants(n_users=n_users, male_ratio=male_ratio)
        )

    def run(self):
        """
        Runs the simulation for a given number of days. In each day, users interact by swiping, liking, and matching.

        This method handles the generation of users and the daily interactions based on the specified male-to-female ratio.
        """
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

    def _get_market_dataframe_by_run(self, users: dict[int, User]) -> pl.DataFrame:
        """
        Creates a DataFrame containing market data from user interactions over the days.

        Args:
            users (dict[int, User]): A dictionary of users, where each user is identified by an ID.

        Returns:
            pl.DataFrame: A DataFrame containing user data, including matches, likes, swipes, and other statistics.
        """
        data = [
            {
                "user": users[u].id,
                "gender": users[u].gender.value,
                "matches": users[u].match_by_days,
                "matches_cumulative": list(np.cumsum(users[u].match_by_days)),
                "likes": users[u].likes_by_day,
                "likes_cumulative": list(np.cumsum(users[u].likes_by_day)),
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
            .explode(
                "day",
                "matches",
                "matches_cumulative",
                "likes",
                "likes_cumulative",
                "swipes",
                "like_rate",
                "match_rate",
                "likes_limit",
            )
        )

    def get_market_data(self):
        """
        Retrieves the market data as a DataFrame.

        If there are multiple male-to-female ratios, the method will generate a DataFrame for each ratio and combine them.
        If there is only one ratio, it generates data for the single participant group.

        Returns:
            pl.DataFrame: A concatenated DataFrame containing all market data.
        """
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
        """
        Retrieves data on individual users, with the option to specify the number of decimal places for floating-point values.

        Args:
            nb_decimals (int): The number of decimal places to round the numerical values to (default is 3).

        Returns:
            pl.DataFrame: A DataFrame containing user data with optional decimal precision.
        """
        if isinstance(self.male_ratio, float):
            return self.participants.get_users_data(nb_decimals=nb_decimals)
        else:
            data: dict[int, pl.DataFrame] = {
                k: self.participants[k].get_users_data().with_columns(pl.lit(k).alias("male_ratio"))
                for k in self.participants
            }

            return pl.concat([data[k] for k in data.keys()], how="vertical")

    def plot_scatter(
        self,
        df: pl.DataFrame,
        x: str,
        y: str,
        color: str,
        title: str,
        slider_column: str | None = None,
        color_map: dict[str, str] = {"Male": "#377ae8", "Female": "#d337e8"},
        width=900,
        height=600,
    ):
        """
        Plots a scatter plot of user data using Plotly. Optionally animates the plot over the days and customizes the appearance.

        Args:
            df (pl.DataFrame): The DataFrame containing the data to plot.
            x (str): The column name for the x-axis.
            y (str): The column name for the y-axis.
            color (str): The column name used to color the data points.
            title (str): The title of the plot.
            slider_column (str | None, optional): The column used for animation frames (default is None).
            color_map (dict[str, str], optional): A mapping for the color of different groups (default maps "Male" to blue and "Female" to pink).
            width (int, optional): The width of the plot (default is 900).
            height (int, optional): The height of the plot (default is 600).
        """

        if isinstance(self.male_ratio, list):
            # Create scatter plot
            fig = px.scatter(
                data_frame=df,
                x=x,
                y=y,
                color=color,
                title=title,
                animation_frame=slider_column,
                color_discrete_map=color_map,
                width=width,
                height=height,
            )
        else:
            fig = px.scatter(
                data_frame=df,
                x=x,
                y=y,
                color=color,
                title=title,
                color_discrete_map=color_map,
                width=width,
                height=height,
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
        fig["layout"].pop("updatemenus")
        fig.show()
