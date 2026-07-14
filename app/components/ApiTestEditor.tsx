"use client";

import { Plus, Trash2 } from "lucide-react";
import type { WorkspaceApiTest } from "../lib/workspace-types";

interface ApiTestEditorProps {
  reportId: string;
  tests: WorkspaceApiTest[];
  readOnly: boolean;
  onChange: (tests: WorkspaceApiTest[]) => void;
}

function newTest(reportId: string): WorkspaceApiTest {
  const suffix = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}`;
  return {
    id: `api-test:${reportId}:custom-${suffix}`,
    endpointId: "",
    endpointName: "New API candidate",
    method: "GET",
    path: "",
    testType: "availability",
    status: "not_tested",
    result: "",
    errorType: "",
    notes: "",
    testedAt: "",
  };
}

export function ApiTestEditor({ reportId, tests, readOnly, onChange }: ApiTestEditorProps) {
  const update = (id: string, patch: Partial<WorkspaceApiTest>) =>
    onChange(tests.map((test) => (test.id === id ? { ...test, ...patch } : test)));

  return (
    <section className="api-test-panel">
      <div className="section-heading-row">
        <div>
          <span className="section-kicker">Connection evidence</span>
          <h2>API candidates and tests</h2>
        </div>
        {!readOnly && (
          <button type="button" className="secondary-button" onClick={() => onChange([...tests, newTest(reportId)])}>
            <Plus aria-hidden="true" size={15} /> Add API record
          </button>
        )}
      </div>

      {tests.length ? (
        <div className="api-test-list">
          {tests.map((test) => (
            <article key={test.id} className="api-test-record">
              <div className="api-test-primary">
                <label><span>Endpoint</span>{readOnly ? <strong>{test.endpointName}</strong> : <input value={test.endpointName} onChange={(event) => update(test.id, { endpointName: event.target.value })} />}</label>
                <label className="method-field"><span>Method</span>{readOnly ? <code>{test.method}</code> : <select value={test.method} onChange={(event) => update(test.id, { method: event.target.value })}><option>GET</option><option>POST</option><option>PUT</option><option>PATCH</option><option>DELETE</option></select>}</label>
                <label><span>Path</span>{readOnly ? <code>{test.path || "Not recorded"}</code> : <input value={test.path} onChange={(event) => update(test.id, { path: event.target.value })} />}</label>
                <label><span>Status</span>{readOnly ? <span className={`status-label status-${test.status}`}>{test.status.replaceAll("_", " ")}</span> : <select value={test.status} onChange={(event) => update(test.id, { status: event.target.value as WorkspaceApiTest["status"] })}><option value="not_tested">Not tested</option><option value="planned">Planned</option><option value="passed">Passed</option><option value="partial">Partial</option><option value="failed">Failed</option><option value="blocked">Blocked</option></select>}</label>
                {!readOnly && <button type="button" className="icon-button danger" data-tooltip="Delete API record" aria-label="Delete API record" onClick={() => onChange(tests.filter((item) => item.id !== test.id))}><Trash2 aria-hidden="true" size={15} /></button>}
              </div>
              <div className="api-test-secondary">
                <label><span>Test type</span>{readOnly ? <span>{test.testType}</span> : <input value={test.testType} onChange={(event) => update(test.id, { testType: event.target.value })} />}</label>
                <label><span>Tested at</span>{readOnly ? <span>{test.testedAt || "Not tested"}</span> : <input type="datetime-local" value={test.testedAt} onChange={(event) => update(test.id, { testedAt: event.target.value })} />}</label>
                <label><span>Error type</span>{readOnly ? <span>{test.errorType || "None recorded"}</span> : <input value={test.errorType} onChange={(event) => update(test.id, { errorType: event.target.value })} />}</label>
                <label className="wide-field"><span>Result</span>{readOnly ? <span>{test.result || "No result recorded"}</span> : <textarea value={test.result} onChange={(event) => update(test.id, { result: event.target.value })} />}</label>
                <label className="wide-field"><span>Engineering notes</span>{readOnly ? <span>{test.notes || "No notes recorded"}</span> : <textarea value={test.notes} onChange={(event) => update(test.id, { notes: event.target.value })} />}</label>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="empty-state compact-empty"><strong>No API candidate recorded</strong><span>API coverage remains unknown for this report.</span></div>
      )}
    </section>
  );
}
