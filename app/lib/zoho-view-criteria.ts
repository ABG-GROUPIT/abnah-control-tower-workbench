function quotedColumn(column: string) {
  if (!/^[A-Za-z0-9_ ]+$/.test(column)) {
    throw new Error(`Unsafe Zoho criteria column: ${column}`);
  }
  return `"${column}"`;
}

function quotedValue(value: string) {
  return `'${value.replaceAll("'", "''")}'`;
}

export function zohoEquals(column: string, value: string) {
  return `(${quotedColumn(column)} = ${quotedValue(value)})`;
}

export function zohoDateRange(column: string, start: string, end: string) {
  const parts = [
    start
      ? `${quotedColumn(column)} >= ${quotedValue(start)}`
      : "",
    end
      ? `${quotedColumn(column)} <= ${quotedValue(end)}`
      : "",
  ].filter(Boolean);
  return parts.length ? `(${parts.join(" AND ")})` : "";
}

export function zohoContains(
  columns: string[],
  value: string,
) {
  const clean = value.trim().toLowerCase();
  if (!clean) return "";
  const pattern = quotedValue(`%${clean}%`);
  const parts = columns.map(
    (column) => `LOWER(${quotedColumn(column)}) LIKE ${pattern}`,
  );
  return `(${parts.join(" OR ")})`;
}

export function combineZohoCriteria(...criteria: string[]) {
  const parts = criteria.filter(Boolean);
  return parts.length ? `(${parts.join(" AND ")})` : "";
}

export function withZohoCriteria(url: string, criteria: string) {
  if (!url || !criteria) return url;
  try {
    const parsed = new URL(url);
    parsed.searchParams.set("ZOHO_CRITERIA", criteria);
    return parsed.toString();
  } catch {
    return url;
  }
}
