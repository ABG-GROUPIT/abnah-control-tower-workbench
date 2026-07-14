"use client";

import { Plus, Trash2 } from "lucide-react";
import type { WorkspaceNote } from "../lib/workspace-types";

interface NotesEditorProps {
  reportId: string;
  notes: WorkspaceNote[];
  readOnly: boolean;
  onChange: (notes: WorkspaceNote[]) => void;
}

function newNote(reportId: string): WorkspaceNote {
  const suffix = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}`;
  return {
    id: `note:${reportId}:custom-${suffix}`,
    category: "engineering",
    body: "",
    author: "",
    createdAt: new Date().toISOString(),
  };
}

export function NotesEditor({ reportId, notes, readOnly, onChange }: NotesEditorProps) {
  const update = (id: string, patch: Partial<WorkspaceNote>) =>
    onChange(notes.map((note) => (note.id === id ? { ...note, ...patch } : note)));

  return (
    <section className="notes-panel">
      <div className="section-heading-row">
        <div>
          <span className="section-kicker">Report notebook</span>
          <h2>Engineering notes</h2>
        </div>
        {!readOnly && (
          <button type="button" className="secondary-button" onClick={() => onChange([...notes, newNote(reportId)])}>
            <Plus aria-hidden="true" size={15} /> Add note
          </button>
        )}
      </div>
      {notes.length ? (
        <div className="notes-list">
          {notes.map((note) => (
            <article key={note.id} className="note-record">
              <div className="note-meta">
                {readOnly ? <span className={`note-category category-${note.category}`}>{note.category}</span> : <select value={note.category} onChange={(event) => update(note.id, { category: event.target.value as WorkspaceNote["category"] })}><option value="engineering">Engineering</option><option value="source">Source</option><option value="decision">Decision</option><option value="issue">Issue</option></select>}
                <span>{note.author || "Unassigned"}</span>
                <time>{note.createdAt ? new Date(note.createdAt).toLocaleString("en-IN") : "Imported baseline"}</time>
                {!readOnly && <button type="button" className="icon-button danger" data-tooltip="Delete note" aria-label="Delete note" onClick={() => onChange(notes.filter((item) => item.id !== note.id))}><Trash2 aria-hidden="true" size={15} /></button>}
              </div>
              {readOnly ? <p>{note.body}</p> : <textarea value={note.body} placeholder="Engineering observation" onChange={(event) => update(note.id, { body: event.target.value })} />}
            </article>
          ))}
        </div>
      ) : (
        <div className="empty-state compact-empty"><strong>No report notes</strong><span>No engineering observation has been recorded.</span></div>
      )}
    </section>
  );
}
