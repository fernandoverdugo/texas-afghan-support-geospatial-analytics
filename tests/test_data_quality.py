from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "asp_zip_metrics.csv"


def load():
    return pd.read_csv(DATA, dtype={"zip_code": str})

def test_expected_shape_and_unique_zip_codes():
    df = load()
    assert len(df) == 192
    assert df["zip_code"].nunique() == len(df)


def test_expected_metro_areas():
    df = load()
    assert set(df["city"]) == {
        "Austin",
        "Dallas",
        "Fort Worth",
        "Houston",
        "San Antonio",
    }


def test_nonnegative_core_metrics():
    df = load()
    columns = [
        "total_households",
        "total_participants",
        "ra_july",
        "ra_august",
        "ra_september",
        "ra_total",
        "fwc_total",
    ]
    assert (df[columns] >= 0).all().all()


def test_total_ra_equals_monthly_sum():
    df = load()
    monthly = df["ra_july"] + df["ra_august"] + df["ra_september"]
    difference = (monthly - df["ra_total"]).abs()
    assert difference.max() < 0.02


def test_enrollment_is_cumulative_and_matches_households():
    df = load()
    assert (df["enrolled_july_cumulative"] <= df["enrolled_august_cumulative"]).all()
    assert (df["enrolled_august_cumulative"] <= df["enrolled_september_cumulative"]).all()
    assert (df["enrolled_september_cumulative"] == df["total_households"]).all()
    assert (df["total_participants"] >= df["total_households"]).all()


def test_fwc_total_is_consistent_with_monthly_attendance():
    df = load()
    monthly = df[["fwc_july", "fwc_august", "fwc_september"]]
    assert (df["fwc_total"] >= monthly.max(axis=1)).all()
    assert (df["fwc_total"] <= monthly.sum(axis=1)).all()


def test_expected_columns_are_present():
    df = load()
    expected = {
        "zip_code", "city", "total_households", "total_participants",
        "ra_july", "ra_august", "ra_september", "ra_total",
        "fwc_july", "fwc_august", "fwc_september", "fwc_total",
        "enrolled_july_cumulative", "enrolled_august_cumulative",
        "enrolled_september_cumulative", "top10_ra_city",
        "latitude", "longitude", "ra_per_household",
        "participants_per_household", "ra_aug_vs_july_pct",
        "ra_sep_vs_aug_pct",
    }
    assert expected.issubset(df.columns)


def test_derived_rates_reconcile():
    df = load()
    ra_per_household = df["ra_total"] / df["total_households"]
    participants_per_household = df["total_participants"] / df["total_households"]
    assert (df["ra_per_household"] - ra_per_household).abs().max() < 1e-6
    assert (df["participants_per_household"] - participants_per_household).abs().max() < 1e-6


def test_top10_flag_count_by_metro():
    df = load()
    flagged = df.groupby("city")["top10_ra_city"].sum()
    assert (flagged == 10).all()

def test_project_summary_matches_source_data():
    df = load()
    summary = json.loads((ROOT / "data" / "processed" / "project_summary.json").read_text())

    assert summary["geography"]["zip_codes"] == len(df)
    assert summary["geography"]["metro_areas"] == df["city"].nunique()
    assert summary["program_totals"]["households"] == int(df["total_households"].sum())
    assert summary["program_totals"]["participants"] == int(df["total_participants"].sum())
    assert summary["program_totals"]["rental_assistance"] == float(df["ra_total"].sum())
    assert summary["program_totals"]["financial_wellness_attendees"] == int(df["fwc_total"].sum())

    expected_share = round(float(df.nlargest(10, "ra_total")["ra_total"].sum() / df["ra_total"].sum()), 4)
    city_ra = df.groupby("city")["ra_total"].sum().sort_values(ascending=False)
    assert summary["concentration"]["top_10_zip_rental_assistance_share"] == expected_share
    assert summary["concentration"]["leading_metro"] == city_ra.index[0]
    assert summary["concentration"]["leading_metro_rental_assistance"] == float(city_ra.iloc[0])


def test_readme_preview_asset_is_present():
    svg = (ROOT / "assets" / "rental_assistance_by_city.svg").read_text()
    for city in ["Austin", "Dallas", "Fort Worth", "Houston", "San Antonio"]:
        assert city in svg
