# Dating Market Simulation

A comprehensive simulation modeling dating app dynamics, user behavior evolution, and market trends through probabilistic interactions.

## Overview

This project simulates a heterosexual dating market where users engage in swiping interactions based on attractiveness scores, like rates, and evolving behavioral patterns. The simulation models realistic dating app dynamics including visibility bias, match detection, and adaptive user behavior.

### Key Research Questions

- How does initial attractiveness impact long-term match rates?
- How do users adapt their swiping behavior based on success rates?
- What market dynamics emerge with different male-to-female ratios?
- How does visibility bias affect user outcomes?

## Model Architecture

### Core Components

#### 1. **User Model**

Each user is characterized by:

- **Static attributes**: `id`, `gender`, `attractiveness_score` (0.2-0.8)
- **Behavioral parameters**: `like_rate`, `likes_limit`, `swipe_limit`
- **Dynamic state**: matches, liked users, seen profiles, daily counters
- **Historical tracking**: like rate evolution, match rate history, daily statistics

#### 2. **Participants Manager**

Handles user populations with:

- Configurable male-to-female ratios
- Weighted profile selection favoring attractive users
- Daily interaction orchestration
- Data collection and export

#### 3. **Market Simulator**

Orchestrates multiple scenarios:

- Support for single or multiple gender ratio experiments
- Multi-day simulation cycles
- Comprehensive data aggregation
- Visualization and analysis tools

### Mathematical Model

#### Swiping Decision

Users decide to like profiles based on a logarithmic attractiveness function:

```
P(like) = min(1 + like_rate × log(other.attractiveness_score), 1)
P(like) = max(P(like), 0)
```

#### Match Detection

Matches occur when both users have liked each other:
```
match ↔ (userA ∈ userB.liked_users) ∧ (userB ∈ userA.liked_users)
```

#### Behavioral Evolution

Users adapt their behavior daily based on match success:

**Match Rate Calculation:**

```
match_rate = matches_count / liked_users_count (if liked > 0)
```

**Like Rate Adaptation:**

```
if match_rate ≥ 0.33:    like_rate -= like_rate × |N(0, 0.1)|  # Become pickier
if match_rate ≤ 0.10:    like_rate += like_rate × |N(0, 0.1)|  # Become less picky
like_rate ∈ [0, 1]
```

**Daily Like Limit Adjustment:**
```
if match_rate ≥ 0.33:    likes_limit -= |N(0, 1)| × likes_limit  # Reduce activity
if match_rate ≤ 0.10:    likes_limit += |N(0, 1)| × likes_limit  # Increase activity
likes_limit ∈ [lower_limit, upper_limit]
```

### Design Choices

#### 1. **Probabilistic Distributions**

- **Attractiveness**: Normal distribution N(0.5, 0.2) clipped to [0.2, 0.8] to avoid extreme outliers
- **Initial Like Rate**: N(0.5, 0.1) clipped to [0.2, 0.8] for behavioral diversity
- **Behavioral Updates**: Gaussian noise ensures realistic, gradual adaptation

#### 2. **Visibility Bias**

Users see profiles through weighted random sampling where attractive profiles have up to 5× higher visibility probability, simulating real app algorithms.

#### 3. **Adaptive Behavior**

- **Success breeds selectivity**: High match rates → reduced like rates and limits

- **Desperation mechanics**: Low success → increased activity and lower standards

- **Bounded rationality**: All parameters have realistic limits

#### 4. **Heterosexual Model**

Simplified to male-female interactions for clearer analysis of gender ratio effects and behavioral differences.

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd DatingAppSimulation

# Setup environment and install dependencies
uv sync

# Install development dependencies (optional)
uv sync --group dev
```

### Basic Usage

#### 1. Simple Simulation

```python
from dating_market import Market

# Create market with 1000 users, 50% male ratio, 10 days
market = Market(n_users=1000, male_ratio=0.5, n_days=10)

# Run simulation
market.run()

# Get user statistics
users_data = market.get_users_data()
print(users_data.head())

# Get daily market dynamics
market_data = market.get_market_data()
print(market_data.head())
```

#### 2. Multi-Scenario Analysis

```python
# Compare different gender ratios
market = Market(n_users=2000, male_ratio=[0.3, 0.5, 0.7], n_days=15)
market.run()

# Analyze by scenario
users_data = market.get_users_data()
balanced_scenario = users_data.filter(pl.col("male_ratio") == 0.5)
male_heavy_scenario = users_data.filter(pl.col("male_ratio") == 0.7)
```

#### 3. Visualization
```python
# Plot match rate vs attractiveness
fig = market.plot_scatter(
    df=market.get_users_data(),
    x="attractiveness_score", 
    y="match_rate",
    color="gender",
    title="Match Rate vs Attractiveness"
)
fig.show()

# Plot behavioral evolution over time
market_data = market.get_market_data()
fig = market.plot_scatter(
    df=market_data,
    x="day",
    y="like_rate", 
    color="gender",
    title="Like Rate Evolution",
    slider_column="day"
)
fig.show()
```

## Output Data

### User-Level Statistics (`get_users_data()`)

- `attractiveness_score`: User's attractiveness (0.2-0.8)
- `like_rate_start/end`: Initial vs final pickiness
- `matches`: Total matches achieved
- `match_rate`: Success rate (matches/likes)
- `liked_by`: Times user was liked
- `liked_by_rate`: Popularity (liked_by/seen_by)
- `seen_by/seen_users`: Visibility metrics

### Market-Level Dynamics (`get_market_data()`)

- Daily progression of matches, likes, swipes
- Cumulative statistics over time
- Like rate and match rate evolution
- Per-user daily activity tracking

