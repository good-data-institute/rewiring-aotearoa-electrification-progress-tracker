import pandas as pd
from pipeline import gold_aggregate, gold_aggregate_nz, silver_transform, bronze_ingest   # your gold_aggregate function
from metrics_config import metrics_config  # your metrics dictionary

def main():
    print(f"📥 Downloading bronze data...")
    bronze_ingest()
    print(f"📥 Creating silver layer...")
    silver_transform()
    SILVER_PATH = "data/silver/mvr_silver_cleaned.parquet"
    print(f"📥 Loading silver layer from {SILVER_PATH} ...")
    df_silver = pd.read_parquet(SILVER_PATH)
    print(f"✅ Loaded {len(df_silver):,} rows")

    print("⚡ Running gold aggregation pipeline ...")
    gold_aggregate(df_silver, metrics_config)
    #gold_aggregate_nz(df_silver, metrics_config)

    print("🎉 Pipeline finished successfully!")

if __name__ == "__main__":
    main()
