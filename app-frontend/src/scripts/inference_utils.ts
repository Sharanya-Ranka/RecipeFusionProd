import { getSecureVerificationToken } from "./turnstile_helpers.ts";
import { SYSTEM_PROMPT, USER_PROMPT_TEMPLATE } from "./prompts.ts";
export async function retrieveInference(requestId: string): Promise<string|null> {
  const publicApiUrl = import.meta.env.VITE_RETRIEVE_INFERENCE_LAMBDA_URL;

  // // 1. Get an invisible proof token from Turnstile ensuring a human is using your actual app
  // const turnstileToken = await getSecureVerificationToken();

  try {
    // 2. Pass BOTH the request_id and the invisible token to your Lambda function
    const response = await fetch(publicApiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        request_id: requestId,
        // cf_token: turnstileToken // <-- The proof packet
      }),
    });

    // console.log("Received Response (retrieveInference) Body used?:", response.bodyUsed);
    // 1. Grab the raw text instead of jumping straight to JSON
    const rawText = await response.text();
    // console.log("Raw Server Response Text:", rawText);

    if (!rawText) {
      return null;
      // throw new Error("Server returned an empty response body. Check your Lambda logs!");
    }

    // 2. Parse it manually now that you know it exists
    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
    const parsedResult = JSON.parse(rawText);
    // const parsedResult = await response.json();
    // console.log("Parsed Result Object:", parsedResult);
    // console.log("Parsed Output text:", parsedResult.output_text);
    return parsedResult.output_text;

  } catch (error) {
    console.error("Retrieval failed:", error);
    throw error;
  }
}

function getMessagePayload(cuisineA: string, cuisineB: string): Array<{role: string, content: string}> {
    const messages_payload = [
            {
                "role": "system", "content": SYSTEM_PROMPT
            },
            {
                "role": "user", "content": USER_PROMPT_TEMPLATE.replace("{CUISINE_A}", cuisineA).replace("{CUISINE_B}", cuisineB)
            }
        ];
    return messages_payload;

      }
export async function sendInferenceRequest(cuisineA: string, cuisineB: string, modelName:string): Promise<Record<string, any>> {
    let modelId:string="";
    const modelApiUrl:string=import.meta.env.VITE_INFERENCE_LAMBDA_URL;
    if (modelName === import.meta.env.VITE_QWEN_MODELNAME){
        modelId = import.meta.env.VITE_QWEN_MODELID;
    }
    else if (modelName === import.meta.env.VITE_LLAMA_MODELNAME){
        modelId = import.meta.env.VITE_LLAMA_MODELID;
    }


    // 1. Get an invisible proof token from Turnstile ensuring a human is using your actual app
    const turnstileToken = await getSecureVerificationToken();

    try {
        const messages_payload = getMessagePayload(cuisineA, cuisineB);
        // 2. Pass BOTH the request_id and the invisible token to your Lambda function
        const response = await fetch(modelApiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            cf_token: turnstileToken, // <-- The proof packet
            model_name: modelName,
            model_payload: {
                "model":modelId,
                "messages": messages_payload,
                "max_tokens": 10000,
                "temperature": 0.7,
            }
        }),
        });

        console.log("Received Response (sendInferenceRequest) Body used?:", response.bodyUsed);
        // 1. Grab the raw text instead of jumping straight to JSON
        const rawText = await response.text();
        console.log("Raw Server Response Text:", rawText);

        if (!rawText) {
          throw new Error("Server returned an empty response body. Check your Lambda logs!");
        }

        // 2. Parse it manually now that you know it exists
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const parsedResult = JSON.parse(rawText) as Record<string, any>;
        // const parsedResult = await response.json();
        return parsedResult;

    } catch (error) {
        console.error("Send inference request failed:", error);
        throw error;
    }
}