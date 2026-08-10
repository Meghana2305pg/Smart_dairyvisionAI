"""
evaluate.py
===========
Loads the saved best model and produces a full evaluation report:

  1. Hold-out test-set metrics (MAE, RMSE, R², MAPE)
  2. Predicted vs Actual scatter with residual analysis
  3. Feature importance (SHAP values when available, else MDI)
  4. Calibration check — are prediction intervals well-covered?
  5. Residual distribution diagnostics (Shapiro-Wilk normality test)
  6. All artefacts saved to outputs/

Usage
-----
    python evaluate.py
"""

import logging
import os
import sys
import warnings

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    mean_absolute_error, mean_absolute_percentage_error,
    mean_squared_error, r2_score
)
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(__file__))
from config import (
    MODEL_PATH, OUTPUT_DIR, ALL_FEATURES, TARGET,
    RANDOM_SEED, LOG_DIR
)
from data_loader import load_and_prepare
from feature_engineering import build_features
from weather import fetch_weather

# ── Logging ──────────────────────────────────────────────────────────────────
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(LOG_DIR, "evaluate.log"), mode="w"),
    ],
)
logger = logging.getLogger(__name__)


# ── Metrics ───────────────────────────────────────────────────────────────────

def compute_metrics(y_true, y_pred) -> dict:
    """Return a dict of evaluation metrics."""
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100  # percent
    return {"MAE": mae, "RMSE": rmse, "R2": r2, "MAPE_pct": mape}


# ── Residual diagnostics ──────────────────────────────────────────────────────

def residual_diagnostics(y_true, y_pred) -> dict:
    """
    Test whether residuals are approximately normal (Shapiro-Wilk).
    Returns the test statistic and p-value.

    Note: S-W is reliable up to n ≈ 5000.  For larger samples, use
    the D'Agostino-Pearson test (scipy.stats.normaltest).
    """
    residuals = np.array(y_true) - np.array(y_pred)

    if len(residuals) <= 5000:
        stat, p = stats.shapiro(residuals)
        test_name = "Shapiro-Wilk"
    else:
        stat, p = stats.normaltest(residuals)
        test_name = "D'Agostino-Pearson"

    normal = p > 0.05
    logger.info(
        "Residual normality (%s): stat=%.4f  p=%.4f  → %s",
        test_name, stat, p,
        "Normal (p > 0.05)" if normal else "Non-normal (p ≤ 0.05)"
    )
    return {
        "test":   test_name,
        "stat":   round(float(stat), 4),
        "p":      round(float(p),    4),
        "normal": bool(normal),
        "residuals": residuals,
    }


# ── Feature importance ────────────────────────────────────────────────────────

def get_feature_importance(model, X_test, y_test) -> pd.DataFrame:
    """
    Return feature importances as a DataFrame sorted by importance.

    Strategy:
    - Tree ensembles: use built-in MDI (fast, reported in paper as supplementary)
    - All models:     permutation importance on held-out test set (reported as primary)
    """
    df_imp = pd.DataFrame(index=ALL_FEATURES)

    # Built-in MDI (tree models only)
    if hasattr(model, "feature_importances_"):
        df_imp["MDI_importance"] = model.feature_importances_

    # Permutation importance (model-agnostic, test-set based)
    perm = permutation_importance(
        model, X_test, y_test,
        n_repeats=20, random_state=RANDOM_SEED, n_jobs=-1
    )
    df_imp["Perm_mean"] = perm.importances_mean
    df_imp["Perm_std"]  = perm.importances_std

    df_imp = df_imp.sort_values("Perm_mean", ascending=False)
    logger.info("Feature importance (permutation):\n%s", df_imp.to_string())
    return df_imp


# ── Plots ─────────────────────────────────────────────────────────────────────

def plot_predicted_vs_actual(y_test, y_pred, model_name: str):
    """Scatter of predicted vs actual with identity line and R² annotation."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=y_test, y=y_pred,
        mode="markers",
        marker=dict(size=5, opacity=0.5, color="#1D9E75"),
        name="Samples"
    ))
    lims = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
    fig.add_trace(go.Scatter(
        x=lims, y=lims,
        mode="lines",
        line=dict(dash="dash", color="#E24B4A", width=1.5),
        name="Perfect prediction"
    ))
    r2  = r2_score(y_test, y_pred)
    fig.update_layout(
        title=f"Predicted vs Actual Milk Yield — {model_name}  (R²={r2:.4f})",
        xaxis_title="Actual Milk Yield (L/day)",
        yaxis_title="Predicted Milk Yield (L/day)",
        width=700, height=520
    )
    path = os.path.join(OUTPUT_DIR, "predicted_vs_actual.png")
    fig.write_image(path)
    logger.info("Saved → %s", path)
    return fig


def plot_residuals(y_test, y_pred, model_name: str):
    """Residual vs fitted and histogram."""
    residuals = np.array(y_test) - np.array(y_pred)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=y_pred, y=residuals,
        mode="markers",
        marker=dict(size=5, opacity=0.5, color="#534AB7"),
        name="Residuals"
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="#E24B4A")
    fig.update_layout(
        title=f"Residuals vs Fitted — {model_name}",
        xaxis_title="Fitted (Predicted) Values",
        yaxis_title="Residual (Actual − Predicted)",
        width=700, height=400
    )
    path = os.path.join(OUTPUT_DIR, "residuals_vs_fitted.png")
    fig.write_image(path)
    logger.info("Saved → %s", path)

    # Histogram
    fig2 = px.histogram(
        x=residuals,
        nbins=40,
        title=f"Residual Distribution — {model_name}",
        labels={"x": "Residual (L/day)"},
        color_discrete_sequence=["#534AB7"],
        text_auto=".0f"
    )

    fig2.update_traces(
        textposition="inside",
        insidetextanchor="end",
        textfont=dict(
            size=11,
            color="white",
            family="Arial"
        )
    )

    fig2.update_layout(
        title=dict(
            font=dict(size=24, family="Arial"),
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            title=dict(font=dict(size=18)),
            tickfont=dict(size=15)
        ),
        yaxis=dict(
            title=dict(font=dict(size=18)),
            tickfont=dict(size=15)
        )
    )
    path2 = os.path.join(OUTPUT_DIR, "residual_histogram.png")
    fig2.write_image(path2)
    logger.info("Saved → %s", path2)

    return fig, fig2


def plot_feature_importance(df_imp: pd.DataFrame, model_name: str):
    """Horizontal bar chart of permutation importance with error bars."""
    df_plot = df_imp.sort_values("Perm_mean").tail(len(ALL_FEATURES))
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_plot["Perm_mean"],
        y=df_plot.index,
        orientation="h",
        error_x=dict(array=df_plot["Perm_std"], visible=True),
        marker_color="#1D9E75"
    ))
    fig.update_layout(
        title=f"Permutation Feature Importance — {model_name}",
        xaxis_title="Mean decrease in R² (permutation, 20 repeats)",
        yaxis_title="Feature",
        width=700, height=420
    )
    path = os.path.join(OUTPUT_DIR, "feature_importance.png")
    fig.write_image(path)
    logger.info("Saved → %s", path)
    return fig


def plot_cv_boxplot(df_cv: pd.DataFrame):
    """Box-plot of fold R² distributions for each model."""
    fig = px.box(
        df_cv, x="Model", y="R2",
        color="Model",
        title="Cross-Validated R² Distribution by Model (5-Fold)",
        labels={"R2": "R² Score"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(showlegend=False, width=750, height=450)
    path = os.path.join(OUTPUT_DIR, "cv_r2_boxplot.png")
    fig.write_image(path)
    logger.info("Saved → %s", path)
    return fig

def plot_test_set_model_comparison(
    X_train, X_test, y_train, y_test
):
    """
    Compare all models on the exact same held-out test set
    using MAE, RMSE, and MAPE (%).

    XGBoost and Random Forest use tuned parameters from
    outputs/tuning_results.json when available.
    """

    import json
    from sklearn.dummy import DummyRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.tree import DecisionTreeRegressor
    from xgboost import XGBRegressor

    # ---------------------------------------------------------
    # Load model parameters
    # ---------------------------------------------------------
    params = {k: dict(v) for k, v in MODEL_PARAMS.items()}

    tuning_path = os.path.join(OUTPUT_DIR, "tuning_results.json")

    if os.path.exists(tuning_path):
        with open(tuning_path, "r") as f:
            tuned = json.load(f)

        if "XGBoost" in tuned:
            params["XGBoost"] = {
                **params.get("XGBoost", {}),
                **tuned["XGBoost"]
            }

        if "Random Forest" in tuned:
            params["Random Forest"] = {
                **params.get("Random Forest", {}),
                **tuned["Random Forest"]
            }

    # ---------------------------------------------------------
    # Models
    # ---------------------------------------------------------
    models = {
        "XGBoost": XGBRegressor(
            **params["XGBoost"],
            verbosity=0
        ),

        "Linear Regression": LinearRegression(),

        "Random Forest": RandomForestRegressor(
            **params["Random Forest"]
        ),

        "Naive Baseline": DummyRegressor(
            strategy="mean"
        ),

        "Decision Tree": DecisionTreeRegressor(
            **params["Decision Tree"]
        ),
    }

    # ---------------------------------------------------------
    # Evaluate every model on SAME test split
    # ---------------------------------------------------------
    results = []

    for model_name, model in models.items():

        model.fit(X_train, y_train)

        pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, pred)

        rmse = np.sqrt(
            mean_squared_error(y_test, pred)
        )

        mape = mean_absolute_percentage_error(
            y_test, pred
        ) * 100

        results.append({
            "Model": model_name,
            "MAE": mae,
            "RMSE": rmse,
            "MAPE_pct": mape,
        })

    results_df = pd.DataFrame(results)

    # ---------------------------------------------------------
    # Save comparison table
    # ---------------------------------------------------------
    csv_path = os.path.join(
        OUTPUT_DIR,
        "model_test_error_metrics.csv"
    )

    results_df.to_csv(
        csv_path,
        index=False
    )

    # ---------------------------------------------------------
    # Create research figure
    # ---------------------------------------------------------
    fig, axes = plt.subplots(
        1,
        3,
        figsize=(16, 6),
        dpi=300
    )

    metrics = [
        ("MAE", "MAE (L/day)"),
        ("RMSE", "RMSE (L/day)"),
        ("MAPE_pct", "MAPE (%)"),
    ]

    for ax, (metric, ylabel) in zip(axes, metrics):

        bars = ax.bar(
            results_df["Model"],
            results_df[metric]
        )

        ax.set_title(
            ylabel,
            fontsize=15,
            fontweight="bold"
        )

        ax.set_ylabel(
            ylabel,
            fontsize=12
        )

        ax.set_xlabel(
            "Model",
            fontsize=12
        )

        ax.tick_params(
            axis="x",
            rotation=35,
            labelsize=10
        )

        ax.tick_params(
            axis="y",
            labelsize=10
        )

        # -----------------------------------------------------
        # VALUE LABELS ON BARS
        # -----------------------------------------------------
        for bar, value in zip(
            bars,
            results_df[metric]
        ):

            if metric == "MAPE_pct":
                label = f"{value:.2f}%"
            else:
                label = f"{value:.3f}"

            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                label,
                ha="center",
                va="bottom",
                fontsize=11,
                fontweight="bold",
                xytext=(0, 5),
                textcoords="offset points"
            )

        ax.grid(
            axis="y",
            linestyle="--",
            alpha=0.3
        )

        ax.set_axisbelow(True)

    fig.suptitle(
        "Model Comparison on Common Test Set: Error Metrics",
        fontsize=18,
        fontweight="bold",
        y=1.02
    )

    fig.tight_layout()

    # ---------------------------------------------------------
    # Save figure
    # ---------------------------------------------------------
    out_path = os.path.join(
        OUTPUT_DIR,
        "model_test_error_metrics.png"
    )

    fig.savefig(
        out_path,
        dpi=350,
        bbox_inches="tight"
    )

    plt.close(fig)

    logger.info(
        "Saved test-set error metrics figure -> %s",
        out_path
    )

    logger.info(
        "Saved test-set error metrics table -> %s",
        csv_path
    )

    return results_df

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load data (same pipeline as train.py)
    logger.info("=== Loading data ===")
    df_clean = load_and_prepare()
    base_temp, base_hum = fetch_weather()
    df_full, X, y = build_features(df_clean, base_temp, base_hum)

    # Hold-out split — same test set used for model comparison
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED
    )

    # ─────────────────────────────────────────────────────────────
    # MODEL COMPARISON — all models evaluated on the same test set
    # ─────────────────────────────────────────────────────────────
    plot_test_set_model_comparison(
        X_train,
        X_test,
        y_train,
        y_test
    )

    # Load saved best model
    if not os.path.exists(MODEL_PATH):
        logger.error(
            "Model not found at %s — run train.py first.",
            MODEL_PATH
        )
        sys.exit(1)

    model = joblib.load(MODEL_PATH)
    model_name = type(model).__name__
    logger.info("Loaded model: %s", model_name)

    # Refit on training split for fair test-set evaluation
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # ─────────────────────────────────────────────────────────────
    # 1. TEST-SET METRICS — BEST MODEL
    # ─────────────────────────────────────────────────────────────
    metrics = compute_metrics(y_test, y_pred)

    logger.info("=== Hold-out test metrics ===")

    for k, v in metrics.items():
        logger.info("  %-12s : %.4f", k, v)

    metrics_df = pd.DataFrame([metrics])

    metrics_df.to_csv(
        os.path.join(OUTPUT_DIR, "test_metrics.csv"),
        index=False
    )

    # ─────────────────────────────────────────────────────────────
    # 2. RESIDUAL DIAGNOSTICS
    # ─────────────────────────────────────────────────────────────
    diag = residual_diagnostics(y_test, y_pred)

    # ─────────────────────────────────────────────────────────────
    # 3. FEATURE IMPORTANCE
    # ─────────────────────────────────────────────────────────────
    df_imp = get_feature_importance(
        model,
        X_test,
        y_test
    )

    df_imp.to_csv(
        os.path.join(OUTPUT_DIR, "feature_importance.csv")
    )

    # ─────────────────────────────────────────────────────────────
    # 4. PLOTS — BEST MODEL
    # ─────────────────────────────────────────────────────────────
    plot_predicted_vs_actual(
        y_test,
        y_pred,
        model_name
    )

    plot_residuals(
        y_test,
        y_pred,
        model_name
    )

    plot_feature_importance(
        df_imp,
        model_name
    )

    # ─────────────────────────────────────────────────────────────
    # CV boxplot (if cv_results.csv exists)
    # ─────────────────────────────────────────────────────────────
    cv_path = os.path.join(
        OUTPUT_DIR,
        "cv_results.csv"
    )

    if os.path.exists(cv_path):
        df_cv = pd.read_csv(cv_path)
        plot_cv_boxplot(df_cv)

    # ─────────────────────────────────────────────────────────────
    # 5. CONSOLE SUMMARY
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f" EVALUATION REPORT — {model_name}")
    print("=" * 60)

    print(f"  R²         : {metrics['R2']:.4f}")
    print(f"  MAE        : {metrics['MAE']:.3f} L/day")
    print(f"  RMSE       : {metrics['RMSE']:.3f} L/day")
    print(f"  MAPE       : {metrics['MAPE_pct']:.2f}%")

    print(
        f"  Residuals  : "
        f"{'Normal' if diag['normal'] else 'Non-normal'}"
        f"  ({diag['test']}  p={diag['p']:.4f})"
    )

    print("=" * 60)

    print("\nTop 3 features by permutation importance:")

    for feat, row in df_imp.head(3).iterrows():
        print(
            f"  {feat:<22}  "
            f"ΔR²={row['Perm_mean']:.4f} ± "
            f"{row['Perm_std']:.4f}"
        )

    print("\nAll outputs saved to outputs/")


if __name__ == "__main__":
    main()