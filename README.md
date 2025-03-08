# Dating Market Simulation

## Overview

This project simulates a dating market where users (males and females) engage in swiping interactions. The goal is to model user behavior based on attractiveness and like rates, track matches, and analyze trends over time.

## Features

- Generate a population of users with customizable male-to-female ratios.
- Simulate swiping interactions with probabilistic liking behavior.
- Track matches, seen users, and like rate evolution.
- Analyze user interactions using data visualization.
- Export results as a structured dataframe using Polars.

## Installation

Ensure you have Python installed along with the required dependencies: Use **UV** to setup the virtual environment.

```bash
uv sync
```

## Usage

### 1. Initialize a Market

```python
from dating_market.market import Market

market = Market(n_users=100, male_ratio=0.5)
market.run(days=10)
```

### 2. Retrieve Simulation Data

```python
df = market.to_dataframe()
```
