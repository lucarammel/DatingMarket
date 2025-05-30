import marimo

__generated_with = "0.13.14"
app = marimo.App()


@app.cell(hide_code=True)
def _():
    import marimo

    return (marimo,)


@app.cell(hide_code=True)
def _(marimo):
    marimo.md(
        r"""
        # 💘 Modeling a Dating Market: A Simulation with Swipes, Scores, and Strategy
        """
    )
    return


@app.cell(hide_code=True)
def _(marimo):
    marimo.md(
        r"""
        ## 1. Motivation

        In online dating, people make quick decisions—liking or skipping potential matches based on a mix of instinct and strategy. But how do attractiveness, behavior, and visibility evolve in such an ecosystem?

        This notebook presents a simplified simulation of a dating market that tries to answer:

        * How does initial attractiveness impact match rates?
        * How does being liked change behavior over time?
        * What happens when the male-female ratio is skewed?
        """
    )
    return


@app.cell(hide_code=True)
def _(marimo):
    marimo.md(
        r"""
        ## 2. Simulation Overview

        ### 2.1 User: **The atomic agent** of the market
        Each user is either a Male or Female, and has:

        * An attractiveness_score (between 0.2–0.8)
        * A like_rate: how likely they are to like others
        * A likes_limit: number of swipes per simulation round
        * Dynamic fields like matches, liked_by, seen_users, etc.

        ### 2.2 Modeling Assumptions

        * **Initial distributions**: 
            * Attractiveness is sampled from a Gaussian around 0.5, clipped between [0.2, 0.8].  
            * Like rate similarly sampled, reflecting varied user pickiness.

        * **Gender targeting**: Heterosexual preference is assumed (each user looks for opposite-gender profiles).

        * **Visibility & popularity bias**: Users don’t see all profiles. Instead, a weighted random sample favors more attractive profiles using a configurable probability_ratio_between_best_and_worth.

        * **Swipe decision:**
        A user swipes right on another user with probability:
        $$P(\text{like}) = \min\left(1 + \text{like\_rate} \cdot \log(\text{other.attractiveness}),\ 1\right)$$
        If a random number < $P(\text{like})$, then it's a **like**.

        * **Match detection:**
        If **both users like each other**, it's a match:
        $$\text{match} \iff u \in v.\text{liked\_users} \land v \in u.\text{liked\_users}$$

        * **Match rate:**
        Updated daily as:
        $$\text{match\_rate} = \frac{\# \text{matches}}{\# \text{liked\_users}} \quad (\text{if liked > 0})$$

        * **Like rate evolution:**
        Adjusted randomly based on match rate:
        $$\text{like\_rate} \leftarrow 
        \begin{cases} 
        \text{like\_rate} - \text{like\_rate} \cdot |\mathcal{N}(0, 0.1)| & \text{if match\_rate} \geq 0.33 \\ 
        \text{like\_rate} + \text{like\_rate} \cdot |\mathcal{N}(0, 0.1)| & \text{if match\_rate} \leq 0.1 \\ 
        \text{(no change)} & \text{otherwise} 
        \end{cases}$$
        $$\text{like\_rate} \in [0, 1]$$

        * **Like limit evolution:**
        Like budget is adjusted daily:
            * If match rate is high ($\geq 0.33$): decrease limit.
            * If match rate is low ($\leq 0.1$): increase limit.

        $$\text{likes\_limit} \leftarrow \text{likes\_limit} \pm \text{likes\_limit} \cdot |\mathcal{N}(0, 1)|$$

        Clipped between `lower_likes_limit` and `upper_likes_limit`.
        """
    )
    return


@app.cell
def _():
    from dating_market import Market

    m = Market(n_users=3000, male_ratio=0.7, n_days=10)
    m.run()
    return (m,)


@app.cell(hide_code=True)
def _(marimo):
    marimo.md(
        r"""
        Each user is shown a sample of unseen users of the opposite gender, makes like/dislike decisions, and potential matches are updated. Users also update their behavior based on recent interaction stats.
        """
    )
    return


@app.cell
def _(m):
    m.get_users_data().sort("match_rate", descending=True)
    return


@app.cell(hide_code=True)
def _(marimo):
    marimo.md(
        r"""
        This returns a table of stats for each user:

        * **like_rate_start** vs **like_rate_end**: how preferences evolved

        * **matches**, **likes**, **liked_by**: behavioral outcomes

        * **seen_by**, **liked_by_rate**: visibility and popularity indicators
        """
    )
    return


@app.cell(hide_code=True)
def _(m):
    m.get_market_data().sort("matches_cumulative", descending=True)
    return


@app.cell
def _(m):
    m.plot_histogram(
        df=m.get_users_data(),
        x="attractiveness_score",
        y=None,
        title="Attractiveness_score",
        color="gender",
        slider_column="male_ratio",
        width=700,
        height=500,
    )
    return


@app.cell
def _(m):
    m.plot_histogram(
        df=m.get_users_data(),
        x="like_rate_evolution",
        y=None,
        title="Like rate evolution",
        color="gender",
        slider_column="male_ratio",
        width=700,
        height=500,
    )
    return


@app.cell
def _(m):
    m.plot_histogram(
        df=m.get_users_data(),
        x="match_rate",
        y=None,
        title="Match rate distribution",
        color="gender",
        slider_column="male_ratio",
        width=700,
        height=500,
    )
    return


@app.cell
def _(m):
    import polars as pl
    df = m.get_users_data().with_columns(pl.col('match_rate').qcut(10, labels=['d10%', 'd20%', 'd30%', 'd40%', 'd50%','u50%', 'u40%', 'u30%', 'u20%', 'u10%']).alias('decile'))

    m.plot_histogram(
        df=df,
        x="decile",
        y=None,
        title="Match rate decile",
        color="gender",
        slider_column="male_ratio",
        width=700,
        height=500,
        category_order={"decile":['d10%', 'd20%', 'd30%', 'd40%', 'd50%','u50%', 'u40%', 'u30%', 'u20%', 'u10%']}
    )


    return


@app.cell(hide_code=True)
def _(m):
    m.plot_scatter(
        df=m.get_users_data(),
        x="match_rate",
        y="liked_by_rate",
        title="Match rate vs Liked by rate",
        color="gender",
        slider_column="male_ratio",
        width=700,
        height=500,
    )

    return


@app.cell(hide_code=True)
def _(m):
    m.plot_scatter(
        df=m.get_users_data(),
        x="attractiveness_score",
        y="match_rate",
        title="Match rate vs Attractiveness score",
        color="gender",
        slider_column="male_ratio",
        width=700,
        height=500,
    )

    return


@app.cell(hide_code=True)
def _(m):
    m.plot_scatter(
        df=m.get_users_data(),
        x="attractiveness_score",
        y="liked_by_rate",
        title="Liked by rate vs Attractiveness score",
        color="gender",
        slider_column="male_ratio",
        width=700,
        height=500,
    )

    return


if __name__ == "__main__":
    app.run()
