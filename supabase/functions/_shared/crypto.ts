const encoder = new TextEncoder();
const decoder = new TextDecoder();

function encodeBase64Url(bytes: Uint8Array) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary)
    .replaceAll("+", "-")
    .replaceAll("/", "_")
    .replace(/=+$/, "");
}

function decodeBase64Url(value: string) {
  const padded = value.replaceAll("-", "+").replaceAll("_", "/");
  const binary = atob(
    padded + "=".repeat((4 - (padded.length % 4 || 4)) % 4),
  );
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

async function encryptionKey(secret: string) {
  const digest = await crypto.subtle.digest("SHA-256", encoder.encode(secret));
  return crypto.subtle.importKey(
    "raw",
    digest,
    { name: "AES-GCM" },
    false,
    ["encrypt", "decrypt"],
  );
}

export function randomOpaqueValue(bytes = 32) {
  return encodeBase64Url(crypto.getRandomValues(new Uint8Array(bytes)));
}

export async function hashOpaqueValue(value: string) {
  const digest = new Uint8Array(
    await crypto.subtle.digest("SHA-256", encoder.encode(value)),
  );
  return encodeBase64Url(digest);
}

export async function encryptSecret(value: string, secret: string) {
  if (!value) return "";
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ciphertext = new Uint8Array(
    await crypto.subtle.encrypt(
      { name: "AES-GCM", iv },
      await encryptionKey(secret),
      encoder.encode(value),
    ),
  );
  const payload = new Uint8Array(iv.length + ciphertext.length);
  payload.set(iv);
  payload.set(ciphertext, iv.length);
  return encodeBase64Url(payload);
}

export async function decryptSecret(value: string, secret: string) {
  if (!value) return "";
  const payload = decodeBase64Url(value);
  if (payload.length < 29) throw new Error("Encrypted token is malformed.");
  const plaintext = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: payload.slice(0, 12) },
    await encryptionKey(secret),
    payload.slice(12),
  );
  return decoder.decode(plaintext);
}
