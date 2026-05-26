
let turnstileWidgetId: string | HTMLElement | null = null;
const TURNSTILE_SITE_KEY = import.meta.env.VITE_TURNSTILE_SITE_KEY; // <-- Replace with your actual site key from Cloudflare

window.onTurnstileLoad = () => {
  console.log("Global script finished parsing via HTML header call.");
  initializeTurnstile();
};


/**
 * Initializes the widget configuration explicitly.
 * This should run once when your app mounts or your page loads.
 */
export function initializeTurnstile() {
  if (typeof window.turnstile !== "undefined") {
    turnstileWidgetId = window.turnstile.render("#turnstile-container", {
      sitekey: TURNSTILE_SITE_KEY,
      appearance: "always",     // Options: always, execute, interaction-only
      execution: "execute",     // <-- Tell Cloudflare NOT to run the challenge on load
      
      callback: function (token) {
        console.log("Challenge passed. Token generated programmatically:", token);
      },
      "error-callback": function (error) {
        console.error("Turnstile challenge execution encountered an error:", error);
      }
    });
  }
}

/**
 * Triggered right before making an API call to your Lambda function
 */
export async function getSecureVerificationToken(): Promise<string> {
  if (!turnstileWidgetId) {
    throw new Error("Turnstile has not been initialized yet.");
  }

  const validTurnstileWidgetId = turnstileWidgetId as string; // Type assertion for better compatibility with the execute method
//   console.log("Getting secure verification token. Current widget ID:", validTurnstileWidgetId);
  return new Promise((resolve, reject) => {
    // Override or hook into the execution loop manually
    window.turnstile.reset(validTurnstileWidgetId); // Reset any previous state to ensure a fresh challenge
    window.turnstile.execute(validTurnstileWidgetId, {
      callback: (token) => {
        resolve(token); // Hands the fresh token over to your fetch handler
      },
      "error-callback": (err) => {
        reject(err);
      }
    });
  });
}