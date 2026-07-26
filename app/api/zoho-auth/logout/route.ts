import { clearZohoSessionCookie } from "../../../lib/zoho-auth-server";

export async function POST(request: Request) {
  return new Response(null, {
    status: 204,
    headers: {
      "set-cookie": clearZohoSessionCookie(request),
      "cache-control": "no-store",
    },
  });
}
