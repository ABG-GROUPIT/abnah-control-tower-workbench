import { resolveZohoSession } from "../../../lib/zoho-auth-server";

export async function GET(request: Request) {
  const resolved = await resolveZohoSession(request);
  const headers = new Headers({
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
  });
  if (resolved.refreshedCookie) {
    headers.append("set-cookie", resolved.refreshedCookie);
  }
  return new Response(JSON.stringify(resolved.publicSession), { headers });
}
