import itertools
import numpy as np
import pandas as pd
from typing import Literal, Union, List
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from functools import reduce
from pathlib import Path

# =============================================================================
# Utility transforms
# =============================================================================


def to_real_line(
    x: Union[float, np.ndarray],
    kind: Literal["Percentage", "Realvalue"],
) -> np.ndarray:
    """Transform data to the real line using either logit (percentage)
    or log (positive real)."""
    x = np.asarray(x, dtype=float)

    if kind == "Percentage":
        x = x / 100.0
        x = np.clip(x, 1e-10, 1 - 1e-10)
        return np.log(x / (1 - x))

    if kind == "Realvalue":
        x = np.clip(x, 1e-10, np.inf)
        return np.log(x)

    raise ValueError("kind must be 'Percentage' or 'Realvalue'.")


def zscore_by_month(
    df: pd.DataFrame,
    value_col: str,
    year_col: str = "Year",
    month_col: str = "Month",
) -> pd.DataFrame:
    """Cross-sectional z-scoring by month. Replace undefined values with 0."""
    if value_col not in df.columns:
        raise KeyError(f"Column '{value_col}' not in DataFrame.")

    out = df.copy()

    grp = out.groupby([year_col, month_col])[value_col]
    mean = grp.transform("mean")
    sd = grp.transform("std")

    z = (out[value_col] - mean) / sd
    z = z.fillna(0)

    out["z_normalised"] = z
    return out


def factor_grid(**factors) -> pd.DataFrame:
    """Cartesian product of factor levels."""
    for k, v in factors.items():
        if not isinstance(v, (list, np.ndarray)):
            raise TypeError(f"Factor '{k}' must be list-like.")
    combos = itertools.product(*factors.values())
    return pd.DataFrame(combos, columns=factors.keys())


# =============================================================================
# PCA Wrapper
# =============================================================================


def apply_monthly_pca(df: pd.DataFrame, metric_cols: List[str]) -> pd.DataFrame:
    """Fit a separate PCA for each (Year, Month) cross-section."""

    missing = [c for c in metric_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns for PCA: {missing}")

    out = []

    for (y, m), g in df.groupby(["Year", "Month"]):
        g = g.copy()
        X = g[metric_cols]

        # Validate non-empty cross-section
        if X.shape[0] < 2:
            raise ValueError(
                f"PCA requires ≥2 regions per month. Found {X.shape[0]} rows for {y}-{m}."
            )

        # Standardise metrics
        scaler = StandardScaler()
        X_sc = scaler.fit_transform(X)

        # Fit PCA
        pca = PCA(n_components=1)
        pc_scores = pca.fit_transform(X_sc)

        # Attach PC1 to dataset
        g["PC"] = pc_scores[:, 0]
        out.append(g)

        # Extract loadings (pc1 is index 0)
        # loadings = pca.components_[0]

        # Assemble a clean table of loadings
        # loading_df = pd.DataFrame({"Metric": metric_cols, "Loading_PC1": loadings})

        # print(loading_df.to_string(index=False))
    result = pd.concat(out, ignore_index=True)
    return result[["Year", "Region", "Month", "PC"]]


# =============================================================================
# SAFE READ FUNCTION
# =============================================================================


def read_csv_checked(path: str) -> pd.DataFrame:
    """Read CSV with early failure and reporting."""
    try:
        df = pd.read_csv(path)
        print(f"      ✓ Read {Path(path).stem.lstrip('_')}")
    except Exception as e:
        raise RuntimeError(f"Failed to read {path}: {e}") from e

    if df.empty:
        raise ValueError(f"File {path} loaded but is empty.")

    return df


# =============================================================================
# MAIN PIPELINE
# =============================================================================


def run_pipeline() -> pd.DataFrame:
    print("\n[1/11] Loading metric data...")
    M1 = read_csv_checked("data/metrics/waka_kotahi_mvr/01_P1_EV_analytics.csv")
    M2 = read_csv_checked("data/metrics/waka_kotahi_mvr/02_P1_FF_analytics.csv")
    M6a = read_csv_checked("data/metrics/emi_battery_solar/_06a_P1_BattPen.csv")
    M6b = read_csv_checked("data/metrics/emi_battery_solar/_06b_P1_BattPen.csv")
    M7 = read_csv_checked("data/metrics/emi_battery_solar/_07_P1_Sol.csv")
    M8 = read_csv_checked("data/metrics/emi_battery_solar/_08_P1_Batt.csv")
    M10 = read_csv_checked("data/metrics/gic/gic_gas_connections_analytics.csv")
    M12 = read_csv_checked("data/metrics/emi_generation/emi_generation_analytics.csv")

    dfs = [M1, M2, M6a, M6b, M7, M8, M10, M12]
    metric_names = [
        "_01_P1_EV",
        "_02_P1_FF",
        "_06a_P1_BattPen",
        "_06b_P1_BattPen",
        "_07_P1_Sol",
        "_08_P1_Batt",
        "_10_P1_Gas",
        "EnergyRenew",
    ]

    print("\n[2/11] Scoping to Total Sub_Category...")
    dfs = [df[df["Sub_Category"] == "Total"].copy() for df in dfs]

    print("\n[3/11] Cleaning redundant columns...")
    drop_cols = ["Metric_Group", "Category", "Sub_Category"]
    dfs = [df.drop(columns=drop_cols, errors="ignore") for df in dfs]

    print("\n[4/11] Restricting years to 2020–2024...")
    dfs = [df[(df["Year"] >= 2020) & (df["Year"] <= 2024)].copy() for df in dfs]

    print("\n[5/11] Extracting key columns...")
    interim = []
    full_joined = []
    for df, metric in zip(dfs, metric_names):
        if metric not in df.columns:
            raise KeyError(f"Expected metric column '{metric}' not found.")
        tmp = df[["Year", "Region", "Month", metric]].rename(columns={metric: "Metric"})
        tmp2 = df[["Year", "Region", "Month", metric]]
        interim.append(tmp)
        full_joined.append(tmp2)

    print("\n[6/11] Creating full Region-Year-Month grid...")
    regions = sorted(M1["Region"].unique())
    full = factor_grid(
        Region=regions,
        Year=np.arange(2020, 2025),
        Month=np.arange(1, 13),
    )
    print(f"      ✓ Grid has {len(full)} rows")

    print("\n[7/11] Joining metric datasets to full grid...")
    completed = []
    full_joined2 = []
    for df, df2 in zip(interim, full_joined):
        merged = full.merge(df, how="left", on=["Region", "Year", "Month"]).fillna(0)
        merged2 = full.merge(df2, how="left", on=["Region", "Year", "Month"]).fillna(0)
        completed.append(merged)
        full_joined2.append(merged2)

    actuals_df = reduce(
        lambda left, right: pd.merge(
            left, right, how="outer", on=["Year", "Month", "Region"]
        ),
        full_joined2,
    )

    print("\n[8/11] Transforming metrics...")

    kinds = [
        "Realvalue",
        "Realvalue",
        "Percentage",
        "Percentage",
        "Realvalue",
        "Realvalue",
        "Realvalue",
        "Percentage",
    ]
    transformed = []
    for i, (df, kind) in enumerate(zip(completed, kinds), start=1):
        df = df.copy()
        df["z"] = to_real_line(df["Metric"], kind=kind)
        df = zscore_by_month(df, "z")
        df = df[["Year", "Region", "Month", "z_normalised"]].rename(
            columns={"z_normalised": f"V{i}"}
        )
        transformed.append(df)
    print("      ✓ Converted to real line")
    print("      ✓ Normalised values by month")
    print("      ✓ Prepared data for join")

    print("\n[9/11] Joining transformed metrics...")
    comb = reduce(
        lambda left, right: pd.merge(
            left, right, how="outer", on=["Year", "Month", "Region"]
        ),
        transformed,
    )

    print("\n[10/11] Running month-specific PCA...")
    comb_pc = apply_monthly_pca(comb, ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8"])
    print("      ✓ Use sklearn to standardise for each Year-Month combination")
    print("      ✓ Add first principal component to data")

    sendOut = pd.merge(
        comb_pc, actuals_df, how="outer", on=["Year", "Month", "Region"], indicator=True
    )
    assert (sendOut["_merge"] == "both").all(), (
        "Merge mismatch detected:\n"
        + sendOut.loc[
            sendOut["_merge"] != "both", ["Year", "Month", "Region", "_merge"]
        ].to_string(index=False)
    )

    print("\n[10/11] Writing file to disk")
    sendOut.to_csv(path_or_buf=Path("data/ScoreCard.csv"))

    return sendOut


# =============================================================================
# EXECUTE PIPELINE
# =============================================================================

if __name__ == "__main__":
    final_output = run_pipeline()
    print("\n✓ Pipeline complete")
    print("\nFinal dataset shape:", final_output.shape)
    print("Columns:", list(final_output.columns))
