"use client";

import {
  Columns3,
  Redo2,
  Rows3,
  TableCellsMerge,
  TableCellsSplit,
  Trash2,
  Undo2,
} from "lucide-react";
import { useMemo, useState } from "react";
import {
  cellAt,
  deleteColumn,
  deleteRow,
  GridOperationError,
  insertColumnAfter,
  insertRowAfter,
  mergeRange,
  normalizeTable,
  pasteMatrix,
  selectionRange,
  setColumnWidth,
  setRangeKind,
  unmergeCell,
  updateCell,
  type GridCoordinate,
} from "../lib/grid-operations";
import type { SchemaCellKind, SchemaTable } from "../lib/workspace-types";

interface SchemaGridEditorProps {
  table: SchemaTable;
  readOnly: boolean;
  onChange: (table: SchemaTable) => void;
}

const cellKinds: Array<{ value: SchemaCellKind; label: string }> = [
  { value: "group", label: "Group header" },
  { value: "field", label: "Data field" },
  { value: "context", label: "Context" },
  { value: "label", label: "Label" },
  { value: "blank", label: "Blank" },
];

function columnLabel(index: number) {
  let value = index + 1;
  let label = "";
  while (value > 0) {
    value -= 1;
    label = String.fromCharCode(65 + (value % 26)) + label;
    value = Math.floor(value / 26);
  }
  return label;
}

export function SchemaGridEditor({ table, readOnly, onChange }: SchemaGridEditorProps) {
  const normalized = useMemo(() => normalizeTable(table), [table]);
  const [anchor, setAnchor] = useState<GridCoordinate>({ row: 0, column: 0 });
  const [focus, setFocus] = useState<GridCoordinate>({ row: 0, column: 0 });
  const [past, setPast] = useState<SchemaTable[]>([]);
  const [future, setFuture] = useState<SchemaTable[]>([]);
  const [error, setError] = useState("");

  const range = selectionRange(anchor, focus);
  const selectedCell = cellAt(normalized, focus) ?? normalized.cells[0];

  const commit = (next: SchemaTable) => {
    setPast((items) => [...items.slice(-49), normalized]);
    setFuture([]);
    setError("");
    onChange(normalizeTable(next));
  };

  const operate = (operation: () => SchemaTable) => {
    try {
      commit(operation());
    } catch (caught) {
      setError(caught instanceof GridOperationError ? caught.message : "The grid operation could not be completed.");
    }
  };

  const undo = () => {
    const previous = past.at(-1);
    if (!previous) return;
    setPast((items) => items.slice(0, -1));
    setFuture((items) => [normalized, ...items].slice(0, 50));
    onChange(previous);
    setError("");
  };

  const redo = () => {
    const next = future[0];
    if (!next) return;
    setFuture((items) => items.slice(1));
    setPast((items) => [...items.slice(-49), normalized]);
    onChange(next);
    setError("");
  };

  const chooseCell = (coordinate: GridCoordinate, extend: boolean) => {
    if (!extend) setAnchor(coordinate);
    setFocus(coordinate);
  };

  const isSelected = (row: number, column: number, rowSpan: number, columnSpan: number) =>
    !(
      row + rowSpan - 1 < range.top ||
      row > range.bottom ||
      column + columnSpan - 1 < range.left ||
      column > range.right
    );

  const rows = Array.from({ length: normalized.rows }, (_, row) =>
    normalized.cells.filter((cell) => cell.row === row).sort((a, b) => a.column - b.column),
  );

  return (
    <section
      className={`schema-grid-editor${readOnly ? " is-readonly" : ""}`}
      aria-label={`${table.name} structural schema`}
      onKeyDown={(event) => {
        if (readOnly || !(event.ctrlKey || event.metaKey)) return;
        if (event.key.toLowerCase() === "z") {
          event.preventDefault();
          if (event.shiftKey) redo();
          else undo();
        }
        if (event.key.toLowerCase() === "y") {
          event.preventDefault();
          redo();
        }
      }}
    >
      {!readOnly && (
        <div className="grid-toolbar" role="toolbar" aria-label="Table structure tools">
          <div className="grid-tool-group">
            <button type="button" className="icon-button" data-tooltip="Undo" aria-label="Undo" disabled={!past.length} onClick={undo}>
              <Undo2 aria-hidden="true" size={16} />
            </button>
            <button type="button" className="icon-button" data-tooltip="Redo" aria-label="Redo" disabled={!future.length} onClick={redo}>
              <Redo2 aria-hidden="true" size={16} />
            </button>
          </div>
          <div className="grid-tool-group">
            <button type="button" className="icon-button" data-tooltip="Insert row below" aria-label="Insert row below" onClick={() => operate(() => insertRowAfter(normalized, focus.row))}>
              <Rows3 aria-hidden="true" size={16} />
            </button>
            <button type="button" className="icon-button" data-tooltip="Insert column right" aria-label="Insert column right" onClick={() => operate(() => insertColumnAfter(normalized, focus.column))}>
              <Columns3 aria-hidden="true" size={16} />
            </button>
            <button type="button" className="icon-button" data-tooltip="Delete selected row" aria-label="Delete selected row" onClick={() => operate(() => deleteRow(normalized, focus.row))}>
              <Trash2 aria-hidden="true" size={15} /><span className="icon-axis">R</span>
            </button>
            <button type="button" className="icon-button" data-tooltip="Delete selected column" aria-label="Delete selected column" onClick={() => operate(() => deleteColumn(normalized, focus.column))}>
              <Trash2 aria-hidden="true" size={15} /><span className="icon-axis">C</span>
            </button>
          </div>
          <div className="grid-tool-group">
            <button type="button" className="icon-button" data-tooltip="Merge selected cells" aria-label="Merge selected cells" onClick={() => operate(() => mergeRange(normalized, range))}>
              <TableCellsMerge aria-hidden="true" size={17} />
            </button>
            <button type="button" className="icon-button" data-tooltip="Unmerge selected cell" aria-label="Unmerge selected cell" onClick={() => operate(() => unmergeCell(normalized, focus))}>
              <TableCellsSplit aria-hidden="true" size={17} />
            </button>
          </div>
          <label className="toolbar-field">
            <span>Cell type</span>
            <select
              value={selectedCell?.kind ?? "blank"}
              onChange={(event) => commit(setRangeKind(normalized, range, event.target.value as SchemaCellKind))}
            >
              {cellKinds.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
            </select>
          </label>
          <label className="toolbar-field toolbar-width-field">
            <span>Column width</span>
            <input
              type="number"
              min={72}
              max={420}
              value={normalized.columnWidths[focus.column] ?? 150}
              onChange={(event) => commit(setColumnWidth(normalized, focus.column, Number(event.target.value)))}
            />
          </label>
          <span className="grid-selection-label">
            {columnLabel(range.left)}{range.top + 1}
            {(range.left !== range.right || range.top !== range.bottom) && `:${columnLabel(range.right)}${range.bottom + 1}`}
          </span>
        </div>
      )}

      {error && <div className="grid-error" role="alert">{error}</div>}

      <div className="schema-grid-scroll">
        <table className="schema-grid" style={{ width: normalized.columnWidths.reduce((sum, width) => sum + width, readOnly ? 0 : 42) }}>
          <colgroup>
            {!readOnly && <col style={{ width: 42 }} />}
            {normalized.columnWidths.map((width, index) => <col key={`${table.id}:width:${index}`} style={{ width }} />)}
          </colgroup>
          {!readOnly && (
            <thead>
              <tr>
                <th className="grid-corner" aria-hidden="true" />
                {normalized.columnWidths.map((_, index) => (
                  <th key={`${table.id}:column:${index}`} className={index >= range.left && index <= range.right ? "is-selected" : ""}>
                    {columnLabel(index)}
                  </th>
                ))}
              </tr>
            </thead>
          )}
          <tbody>
            {rows.map((cells, rowIndex) => (
              <tr key={`${table.id}:row:${rowIndex}`}>
                {!readOnly && <th className={rowIndex >= range.top && rowIndex <= range.bottom ? "is-selected" : ""}>{rowIndex + 1}</th>}
                {cells.map((cell) => {
                  const selected = isSelected(cell.row, cell.column, cell.rowSpan, cell.columnSpan);
                  return (
                    <td
                      key={cell.id}
                      rowSpan={cell.rowSpan}
                      colSpan={cell.columnSpan}
                      className={`schema-cell cell-${cell.kind}${selected ? " is-selected" : ""}`}
                      onMouseDown={(event) => {
                        if (readOnly) return;
                        if (event.shiftKey) event.preventDefault();
                        chooseCell({ row: cell.row, column: cell.column }, event.shiftKey);
                      }}
                    >
                      {readOnly ? (
                        <span>{cell.text}</span>
                      ) : (
                        <textarea
                          value={cell.text}
                          rows={1}
                          aria-label={`Cell ${columnLabel(cell.column)}${cell.row + 1}`}
                          onFocus={() => chooseCell({ row: cell.row, column: cell.column }, false)}
                          onChange={(event) => commit(updateCell(normalized, cell.id, { text: event.target.value }))}
                          onPaste={(event) => {
                            const text = event.clipboardData.getData("text/plain");
                            if (!text.includes("\t") && !text.includes("\n") && !text.includes("\r")) return;
                            event.preventDefault();
                            const matrix = text.replaceAll("\r\n", "\n").replaceAll("\r", "\n").split("\n").filter((row, index, items) => row || index < items.length - 1).map((row) => row.split("\t"));
                            operate(() => pasteMatrix(normalized, { row: cell.row, column: cell.column }, matrix));
                          }}
                        />
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
