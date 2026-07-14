"use client";

import { ArrowDown, ArrowUp, Plus, Trash2 } from "lucide-react";
import type { WorkspaceField } from "../lib/workspace-types";

interface DataPointEditorProps {
  reportId: string;
  fields: WorkspaceField[];
  readOnly: boolean;
  onChange: (fields: WorkspaceField[]) => void;
}

function newField(reportId: string): WorkspaceField {
  const suffix = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}`;
  return {
    id: `workspace-field:${reportId}:custom-${suffix}`,
    key: `new_field_${suffix.slice(0, 8)}`,
    label: "New data point",
    semanticRole: "unknown",
    dataType: "unknown",
    status: "candidate",
    notes: "",
  };
}

export function DataPointEditor({ reportId, fields, readOnly, onChange }: DataPointEditorProps) {
  const update = (id: string, patch: Partial<WorkspaceField>) =>
    onChange(fields.map((field) => (field.id === id ? { ...field, ...patch } : field)));
  const move = (index: number, direction: -1 | 1) => {
    const target = index + direction;
    if (target < 0 || target >= fields.length) return;
    const next = [...fields];
    [next[index], next[target]] = [next[target], next[index]];
    onChange(next);
  };

  return (
    <section className="data-point-panel">
      <div className="section-heading-row">
        <div>
          <span className="section-kicker">Semantic schema</span>
          <h2>Data points</h2>
        </div>
        {!readOnly && (
          <button type="button" className="secondary-button" onClick={() => onChange([...fields, newField(reportId)])}>
            <Plus aria-hidden="true" size={15} /> Add data point
          </button>
        )}
      </div>

      {fields.length ? (
        <div className="data-point-table" role="table" aria-label="Report data points">
          <div className="data-point-header" role="row">
            <span>Display label</span><span>Stable key</span><span>Role</span><span>Type</span><span>Status</span><span aria-hidden="true" />
          </div>
          {fields.map((field, index) => (
            <div className="data-point-row" role="row" key={field.id}>
              {readOnly ? <strong>{field.label}</strong> : <input value={field.label} aria-label="Data point label" onChange={(event) => update(field.id, { label: event.target.value })} />}
              {readOnly ? <code>{field.key}</code> : <input value={field.key} aria-label="Stable field key" onChange={(event) => update(field.id, { key: event.target.value })} />}
              {readOnly ? <span>{field.semanticRole}</span> : <input value={field.semanticRole} aria-label="Semantic role" onChange={(event) => update(field.id, { semanticRole: event.target.value })} />}
              {readOnly ? <span>{field.dataType}</span> : <input value={field.dataType} aria-label="Data type" onChange={(event) => update(field.id, { dataType: event.target.value })} />}
              {readOnly ? (
                <span className={`status-label status-${field.status}`}>{field.status.replaceAll("_", " ")}</span>
              ) : (
                <select value={field.status} aria-label="Data point status" onChange={(event) => update(field.id, { status: event.target.value as WorkspaceField["status"] })}>
                  <option value="captured">Captured</option>
                  <option value="candidate">Candidate</option>
                  <option value="needs_review">Needs review</option>
                </select>
              )}
              {!readOnly && (
                <div className="row-actions">
                  <button type="button" className="icon-button" data-tooltip="Move up" aria-label="Move data point up" disabled={index === 0} onClick={() => move(index, -1)}><ArrowUp aria-hidden="true" size={14} /></button>
                  <button type="button" className="icon-button" data-tooltip="Move down" aria-label="Move data point down" disabled={index === fields.length - 1} onClick={() => move(index, 1)}><ArrowDown aria-hidden="true" size={14} /></button>
                  <button type="button" className="icon-button danger" data-tooltip="Delete data point" aria-label="Delete data point" onClick={() => onChange(fields.filter((item) => item.id !== field.id))}><Trash2 aria-hidden="true" size={14} /></button>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state compact-empty"><strong>No data points captured</strong><span>This report remains explicitly pending or unavailable.</span></div>
      )}
    </section>
  );
}
