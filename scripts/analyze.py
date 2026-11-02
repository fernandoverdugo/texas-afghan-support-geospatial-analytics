from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "asp_zip_metrics.csv"
OUT = ROOT / "data" / "processed"
ASSETS = ROOT / "assets"


def money(value):
    return f"${value:,.0f}"


def main():
    df = pd.read_csv(DATA, dtype={"zip_code": str})
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    city = (
        df.groupby("city", as_index=False)
        .agg(
            zip_codes=("zip_code", "nunique"),
            households=("total_households", "sum"),
            participants=("total_participants", "sum"),
            rental_assistance=("ra_total", "sum"),
            fwc_attendees=("fwc_total", "sum"),
        )
        .sort_values("rental_assistance", ascending=False)
    )
    city.to_csv(OUT / "city_summary.csv", index=False)

    top = df.nlargest(15, "ra_total")[
        ["zip_code", "city", "total_households", "total_participants", "ra_total"]
    ]
    top.to_csv(OUT / "top_zip_codes_by_ra.csv", index=False)

    print("Portfolio dataset summary")
    print("-------------------------")
    print(f"ZIP codes: {len(df):,}")
    print(f"Households: {df['total_households'].sum():,.0f}")
    print(f"Participants: {df['total_participants'].sum():,.0f}")
    print(f"Rental assistance: {money(df['ra_total'].sum())}")
    print(f"Median ZIP rental assistance: {money(df['ra_total'].median())}")
    print()
    print("City summary")
    print(city.to_string(index=False))

    plt.figure(figsize=(8, 5))
    plot_city = city.sort_values("rental_assistance")
    plt.barh(plot_city["city"], plot_city["rental_assistance"])
    plt.xlabel("Rental assistance ($)")
    plt.ylabel("Metro area")
    plt.title("Rental Assistance by Metro Area")
    plt.tight_layout()
    plt.savefig(ASSETS / "rental_assistance_by_city.png", dpi=160)
    plt.close()

    plt.figure(figsize=(7, 5))
    plt.scatter(df["total_households"], df["ra_total"], alpha=0.65)
    plt.xlabel("Households")
    plt.ylabel("Rental assistance ($)")
    plt.title("Households and Rental Assistance by ZIP Code")
    plt.tight_layout()
    plt.savefig(ASSETS / "households_vs_ra.png", dpi=160)
    plt.close()


if __name__ == "__main__":
    main()