import pandas as pd
from omegaconf import DictConfig
from typing import Dict
from src.utils.utils import save_to_jsonl, load_from_jsonl
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
from sklearn.metrics import cohen_kappa_score
import matplotlib.figure
import os

logger = logging.getLogger(__name__)


def iter_rows_from_records(analysis_cfg: DictConfig, records):
    ignore_values = set(analysis_cfg.filter_out_values)
    for record in records:
        row = {**record["key"]["inference_key"]}
        row.update(**record["key"])
        row["dimension2"] = None
        row["value"] = None
        dimension = row["dimension"]

        for value_type, value in record["values"].items():
            if value_type not in ignore_values:
                row["dimension2"] = value_type
                row["value"] = value
                # breakpoint()
                yield row.copy()


def form_granular_df(cfg: DictConfig, records_filepath: str) -> pd.DataFrame:
    analysis_cfg = cfg.analysis
    records = load_from_jsonl(records_filepath, context="Assimilating records to df")

    granular_df = pd.DataFrame(
        iter_rows_from_records(analysis_cfg=analysis_cfg, records=records)
    )

    return granular_df


def save_plots(plots_dict: dict, output_folder: str = "."):
    import os
    import matplotlib.pyplot as plt

    os.makedirs(output_folder, exist_ok=True)

    for plot_name, fig in plots_dict.items():
        filepath = os.path.join(output_folder, f"{plot_name}.png")
        fig.savefig(filepath, bbox_inches="tight")
        plt.close(fig)


def heuristic_scores_heatmap(granular_df: pd.DataFrame) -> dict:
    logger.info("Generating heuristic scores heatmap")

    # Data
    df = granular_df.loc[
        (granular_df["evaluation_type"] == "heuristic")
        & (granular_df["dimension2"] == "score"),
    ]

    # Graphing
    evaluators = df["evaluator_model"].unique()
    pivot_df = (
        df.pivot_table(
            index=["id", "cuisine_a", "cuisine_b", "dimension"],
            columns="evaluator_model",
            values="value",
        )
        .dropna()
        .astype(int)
    )

    # breakpoint()

    evaluator1_scores = pivot_df[evaluators[0]]
    evaluator2_scores = pivot_df[evaluators[1]]

    from sklearn.metrics import confusion_matrix

    # Generate confusion matrix
    cm = confusion_matrix(evaluator1_scores, evaluator2_scores, labels=[1, 2, 3, 4, 5])

    # Plotting (Converted to Object-Oriented Style)
    fig, ax = plt.subplots(figsize=(8, 6))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=[1, 2, 3, 4, 5],
        yticklabels=[1, 2, 3, 4, 5],
        ax=ax,  # Explicitly draw onto the created axes object
    )

    ax.invert_yaxis()

    # Use the ax.set_ methods instead of plt.
    ax.set_xlabel(evaluators[1])
    ax.set_ylabel(evaluators[0])
    ax.set_title("Agreement Heatmap (Raw Counts)")

    fig.tight_layout()

    # Return the figure packaged in a dictionary
    return {"heuristic_scores_correlation": fig}


def basic_heuristic_scores_display(granular_df: pd.DataFrame):
    logger.info("Generating basic heuristic scores display")

    # Data massaging
    df = granular_df.loc[
        (granular_df["evaluation_type"] == "heuristic")
        & (granular_df["dimension2"] == "score"),
    ]

    # Graphing
    plots = {}
    evaluators = df["evaluator_model"].unique()
    for i, evaluator in enumerate(evaluators):
        # Create a new figure
        fig, ax = plt.subplots(figsize=(8, 6))
        # Filter data for specific evaluator
        subset = df[df["evaluator_model"] == evaluator]

        # Group and calculate mean
        mean_scores = subset.groupby(["id", "dimension"])["value"].mean().reset_index()

        # Create clustered bar plot
        sns.barplot(data=mean_scores, x="id", y="value", hue="dimension", ax=ax)

        ax.set_title(f"Evaluator: {evaluator}")
        ax.set_ylim(0, 5)
        ax.set_xlabel("Model")
        ax.set_ylabel("Average Score")
        ax.tick_params(axis="x", rotation=45)
        ax.legend(title="Dimension", bbox_to_anchor=(1.05, 1), loc="upper left")

        fig.tight_layout()
        plots[f"heuristic_basicdisplay_{evaluator}"] = fig

    return plots


def heuristic_cuisines_finetuning_impact(granular_df: pd.DataFrame) -> dict:
    logger.info("Generating heuristic cuisine-level finetuning impact")

    # Data
    df = granular_df.loc[
        (granular_df["evaluation_type"] == "heuristic")
        & (granular_df["dimension2"] == "score"),
    ].copy()  # Using .copy() to avoid SettingWithCopyWarning

    conditions = [
        df["id"].isin(["qwen4bft", "llama8bft"]),
        df["id"].isin(["qwen4bbase", "llama8bbase"]),
    ]
    choices = ["finetuned", "base"]
    df["model_status"] = np.select(conditions, choices, default="teacher")

    # Graphing
    melted = pd.melt(
        df,
        id_vars=["model_status", "value"],
        value_vars=["cuisine_a", "cuisine_b"],
        value_name="cuisine",
    )

    # Calculate means
    cuisine_scores = (
        melted.groupby(["cuisine", "model_status"])["value"].mean().reset_index()
    )

    # Sort values logically
    cuisine_scores = cuisine_scores.sort_values(by="cuisine")

    breakpoint()

    # Plotting (Converted to Object-Oriented Style)
    fig, ax = plt.subplots(figsize=(16, 6))

    # Fixed y and hue to match your grouped dataframe columns
    sns.barplot(
        data=cuisine_scores,
        x="cuisine",
        y="value",
        hue="model_status",
        ax=ax,
    )

    # Use ax.set_ methods instead of plt.
    ax.set_title(
        'Average Representation Score per Cuisine (Averages over evaluators)\nBase vs Fine-tuned (Note unseen "French" test data)',
        fontsize=14,
    )
    ax.set_xlabel("Cuisine")
    ax.set_ylabel("Average Score")
    ax.set_ylim(0, 5)

    # Use plt.setp to handle rotation and alignment cleanly on the axes text objects
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    # Highlight 'French' label in red on the x-axis to draw attention
    for tick_label in ax.get_xticklabels():
        if tick_label.get_text() == "French":
            tick_label.set_color("red")
            tick_label.set_fontweight("bold")

    ax.legend(title="Model Version")

    fig.tight_layout()

    # Return the figure packaged in a dictionary
    return {"heuristic_cuisines_finetuning_impact": fig}


def heuristic_evaluation_distributions(granular_df: pd.DataFrame) -> dict:
    logger.info("Generating heuristic score distributions (evaluator comparison)")

    df = granular_df.loc[
        (granular_df["evaluation_type"] == "heuristic")
        & (granular_df["dimension2"] == "score"),
    ].copy()  # Using .copy() to avoid SettingWithCopyWarning

    # Plotting (Converted to Object-Oriented Style)
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot overlapping histograms with KDE for the raw scores
    sns.histplot(
        data=df,
        x="value",
        hue="evaluator_model",
        discrete=True,  # Perfectly centers bins on integers 0-5
        multiple="layer",  # Overlaps the histograms
        alpha=0.4,  # Makes the layers transparent
        kde=True,  # Adds the smooth density curves
        kde_kws={"bw_adjust": 2.0},
        shrink=0.8,  # Leaves a slight gap between bars for readability
        palette="muted",
        ax=ax,  # Explicitly draw onto the created axes object
    )

    # Use ax.set_ methods instead of plt.
    ax.set_title(
        "Heuristic Score Distribution Comparison by Evaluator\n(Aggregated across all models, dimensions, and cuisines)"
    )
    ax.set_xlabel("Score (1-5)")
    ax.set_ylabel("Frequency (Count)")

    # Lock x-ticks to the exact score values using the axes object
    ax.set_xticks(range(6))

    fig.tight_layout()

    # Return the figure packaged in a dictionary
    return {"heuristic_evaluation_distributions": fig}


def graphing_pipeline(cfg: DictConfig, df):
    logger.info("Starting the full graphing pipeline...")

    granular_df = df[~(df["value"].isin([0, -1]))]

    # 1. Call all refactored plotting functions
    # (Adjust 'task1_basic_display' if it still requires a 'self' object reference)
    task1_plots = basic_heuristic_scores_display(granular_df)
    correlation_plots = heuristic_scores_heatmap(granular_df)
    impact_plots = heuristic_cuisines_finetuning_impact(granular_df)
    distribution_plots = heuristic_evaluation_distributions(granular_df)

    # Define the destination directory
    output_folder = os.path.join(cfg.evaluation_folder_path, "plots")

    # 2. Combine all plot dictionaries into a single master dictionary
    all_plots = {}
    plot_collections = [
        task1_plots,
        correlation_plots,
        impact_plots,
        distribution_plots,
    ]

    for task_plots in plot_collections:
        if isinstance(task_plots, dict):
            all_plots.update(task_plots)

    # 3. Send the master dictionary to be saved to disk
    save_plots(all_plots, output_folder=output_folder)
    logger.info("Graphing pipeline completed successfully.")


# def perform_analysis_df(cfg: DictConfig, df: pd.DataFrame):
#     analysis_cfg = cfg.analysis

#     df = df.drop(columns=analysis_cfg.drop_columns)
#     all_columns = df.columns

#     df.set_index()
