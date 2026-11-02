from pathlib import Path

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