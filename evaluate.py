@hydra.main(config_path="configs", config_name="config")
def main(cfg):
    # 1. Load Eval Dataset
    dataset = load_dataset(cfg.evaluation.dataset_id)

    # 2. Run Inference (use the server or local LLM)
    results = []
    for sample in dataset:
        output = model.generate(sample["prompt"])

        # 3. Deterministic Metrics
        dist_score = compute_json_validity(output)  # Does it follow the DSL?

        # 4. Teacher Metrics
        teacher_score = get_teacher_score(output, cfg.evaluation.teacher)

        results.append({"deterministic": dist_score, "teacher": teacher_score})
