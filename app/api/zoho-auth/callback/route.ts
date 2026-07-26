import {
  completeZohoAuthorization,
  getZohoAuthConfiguration,
} from "../../../lib/zoho-auth-server";

function portalRedirect(request: Request, error?: string) {
  const url = new URL("/portal", request.url);
  if (error) url.searchParams.set("auth_error", error);
  return url;
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  const oauthError = url.searchParams.get("error");
  if (oauthError) {
    return Response.redirect(
      portalRedirect(request, `Zoho sign-in was not completed: ${oauthError}.`),
      302,
    );
  }

  try {
    const config = await getZohoAuthConfiguration(request);
    if (!config.configured) {
      throw new Error(
        `Zoho OAuth is not configured: ${config.missing.join(", ")}.`,
      );
    }
    const code = url.searchParams.get("code") ?? "";
    const state = url.searchParams.get("state") ?? "";
    if (!code) throw new Error("Zoho did not return an authorization code.");
    const completed = await completeZohoAuthorization(
      request,
      config,
      code,
      state,
    );
    const headers = new Headers({
      location: portalRedirect(request).toString(),
      "cache-control": "no-store",
    });
    headers.append("set-cookie", completed.sessionCookie);
    headers.append("set-cookie", completed.clearStateCookie);
    return new Response(null, { status: 302, headers });
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Zoho sign-in failed.";
    return Response.redirect(portalRedirect(request, message), 302);
  }
}
