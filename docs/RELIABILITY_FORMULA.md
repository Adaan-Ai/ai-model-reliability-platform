# Platform Reliability Scoring Formula & Mathematical Rationale

## 1. The Core Philosophy of Reliability

A fundamental premise of this platform is that **accuracy is not reliability**. 

A model achieving $95\%$ accuracy on synthetic test data is **dangerous** if:
- The incoming production data has a $40\%$ missing value rate.
- The population distribution has drifted drastically away from the historical baseline.
- The model will soon make catastrophic errors because reality no longer matches its assumptions.

Therefore, our platform computes a holistic, transparent composite index balancing three orthogonal pillars:
1. **Data Quality Score ($S_{\text{DQ}}$):** Are the inputs clean, unique, well-typed, and complete?
2. **Model Performance Score ($S_{\text{Model}}$):** How accurately and robustly does the model classify holdout data?
3. **Drift Health Score ($S_{\text{Drift}}$):** Has the underlying data distribution remained stable relative to the reference baseline?

---

## 2. The Signature Formula

$$\text{Overall Reliability} = (0.35 \times S_{\text{DQ}}) + (0.45 \times S_{\text{Model}}) + (0.20 \times S_{\text{Drift}})$$

All components are strictly normalized between $0.00$ and $100.00$.

### 2.1 Pillar 1: Data Quality Score ($S_{\text{DQ}}$)
Calculated as the arithmetic mean of all registered data quality checks executed against the dataset version:
$$S_{\text{DQ}} = \frac{1}{K} \sum_{k=1}^K \text{score}_k$$
- Missing Values check: $(1 - \frac{\text{null\_cells}}{\text{total\_cells}}) \times 100$
- Duplicates check: $(1 - \frac{\text{duplicate\_rows}}{\text{total\_rows}}) \times 100$
- Type consistency, suspicious categorical placeholders, potential numeric outliers, and basic schema issues are scored on a $0–100$ scale using generic heuristics.
- Potential outliers are detected with a robust median/MAD rule and an IQR fallback. They are not necessarily invalid; business-specific allowed values and ranges require an expected schema.
- If no checks have been defined yet, defaults honestly to $100.0$.

### 2.2 Pillar 2: Model Performance Score ($S_{\text{Model}}$)
Calculated as a weighted harmonic-arithmetic combination of test Accuracy and weighted F1-Score:
$$S_{\text{Model}} = (0.40 \times \text{Accuracy}) + (0.60 \times \text{F1-score})$$
- We weight F1-score at $60\%$ because in real-world imbalanced datasets (e.g. fraud detection), accuracy alone can be misleadingly high. F1 penalizes false positives and false negatives simultaneously.

### 2.3 Pillar 3: Drift Health Score ($S_{\text{Drift}}$)
Measured via the Population Stability Index (PSI):
$$PSI = \sum_{b=1}^{B} \left( (\text{Actual}_b\% - \text{Expected}_b\%) \times \ln\left(\frac{\text{Actual}_b\%}{\text{Expected}_b\%}\right) \right)$$

To fulfill the core requirement that **higher drift severity must reduce the reliability score**, raw PSI (where $0.0$ is zero drift and $>0.25$ is high drift) is inverted into a $0–100$ health score:
$$S_{\text{Drift}} = \max\Big(0, \min\big(100, 100 - (\text{PSI} \times 200)\big)\Big)$$

#### PSI to Drift Health Mapping Table:
| Observed PSI | Drift Category | Drift Health ($S_{\text{Drift}}$) | Interpretation |
|---|---|---|---|
| $0.0000$ | **LOW** | $100.00$ | Baseline / identical distribution |
| $0.0500$ | **LOW** | $90.00$ | Negligible natural variation |
| $0.1000$ | **MEDIUM** | $80.00$ | Noticeable shift, within acceptable bounds |
| $0.2000$ | **MEDIUM** | $60.00$ | Significant shift, monitoring recommended |
| $0.2500$ | **HIGH** | $50.00$ | Critical threshold exceeded |
| $\ge 0.5000$ | **HIGH** | $0.00$ | Severe population shift; retrain mandatory |

---

## 3. Rating Tiers

| Overall Score Range | Rating | Operational Action |
|---|---|---|
| **80.00 – 100.00** | <span style="color:#10b981;font-weight:bold;">HIGH</span> | **Production Approved:** Model is accurate, data is verified clean, and data distribution is statistically stable. |
| **60.00 – 79.99** | <span style="color:#f59e0b;font-weight:bold;">MEDIUM</span> | **Conditional Approval:** Minor quality anomalies or moderate drift detected. Human-in-the-loop review recommended. |
| **Below 60.00** | <span style="color:#ef4444;font-weight:bold;">LOW</span> | **Critical Attention Required:** High error rate, severe distribution shift, or corrupt incoming data. Deployment halted. |

---

## 4. Concrete Numerical Examples

### Scenario A: High Reliability (Financial Fraud Sentinel v1.0 on Fraud Data v1.0)
- Data Quality Score: $96.88$ (Clean baseline with minor missing values)
- Accuracy: $84.36\%$, F1-Score: $82.42\%$
- Model Performance Score: $(0.40 \times 84.36) + (0.60 \times 82.42) = 33.74 + 49.45 = 83.19$
- Reference Version: None (Baseline v1.0 &rarr; $\text{PSI} = 0.0000$ &rarr; $S_{\text{Drift}} = 100.00$)
- Calculation:
  $$\text{Overall Score} = (0.35 \times 96.88) + (0.45 \times 83.19) + (0.20 \times 100.00)$$
  $$\text{Overall Score} = 33.91 + 37.44 + 20.00 = 91.35$$
- **Rating:** <span style="color:#10b981;font-weight:bold;">HIGH</span> (Approved for inference)

---

### Scenario B: Medium Reliability from Drift (Financial Fraud Sentinel v2.0 on Drifted Fraud Data v2.0)
- Data Quality Score: $95.50$
- Accuracy: $72.33\%$, F1-Score: $69.90\%$
- Model Performance Score: $(0.40 \times 72.33) + (0.60 \times 69.90) = 28.93 + 41.94 = 70.87$
- Reference Version: Fraud v1.0
- Observed Feature Drift: Mean $\text{PSI} = 0.2620$ (HIGH drift in transaction amounts and foreign origins)
- Drift Health Score: $\max(0, 100 - (0.2620 \times 200)) = 100 - 52.40 = 47.60$
- Calculation:
  $$\text{Overall Score} = (0.35 \times 95.50) + (0.45 \times 70.87) + (0.20 \times 47.60)$$
  $$\text{Overall Score} = 33.43 + 31.89 + 9.52 = 74.84$$
- **Rating:** <span style="color:#f59e0b;font-weight:bold;">MEDIUM</span> (Retraining alert triggered due to distribution divergence!)
