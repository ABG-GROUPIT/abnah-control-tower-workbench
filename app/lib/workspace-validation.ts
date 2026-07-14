import type {
  ApiTestStatus,
  LayoutKind,
  ReportWorkspaceDocument,
  SchemaCellKind,
  SchemaStatus,
  VerificationStatus,
  WorkflowStatus,
  WorkspaceNote,
} from "./workspace-types";

const SOURCE_POLICY = "Schema definitions only. Local screenshots, paths, and source images are excluded.";
const schemaStatuses = new Set<SchemaStatus>(["captured", "partial", "pending", "unavailable"]);
const verificationStatuses = new Set<VerificationStatus>(["needs_review", "reviewed", "uat_verified"]);
const layoutKinds = new Set<LayoutKind>(["flat", "grouped_columns", "grouped_rows", "mixed", "freeform"]);
const workflowStatuses = new Set<WorkflowStatus>(["draft", "in_review", "published"]);
const cellKinds = new Set<SchemaCellKind>(["group", "field", "label", "context", "blank"]);
const apiStatuses = new Set<ApiTestStatus>(["not_tested", "planned", "passed", "partial", "failed", "blocked"]);
const noteCategories = new Set<WorkspaceNote["category"]>(["engineering", "source", "decision", "issue"]);

export class WorkspaceValidationError extends Error {}

function record(value: unknown, label: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new WorkspaceValidationError(`${label} must be an object.`);
  }
  return value as Record<string, unknown>;
}

function list(value: unknown, label: string, limit: number): unknown[] {
  if (!Array.isArray(value)) throw new WorkspaceValidationError(`${label} must be an array.`);
  if (value.length > limit) throw new WorkspaceValidationError(`${label} exceeds the ${limit}-item limit.`);
  return value;
}

function stringValue(value: unknown, label: string, maxLength: number, required = false): string {
  if (value === undefined || value === null) value = "";
  if (typeof value !== "string") throw new WorkspaceValidationError(`${label} must be text.`);
  const result = value.trim();
  if (required && !result) throw new WorkspaceValidationError(`${label} is required.`);
  if (result.length > maxLength) throw new WorkspaceValidationError(`${label} exceeds ${maxLength} characters.`);
  return result;
}

function integer(value: unknown, label: string, min: number, max: number): number {
  if (!Number.isInteger(value) || Number(value) < min || Number(value) > max) {
    throw new WorkspaceValidationError(`${label} must be between ${min} and ${max}.`);
  }
  return Number(value);
}

function enumValue<T extends string>(value: unknown, label: string, allowed: Set<T>, fallback: T): T {
  if (value === undefined || value === null || value === "") return fallback;
  if (typeof value !== "string" || !allowed.has(value as T)) {
    throw new WorkspaceValidationError(`${label} has an unsupported value.`);
  }
  return value as T;
}

export function sanitizeWorkspaceDocument(input: unknown): ReportWorkspaceDocument {
  const source = record(input, "document");
  const id = stringValue(source.id, "report id", 300, true);
  if (!/^(report:|custom:)[a-zA-Z0-9:_-]+$/.test(id)) {
    throw new WorkspaceValidationError("Report id contains unsupported characters.");
  }

  let totalCells = 0;
  const fields = list(source.fields, "fields", 5000).map((value, index) => {
    const field = record(value, `field ${index + 1}`);
    return {
      id: stringValue(field.id, `field ${index + 1} id`, 400, true),
      key: stringValue(field.key, `field ${index + 1} key`, 160, true),
      label: stringValue(field.label, `field ${index + 1} label`, 300, true),
      semanticRole: stringValue(field.semanticRole, `field ${index + 1} role`, 120),
      dataType: stringValue(field.dataType, `field ${index + 1} type`, 120),
      status: enumValue(field.status, `field ${index + 1} status`, new Set(["captured", "candidate", "needs_review"] as const), "needs_review"),
      notes: stringValue(field.notes, `field ${index + 1} notes`, 2000),
    };
  });

  const tables = list(source.tables, "tables", 50).map((value, tableIndex) => {
    const table = record(value, `table ${tableIndex + 1}`);
    const rows = integer(table.rows, `table ${tableIndex + 1} rows`, 1, 500);
    const columns = integer(table.columns, `table ${tableIndex + 1} columns`, 1, 500);
    const widths = list(table.columnWidths, `table ${tableIndex + 1} column widths`, 500);
    if (widths.length !== columns) throw new WorkspaceValidationError(`Table ${tableIndex + 1} has an invalid width count.`);
    const occupied = new Set<string>();
    const cells = list(table.cells, `table ${tableIndex + 1} cells`, 100000).map((value, cellIndex) => {
      totalCells += 1;
      if (totalCells > 100000) throw new WorkspaceValidationError("Document exceeds the 100000-cell limit.");
      const cell = record(value, `table ${tableIndex + 1} cell ${cellIndex + 1}`);
      const row = integer(cell.row, "cell row", 0, rows - 1);
      const column = integer(cell.column, "cell column", 0, columns - 1);
      const rowSpan = integer(cell.rowSpan, "cell row span", 1, rows);
      const columnSpan = integer(cell.columnSpan, "cell column span", 1, columns);
      if (row + rowSpan > rows || column + columnSpan > columns) {
        throw new WorkspaceValidationError(`A cell exceeds table ${tableIndex + 1} bounds.`);
      }
      for (let r = row; r < row + rowSpan; r += 1) {
        for (let c = column; c < column + columnSpan; c += 1) {
          const coordinate = `${r}:${c}`;
          if (occupied.has(coordinate)) throw new WorkspaceValidationError(`Table ${tableIndex + 1} contains overlapping cells.`);
          occupied.add(coordinate);
        }
      }
      return {
        id: stringValue(cell.id, "cell id", 500, true),
        row,
        column,
        rowSpan,
        columnSpan,
        text: stringValue(cell.text, "cell text", 300),
        kind: enumValue(cell.kind, "cell kind", cellKinds, "blank"),
        ...(cell.fieldId ? { fieldId: stringValue(cell.fieldId, "cell field id", 300) } : {}),
      };
    });
    return {
      id: stringValue(table.id, `table ${tableIndex + 1} id`, 200, true),
      name: stringValue(table.name, `table ${tableIndex + 1} name`, 200, true),
      rows,
      columns,
      columnWidths: widths.map((width, index) => integer(width, `column ${index + 1} width`, 72, 420)),
      cells,
    };
  });

  const apiTests = list(source.apiTests, "API tests", 500).map((value, index) => {
    const test = record(value, `API test ${index + 1}`);
    return {
      id: stringValue(test.id, `API test ${index + 1} id`, 400, true),
      endpointId: stringValue(test.endpointId, `API test ${index + 1} endpoint id`, 300),
      endpointName: stringValue(test.endpointName, `API test ${index + 1} endpoint name`, 300, true),
      method: stringValue(test.method, `API test ${index + 1} method`, 20),
      path: stringValue(test.path, `API test ${index + 1} path`, 800),
      testType: stringValue(test.testType, `API test ${index + 1} type`, 120),
      status: enumValue(test.status, `API test ${index + 1} status`, apiStatuses, "not_tested"),
      result: stringValue(test.result, `API test ${index + 1} result`, 4000),
      errorType: stringValue(test.errorType, `API test ${index + 1} error type`, 200),
      notes: stringValue(test.notes, `API test ${index + 1} notes`, 4000),
      testedAt: stringValue(test.testedAt, `API test ${index + 1} date`, 80),
    };
  });

  const notes = list(source.notes, "notes", 1000).map((value, index) => {
    const note = record(value, `note ${index + 1}`);
    return {
      id: stringValue(note.id, `note ${index + 1} id`, 400, true),
      category: enumValue(note.category, `note ${index + 1} category`, noteCategories, "engineering"),
      body: stringValue(note.body, `note ${index + 1} body`, 4000, true),
      author: stringValue(note.author, `note ${index + 1} author`, 300),
      createdAt: stringValue(note.createdAt, `note ${index + 1} date`, 80),
    };
  });

  return {
    id,
    name: stringValue(source.name, "report name", 300, true),
    page: stringValue(source.page, "page", 160, true),
    section: stringValue(source.section, "section", 200, true),
    domain: stringValue(source.domain, "domain", 160, true),
    priority: enumValue(source.priority, "priority", new Set(["P0", "P1", "P2"] as const), "P2"),
    schemaStatus: enumValue(source.schemaStatus, "schema status", schemaStatuses, "pending"),
    verificationStatus: enumValue(source.verificationStatus, "verification status", verificationStatuses, "needs_review"),
    layoutKind: enumValue(source.layoutKind, "layout kind", layoutKinds, "freeform"),
    captureMethod: stringValue(source.captureMethod, "capture method", 300),
    sourcePolicy: SOURCE_POLICY,
    workflowStatus: enumValue(source.workflowStatus, "workflow status", workflowStatuses, "draft"),
    version: integer(source.version ?? 0, "version", 0, 1000000),
    isArchived: Boolean(source.isArchived),
    isCustom: Boolean(source.isCustom),
    fields,
    tables,
    apiTests,
    notes,
    updatedAt: stringValue(source.updatedAt, "updated date", 80),
    updatedBy: stringValue(source.updatedBy, "updated by", 300),
  };
}
