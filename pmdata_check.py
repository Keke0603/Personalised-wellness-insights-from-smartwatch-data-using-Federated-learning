"""
pmdata_check.py
Dataset audit and integrity verification script for PMData.
"""
from src.data_audit import audit_dataset, RESULTS_DIR, CHECKS_DIR

if __name__ == "__main__":
    df = audit_dataset("Europe/Oslo")
    df_save = df.drop(columns=["days_rhr_raw"])
    df_save.to_csv(RESULTS_DIR / "data_audit.csv", index=False)
    df_save.to_csv(CHECKS_DIR / "pmdata_summary.csv", index=False)
    print("Audit completed successfully.")
    print(df_save.to_string(index=False))
