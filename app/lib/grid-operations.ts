import type { SchemaCell, SchemaCellKind, SchemaTable } from "./workspace-types";

export interface GridCoordinate {
  row: number;
  column: number;
}

export interface GridRange {
  top: number;
  left: number;
  bottom: number;
  right: number;
}

export class GridOperationError extends Error {}

function cellId(tableId: string) {
  const suffix = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `${tableId}:cell:${suffix}`;
}

function blankCell(tableId: string, row: number, column: number): SchemaCell {
  return {
    id: cellId(tableId),
    row,
    column,
    rowSpan: 1,
    columnSpan: 1,
    text: "",
    kind: "blank",
  };
}

function coordinatesForCell(cell: SchemaCell) {
  const result: GridCoordinate[] = [];
  for (let row = cell.row; row < cell.row + cell.rowSpan; row += 1) {
    for (let column = cell.column; column < cell.column + cell.columnSpan; column += 1) {
      result.push({ row, column });
    }
  }
  return result;
}

function intersects(cell: SchemaCell, range: GridRange) {
  return !(
    cell.row + cell.rowSpan - 1 < range.top ||
    cell.row > range.bottom ||
    cell.column + cell.columnSpan - 1 < range.left ||
    cell.column > range.right
  );
}

function inside(cell: SchemaCell, range: GridRange) {
  return (
    cell.row >= range.top &&
    cell.column >= range.left &&
    cell.row + cell.rowSpan - 1 <= range.bottom &&
    cell.column + cell.columnSpan - 1 <= range.right
  );
}

export function selectionRange(anchor: GridCoordinate, focus: GridCoordinate): GridRange {
  return {
    top: Math.min(anchor.row, focus.row),
    left: Math.min(anchor.column, focus.column),
    bottom: Math.max(anchor.row, focus.row),
    right: Math.max(anchor.column, focus.column),
  };
}

export function normalizeTable(table: SchemaTable): SchemaTable {
  const rows = Math.max(1, table.rows);
  const columns = Math.max(1, table.columns);
  const occupied = new Set<string>();
  const cells: SchemaCell[] = [];
  for (const cell of table.cells) {
    if (
      cell.row < 0 ||
      cell.column < 0 ||
      cell.rowSpan < 1 ||
      cell.columnSpan < 1 ||
      cell.row + cell.rowSpan > rows ||
      cell.column + cell.columnSpan > columns
    ) {
      continue;
    }
    const coordinates = coordinatesForCell(cell);
    if (coordinates.some((coordinate) => occupied.has(`${coordinate.row}:${coordinate.column}`))) continue;
    coordinates.forEach((coordinate) => occupied.add(`${coordinate.row}:${coordinate.column}`));
    cells.push(cell);
  }
  for (let row = 0; row < rows; row += 1) {
    for (let column = 0; column < columns; column += 1) {
      const coordinate = `${row}:${column}`;
      if (!occupied.has(coordinate)) cells.push(blankCell(table.id, row, column));
    }
  }
  const widths = table.columnWidths.slice(0, columns).map((value) => Math.max(72, Math.min(420, value || 150)));
  while (widths.length < columns) widths.push(150);
  return {
    ...table,
    rows,
    columns,
    columnWidths: widths,
    cells: cells.sort((a, b) => a.row - b.row || a.column - b.column),
  };
}

export function cellAt(table: SchemaTable, coordinate: GridCoordinate) {
  return table.cells.find(
    (cell) =>
      coordinate.row >= cell.row &&
      coordinate.row < cell.row + cell.rowSpan &&
      coordinate.column >= cell.column &&
      coordinate.column < cell.column + cell.columnSpan,
  );
}

export function updateCell(
  table: SchemaTable,
  id: string,
  patch: Partial<Pick<SchemaCell, "text" | "kind" | "fieldId">>,
) {
  return {
    ...table,
    cells: table.cells.map((cell) => (cell.id === id ? { ...cell, ...patch } : cell)),
  };
}

export function mergeRange(table: SchemaTable, range: GridRange): SchemaTable {
  const candidates = table.cells.filter((cell) => intersects(cell, range));
  if (candidates.some((cell) => !inside(cell, range))) {
    throw new GridOperationError("Unmerge partially selected cells before merging this range.");
  }
  const populated = candidates.filter((cell) => cell.text.trim());
  if (populated.length > 1) {
    throw new GridOperationError("Clear all but one populated cell before merging to avoid losing schema labels.");
  }
  const source = populated[0] ?? candidates[0];
  const candidateIds = new Set(candidates.map((cell) => cell.id));
  const merged: SchemaCell = {
    id: cellId(table.id),
    row: range.top,
    column: range.left,
    rowSpan: range.bottom - range.top + 1,
    columnSpan: range.right - range.left + 1,
    text: source?.text ?? "",
    kind: source?.kind === "blank" ? "group" : source?.kind ?? "group",
    ...(source?.fieldId ? { fieldId: source.fieldId } : {}),
  };
  return normalizeTable({ ...table, cells: [...table.cells.filter((cell) => !candidateIds.has(cell.id)), merged] });
}

export function unmergeCell(table: SchemaTable, coordinate: GridCoordinate): SchemaTable {
  const source = cellAt(table, coordinate);
  if (!source || (source.rowSpan === 1 && source.columnSpan === 1)) return table;
  return normalizeTable({
    ...table,
    cells: table.cells
      .filter((cell) => cell.id !== source.id)
      .concat({ ...source, rowSpan: 1, columnSpan: 1 }),
  });
}

export function insertRowAfter(table: SchemaTable, rowIndex: number): SchemaTable {
  if (table.rows >= 500) throw new GridOperationError("This table already has the maximum 500 rows.");
  const cells = table.cells.map((cell) => {
    const end = cell.row + cell.rowSpan - 1;
    if (cell.row <= rowIndex && end > rowIndex) return { ...cell, rowSpan: cell.rowSpan + 1 };
    if (cell.row > rowIndex) return { ...cell, row: cell.row + 1 };
    return cell;
  });
  return normalizeTable({ ...table, rows: table.rows + 1, cells });
}

export function insertColumnAfter(table: SchemaTable, columnIndex: number): SchemaTable {
  if (table.columns >= 500) throw new GridOperationError("This table already has the maximum 500 columns.");
  const cells = table.cells.map((cell) => {
    const end = cell.column + cell.columnSpan - 1;
    if (cell.column <= columnIndex && end > columnIndex) return { ...cell, columnSpan: cell.columnSpan + 1 };
    if (cell.column > columnIndex) return { ...cell, column: cell.column + 1 };
    return cell;
  });
  const widths = [...table.columnWidths];
  widths.splice(columnIndex + 1, 0, widths[columnIndex] ?? 150);
  return normalizeTable({ ...table, columns: table.columns + 1, columnWidths: widths, cells });
}

export function deleteRow(table: SchemaTable, rowIndex: number): SchemaTable {
  if (table.rows <= 1) throw new GridOperationError("A table must keep at least one row.");
  const cells = table.cells.flatMap((cell) => {
    const end = cell.row + cell.rowSpan - 1;
    if (end < rowIndex) return [cell];
    if (cell.row > rowIndex) return [{ ...cell, row: cell.row - 1 }];
    if (cell.rowSpan === 1) return [];
    return [{ ...cell, rowSpan: cell.rowSpan - 1 }];
  });
  return normalizeTable({ ...table, rows: table.rows - 1, cells });
}

export function deleteColumn(table: SchemaTable, columnIndex: number): SchemaTable {
  if (table.columns <= 1) throw new GridOperationError("A table must keep at least one column.");
  const cells = table.cells.flatMap((cell) => {
    const end = cell.column + cell.columnSpan - 1;
    if (end < columnIndex) return [cell];
    if (cell.column > columnIndex) return [{ ...cell, column: cell.column - 1 }];
    if (cell.columnSpan === 1) return [];
    return [{ ...cell, columnSpan: cell.columnSpan - 1 }];
  });
  const widths = table.columnWidths.filter((_, index) => index !== columnIndex);
  return normalizeTable({ ...table, columns: table.columns - 1, columnWidths: widths, cells });
}

export function setColumnWidth(table: SchemaTable, columnIndex: number, width: number): SchemaTable {
  const widths = [...table.columnWidths];
  widths[columnIndex] = Math.max(72, Math.min(420, width));
  return { ...table, columnWidths: widths };
}

export function setRangeKind(table: SchemaTable, range: GridRange, kind: SchemaCellKind): SchemaTable {
  return {
    ...table,
    cells: table.cells.map((cell) => (inside(cell, range) ? { ...cell, kind } : cell)),
  };
}

export function pasteMatrix(
  table: SchemaTable,
  start: GridCoordinate,
  matrix: string[][],
): SchemaTable {
  if (!matrix.length || !matrix.some((row) => row.length)) return table;
  const neededRows = start.row + matrix.length;
  const neededColumns = start.column + Math.max(...matrix.map((row) => row.length));
  if (neededRows > 500 || neededColumns > 500) throw new GridOperationError("Pasted structure exceeds the 500 by 500 grid limit.");
  let next = normalizeTable({
    ...table,
    rows: Math.max(table.rows, neededRows),
    columns: Math.max(table.columns, neededColumns),
    columnWidths: [...table.columnWidths, ...Array(Math.max(0, neededColumns - table.columns)).fill(150)],
  });
  const range: GridRange = {
    top: start.row,
    left: start.column,
    bottom: neededRows - 1,
    right: neededColumns - 1,
  };
  if (next.cells.some((cell) => intersects(cell, range) && (cell.rowSpan > 1 || cell.columnSpan > 1))) {
    throw new GridOperationError("Unmerge cells in the paste area before pasting tabular labels.");
  }
  const replacements = new Map<string, string>();
  matrix.forEach((row, rowOffset) => {
    row.forEach((value, columnOffset) => {
      replacements.set(`${start.row + rowOffset}:${start.column + columnOffset}`, value.trim());
    });
  });
  next = {
    ...next,
    cells: next.cells.map((cell) => {
      const value = replacements.get(`${cell.row}:${cell.column}`);
      return value === undefined ? cell : { ...cell, text: value, kind: value ? "field" : "blank" };
    }),
  };
  return next;
}
