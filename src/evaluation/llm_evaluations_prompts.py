from src.utils.utils import fill_prompt_template

BASE_PROMPT_TEMPLATE = """
# Role
You are an impartial judge evaluating the quality of an LLM response.

{{DEFINITION_EVALSTEPS_RUBRIC}}

# Task
Follow the Evaluation Steps carefully. 
1. Provide a "Rationale" explaining your thought process regarding this specific example.
2. Provide a "Score" based on the rubric.

# Output Format
Your final output MUST be a JSON object with the following format:
```json
{
    "rationale": "Your detailed reasoning here.",
    "score": 1  // An integer score based on the rubric
}
```
"""

# DER = Definition, Evaluation Steps, Rubric
CULINARY_CREATIVITY_DER = """
## 1. Culinary Creativity (The Fusion Delta)

**Formal Definition**
Culinary Creativity measures the degree of novel synthesis and the transformative "delta" between source cuisines, evaluating whether the output achieves a distinct, new culinary identity rather than a simple assembly or basic ingredient swap. It strictly does NOT measure flavor profile, physical plausibility of the cooking process, or adherence to formatting constraints; a conceptually bizarre but highly novel fusion is rewarded here while a traditional dish is penalized.

**Evaluation Steps**
1. **Identify the Baselines:** Determine the distinct base cuisines, dishes, or core concepts intended for fusion within the prompt.
2. **Analyze the Structural Integration:** Examine how the components are combined—look for deep methodological integration rather than superficial plating (e.g., side-by-side assembly).
3. **Assess the "Delta":** Measure the conceptual distance between the final generated concept and the original baseline dishes.
4. **Evaluate Technique Transference:** Identify if a process or technique native to one cuisine is uniquely and unexpectedly applied to an ingredient native to the other.
5. **Isolate the Construct:** Verify that the final assessment strictly ignores whether the dish would taste good, be physically possible to cook, or make logical sense.

**Scoring Rubric**
* **1 (Fail):** Zero integration. Cuisines or ingredients are served side-by-side or remain entirely distinct on the plate (e.g., serving a taco next to a bowl of ramen). 
* **2 (Below Average):** Lazy fusion. Relies exclusively on basic, superficial ingredient swaps (e.g., using soy sauce instead of salt) without altering the core structure of the base dish.
* **3 (Average):** Noticeable structural synthesis. Combines elements of both cuisines into a cohesive single item, but the conceptual leap is predictable, safe, or heavily standardized (e.g., a standard "kimchi burger").
* **4 (Above Average):** High degree of synthesis. Introduces unexpected combinations of techniques and ingredients, pushing past safe tropes to create a clearly new culinary identity.
* **5 (Excellent):** Transformative synthesis. Entirely reimagines the source materials through masterful cross-pollination of techniques and core components, resulting in an unprecedented, highly original culinary paradigm.
"""

CAUSAL_REALISM_DER = """
## 2. Causal Realism (Physical Grounding)

**Formal Definition**
Causal Realism evaluates the physical grounding and internal consistency of the described cooking process, ensuring the explicit instructions logically dictate the claimed textures, states, and final outcomes. It strictly does NOT evaluate conceptual innovation, flavor harmony, or accurate representation of the original source dishes; it focuses purely on minimizing the "narrative-physics gap" of the generated text.

**Evaluation Steps**
1. **Extract End States:** Identify the claimed final physical states, visual appearances, and textures of the dish as described by the model.
2. **Trace the Causal Chain:** Review the step-by-step instructions provided to achieve these specific end states.
3. **Evaluate Material Properties:** Assess whether the stated ingredients behave according to their real-world physical and chemical properties under the described conditions (e.g., melting points, coagulation).
4. **Identify Narrative-Physics Gaps:** Pinpoint any contradictions where the described process physically cannot yield the described result (e.g., achieving a dry, crispy crust via steaming).
5. **Isolate the Construct:** Ensure the score is completely divorced from the dish's creativity, novelty, or palatability, judging strictly on process-to-outcome causality.

**Scoring Rubric**
* **1 (Fail):** Complete physical disconnect. The instructions fundamentally contradict the described outcome (e.g., deep-frying a liquid resulting in a cold, clear broth).
* **2 (Below Average):** Significant logical gaps. States and textures are claimed, but the methods used to achieve them are highly improbable, contradictory, or ignore basic ingredient properties.
* **3 (Average):** Generally sound physical grounding. The steps logically produce the intended result, with only minor or forgivable incongruities in time, temperature, or physical texture mapping.
* **4 (Above Average):** Strong internal consistency. The text demonstrates a solid grasp of ingredient behavior and thermal state changes, accurately matching detailed steps to the resulting textures.
* **5 (Excellent):** Perfect causal realism. Flawlessly detailed physical transformations where the variables of time, temperature, and material properties impeccably and undeniably result in the claimed physical output.
"""

CULINARY_VIABILITY_DER = """
## 3. Culinary Viability (Cohesion + Feasibility)

**Formal Definition**
Culinary Viability assesses the practical feasibility and chemical harmony of the recipe, determining if the ingredients logically complement each other and if the proportions, times, and tools reflect standard kitchen realities. It strictly does NOT measure the creativity or "delta" of the fusion (safe dishes score high), nor does it evaluate narrative-physics consistency; it answers the purely pragmatic questions of "Should we?" and "Can we?" cook this.

**Evaluation Steps**
1. **Audit Proportions:** Analyze the ingredient list and quantities to ensure they are realistic for human consumption and standard serving sizes.
2. **Evaluate Chemical Harmony:** Assess the flavor profiles (fat, acid, salt, heat, sweet) for fundamental culinary balance, looking for severe molecular clashes or inherently unpalatable combinations.
3. **Verify Operational Logic:** Review the required equipment, cooking times, and temperatures to confirm they are standard and exist in actual home or professional kitchens.
4. **Identify Resource Constraints:** Flag any toxic, inherently inedible, physically dangerous, or practically impossible resource requirements.
5. **Isolate the Construct:** Purposely ignore the novelty or "boringness" of the dish, ensuring a highly traditional, uncreative—but perfectly cookable and tasty—recipe receives maximum points.

**Scoring Rubric**
* **1 (Fail):** Completely unviable. Features fundamentally clashing/inedible flavors, dangerously absurd proportions (e.g., 2 cups of baking soda), or requires imaginary/impossible equipment.
* **2 (Below Average):** Poor viability. Contains major flaws in chemical harmony (e.g., extreme over-salting, high acidity curdling dairy unintentionally) or operational logic that makes execution highly problematic or unpalatable.
* **3 (Average):** Baseline viability. Flavors generally make sense and the dish can be cooked with standard tools, though ingredient proportions, ratios, or flavor balances may require minor tweaking by a human chef to be truly good.
* **4 (Above Average):** High viability. Exhibits well-balanced flavor chemistry, precise and realistic proportions, and a highly executable, practical process for a standard kitchen.
* **5 (Excellent):** Flawless viability. Demonstrates expert-level flavor harmony, meticulously balanced ingredient proportions, and a completely pragmatic, highly executable procedure using standard kitchen resources to yield a delicious result.
"""


CULINARY_CREATIVITY_PROMPT = fill_prompt_template(
    BASE_PROMPT_TEMPLATE, dict(DEFINITION_EVALSTEPS_RUBRIC=CULINARY_CREATIVITY_DER)
)
CAUSAL_REALISM_PROMPT = fill_prompt_template(
    BASE_PROMPT_TEMPLATE, dict(DEFINITION_EVALSTEPS_RUBRIC=CAUSAL_REALISM_DER)
)
CULINARY_VIABILITY_PROMPT = fill_prompt_template(
    BASE_PROMPT_TEMPLATE, dict(DEFINITION_EVALSTEPS_RUBRIC=CULINARY_VIABILITY_DER)
)

# breakpoint()
