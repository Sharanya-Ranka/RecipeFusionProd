import hydra
from omegaconf import DictConfig
from src.data_engine.loader import load_fusion_dataset
from dotenv import load_dotenv
import os
import logging
import json
from src.evaluation.parse_responses import parse_recipefusion_file
from src.evaluation.format_fix_responses import fix_response_format_file
from src.evaluation.heuristic_requests_batched import (
    createAndSaveBatchRequests,
    sendRequests,
    monitorBatch,
    saveBatchResultsOpenAI,
    saveBatchResultsGemini,
)
from src.evaluation.heuristic_evaluation import extract_heuristic_evaluations
from src.evaluation.deterministic_evaluation import extract_deterministic_evaluations
from src.evaluation.analysis import form_granular_df, graphing_pipeline
from src.utils.utils import save_to_jsonl, load_from_jsonl
from src.utils.types import EvaluationKey, RecipeFusionInferenceKey

logger = logging.getLogger(__name__)
load_dotenv()

# --- Function Stubs ---


def eval_step_parse(cfg: DictConfig):
    """
    Parses LLM responses (RecipeFusions) to prepare for evaluation
    Logs requests that couldn't be parsed for format fixing.
    """
    logger.info("Starting step: parse")
    eval_cfg = cfg.evaluation

    base_folderpath = eval_cfg.evaluation_folder_path

    for filename in eval_cfg.filenames:
        filepath = os.path.join(
            base_folderpath, f"{filename}{eval_cfg.suffixes.inference_responses}.jsonl"
        )
        ff_filepath = os.path.join(
            base_folderpath, f"{filename}{eval_cfg.suffixes.format_fixed}.jsonl"
        )

        if os.path.exists(ff_filepath):
            logger.info(
                f"Found 'format_fixed' version of the path, using this instead: {ff_filepath}"
            )
            filepath = ff_filepath

        output_filepath = os.path.join(
            base_folderpath, f"{filename}{eval_cfg.suffixes.parse}.jsonl"
        )
        parse_recipefusion_file(filepath, output_filepath)
    logger.info("Completed step: parse")


def eval_step_format_fix(cfg: DictConfig):
    """Fixes formatting using an LLM."""
    logger.info("Starting step: format_fix")
    eval_cfg = cfg.evaluation

    base_folderpath = eval_cfg.evaluation_folder_path

    for filename, indices_to_fix in zip(
        eval_cfg.filenames, eval_cfg.format_fix_indices
    ):
        filepath = os.path.join(
            base_folderpath, f"{filename}{eval_cfg.suffixes.inference_responses}.jsonl"
        )
        output_filepath = os.path.join(
            base_folderpath, f"{filename}{eval_cfg.suffixes.format_fixed}.jsonl"
        )
        fix_response_format_file(filepath, output_filepath, indices_to_fix)
    logger.info("Completed step: fix_format")


def eval_step_heuristic_requests(cfg: DictConfig):
    """Forms and sends batched requests."""
    logger.info("Starting step: heuristic_requests")
    eval_cfg = cfg.evaluation

    if eval_cfg.create_requests:
        logger.info("Creating heuristic evaluation requests")
        for filename in eval_cfg.filenames:
            filepath = os.path.join(
                eval_cfg.evaluation_folder_path,
                f"{filename}{eval_cfg.suffixes.parse}.jsonl",
            )
            for evaluator in eval_cfg.evaluator_models:
                output_filepath = os.path.join(
                    eval_cfg.evaluation_folder_path,
                    f"{filename}_evalreq_{evaluator.name}.jsonl",
                )
                createAndSaveBatchRequests(
                    filepath, output_filepath, evaluator, partial_id=filename
                )

    if eval_cfg.send_requests:
        logger.info("Sending heuristic evaluation requests")
        for filename in eval_cfg.filenames:
            for evaluator in eval_cfg.evaluator_models:
                input_filepath = os.path.join(
                    eval_cfg.evaluation_folder_path,
                    f"{filename}_evalreq_{evaluator.name}.jsonl",
                )
                sendRequests(input_filepath, evaluator)

    logger.info(
        f"Completed step: heuristic_requests\nCreated Requests={eval_cfg.create_requests}\nSent requests={eval_cfg.send_requests}"
    )


def eval_step_batch_monitor(cfg: DictConfig):
    """Monitors batches, and saves the responses when completed"""
    logger.info("Starting step: monitor_batches")
    eval_cfg = cfg.evaluation

    for filename, evaluator_name, batch_id, batch_type in eval_cfg.batch_info:
        batch_info = monitorBatch(batch_id, batch_type)
        output_filepath = os.path.join(
            eval_cfg.evaluation_folder_path,
            f"{filename}_evalres_{evaluator_name}.jsonl",
        )
        if batch_type == "openai" and batch_info.status == "completed":
            saveBatchResultsOpenAI(batch_info.output_file_id, output_filepath)
            logger.info(f"Responses saved to {output_filepath}")
        elif batch_type == "google" and batch_info.state.name == "JOB_STATE_SUCCEEDED":
            saveBatchResultsGemini(batch_info.dest.file_name, output_filepath)
            logger.info(f"Responses saved to {output_filepath}")
        else:
            logger.info("Batches did not complete. Check logs for status")

    logger.info("Completed step: monitor_batches")


def eval_step_heuristic_eval(cfg: DictConfig):
    """Saves LLM heuristic evaluation responses."""
    logger.info("Starting step: heuristic_eval")
    eval_cfg = cfg.evaluation
    output_filepath = os.path.join(
        eval_cfg.evaluation_folder_path,
        f"{eval_cfg.evaluations_granular_filename}.jsonl",
    )

    # Save empty data to clean up any previous records if the file already exists
    save_to_jsonl([], output_filepath, "w", context="Heuristic Evals")

    for filename in eval_cfg.filenames:
        for evaluator in eval_cfg.evaluator_models:
            input_filepath = os.path.join(
                eval_cfg.evaluation_folder_path,
                f"{filename}_evalres_{evaluator.name}.jsonl",
            )

            heuristic_evaluations = extract_heuristic_evaluations(input_filepath)
            heuristic_evals_json = [he.model_dump() for he in heuristic_evaluations]

            save_to_jsonl(
                heuristic_evals_json, output_filepath, "a", context="Heuristic Evals"
            )


def eval_step_deterministic_eval(cfg: DictConfig):
    """Performs deterministic evaluation."""
    logger.info("Starting step: deterministic evaluation")
    eval_cfg = cfg.evaluation
    output_filepath = os.path.join(
        eval_cfg.evaluation_folder_path,
        f"{eval_cfg.evaluations_granular_filename}.jsonl",
    )

    for filename in eval_cfg.filenames:
        input_filepath = os.path.join(
            eval_cfg.evaluation_folder_path,
            f"{filename}{eval_cfg.suffixes.parse}.jsonl",
        )

        deterministic_evaluations = extract_deterministic_evaluations(input_filepath)
        deterministic_evals_json = [de.model_dump() for de in deterministic_evaluations]

        save_to_jsonl(
            deterministic_evals_json,
            output_filepath,
            "a",
            context="Deterministic Evals",
        )


def eval_step_analysis(cfg: DictConfig):
    """Analyzes the evaluation results."""
    logger.info("Starting step: analysis")
    eval_cfg = cfg.evaluation
    records_filepath = os.path.join(
        eval_cfg.evaluation_folder_path,
        f"{eval_cfg.evaluations_granular_filename}.jsonl",
    )
    df = form_granular_df(eval_cfg, records_filepath)
    output_filepath = os.path.join(
        eval_cfg.evaluation_folder_path,
        f"{eval_cfg.evaluations_granular_filename}.csv",
    )

    df.to_csv(output_filepath)

    graphing_pipeline(eval_cfg, df)
    logger.info("Completed step: analysis")


# --- Main Entrypoint ---


@hydra.main(version_base=None, config_path="configs", config_name="config")
def main(cfg: DictConfig):
    step = cfg.evaluation.eval_step

    if step == "parse":
        eval_step_parse(cfg)
    elif step == "format_fix":
        eval_step_format_fix(cfg)
    elif step == "heuristic_requests":
        eval_step_heuristic_requests(cfg)
    elif step == "batch_monitor":
        eval_step_batch_monitor(cfg)
    elif step == "heuristic_eval":
        eval_step_heuristic_eval(cfg)
    elif step == "deterministic_eval":
        eval_step_deterministic_eval(cfg)
    elif step == "analysis":
        eval_step_analysis(cfg)
    else:
        logger.error(f"Unknown evaluation step: {step}")


if __name__ == "__main__":
    main()
