import { useMemo } from 'react';
import type { FusionJob } from '../types';
import type { ParsedRecipeResult } from '../types';
import { DUMMY_RESPONSE } from '../constants';
import RecipeDAGViewer from './RecipeDAGViewer';

// --- Parsing Logic ---
const parseLLMResponse = (text: string): ParsedRecipeResult | null => {
  try {
    const recipeARegex = /RecipeA:\s*\n([^\n]+)\s*\n(\{[\s\S]*?\})\s*RecipeB:/;
    const recipeBRegex = /RecipeB:\s*\n([^\n]+)\s*\n(\{[\s\S]*?\})\s*Fusion Explanation:/;
    const explanationRegex = /Fusion Explanation:\s*\n([\s\S]*?)\s*RecipeFusion:/;
    const fusionRegex = /RecipeFusion:\s*\n([^\n]+)\s*\n(\{[\s\S]*\})$/;

    const matchA = text.match(recipeARegex);
    const matchB = text.match(recipeBRegex);
    const matchExpl = text.match(explanationRegex);
    const matchFusion = text.match(fusionRegex);

    if (!matchA || !matchB || !matchExpl || !matchFusion) {
      throw new Error("Could not match all required sections in the text.");
    }

    return {
      recipeAName: matchA[1].trim(),
      recipeAData: JSON.parse(matchA[2]),
      recipeBName: matchB[1].trim(),
      recipeBData: JSON.parse(matchB[2]),
      explanation: matchExpl[1].trim(),
      fusionName: matchFusion[1].trim(),
      fusionData: JSON.parse(matchFusion[2]),
    };
  } catch (error) {
    console.error("Failed to parse recipe text:", error);
    return null;
  }
};

export default function Recipe({ job }: { job: FusionJob }) {
  const rawData: string = job.resultData;
  console.log("Received job data:", job);
  
  const textToParse = rawData || DUMMY_RESPONSE;
  const parsedData = useMemo(() => parseLLMResponse(textToParse), [textToParse]);
  const fusionLabel = job.cuisineA + " + " + job.cuisineB + " (" + job.modelName + ")";

  if (!parsedData) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-6 rounded-lg">
        <h3 className="font-bold">Error parsing recipe data</h3>
        <p className="text-sm mt-2">The model output could not be parsed into the expected JSON format.</p>
        <pre className="mt-4 text-xs bg-white p-4 rounded overflow-auto max-h-64">
          {textToParse}
        </pre>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12">
      {/* Fusion Header & Explanation */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-blue-100">
        <div className="inline-block bg-blue-100 text-blue-800 text-xs font-bold px-2 py-1 rounded mb-3 uppercase tracking-wide">
          Fusion Result
        </div>
        <h3 className="text-3xl font-bold text-gray-900 mb-4">{fusionLabel}</h3>
        <h3 className="text-3xl font-bold text-gray-900 mb-4">{parsedData.fusionName}</h3>
        <div className="bg-slate-50 p-4 rounded-md border border-slate-200 text-slate-700 italic">
          "{parsedData.explanation}"
        </div>
      </div>

      {/* Fusion Recipe Details */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Fusion Recipe Data</h3>
        <RecipeDAGViewer recipe={parsedData.fusionData} />
      </div>

      {/* Original Source Recipes Stacked Vertically */}
      <div className="flex flex-col gap-6 mt-8">
        
        {/* Source Recipe A */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-xs text-gray-500 font-bold uppercase mb-1">Source Recipe A</div>
          <h4 className="text-2xl font-bold text-gray-800 mb-4">{parsedData.recipeAName}</h4>
          <RecipeDAGViewer recipe={parsedData.recipeAData} />
        </div>

        {/* Source Recipe B */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-xs text-gray-500 font-bold uppercase mb-1">Source Recipe B</div>
          <h4 className="text-2xl font-bold text-gray-800 mb-4">{parsedData.recipeBName}</h4>
          <RecipeDAGViewer recipe={parsedData.recipeBData} />
        </div>

      </div>
    </div>
  );
}