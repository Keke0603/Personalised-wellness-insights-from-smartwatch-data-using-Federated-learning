# Project Context

- Project: personalized wellness insights from smartwatch data using federated learning (Flower), 1D CNN, PMData only. Each participant = one federated client.
- Task: predict TARGET for the next day from the previous WINDOW days of features.
- Rules: splits are chronological per user, never shuffled; normalize per user using TRAIN data only; fixed seeds; the test set is never used to choose anything.
- Results files use columns: model, user, checkpoint, seed, mae, rmse, r2, n_test (checkpoint empty when not applicable).
- Stack: Python, pandas, numpy, PyTorch, Flower simulation, scipy, matplotlib, streamlit.
- Rule for every task: inspect files before assuming their layout, keep code simple, print a summary at the end, and list assumptions and anything unverified.

## Decisions (Step 2 Pipeline)

- **Target**: `readiness` on day `t` from `pmsys/wellness.csv`. Actual range observed in PMData is `[0, 10]`, mean ~4.95. Target remains in original readiness units (no per-user target scaling).
- **Features** (smartwatch data only, 8 features + 8 observation indicator channels = 16 channels total):
  1. `steps`: daily steps sum from `fitbit/steps.json`. Days with 0 steps are treated as "not worn" (missing/NaN).
  2. `very_active_minutes`: daily from `fitbit/very_active_minutes.json`.
  3. `moderately_active_minutes`: daily from `fitbit/moderately_active_minutes.json`.
  4. `lightly_active_minutes`: daily from `fitbit/lightly_active_minutes.json`.
  5. `resting_heart_rate`: daily from `fitbit/resting_heart_rate.json` (0.0/null is missing); fall back to `sleep_score.csv` `resting_heart_rate` if missing.
  6. `sleep_overall_score`: daily from `fitbit/sleep_score.csv` (`overall_score`).
  7. `deep_sleep_in_minutes`: daily from `fitbit/sleep_score.csv` (`deep_sleep_in_minutes`).
  8. `restlessness`: daily from `fitbit/sleep_score.csv` (`restlessness`).
  - No wellness column is used as an input feature.
  - Second-level `heart_rate.json` is not parsed.
- **Input Window**: Calendar days `t-7` through `t-1` (strictly prior to day `t`; no data from day `t` or later may enter the input window).
- **Window Parameters**:
  - `WINDOW = 7`
  - `TEST_DAYS = 14` (last 14 usable target days per client)
  - `VAL_RATIO = 0.15` (15% of usable days before test window, rounded)
  - `MIN_OBSERVED_DAYS = 4` (at least 4 worn/observed days within the 7-day input window)
  - `MIN_USABLE_DAYS = 60` (minimum usable target windows per client)
  - `SEEDS = [0, 1, 2]`
  - `CHECKPOINTS = [15, 30, 60, 75, 90]`
- **Participant Filtering**:
  - `p12`: Excluded explicitly due to almost complete absence of sleep data (only 1 night recorded).
  - `p03` and `p13`: Dropped by `MIN_USABLE_DAYS = 60` (`p03` has 58 usable days, `p13` has 46 usable days).
  - 13 retained participants: `p01, p02, p04, p05, p06, p07, p08, p09, p10, p11, p14, p15, p16`.
- **Cleaning & Alignment Rules**:
  - Timestamps in `sleep_score.csv` and `wellness.csv` converted to local time (`Europe/Oslo`).
  - Wellness duplicate reports on the same day: keep the last submission of the day.
  - Sleep duplicates (naps): select main sleep record with maximum `duration_score` (tiebreak: higher `overall_score`).
  - Imputation: missing feature values in any window are filled with that user's TRAIN-period median (val/test data never used).
  - Normalization: Z-score continuous features per user using TRAIN statistics only (`mean` and `std`). Observed flags remain 0.0 or 1.0.
