declare module "cloudflare:workers" {
  type D1Binding = Parameters<typeof import("drizzle-orm/d1").drizzle>[0];
  export const env: {
    DB: D1Binding;
    ASSETS?: {
      fetch(request: Request): Promise<Response>;
    };
    ZOHO_OAUTH_CLIENT_ID?: string;
    ZOHO_OAUTH_CLIENT_SECRET?: string;
    ZOHO_SESSION_SECRET?: string;
    ZOHO_ALLOWED_WORKSPACE_ID?: string;
    ZOHO_OAUTH_REDIRECT_URI?: string;
    ZOHO_PORTAL_ADMIN_EMAILS?: string;
    ZOHO_ACCOUNTS_BASE_URL?: string;
    ZOHO_ANALYTICS_API_BASE_URL?: string;
    ZOHO_PROFILE_BASE_URL?: string;
  };
}
