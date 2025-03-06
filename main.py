from src.market import Market

if __name__ == "__main__":
    market = Market(n_users=100, male_ratio=0.2)

    market.run(days=10)
