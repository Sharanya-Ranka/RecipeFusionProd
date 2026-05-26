import React, { useState } from 'react';
import IngredientCard from './IngredientCard';
import StepCard from './StepCard';

// Using the interfaces defined from your JSON structure
interface RecipeJSON {
  description: string;
  ingredients: { name: string; amount: number | string; unit: string }[];
  steps: {
    instruction: string;
    action: string;
    inputs: string[];
    result_name: string;
    metadata: string[][];
  }[];
}

export default function RecipeDAGViewer({ recipe }: { recipe: RecipeJSON }) {
  // We store the active step's result_name (or index) to track what is being hovered
  const [activeStepIndex, setActiveStepIndex] = useState<number | null>(null);

  const activeStep = activeStepIndex !== null ? recipe.steps[activeStepIndex] : null;

  return (
    <div className="flex flex-col md:flex-row gap-8 items-start">
      
      {/* Left Column: Base Ingredients */}
      <div className="w-full md:w-1/3 space-y-3">
        <h3 className="text-lg font-bold text-gray-800 border-b pb-2 mb-4">Base Ingredients</h3>
        <div className="flex flex-col gap-2">
          {recipe.ingredients.map((ing, idx) => {
            // Check if this base ingredient is an input for the currently hovered step
            const isInput = activeStep?.inputs.includes(ing.name);
            
            return (
              <IngredientCard 
                key={idx}
                name={ing.name}
                amount={ing.amount}
                unit={ing.unit}
                highlightStatus={isInput ? 'input' : 'none'}
              />
            );
          })}
        </div>
      </div>

      {/* Right Column: Execution Steps */}
      <div className="w-full md:w-2/3 space-y-3">
        <h3 className="text-lg font-bold text-gray-800 border-b pb-2 mb-4">Execution Graph (Steps)</h3>
        <div className="flex flex-col gap-3">
          {recipe.steps.map((step, idx) => {
            // 1. Is this the exact step the user is hovering?
            const isActive = activeStepIndex === idx;
            
            // 2. Is this step's output (result_name) used as an input for the hovered step?
            const isInputForActive = activeStep?.inputs.includes(step.result_name);

            let highlightStatus: 'none' | 'active' | 'input' = 'none';
            if (isActive) highlightStatus = 'active';
            if (isInputForActive) highlightStatus = 'input';

            return (
              <StepCard
                key={idx}
                index={idx}
                step={step}
                highlightStatus={highlightStatus}
                onHover={() => setActiveStepIndex(idx)}
                onLeave={() => setActiveStepIndex(null)}
              />
            );
          })}
        </div>
      </div>
      
    </div>
  );
}