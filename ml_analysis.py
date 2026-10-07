from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.dummy import DummyClassifier
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "ml_results"

RESULTS_DIR.mkdir(exist_ok=True)


# ============================================================
# NSE DATASETS
# ============================================================

STOCK_FILES = {
    "Bajaj Auto": "Bajaj_Auto.csv",
    "Eicher Motors": "Eicher_Motors.csv",
    "Hero Motocorp": "Hero_Motocorp.csv",
    "Infosys": "Infosys.csv",
    "TCS": "TCS.csv",
    "TVS Motors": "TVS_Motors.csv",
}


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "ret_1",
    "ret_5",
    "ret_20",
    "sma_5_ratio",
    "sma_20_ratio",
    "vol_20",
    "hl_pct",
    "co_pct",
    "volume_chg",
    "turnover_chg",
    "delivery_pct",
    "rsi_14",
]


# ============================================================
# 1. LOAD AND ADJUST DATA
# ============================================================

def load_and_adjust_data():
    """
    Load all six NSE datasets.

    Known 1:1 bonus adjustments:
        Infosys: 2015-06-15
        TCS:     2018-05-31

    Historical prices before the bonus are divided by 2.
    Share quantities are multiplied by 2.
    """

    frames = []

    bonus_dates = {
        "Infosys": pd.Timestamp("2015-06-15"),
        "TCS": pd.Timestamp("2018-05-31"),
    }

    price_columns = [
        "Open Price",
        "High Price",
        "Low Price",
        "Close Price",
        "WAP",
        "Spread High-Low",
        "Spread Close-Open",
    ]

    quantity_columns = [
        "No.of Shares",
        "Deliverable Quantity",
    ]

    for stock, filename in STOCK_FILES.items():
        path = DATA_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"\nMissing file:\n{path}\n\n"
                f"Make sure '{filename}' is inside the data folder."
            )

        print(f"Loading {stock}...")

        df = pd.read_csv(path)

        required = [
            "Date",
            "Open Price",
            "High Price",
            "Low Price",
            "Close Price",
            "No.of Shares",
            "Total Turnover (Rs.)",
        ]

        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(
                f"{filename} is missing required columns: {missing}"
            )

        df["Date"] = pd.to_datetime(
            df["Date"],
            dayfirst=True,
            errors="coerce",
        )

        if df["Date"].isna().all():
            raise ValueError(f"Could not parse dates in {filename}")

        numeric_columns = [
            col for col in df.columns
            if col not in ["Date", "stock"]
        ]

        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = (
            df.dropna(subset=["Date"])
            .sort_values("Date")
            .reset_index(drop=True)
        )

        bonus_date = bonus_dates.get(stock)

        if bonus_date is not None:
            before_bonus = df["Date"] < bonus_date

            for col in price_columns:
                if col in df.columns:
                    df.loc[before_bonus, col] = (
                        df.loc[before_bonus, col] * 0.5
                    )

            for col in quantity_columns:
                if col in df.columns:
                    df.loc[before_bonus, col] = (
                        df.loc[before_bonus, col] * 2
                    )

        df["stock"] = stock
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)

    combined = (
        combined
        .sort_values(["Date", "stock"])
        .reset_index(drop=True)
    )

    return combined


# ============================================================
# 2. FEATURE ENGINEERING
# ============================================================

def calculate_rsi(series, window=14):
    delta = series.diff()

    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()

    # When average loss is zero and gain is positive, RSI is 100.
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    rsi = rsi.where(~((loss == 0) & (gain > 0)), 100)
    return rsi


def add_features(df):
    """
    Create features using only information available on or before
    the prediction day.

    Target:
        1 = next trading day's close is higher
        0 = next trading day's close is not higher
    """

    result = df.copy()

    result = (
        result
        .sort_values(["stock", "Date"])
        .reset_index(drop=True)
    )

    grouped = result.groupby("stock", group_keys=False)

    # Return-based features
    result["ret_1"] = grouped["Close Price"].pct_change()
    result["ret_5"] = grouped["Close Price"].pct_change(5)
    result["ret_20"] = grouped["Close Price"].pct_change(20)

    # Moving-average features
    result["sma_5_ratio"] = grouped["Close Price"].transform(
        lambda s: s / s.rolling(5).mean() - 1
    )

    result["sma_20_ratio"] = grouped["Close Price"].transform(
        lambda s: s / s.rolling(20).mean() - 1
    )

    # Volatility
    result["vol_20"] = grouped["ret_1"].transform(
        lambda s: s.rolling(20).std()
    )

    # Daily high-low range
    result["hl_pct"] = (
        (result["High Price"] - result["Low Price"])
        / result["Close Price"]
    )

    # Close-to-open movement
    result["co_pct"] = (
        (result["Close Price"] - result["Open Price"])
        / result["Open Price"]
    )

    # Volume change
    result["volume_chg"] = grouped["No.of Shares"].pct_change()

    # Turnover change
    result["turnover_chg"] = grouped[
        "Total Turnover (Rs.)"
    ].pct_change()

    # Delivery percentage
    if "Deliverable Quantity" in result.columns:
        result["delivery_pct"] = (
            result["Deliverable Quantity"]
            / result["No.of Shares"].replace(0, np.nan)
        )
    else:
        result["delivery_pct"] = np.nan

    # RSI
    result["rsi_14"] = grouped["Close Price"].transform(
        calculate_rsi
    )

    # --------------------------------------------------------
    # Future target
    # --------------------------------------------------------
    # next_return is used only to create the target.
    # It is never included in FEATURES.
    result["next_return"] = (
        grouped["Close Price"].shift(-1)
        / result["Close Price"]
        - 1
    )

    result["target"] = (
        result["next_return"] > 0
    ).astype(int)

    # Remove invalid rows
    result = result.replace([np.inf, -np.inf], np.nan)

    result = result.dropna(
        subset=FEATURES + ["next_return", "target"]
    ).reset_index(drop=True)

    return result


# ============================================================
# 3. CHRONOLOGICAL TRAIN / VALIDATION / TEST SPLIT
# ============================================================

def temporal_split(df, train_pct=0.70, validation_pct=0.15):
    """
    Date-based chronological split:

        70% Train
        15% Validation
        15% Test

    No random shuffling.
    """

    unique_dates = np.sort(df["Date"].dropna().unique())

    if len(unique_dates) < 10:
        raise ValueError("Not enough unique dates for temporal split.")

    train_index = max(
        1,
        int(len(unique_dates) * train_pct)
    )

    validation_index = max(
        train_index + 1,
        int(len(unique_dates) * (train_pct + validation_pct))
    )

    validation_index = min(
        validation_index,
        len(unique_dates) - 1
    )

    train_end = unique_dates[train_index - 1]
    validation_end = unique_dates[validation_index - 1]

    train = df[df["Date"] <= train_end].copy()

    validation = df[
        (df["Date"] > train_end)
        & (df["Date"] <= validation_end)
    ].copy()

    test = df[df["Date"] > validation_end].copy()

    if train.empty or validation.empty or test.empty:
        raise ValueError(
            "Temporal split produced an empty dataset. "
            "Check the available dates."
        )

    return (
        train,
        validation,
        test,
        pd.Timestamp(train_end),
        pd.Timestamp(validation_end),
    )


# ============================================================
# 4. MODEL EVALUATION
# ============================================================

def evaluate(model, X, y):
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]

    return {
        "accuracy": accuracy_score(y, predictions),
        "balanced_accuracy": balanced_accuracy_score(
            y, predictions
        ),
        "precision": precision_score(
            y, predictions, zero_division=0
        ),
        "recall": recall_score(
            y, predictions, zero_division=0
        ),
        "f1": f1_score(
            y, predictions, zero_division=0
        ),
        "roc_auc": roc_auc_score(
            y, probabilities
        ),
        "confusion_matrix": confusion_matrix(
            y, predictions
        ),
    }


# ============================================================
# 5. BASELINE MODEL
# ============================================================

def run_baseline(train, validation, test):
    model = DummyClassifier(
        strategy="most_frequent"
    )

    model.fit(
        train[FEATURES],
        train["target"]
    )

    train_metrics = evaluate(
        model,
        train[FEATURES],
        train["target"]
    )

    validation_metrics = evaluate(
        model,
        validation[FEATURES],
        validation["target"]
    )

    test_metrics = evaluate(
        model,
        test[FEATURES],
        test["target"]
    )

    return {
        "model": "Majority Class Baseline",
        "train_accuracy": train_metrics["accuracy"],
        "validation_accuracy": validation_metrics["accuracy"],
        "test_accuracy": test_metrics["accuracy"],
        "test_f1": test_metrics["f1"],
        "test_roc_auc": test_metrics["roc_auc"],
    }


# ============================================================
# 6. MODEL SELECTION + HYPERPARAMETER TUNING
# ============================================================

def train_and_compare(train, validation, test):
    X_train = train[FEATURES]
    y_train = train["target"]

    X_validation = validation[FEATURES]
    y_validation = validation["target"]

    X_test = test[FEATURES]
    y_test = test["target"]

    # Time-series cross-validation on training data only
    cv = TimeSeriesSplit(n_splits=4)

    candidates = {
        "Logistic Regression": (
            Pipeline(
                [
                    ("scaler", StandardScaler()),
                    (
                        "model",
                        LogisticRegression(
                            max_iter=3000,
                            random_state=42,
                        ),
                    ),
                ]
            ),
            {
                "model__C": [
                    0.001,
                    0.01,
                    0.1,
                    1,
                    10,
                ]
            },
        ),

        "Random Forest": (
            RandomForestClassifier(
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ),
            {
                "n_estimators": [
                    150,
                    250,
                ],
                "max_depth": [
                    3,
                    4,
                    6,
                ],
                "min_samples_leaf": [
                    3,
                    5,
                ],
                "max_features": [
                    "sqrt",
                ],
            },
        ),

        "HistGradientBoosting": (
            HistGradientBoostingClassifier(
                random_state=42,
            ),
            {
                "max_iter": [
                    100,
                    200,
                ],
                "learning_rate": [
                    0.03,
                    0.05,
                    0.1,
                ],
                "max_leaf_nodes": [
                    7,
                    15,
                ],
                "l2_regularization": [
                    0,
                    1,
                ],
            },
        ),
    }

    fitted_models = {}
    rows = []

    for name, (estimator, parameter_grid) in candidates.items():
        print(f"\nTraining {name}...")

        search = GridSearchCV(
            estimator=estimator,
            param_grid=parameter_grid,
            cv=cv,
            scoring="roc_auc",
            n_jobs=-1,
            refit=True,
        )

        search.fit(X_train, y_train)

        fitted_models[name] = search

        train_metrics = evaluate(
            search,
            X_train,
            y_train,
        )

        validation_metrics = evaluate(
            search,
            X_validation,
            y_validation,
        )

        test_metrics = evaluate(
            search,
            X_test,
            y_test,
        )

        rows.append(
            {
                "model": name,
                "cv_roc_auc": search.best_score_,
                "train_accuracy": train_metrics["accuracy"],
                "train_roc_auc": train_metrics["roc_auc"],
                "validation_accuracy": validation_metrics[
                    "accuracy"
                ],
                "validation_f1": validation_metrics["f1"],
                "validation_roc_auc": validation_metrics[
                    "roc_auc"
                ],
                "test_accuracy": test_metrics["accuracy"],
                "test_f1": test_metrics["f1"],
                "test_roc_auc": test_metrics["roc_auc"],
                "best_params": str(search.best_params_),
            }
        )

    comparison = pd.DataFrame(rows)

    # Model selection uses validation data, not test data.
    comparison = (
        comparison
        .sort_values(
            "validation_roc_auc",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    selected_name = comparison.iloc[0]["model"]
    selected_model = fitted_models[selected_name]

    metrics = {
        "train": evaluate(
            selected_model,
            X_train,
            y_train,
        ),
        "validation": evaluate(
            selected_model,
            X_validation,
            y_validation,
        ),
        "test": evaluate(
            selected_model,
            X_test,
            y_test,
        ),
    }

    return (
        selected_name,
        selected_model,
        comparison,
        fitted_models,
        metrics,
    )


# ============================================================
# 7. FEATURE IMPORTANCE
# ============================================================

def get_feature_importance(model, feature_names):
    estimator = model.best_estimator_

    # Random Forest
    if hasattr(estimator, "feature_importances_"):
        importance = estimator.feature_importances_

    # Logistic Regression pipeline
    elif hasattr(estimator, "named_steps"):
        final_model = estimator.named_steps.get("model")

        if final_model is not None and hasattr(
            final_model,
            "coef_",
        ):
            importance = np.abs(final_model.coef_[0])
        else:
            return pd.DataFrame()

    # HistGradientBoosting does not expose feature_importances_
    else:
        return pd.DataFrame()

    result = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": importance,
        }
    )

    return (
        result
        .sort_values(
            "importance",
            ascending=False,
        )
        .reset_index(drop=True)
    )


# ============================================================
# 8. COMPLEXITY ANALYSIS
# ============================================================

def complexity_description(selected_name, selected_model):
    params = selected_model.best_params_

    if selected_name == "Logistic Regression":
        c_value = params.get("model__C")
        return (
            f"Logistic Regression was selected. "
            f"The model is relatively simple and uses "
            f"L2 regularization with C={c_value}. "
            f"This limits unnecessary model complexity."
        )

    if selected_name == "Random Forest":
        return (
            f"Random Forest was selected with "
            f"n_estimators={params.get('n_estimators')}, "
            f"max_depth={params.get('max_depth')}, "
            f"min_samples_leaf={params.get('min_samples_leaf')}. "
            f"Depth and minimum leaf size constrain tree complexity."
        )

    return (
        f"HistGradientBoosting was selected with "
        f"max_iter={params.get('max_iter')}, "
        f"learning_rate={params.get('learning_rate')}, "
        f"max_leaf_nodes={params.get('max_leaf_nodes')}, "
        f"l2_regularization={params.get('l2_regularization')}. "
        f"Leaf limits, learning rate and regularization control complexity."
    )


# ============================================================
# 9. COMPLETE ML REPORT
# ============================================================

def build_report():
    print("\nLoading NSE data...")

    raw_data = load_and_adjust_data()

    print(f"Raw rows: {len(raw_data):,}")

    print("\nCreating engineered features...")

    data = add_features(raw_data)

    print(
        f"Rows after feature engineering: "
        f"{len(data):,}"
    )

    (
        train,
        validation,
        test,
        train_end,
        validation_end,
    ) = temporal_split(data)

    # --------------------------------------------------------
    # Save split information
    # --------------------------------------------------------

    split_summary = pd.DataFrame(
        {
            "split": [
                "Train",
                "Validation",
                "Test",
            ],
            "rows": [
                len(train),
                len(validation),
                len(test),
            ],
            "start_date": [
                train["Date"].min(),
                validation["Date"].min(),
                test["Date"].min(),
            ],
            "end_date": [
                train["Date"].max(),
                validation["Date"].max(),
                test["Date"].max(),
            ],
        }
    )

    split_summary.to_csv(
        RESULTS_DIR / "train_validation_test_split.csv",
        index=False,
    )

    # --------------------------------------------------------
    # Baseline
    # --------------------------------------------------------

    print("\nRunning baseline model...")

    baseline = run_baseline(
        train,
        validation,
        test,
    )

    # --------------------------------------------------------
    # Model comparison
    # --------------------------------------------------------

    print("\nRunning model selection and tuning...")

    (
        selected_name,
        selected_model,
        comparison,
        fitted_models,
        metrics,
    ) = train_and_compare(
        train,
        validation,
        test,
    )

    # --------------------------------------------------------
    # Add baseline to comparison
    # --------------------------------------------------------

    baseline_row = pd.DataFrame(
        [
            {
                "model": baseline["model"],
                "cv_roc_auc": np.nan,
                "train_accuracy": baseline[
                    "train_accuracy"
                ],
                "train_roc_auc": np.nan,
                "validation_accuracy": baseline[
                    "validation_accuracy"
                ],
                "validation_f1": np.nan,
                "validation_roc_auc": np.nan,
                "test_accuracy": baseline[
                    "test_accuracy"
                ],
                "test_f1": baseline["test_f1"],
                "test_roc_auc": baseline[
                    "test_roc_auc"
                ],
                "best_params": "Most frequent class",
            }
        ]
    )

    comparison_with_baseline = pd.concat(
        [
            baseline_row,
            comparison,
        ],
        ignore_index=True,
    )

    comparison_with_baseline.to_csv(
        RESULTS_DIR / "model_comparison.csv",
        index=False,
    )

    # --------------------------------------------------------
    # Selected model metrics
    # --------------------------------------------------------

    metrics_rows = []

    for split_name in [
        "train",
        "validation",
        "test",
    ]:
        m = metrics[split_name]

        metrics_rows.append(
            {
                "split": split_name,
                "accuracy": m["accuracy"],
                "balanced_accuracy": m[
                    "balanced_accuracy"
                ],
                "precision": m["precision"],
                "recall": m["recall"],
                "f1": m["f1"],
                "roc_auc": m["roc_auc"],
            }
        )

    metrics_df = pd.DataFrame(metrics_rows)

    metrics_df.to_csv(
        RESULTS_DIR / "selected_model_metrics.csv",
        index=False,
    )

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    importance_df = get_feature_importance(
        selected_model,
        FEATURES,
    )

    if not importance_df.empty:
        importance_df.to_csv(
            RESULTS_DIR / "feature_importance.csv",
            index=False,
        )

    # --------------------------------------------------------
    # Overfitting / underfitting analysis
    # --------------------------------------------------------

    train_auc = metrics["train"]["roc_auc"]
    validation_auc = metrics["validation"]["roc_auc"]
    test_auc = metrics["test"]["roc_auc"]

    train_validation_gap = (
        train_auc - validation_auc
    )

    validation_test_gap = (
        validation_auc - test_auc
    )

    if train_validation_gap > 0.10:
        overfit_status = (
            "Potential overfitting: training ROC-AUC "
            "is substantially higher than validation ROC-AUC."
        )
    elif train_auc < 0.60 and validation_auc < 0.60:
        overfit_status = (
            "Potential underfitting: both training and "
            "validation ROC-AUC are weak."
        )
    else:
        overfit_status = (
            "No strong overfitting signal from the "
            "train-validation ROC-AUC gap."
        )

    # --------------------------------------------------------
    # Complexity justification
    # --------------------------------------------------------

    model_complexity_note = complexity_description(
        selected_name,
        selected_model,
    )

    # --------------------------------------------------------
    # Save diagnostic summary
    # --------------------------------------------------------

    diagnostic = pd.DataFrame(
        [
            {
                "selected_model": selected_name,
                "train_roc_auc": train_auc,
                "validation_roc_auc": validation_auc,
                "test_roc_auc": test_auc,
                "train_validation_gap": train_validation_gap,
                "validation_test_gap": validation_test_gap,
                "diagnosis": overfit_status,
                "complexity_justification": model_complexity_note,
            }
        ]
    )

    diagnostic.to_csv(
        RESULTS_DIR / "overfitting_diagnostics.csv",
        index=False,
    )

    # --------------------------------------------------------
    # Save CV / tuning evidence
    # --------------------------------------------------------

    tuning_rows = []

    for name, model in fitted_models.items():
        tuning_rows.append(
            {
                "model": name,
                "best_cv_roc_auc": model.best_score_,
                "best_parameters": str(
                    model.best_params_
                ),
            }
        )

    tuning_df = pd.DataFrame(tuning_rows)

    tuning_df.to_csv(
        RESULTS_DIR / "hyperparameter_tuning.csv",
        index=False,
    )

    # --------------------------------------------------------
    # Complete report
    # --------------------------------------------------------

    report = {
        "rows_after_feature_engineering": len(data),
        "train_rows": len(train),
        "validation_rows": len(validation),
        "test_rows": len(test),

        "train_start": str(
            pd.Timestamp(
                train["Date"].min()
            ).date()
        ),
        "train_end": str(
            pd.Timestamp(train_end).date()
        ),

        "validation_start": str(
            pd.Timestamp(
                validation["Date"].min()
            ).date()
        ),
        "validation_end": str(
            pd.Timestamp(validation_end).date()
        ),

        "test_start": str(
            pd.Timestamp(
                test["Date"].min()
            ).date()
        ),
        "test_end": str(
            pd.Timestamp(
                test["Date"].max()
            ).date()
        ),

        "baseline_test_accuracy": baseline[
            "test_accuracy"
        ],

        "selected_model": selected_name,

        "train_validation_auc_gap": train_validation_gap,
        "validation_test_auc_gap": validation_test_gap,

        "diagnosis": overfit_status,
    }

    return (
        report,
        selected_model,
        data,
        comparison_with_baseline,
        metrics_df,
        importance_df,
    )


# ============================================================
# 10. MAIN
# ============================================================

if __name__ == "__main__":
    (
        report,
        model,
        data,
        comparison,
        metrics,
        importance,
    ) = build_report()

    print("\n")
    print("=" * 80)
    print("NSE STOCK MARKET ML ANALYSIS")
    print("=" * 80)

    print(
        f"\nRows after feature engineering: "
        f"{report['rows_after_feature_engineering']:,}"
    )

    print(f"\nTrain      : {report['train_rows']:,}")
    print(f"Validation : {report['validation_rows']:,}")
    print(f"Test       : {report['test_rows']:,}")

    print(
        f"\nTrain period: "
        f"{report['train_start']} to {report['train_end']}"
    )

    print(
        f"Validation period: "
        f"{report['validation_start']} to "
        f"{report['validation_end']}"
    )

    print(
        f"Test period: "
        f"{report['test_start']} to {report['test_end']}"
    )

    print(
        f"\nSelected model: "
        f"{report['selected_model']}"
    )

    print(
        f"\nBaseline test accuracy: "
        f"{report['baseline_test_accuracy']:.3f}"
    )

    print("\n")
    print("-" * 80)
    print("MODEL COMPARISON")
    print("-" * 80)
    print(
        comparison.to_string(index=False)
    )

    print("\n")
    print("-" * 80)
    print("SELECTED MODEL METRICS")
    print("-" * 80)
    print(
        metrics.to_string(index=False)
    )

    print("\n")
    print("-" * 80)
    print("OVERFITTING / UNDERFITTING CHECK")
    print("-" * 80)

    train_auc = metrics.loc[
        metrics["split"] == "train",
        "roc_auc",
    ].iloc[0]

    validation_auc = metrics.loc[
        metrics["split"] == "validation",
        "roc_auc",
    ].iloc[0]

    test_auc = metrics.loc[
        metrics["split"] == "test",
        "roc_auc",
    ].iloc[0]

    print(
        f"Train ROC-AUC      : {train_auc:.3f}"
    )
    print(
        f"Validation ROC-AUC : {validation_auc:.3f}"
    )
    print(
        f"Test ROC-AUC       : {test_auc:.3f}"
    )

    print(
        f"\nTrain-Validation gap: "
        f"{report['train_validation_auc_gap']:.3f}"
    )

    print(
        f"Validation-Test gap: "
        f"{report['validation_test_auc_gap']:.3f}"
    )

    print(
        f"\nDiagnosis: "
        f"{report['diagnosis']}"
    )

    print("\n")
    print("-" * 80)
    print("FEATURE IMPORTANCE")
    print("-" * 80)

    if not importance.empty:
        print(
            importance.to_string(index=False)
        )
    else:
        print(
            "Feature importance is not directly available "
            "for the selected model."
        )

    print("\n")
    print("-" * 80)
    print("RESULT FILES")
    print("-" * 80)

    print(
        f"Results saved in:\n{RESULTS_DIR}"
    )

    print("\nCreated files:")

    for file in sorted(RESULTS_DIR.iterdir()):
        print(f"  ✓ {file.name}")

    print("\n")
    print("=" * 80)
    print("ML ANALYSIS COMPLETED")
    print("=" * 80)
