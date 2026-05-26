import type { FusionJob } from "./types";

export const DUMMY_RESPONSE = `Original Recipes: Doro Wat (Ethiopian) + Butter Chicken (Indian)

RecipeA:
Doro Wat
{
  "description": "Doro Wat is Ethiopia’s iconic spicy chicken stew, slow-cooked in a deeply aromatic sauce of berbere spice and niter kibbeh (spiced clarified butter), finished with hard-boiled eggs and served with injera. The berbere blend provides a complex, warm heat and smoky depth, while niter kibbeh adds a toasty, slightly sweet richness that mellows the berbere. Long simmering reduces the sauce into a glossy, clinging coating that soaks the chicken and eggs. The dish is traditionally served with flat, spongy injera for scooping and savoring the sauce.",
  "ingredients": [
    {"name": "chicken thighs", "amount": 1.2, "unit": "kg"},
    {"name": "onion", "amount": 2, "unit": "large"},
    {"name": "garlic cloves", "amount": 8, "unit": "pieces"},
    {"name": "ginger", "amount": 30, "unit": "g"},
    {"name": "berbere spice", "amount": 100, "unit": "g"},
    {"name": "niter kibbeh", "amount": 120, "unit": "g"},
    {"name": "tomato paste", "amount": 80, "unit": "g"},
    {"name": "chicken stock", "amount": 1.2, "unit": "L"},
    {"name": "hard-boiled eggs", "amount": 6, "unit": "pieces"},
    {"name": "salt", "amount": 1.5, "unit": "tsp"},
    {"name": "black pepper", "amount": 0.5, "unit": "tsp"},
    {"name": "lime", "amount": 1, "unit": "piece"}
  ],
  "steps": [
    {
      "instruction": "Peel and roughly chop the onions and garlic, and finely grate the ginger.",
      "action": "PREPARE",
      "inputs": ["onion", "garlic cloves", "ginger"],
      "result_name": "aromatics",
      "metadata": [["size", "rough chop"], ["container", "bowl"]]
    },
    {
      "instruction": "Heat a heavy pot over medium-high heat and add niter kibbeh, melting it until fragrant and slightly darkened.",
      "action": "MELT",
      "inputs": ["niter kibbeh"],
      "result_name": "niter_kibbeh_base",
      "metadata": [["container", "heavy pot"], ["time", "3-4 min"], ["visual", "fragrant, slightly darkened"]]
    },
    {
      "instruction": "Add the chopped aromatics to the pot and sauté until the onions are translucent and the garlic and ginger are softened.",
      "action": "SAUTE",
      "inputs": ["aromatics", "niter_kibbeh_base"],
      "result_name": "sautéed_aromatics",
      "metadata": [["container", "heavy pot"], ["time", "8-10 min"], ["visual", "translucent onions"]]
    },
    {
      "instruction": "Stir in the berbere spice and tomato paste and cook until the oil separates and the spice oils bloom, about 2-3 minutes.",
      "action": "BLOOM",
      "inputs": ["sautéed_aromatics", "berbere spice", "tomato paste"],
      "result_name": "spiced_base",
      "metadata": [["container", "heavy pot"], ["time", "2-3 min"], ["visual", "oil separates"]]
    },
    {
      "instruction": "Add the chicken thighs to the pot, season with salt and black pepper, and brown the chicken on all sides until a golden crust forms.",
      "action": "BROWN",
      "inputs": ["spiced_base", "chicken thighs", "salt", "black pepper"],
      "result_name": "browned_chicken",
      "metadata": [["container", "heavy pot"], ["time", "8-10 min"], ["visual", "golden crust"]]
    },
    {
      "instruction": "Pour in the chicken stock, bring to a simmer, then reduce heat to low and cook gently until the chicken is tender, about 45-60 minutes.",
      "action": "SIMMER",
      "inputs": ["browned_chicken", "chicken stock"],
      "result_name": "simmered_doro",
      "metadata": [["container", "heavy pot"], ["time", "45-60 min"], ["visual", "tender chicken"]]
    },
    {
      "instruction": "Remove the chicken to a cutting board, shred the meat and return to the pot with the sauce, then add the hard-boiled eggs and simmer 5 minutes to meld flavors.",
      "action": "SHRED_AND_COMBINE",
      "inputs": ["simmered_doro", "hard-boiled eggs"],
      "result_name": "finished_doro",
      "metadata": [["container", "heavy pot"], ["time", "5 min"], ["visual", "sauce coats shredded chicken"]]
    },
    {
      "instruction": "Serve the finished_doro hot with injera and squeeze lime over the eggs.",
      "action": "SERVE",
      "inputs": ["finished_doro", "lime"],
      "result_name": "served_doro",
      "metadata": [["container", "plate"], ["visual", "sauce clinging to shredded chicken and eggs"]]
    }
  ]
}

RecipeB:
Butter Chicken
{
  "description": "Butter Chicken is a classic North Indian curry of tender chicken simmered in a tangy, spiced tomato-butter sauce with warm spices and yogurt. The dish balances bright acidity from yogurt and tamarind with warm, aromatic spices like garam masala and coriander. Chicken is typically marinated briefly in yogurt and spices, then gently cooked so the sauce coats the meat and develops a glossy sheen. It is traditionally served with basmati rice or naan for scooping and pairing.",
  "ingredients": [
    {"name": "chicken thighs", "amount": 1.2, "unit": "kg"},
    {"name": "yogurt", "amount": 120, "unit": "g"},
    {"name": "garlic cloves", "amount": 4, "unit": "pieces"},
    {"name": "ginger", "amount": 20, "unit": "g"},
    {"name": "turmeric", "amount": 1, "unit": "tsp"},
    {"name": "garam masala", "amount": 1.5, "unit": "tsp"},
    {"name": "salt", "amount": 1.5, "unit": "tsp"},
    {"name": "tomato paste", "amount": 60, "unit": "g"},
    {"name": "onion", "amount": 1, "unit": "large"},
    {"name": "butter", "amount": 80, "unit": "g"},
    {"name": "oil", "amount": 20, "unit": "ml"},
    {"name": "lemon juice", "amount": 1, "unit": "tbsp"},
    {"name": "fresh cilantro", "amount": 30, "unit": "g"}
  ],
  "steps": [
    {
      "instruction": "Peel and finely chop the onion, garlic, and ginger.",
      "action": "PREPARE",
      "inputs": ["onion", "garlic cloves", "ginger"],
      "result_name": "aromatics",
      "metadata": [["size", "finely chopped"], ["container", "bowl"]]
    },
    {
      "instruction": "Mix yogurt with turmeric, salt, garam masala, and half the garlic and ginger to create a marinade and coat the chicken thighs.",
      "action": "MARINATE",
      "inputs": ["yogurt", "turmeric", "salt", "garam masala", "aromatics", "chicken thighs"],
      "result_name": "marinated_chicken",
      "metadata": [["container", "bowl"], ["time", "30 min"], ["visual", "coated chicken"]]
    },
    {
      "instruction": "Heat oil in a heavy skillet over medium heat and add the remaining garlic and ginger, sauté until fragrant.",
      "action": "SAUTE",
      "inputs": ["aromatics", "oil"],
      "result_name": "sautéed_garlic_ginger",
      "metadata": [["container", "skillet"], ["time", "2-3 min"], ["visual", "fragrant"]]
    },
    {
      "instruction": "Add tomato paste to the skillet and cook until it darkens and oil separates, about 3-4 minutes.",
      "action": "COOK",
      "inputs": ["sautéed_garlic_ginger", "tomato paste"],
      "result_name": "tomato_base",
      "metadata": [["container", "skillet"], ["time", "3-4 min"], ["visual", "oil separates"]]
    },
    {
      "instruction": "Add the marinated_chicken to the skillet, sear briefly to brown the exterior, then add the onion and cook until softened.",
      "action": "SEAR_AND_COOK",
      "inputs": ["marinated_chicken", "tomato_base", "onion"],
      "result_name": "seared_chicken",
      "metadata": [["container", "skillet"], ["time", "8-10 min"], ["visual", "browned exterior"]]
    },
    {
      "instruction": "Pour in warm water or stock, bring to a simmer, then reduce heat and simmer until the chicken is tender, about 20-25 minutes.",
      "action": "SIMMER",
      "inputs": ["seared_chicken", "water or stock"],
      "result_name": "simmered_chicken",
      "metadata": [["container", "skillet"], ["time", "20-25 min"], ["visual", "tender chicken"]]
    },
    {
      "instruction": "Stir in butter and lemon juice, simmer 2-3 minutes to emulsify and brighten the sauce, then finish with chopped cilantro.",
      "action": "FINISH",
      "inputs": ["simmered_chicken", "butter", "lemon juice", "fresh cilantro"],
      "result_name": "finished_butter_chicken",
      "metadata": [["container", "skillet"], ["time", "2-3 min"], ["visual", "glossy sauce"]]
    },
    {
      "instruction": "Serve the finished_butter_chicken hot with basmati rice or naan.",
      "action": "SERVE",
      "inputs": ["finished_butter_chicken"],
      "result_name": "served_butter_chicken",
      "metadata": [["container", "plate"], ["visual", "glossy sauce over chicken"]]
    }
  ]
}

Fusion Explanation:
I fused Doro Wat and Butter Chicken to create a dish that preserves the soul of both cuisines: Doro Wat’s berbere heat, niter kibbeh richness, and long-simmered sauce; and Butter Chicken’s tangy yogurt, tamarind brightness, and buttery finish. The strategy is to layer berbere and garam masala for a balanced heat and aromatic complexity, use niter kibbeh as a foundational fat and umami element, and introduce yogurt and tamarind to provide the Indian tang and cooling contrast. Chicken is briefly marinated in a hybrid yogurt-berbere marinade to marry textures and flavors, then simmered in a combined sauce that melds berbere-tomato base with butter and yogurt to create a glossy, clinging coating. The fusion keeps the scooping vehicle (injera or rice) and finishes with cilantro and lime to bridge Ethiopian and Indian herbaceousness.

RecipeFusion:
Niter Berbere Butter Chicken with Tamarind Yogurt
{
  "description": "Niter Berbere Butter Chicken marries Ethiopian berbere and niter kibbeh with Indian yogurt, tamarind, and butter to create a glossy, tangy-spicy chicken stew. The chicken is marinated in a yogurt-berbere blend, then cooked in a niter kibbeh-butter base that is enriched with tomato and finished with tamarind yogurt for brightness. The result is a deeply aromatic, slightly sweet, and tangy sauce that clings to tender chicken and hard-boiled eggs, served with injera or basmati rice. The dish balances warm spice, toasty clarified butter, and cooling yogurt to create a harmonious cross-cultural curry.",
  "ingredients": [
    {"name": "chicken thighs", "amount": 1.2, "unit": "kg"},
    {"name": "yogurt", "amount": 120, "unit": "g"},
    {"name": "berbere spice", "amount": 70, "unit": "g"},
    {"name": "garam masala", "amount": 1.5, "unit": "tsp"},
    {"name": "niter kibbeh", "amount": 100, "unit": "g"},
    {"name": "butter", "amount": 80, "unit": "g"},
    {"name": "garlic cloves", "amount": 6, "unit": "pieces"},
    {"name": "ginger", "amount": 20, "unit": "g"},
    {"name": "onion", "amount": 2, "unit": "large"},
    {"name": "tomato paste", "amount": 60, "unit": "g"},
    {"name": "tamarind paste", "amount": 1, "unit": "tbsp"},
    {"name": "chicken stock", "amount": 1.2, "unit": "L"},
    {"name": "hard-boiled eggs", "amount": 6, "unit": "pieces"},
    {"name": "salt", "amount": 1.5, "unit": "tsp"},
    {"name": "black pepper", "amount": 0.5, "unit": "tsp"},
    {"name": "lemon juice", "amount": 1, "unit": "tbsp"},
    {"name": "fresh cilantro", "amount": 30, "unit": "g"},
    {"name": "lime", "amount": 1, "unit": "piece"}
  ],
  "steps": [
    {
      "instruction": "Peel and finely chop the onions, garlic, and ginger.",
      "action": "PREPARE",
      "inputs": ["onion", "garlic cloves", "ginger"],
      "result_name": "aromatics",
      "metadata": [["size", "finely chopped"], ["container", "bowl"]]
    },
    {
      "instruction": "Mix yogurt with berbere spice, garam masala, half the garlic and ginger, and salt to create a hybrid marinade and coat the chicken thighs.",
      "action": "MARINATE",
      "inputs": ["yogurt", "berbere spice", "garam masala", "aromatics", "chicken thighs", "salt"],
      "result_name": "berbere_yogurt_marinade",
      "metadata": [["container", "bowl"], ["time", "30 min"], ["visual", "coated chicken"]]
    },
    {
      "instruction": "Heat a heavy pot over medium-high heat and add niter kibbeh, melting it until fragrant and slightly darkened.",
      "action": "MELT",
      "inputs": ["niter kibbeh"],
      "result_name": "niter_kibbeh_base",
      "metadata": [["container", "heavy pot"], ["time", "3-4 min"], ["visual", "fragrant, slightly darkened"]]
    },
    {
      "instruction": "Add the chopped aromatics to the pot and sauté until the onions are translucent and the garlic and ginger are softened.",
      "action": "SAUTE",
      "inputs": ["aromatics", "niter_kibbeh_base"],
      "result_name": "sautéed_aromatics",
      "metadata": [["container", "heavy pot"], ["time", "8-10 min"], ["visual", "translucent onions"]]
    },
    {
      "instruction": "Stir in tomato paste and cook until oil separates and the tomato base darkens, about 3-4 minutes.",
      "action": "COOK",
      "inputs": ["sautéed_aromatics", "tomato paste"],
      "result_name": "tomato_base",
      "metadata": [["container", "heavy pot"], ["time", "3-4 min"], ["visual", "oil separates"]]
    },
    {
      "instruction": "Add the marinated_chicken to the pot, sear briefly to brown the exterior, then add the remaining garlic and ginger and cook until softened.",
      "action": "SEAR_AND_COOK",
      "inputs": ["berbere_yogurt_marinade", "tomato_base", "garlic cloves", "ginger"],
      "result_name": "seared_chicken",
      "metadata": [["container", "heavy pot"], ["time", "8-10 min"], ["visual", "browned exterior"]]
    },
    {
      "instruction": "Pour in chicken stock and bring to a simmer, then reduce heat to low and cook gently until the chicken is tender, about 35-45 minutes.",
      "action": "SIMMER",
      "inputs": ["seared_chicken", "chicken stock"],
      "result_name": "simmered_chicken",
      "metadata": [["container", "heavy pot"], ["time", "35-45 min"], ["visual", "tender chicken"]]
    },
    {
      "instruction": "Remove the chicken to a cutting board, shred the meat and return to the pot with the sauce, then add the hard-boiled eggs and simmer 5 minutes to meld flavors.",
      "action": "SHRED_AND_COMBINE",                                                                                                                      
      "inputs": ["simmered_chicken", "hard-boiled eggs"],                                                                                                 
      "result_name": "combined_chicken",                                                                                                                  
      "metadata": [["container", "heavy pot"], ["time", "5 min"], ["visual", "sauce coats shredded chicken"]]                                             
    },                                                                                                                                                    
    {                                                                                                                                                     
      "instruction": "Stir in butter and tamarind paste, then simmer 2-3 minutes to emulsify and deepen the sauce color.",                                
      "action": "EMULSIFY",                                                                                                                               
      "inputs": ["combined_chicken", "butter", "tamarind paste"],                                                                                         
      "result_name": "emulsified_chicken",                                                                                                                
      "metadata": [["container", "heavy pot"], ["time", "2-3 min"], ["visual", "glossy, darkened sauce"]]                                                 
    },                                                                                                                                                    
    {                                                                                                                                                     
      "instruction": "Stir in lemon juice and a splash of yogurt to brighten and cool the sauce, then finish with chopped cilantro and a squeeze of lime.",                                                                                                                                                         
      "action": "FINISH",                                                                                                                                 
      "inputs": ["emulsified_chicken", "lemon juice", "yogurt", "fresh cilantro", "lime"],                                                                
      "result_name": "finished_fusion_chicken",                                                                                                           
      "metadata": [["container", "heavy pot"], ["time", "2 min"], ["visual", "glossy, tangy sauce"]]                                                      
    },                                                                                                                                                    
    {                                                                                                                                                     
      "instruction": "Serve the finished_fusion_chicken hot with injera or basmati rice and squeeze lime over the eggs.",                                 
      "action": "SERVE",                                                                                                                                  
      "inputs": ["finished_fusion_chicken", "lime"],                                                                                                      
      "result_name": "served_fusion_chicken",                                                                                                             
      "metadata": [["container", "plate"], ["visual", "sauce clinging to shredded chicken and eggs"]]                                                     
    }                                                                                                                                                     
  ]                                                                                                                                                       
}`


export const exampleJob: FusionJob = {
  id: 'example-job-123',
  cuisineA: 'Ethiopian',
  cuisineB: 'Indian',
  modelName: import.meta.env.VITE_QWEN_MODELNAME,
  s3OutputPath: 'None',
  status: 'completed',
  timestamp: Date.now(),
  resultData: DUMMY_RESPONSE,
};