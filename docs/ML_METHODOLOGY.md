# Machine Learning Methodology & Evaluation Engine

## 1. Machine Learning Paradigm

The platform supports **supervised classification**, where a model learns a predictive mapping from a set of input feature vectors $\mathbf{X}$ to a discrete ground-truth target vector $\mathbf{y}$.

---

## 2. Leak-Free Preprocessing Pipeline Architecture

A common flaw in data science implementations is **data leakage**—where information from the holdout evaluation set contaminates the model training process (e.g. scaling or imputing values before splitting).

The platform prevents data leakage using Scikit-learn's `Pipeline` and `ColumnTransformer`:

```
                 Incoming Raw Dataset
                         |
           Stratified Train / Test Split (e.g. 80 / 20)
            /                                    \
       Train Set (80%)                       Test Set (20%)
            |                                      |
  +---------v-------------------------+            |
  |     Fit Preprocessing Pipeline    |            |
  |  (Learns Medians & Mean/Variance) |            |
  +---------+-------------------------+            |
            |                                      |
  +---------v-------------------------+            |
  |      Fit Classifier Model         |            |
  +---------+-------------------------+            |
            |                                      |
            +---------------------> Transform Test Set & Predict
                                                   |
                                     Compute Evaluation Metrics
                                     (Acc, Precision, Recall, F1)
```

### Preprocessing Transformers:
1. **Numerical Transformer:**
   - `SimpleImputer(strategy='median')`: Replaces missing numeric values with the training set median (robust to outliers).
   - `StandardScaler()`: Standardizes features by removing the mean and scaling to unit variance:
     $$z = \frac{x - \mu}{\sigma}$$
2. **Categorical Transformer:**
   - `SimpleImputer(strategy='most_frequent')`: Imputes missing categorical values using the most frequent category.
   - `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`: Converts discrete string categories into binary indicator columns. `handle_unknown='ignore'` guarantees the pipeline won't crash if previously unseen categories appear in incoming test sets.

---

## 3. Supported Algorithmic Classifiers

### 3.1 Logistic Regression
- **Mechanism:** Linear decision boundary passed through the sigmoid logistic function:
  $$P(y=1|\mathbf{x}) = \frac{1}{1 + e^{-(\mathbf{w}^T\mathbf{x} + b)}}$$
- **Role:** Serves as a fast, interpretable linear baseline.

### 3.2 Random Forest Classifier
- **Mechanism:** Ensemble method constructing $100$ decorrelated decision trees using bagging (bootstrap aggregation) and random feature subspace selection. Final classification is determined by majority vote.
- **Role:** Provides high predictive power, handles non-linear feature interactions, and is resistant to overfitting.

### 3.3 Decision Tree Classifier
- **Mechanism:** Non-parametric hierarchical tree splitting nodes using the Gini impurity criterion:
  $$\text{Gini}(D) = 1 - \sum_{i=1}^C p_i^2$$
- **Role:** Highly visual, rule-based explainability.

---

## 4. Evaluation Metrics & Metric Averaging

### 4.1 Confusion Matrix Terminology
- **True Positives (TP):** Fraud/Churn correctly flagged.
- **True Negatives (TN):** Normal activity correctly flagged.
- **False Positives (FP):** Normal activity incorrectly flagged (Type I error).
- **False Negatives (FN):** Fraud/Churn missed (Type II error).

### 4.2 Mathematical Definitions
- **Accuracy:** Overall proportion of correct predictions:
  $$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN} \times 100$$
- **Precision:** Of all predicted positive instances, how many were genuinely positive:
  $$\text{Precision} = \frac{TP}{TP + FP} \times 100$$
- **Recall (Sensitivity):** Of all actual positive instances, how many were detected:
  $$\text{Recall} = \frac{TP}{TP + FN} \times 100$$
- **F1-Score:** The harmonic mean of precision and recall:
  $$F_1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}} \times 100$$

### 4.3 Why Weighted Averaging is Used
Real-world datasets like fraud and churn suffer from **class imbalance** (e.g. 5% fraud, 95% legitimate). In this scenario, a naive model that always predicts legitimate would achieve 95% accuracy while missing 100% of frauds!

The platform calculates `average='weighted'` for precision, recall, and F1-score:
$$\text{Metric}_{\text{weighted}} = \sum_{c=1}^C \frac{N_c}{N} \times \text{Metric}_c$$
where $N_c$ is the true support for class $c$. This penalizes models that underperform on minority classes.

---

## 5. Artifact Serialization & Reproducibility

- **Joblib Serialization:** Fitted pipelines (transformers + model weights) are serialized to disk in `storage/models/model_version_{id}.joblib`.
- **Reproducibility:** Evaluation requests accept a configurable `random_state` seed (default `42`) passed to both `train_test_split` and classifier estimators, guaranteeing identical, reproducible metric outputs on identical data splits.
