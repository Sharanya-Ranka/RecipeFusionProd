

export type JobStatus = 'pending' | 'completed' | 'failed';

export interface FusionJob {
  id: string;
  cuisineA: string;
  cuisineB: string;
  modelName: string;
  s3OutputPath: string;
  status: JobStatus;
  timestamp: number;
  resultData?: any; 
}


// --- TypeScript Interfaces for the parsed JSON ---
export interface Ingredient {
  name: string;
  amount: number | string;
  unit: string;
}

export interface Step {
  instruction: string;
  action: string;
  inputs: string[];
  result_name: string;
  metadata: string[][];
}

export interface RecipeJSON {
  description: string;
  ingredients: Ingredient[];
  steps: Step[];
}

export interface ParsedRecipeResult {
  recipeAName: string;
  recipeAData: RecipeJSON;
  recipeBName: string;
  recipeBData: RecipeJSON;
  explanation: string;
  fusionName: string;
  fusionData: RecipeJSON;
}




// --- TypeScript Declarations for Turnstile (Cloudflare's CAPTCHA) ---

interface TurnstileRenderOptions {
  sitekey: string;
  callback?: (token: string) => void;
  "error-callback"?: (errorCode: string) => void;
  "expired-callback"?: () => void;
  "timeout-callback"?: () => void;
  theme?: "light" | "dark" | "auto";
  action?: string;
  cData?: string;
  appearance?: "always" | "execute" | "interaction-only";
  execution?: "render" | "execute"; // <-- Added to control when the challenge runs
}

declare global {
  interface Window {
    turnstile: {
      execute: (container: string | HTMLElement, options: { sitekey?: string; callback: (token: string) => void, "error-callback"?: (errorCode: string) => void;}) => void;
      render: (container: string | HTMLElement, options: TurnstileRenderOptions) => string;
      reset: (container: string | HTMLElement) => void;
    };
    onTurnstileLoad?: () => void;
  }
}