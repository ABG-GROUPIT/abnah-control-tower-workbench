import {
  createZohoAuthorization,
  getZohoAuthConfiguration,
} from "../../../lib/zoho-auth-server";

export async function GET(request: Request) {
  const config = await getZohoAuthConfiguration(request);
  if (!config.configured) {
    const portalUrl = new URL("/portal", request.url);
    portalUrl.searchParams.set(
      "auth_error",
      `Zoho OAuth is not configured: ${config.missing.join(", ")}`,
    );
    return Response.redirect(portalUrl, 302);
  }
  const authorization = createZohoAuthorization(request, config);
  return new Response(null, {
    status: 302,
    headers: {
      location: authorization.authorizationUrl,
      "set-cookie": authorization.stateCookie,
      "cache-control": "no-store",
    },
  });
}
