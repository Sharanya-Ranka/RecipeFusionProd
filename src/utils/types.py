from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class RecipeFusionInferenceKey(BaseModel):
    # 'frozen=True' makes the object immutable and hashable,
    # allowing it to be used as a key in dictionaries or sets.
    model_config = ConfigDict(frozen=True)

    id: str = Field(
        ..., description="Usually the name of the model that created the response"
    )
    cuisine_a: str
    cuisine_b: str


class EvaluationKey(BaseModel):
    # model_config = ConfigDict(frozen=True)
    model_config = ConfigDict(validate_assignment=True)  # Enables validation on updates

    inference_key: RecipeFusionInferenceKey
    evaluation_type: Literal["heuristic", "deterministic"]
    dimension: str = Field(
        ...,
        description="The specific metric being evaluated (e.g., 'culinary_creativity')",
    )
    evaluator_model: Optional[str] = None


class Evaluation(BaseModel):
    key: EvaluationKey
    values: Dict[str, Any] = Field(default_factory=dict)
