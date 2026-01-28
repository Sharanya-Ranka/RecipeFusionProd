# RecipeFusion
*AI techniques to create innovative culinary fusions.*

---

## 1. Initial Research (Ingredients Only)
This phase focuses on modeling recipes using graph-based structures to understand ingredient relationships and pairings.

* **Technique:** Recipe as a Graph (Graph-based generative techniques)
* **Directory:** `/Research/InitialResearch`



---

## 2. LLM Finetuning (Ingredients + Procedure)
This phase involves training Large Language Models to handle both ingredient lists and step-by-step cooking instructions.

### A. Domain-Specific Language (DSL)
Utilizing a custom language syntax to standardize recipe representation for improved model performance and logical consistency.

* **Directory:** `/Research/RecipeDSL`
* **Directory:** `/Research/RecipeFusion`

### B. JSON Directed Acyclic Graph (DAG)
Representing the cooking process as a flow of operations to ensure logical sequencing and dependency tracking in generated recipes.

* **Directory:** `/Research/RecipeFusionv2`