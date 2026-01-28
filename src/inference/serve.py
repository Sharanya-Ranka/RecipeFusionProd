import hydra
from omegaconf import DictConfig
from vllm import LLM, SamplingParams
from src.data_engine.formatter import create_conversation  # Reusing your logic!


class FusionChefServer:
    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        # Initialize the engine
        self.llm = LLM(
            model=cfg.model.path,
            gpu_memory_utilization=cfg.inference.gpu_utilization,
            tensor_parallel_size=cfg.inference.tensor_parallel,
        )
        self.sampling_params = SamplingParams(
            temperature=cfg.inference.temperature,
            top_p=cfg.inference.top_p,
            max_tokens=cfg.inference.max_tokens,
        )

    def generate(self, cuisine_a, cuisine_b):
        # 1. Reuse the exact sample structure from your notebook
        sample = {
            "recipe_a": {"cuisine": cuisine_a, "title": "...", "recipe_json_str": "{}"},
            "recipe_b": {"cuisine": cuisine_b, "title": "...", "recipe_json_str": "{}"},
            "fusion_dish_name": "...",
            "fusion_recipe": "{}",
            "fusion_strategy": "...",
            "fusion_explanation": "...",
        }

        # 2. Reuse the conversion logic from your original code
        # We pass the templates from our Hydra config
        conv = create_conversation(sample, self.cfg.prompts.fusion_chef)

        # 3. Run inference
        outputs = self.llm.generate([conv["messages"]], self.sampling_params)
        return outputs[0].outputs[0].text


@hydra.main(version_base=None, config_path="configs", config_name="config")
def main(cfg: DictConfig):
    server = FusionChefServer(cfg)
    # In a full production script, you would wrap this in a FastAPI app here:
    # uvicorn.run(app, host=cfg.server.host, port=cfg.server.port)
    print(f"Server initialized on {cfg.server.host}:{cfg.server.port}")


if __name__ == "__main__":
    main()
