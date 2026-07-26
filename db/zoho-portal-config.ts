import type {
  ZohoPortalConfigEnvelope,
  ZohoPortalHandoff,
} from "../app/lib/zoho-portal-types";
import { getD1 } from ".";

const configKey = "production";
let initialized = false;

async function ensureSchema() {
  if (initialized) return;
  const d1 = await getD1();
  await d1
    .prepare(`CREATE TABLE IF NOT EXISTS zoho_portal_config (
      config_key TEXT PRIMARY KEY NOT NULL,
      version INTEGER DEFAULT 1 NOT NULL,
      payload TEXT NOT NULL,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
      updated_by TEXT NOT NULL
    )`)
    .run();
  initialized = true;
}

interface PortalConfigRow {
  version: number;
  payload: string;
  updated_at: string;
  updated_by: string;
}

export class PortalConfigConflictError extends Error {}

export async function getZohoPortalConfig(): Promise<ZohoPortalConfigEnvelope | null> {
  await ensureSchema();
  const d1 = await getD1();
  const row = await d1
    .prepare(
      `SELECT version, payload, updated_at, updated_by
       FROM zoho_portal_config
       WHERE config_key = ?`,
    )
    .bind(configKey)
    .first<PortalConfigRow>();
  if (!row) return null;
  return {
    handoff: JSON.parse(row.payload) as ZohoPortalHandoff,
    version: row.version,
    updatedAt: row.updated_at,
    updatedBy: row.updated_by,
  };
}

export async function saveZohoPortalConfig(options: {
  handoff: ZohoPortalHandoff;
  expectedVersion: number;
  actor: string;
}): Promise<ZohoPortalConfigEnvelope> {
  await ensureSchema();
  const d1 = await getD1();
  const current = await d1
    .prepare(
      "SELECT version FROM zoho_portal_config WHERE config_key = ?",
    )
    .bind(configKey)
    .first<{ version: number }>();
  const currentVersion = current?.version ?? 0;
  if (currentVersion !== options.expectedVersion) {
    throw new PortalConfigConflictError(
      `The URL handoff changed from version ${options.expectedVersion} to ${currentVersion}. Reload it before saving.`,
    );
  }

  const version = currentVersion + 1;
  const updatedAt = new Date().toISOString();
  const payload = JSON.stringify(options.handoff);
  if (current) {
    const result = await d1
      .prepare(
        `UPDATE zoho_portal_config
         SET version = ?, payload = ?, updated_at = ?, updated_by = ?
         WHERE config_key = ? AND version = ?`,
      )
      .bind(
        version,
        payload,
        updatedAt,
        options.actor,
        configKey,
        options.expectedVersion,
      )
      .run();
    if (!result.meta.changes) {
      throw new PortalConfigConflictError(
        "The URL handoff changed before this save completed.",
      );
    }
  } else {
    await d1
      .prepare(
        `INSERT INTO zoho_portal_config
         (config_key, version, payload, updated_at, updated_by)
         VALUES (?, ?, ?, ?, ?)`,
      )
      .bind(configKey, version, payload, updatedAt, options.actor)
      .run();
  }
  return {
    handoff: options.handoff,
    version,
    updatedAt,
    updatedBy: options.actor,
  };
}
