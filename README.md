# SmartFit: Federated Learning & Personal Wellness Insights

Personalized wellness insights and next-day readiness prediction from longitudinal smartwatch telemetry using Federated Learning (Flower) on the PMData dataset.

---

## 🚀 Running the Streamlit Dashboard

To launch the mobile-friendly interactive dashboard, execute the following command in your terminal from the project root:

```bash
streamlit run app/dashboard.py
```

*(On Windows environments where Python Scripts are not in the system PATH, you can also run: `py -m streamlit run app/dashboard.py`)*

---

## 📱 Single-Screen Analytics Dashboard Structure

The dashboard is built with a responsive desktop-first layout with sidebar radio navigation:

1. **Sidebar Navigation & Client Switcher**:
   - Quick navigation menu across top-level views: **Dashboard**, **Recommendations**, **Data**, **Results**, **Correlation finder**, **Daily report**, **Privacy**, **Research view**, and **About**.
   - Active client selector (retained cohort `p01`–`p16`) with persistent session state and one-click quick switch.
2. **Global Header & Checkpoint Controls**:
   - History checkpoint selector (`15, 30, 60, 90` days or `All` recorded days).
   - Trailing date selector ("View ending on") with strict window isolation.
   - All pages dynamically respond to client, checkpoint, and viewed date selections.
3. **Dashboard Page**:
   - Dynamic anomaly alert banner directly under header filters.
   - Collapsible 30-day anomaly alert log with CSV export and trajectory chart.
   - 5 KPI summary cards: Today's Baseline Status, Sleep Quality, Daily Steps, Resting Heart Rate, and 7-day Alert Frequency.
   - Biometric trajectory panels against personal rolling baseline bands.
   - Bottom analysis tabs: **Model Benchmark**, **Privacy & Edge Network**, and **Scientific Claims**.
4. **Dedicated Recommendations Page**:
   - Personalised, rule-based recommendations combining personal rolling baselines and verified sensor patterns.

---

## 🚨 Anomaly Alerts

The SmartFit Anomaly Alerts engine (`src/alerts.py`) evaluates longitudinal daily biometric telemetry against each user's personalized 28-day rolling baseline ($\text{median} \pm 1.4826 \times \text{MAD}$) using strictly historical observation days ($[t-28, t-1]$):

- **Data Isolation & Leakage Prevention**:
  - Requires at least 14 observed historical days within the 28-day window before issuing any alert; days with $< 14$ observed days are designated as *insufficient baseline* (learning).
  - Unworn/missing days are skipped, never imputed as anomalies.
  - Baseline calculations strictly use days prior to day $t$ (shifted by one day) and never exceed the active learning checkpoint.
- **Alert Levels**:
  - **Normal**: All evaluated metrics remain within the personal normal band ($|z_{\text{robust}}| < 2.0$).
  - **Watch**: A single metric deviates outside the personal band ($2.0 \le |z_{\text{robust}}| < 3.0$).
  - **Alert**: Triggered when:
    1. An extreme biometric deviation occurs ($|z_{\text{robust}}| \ge 3.0$), OR
    2. Two or more distinct metrics fall outside the band on the same calendar day, OR
    3. The same metric remains outside the band on two consecutive observed calendar days.
- **Interactive Dashboard Features**:
  - Dynamic status banner (`st.error`, `st.warning`, `st.success`) summarizing today's telemetry directly under the global header.
  - 7-day anomaly event counter and top flagged channel KPI metrics.
  - Trailing 30-day collapsible alert audit log with colored severity badges, biometric values, personal normal ranges, and CSV export (`st.download_button`).
  - Interactive Plotly 30-day trajectory with out-of-band alerts highlighted in red diamond markers.
- **Disclaimer**:
  - **Wellness insight, not medical advice.** All anomaly detections, baseline ranges, and wellness explanations are intended solely for personal health lifestyle exploration and educational demonstration replaying recorded PMData. They do not constitute diagnostic or clinical evaluations.

---

## 💡 Personalised Recommendations

The SmartFit Personalised Recommendations engine (`src/recommendations.py`) provides rule-based, transparent wellness insights tailored to each participant:

- **Dual-Source Generation**:
  1. **Baseline-Driven (Recent Trailing State)**: Compares the participant's trailing 7-day median values to their personal 28-day baseline band ($\text{median} \pm 2 \times 1.4826 \times \text{MAD}$):
     - *Sleep Routine*: Identifies multi-day drops in sleep score or deep sleep, recommending consistent bedtime wind-down and reduced evening stimulation.
     - *Sleep Environment*: Triggers when night-time restlessness is elevated, suggesting cooler, darker, and quieter surroundings.
     - *Pacing & Hydration*: Flags 3+ days of elevated resting heart rate, suggesting gentle pacing, hydration, and rest (with advice to speak with a healthcare professional if unwell).
     - *Activity Goals*: Suggests small, realistic walking goals based on their *own* typical baseline (not a generic 10,000 steps).
     - *Recovery Balance*: Identifies high activity paired with low readiness/sleep, suggesting active recovery sessions.
     - *Routine Maintenance*: Acknowledges stable routines when all core telemetry tracks smoothly within normal limits.
  2. **Pattern-Driven (Personal Sensor Associations)**: Incorporates verified statistically reliable pairwise correlations ($n \ge 30$, FDR $q < 0.10$, sign-stable across temporal halves, $|r| \ge 0.25$) at the selected checkpoint to highlight how daytime habits connect with morning energy.
- **Ranking & Prioritization**:
  - Dynamically links to active alerts: if an active Alert or Watch is present on the viewed day, recommendations addressing the affected metric are promoted first.
  - Ranked by urgency (`High` $\rightarrow$ Pattern-Driven $\rightarrow$ `Medium` $\rightarrow$ `Low`) and capped at at most 5 items for clarity.
- **Interactive UI & Dedicated Navigation Page**:
  - Accessible directly as a dedicated top-level navigation item **"Recommendations"** in the sidebar menu (placed directly alongside Dashboard).
  - Synchronized with active client and history checkpoint selections across pages.
  - Displays a "Your current status" summary line (Sleep, Activity, Resting HR, Readiness vs personal baseline).
  - Features an active alert banner (Alert / Watch) that automatically prioritizes alert-relevant recommendations first.
  - Actionable recommendation cards with color-coded priority badges (`High`, `Medium`, `Low`), categories, observed numerical evidence, and confidence indicators (max 5 items).
  - Trajectory Plotly chart visualizing the metric behind the primary recommendation with personal 28-day baseline band and anomaly flags.
  - Expandable cohort comparison table ("Compare all participants") summarizing recommendation counts, top advice, and pattern-driven items across all participants.
  - Dual export options via `st.download_button`: export recommendations as CSV, or download the comprehensive personal markdown report (`results/recommendations/<participant>.md`).
- **Wellness Disclaimer**:
  - **Wellness insight, not medical advice.** Patterns are associations in personal telemetry data, not proof of cause. Zero diagnostic or treatment language is used.

---

## 🏃 Personal Client (Google Fit)

SmartFit supports private local ingestion and personal telemetry analysis for personal client **Keerthana** from Google Fit Takeout archives:

- **What It Is**:
  - Standalone ingestion script (`src/ingest_google_fit.py`) reading `Daily activity metrics.csv` directly from a Google Takeout zip (`data_private/takeout.zip`).
  - Covers 2026-10-05 to 2026-11-01 (27 full days + 1 partial day), recording pedometer steps, move minutes (Google Fit definition), daily calories, walking distance, and heart points.
  - Automatically identifies days where the phone was not carried (`steps < 1,500`), keeping them in charts with hollow markers while excluding them from baseline calculations and anomaly alerts.
  - Computes personal 28-day rolling median $\pm 1.4826 \times \text{MAD}$ baselines strictly using past days ($t \ge 14$ days, starting on 2026-10-19).
- **What Is Missing**:
  - Sleep architecture (overall sleep score, deep sleep minutes, tossing-and-turning restlessness ratio) is not recorded by the phone.
  - Continuous resting heart rate is absent (only 3 spot pulse logs across the month).
  - Subjective morning readiness logs are not tracked.
  - All missing physiological metrics are preserved as missing (`NaN`) and never zero-imputed.
- **Why It Is Excluded from Federated Training**:
  - The federated 1D-CNN temporal architecture strictly requires a 16-channel input representation across sleep stages, continuous pulse, and activity.
  - Applying the model to phone-only pedometer telemetry would require zero-filling 10 out of 16 channels, violating clinical validity standards.
  - Keerthana is strictly a dashboard-only client and never participates in federated rounds, model benchmarks, or cross-cohort participant comparisons.
- **Privacy & Repo Hygiene**:
  - **"Personal data stays on this machine."**
  - Raw Takeout archives (`data_private/`) and processed daily summaries (`data/personal/`) are added to `.gitignore` and never committed to version control.
  - Highly private attributes (body weight, height, speed, GPS traces) are permanently dropped during ingestion.
  - Accessible exclusively via its own visually separated `"My data"` sidebar section.
- **28-Day Anomaly View & Recommendations**:
  - **Stacked Longitudinal Charts**: 4 stacked Plotly subplots on a shared x-axis (Daily Steps, Move Minutes, Heart Points, Energy Burned/Calories with non-zero y-axis `1400–2050`).
  - **Visual Language**: Light-grey usual-range band ($\text{median} \pm 2 \times 1.4826 \times \text{MAD}$), dashed baseline median, amber diamond markers (`symbol="diamond"`) for Watch, red triangle markers (`symbol="triangle-up"`) for Alert with values labeled, hollow circle markers (`symbol="circle-open"`) for not-worn days (`steps < 1,500`), and light-grey pre-baseline shading before 2026-10-22 with caption *"No baseline yet (needs 14 valid days)"*.
  - **Verified Anomaly Findings**: First baseline strictly on 2026-10-22; 4 not-worn days suppressed; 0 heart points anomalies; exactly 4 Alert-level anomalies flagged (2026-10-29 Move minutes 31, low; 2026-10-29 Calories 1,572, low; 2026-10-30 Move minutes 154, high; 2026-10-30 Steps 10,850, high).
  - **Anomaly Table & Export**: Tabular view with date, metric, value, usual range, direction, robust z-score, colored severity badges, and one-click CSV download (`keerthana_28day_anomalies.csv`).
  - **Personal Recommendations ("What this means for you")**: Rule-based lifestyle insights derived from the trailing 7 valid days vs. personal baseline (median steps ~5,175 vs. 5,599; move mins ~74 vs. 72.5), activity swings pacing, natural recovery balance, device carry consistency notice, and scope note for missing smartwatch sleep/pulse sensors. Zero clinical/diagnostic language (*"Wellness insight, not medical advice"*).


---

## 📦 Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`:
  - `pandas`
  - `numpy`
  - `scipy`
  - `scikit-learn`
  - `torch`
  - `flwr[simulation]`
  - `matplotlib`
  - `streamlit`
  - `plotly`

Install dependencies with:
```bash
py -m pip install -r requirements.txt
```

---

## ⚠️ Disclaimer

**Wellness insight, not medical advice.** All findings, baseline flags, and correlation patterns are intended strictly for lifestyle tracking and wellness exploration.
