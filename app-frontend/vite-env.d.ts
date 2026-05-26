interface ImportMetaEnv {
  readonly VITE_QWEN_LAMBDA_URL: string;
  readonly VITE_LLAMA_LAMBDA_URL: string;
  readonly VITE_RETRIEVE_INFERENCE_LAMBDA_URL: string;
  
  readonly VITE_QWEN_MODELNAME: string;
  readonly VITE_LLAMA_MODELNAME: string;
  readonly VITE_QWEN_MODELID: string;
  readonly VITE_LLAMA_MODELID: string;
  
  readonly VITE_TURNSTILE_SITE_KEY: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}