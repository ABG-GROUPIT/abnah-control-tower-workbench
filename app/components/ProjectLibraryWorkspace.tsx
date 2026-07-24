"use client";

import {
  Archive,
  BookOpen,
  Braces,
  CheckCircle2,
  ChevronRight,
  Database,
  Download,
  ExternalLink,
  File,
  FileCode2,
  FileJson,
  FileSpreadsheet,
  FolderArchive,
  Search,
  ShieldCheck,
  TestTube2,
} from "lucide-react";
import { useMemo, useState } from "react";
import type {
  ProjectPackFile,
  ProjectPackIndex,
} from "../lib/project-pack-types";

interface ProjectLibraryWorkspaceProps {
  index: ProjectPackIndex;
}

type FileFilter = "all" | "data" | "sql" | "guides" | "contracts" | "code";

const PAGES_ROOT = "https://abg-groupit.github.io/abnah-control-tower-workbench";
const INITIAL_LIMIT = 100;

const fileFilters: Array<{ id: FileFilter; label: string }> = [
  { id: "all", label: "All files" },
  { id: "data", label: "CSV data" },
  { id: "sql", label: "SQL" },
  { id: "guides", label: "Guides" },
  { id: "contracts", label: "Contracts" },
  { id: "code", label: "Code & tools" },
];

function projectFileUrl(path: string) {
  return `${PAGES_ROOT}/project-pack/zoho-control-tower/${path
    .split("/")
    .map((segment) => encodeURIComponent(segment))
    .join("/")}`;
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(bytes < 10240 ? 1 : 0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function matchesFileFilter(file: ProjectPackFile, filter: FileFilter) {
  if (filter === "all") return true;
  if (filter === "data") return file.extension === ".csv";
  if (filter === "sql") return file.extension === ".sql";
  if (filter === "guides") return file.extension === ".md";
  if (filter === "contracts") return file.extension === ".json";
  return [".py", ".ps1", ".bat", ".html", ".yaml", ".yml", ".txt"].includes(file.extension);
}

function FileKindIcon({ file }: { file: ProjectPackFile }) {
  if (file.extension === ".csv") return <FileSpreadsheet aria-hidden="true" size={16} />;
  if (file.extension === ".sql") return <Database aria-hidden="true" size={16} />;
  if (file.extension === ".md") return <BookOpen aria-hidden="true" size={16} />;
  if (file.extension === ".json") return <FileJson aria-hidden="true" size={16} />;
  if (file.extension === ".zip") return <Archive aria-hidden="true" size={16} />;
  if ([".py", ".ps1", ".bat", ".html"].includes(file.extension)) {
    return <FileCode2 aria-hidden="true" size={16} />;
  }
  return <File aria-hidden="true" size={16} />;
}

function CategoryIcon({ category }: { category: string }) {
  if (category === "synthetic_data") return <FileSpreadsheet aria-hidden="true" size={15} />;
  if (category === "sql") return <Database aria-hidden="true" size={15} />;
  if (category === "documentation") return <BookOpen aria-hidden="true" size={15} />;
  if (category === "tests") return <TestTube2 aria-hidden="true" size={15} />;
  if (category === "schema_api") return <Braces aria-hidden="true" size={15} />;
  if (category === "final_zoho") return <CheckCircle2 aria-hidden="true" size={15} />;
  return <FolderArchive aria-hidden="true" size={15} />;
}

export function ProjectLibraryWorkspace({ index }: ProjectLibraryWorkspaceProps) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [fileFilter, setFileFilter] = useState<FileFilter>("all");
  const [visibleLimit, setVisibleLimit] = useState(INITIAL_LIMIT);

  const categoryMap = useMemo(
    () => new Map(index.categories.map((entry) => [entry.id, entry])),
    [index.categories],
  );
  const featuredFiles = useMemo(
    () => index.files
      .filter((file) => file.featuredOrder !== null)
      .sort((left, right) => (left.featuredOrder ?? 999) - (right.featuredOrder ?? 999)),
    [index.files],
  );
  const filteredFiles = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase();
    return index.files.filter((file) => {
      if (category !== "all" && file.category !== category) return false;
      if (!matchesFileFilter(file, fileFilter)) return false;
      if (!needle) return true;
      const categoryLabel = categoryMap.get(file.category)?.label ?? file.category;
      return [
        file.path,
        file.title,
        file.kind,
        categoryLabel,
        file.description,
      ].some((value) => value.toLocaleLowerCase().includes(needle));
    });
  }, [category, categoryMap, fileFilter, index.files, query]);
  const visibleFiles = filteredFiles.slice(0, visibleLimit);

  const applyCategory = (nextCategory: string) => {
    setCategory(nextCategory);
    setVisibleLimit(INITIAL_LIMIT);
  };

  const applyFileFilter = (nextFilter: FileFilter) => {
    setFileFilter(nextFilter);
    setVisibleLimit(INITIAL_LIMIT);
  };

  return (
    <section className="project-library" aria-labelledby="project-library-title">
      <header className="project-library-header">
        <div className="project-library-title">
          <span className="project-library-kicker"><FolderArchive aria-hidden="true" size={15} /> Transferable project handoff</span>
          <h1 id="project-library-title">Complete project library</h1>
          <p>Search and open every validated implementation artifact used to reproduce, audit, and extend the ABNAH Control Tower.</p>
        </div>
        <dl className="project-library-metrics" aria-label="Project library summary">
          <div><dt>Files</dt><dd>{index.summary.files}</dd></div>
          <div><dt>Pack size</dt><dd>{formatBytes(index.summary.sizeBytes)}</dd></div>
          <div><dt>CSV</dt><dd>{index.summary.csvFiles}</dd></div>
          <div><dt>SQL</dt><dd>{index.summary.sqlFiles}</dd></div>
          <div><dt>Guides</dt><dd>{index.summary.guideFiles}</dd></div>
        </dl>
        <div className="project-library-actions">
          <a className="project-library-primary-action" href={`${PAGES_ROOT}/ABNAH_COMPLETE_PROJECT_PACK.zip`} download>
            <Download aria-hidden="true" size={15} /> Download complete pack
          </a>
          <a className="project-library-secondary-action" href={index.sourceRepository} target="_blank" rel="noreferrer">
            <ExternalLink aria-hidden="true" size={14} /> Source repository
          </a>
        </div>
        <p className="project-library-policy">
          <ShieldCheck aria-hidden="true" size={14} />
          <span><strong>Validated public scope.</strong> {index.policy}</span>
        </p>
      </header>

      <section className="project-library-featured" aria-labelledby="project-library-featured-title">
        <div className="project-library-featured-heading">
          <span>Start here</span>
          <strong id="project-library-featured-title">Pinned implementation references</strong>
        </div>
        <div className="project-library-featured-list">
          {featuredFiles.map((file) => (
            <a key={file.path} href={projectFileUrl(file.path)} target="_blank" rel="noreferrer">
              <span>{file.featuredOrder?.toString().padStart(2, "0")}</span>
              <div>
                <strong>{file.featuredTitle}</strong>
                <small>{file.description}</small>
              </div>
              <ChevronRight aria-hidden="true" size={15} />
            </a>
          ))}
        </div>
      </section>

      <div className="project-library-layout">
        <aside className="project-library-categories" aria-label="Project library categories">
          <div className="project-library-category-heading">
            <strong>Sections</strong>
            <span>{index.categories.length}</span>
          </div>
          <button
            type="button"
            className={category === "all" ? "is-active" : ""}
            onClick={() => applyCategory("all")}
          >
            <FolderArchive aria-hidden="true" size={15} />
            <span><strong>Complete library</strong><small>All validated artifacts</small></span>
            <b>{index.summary.files}</b>
          </button>
          {index.categories.map((entry) => (
            <button
              key={entry.id}
              type="button"
              className={category === entry.id ? "is-active" : ""}
              onClick={() => applyCategory(entry.id)}
              title={entry.description}
            >
              <CategoryIcon category={entry.id} />
              <span><strong>{entry.label}</strong><small>{formatBytes(entry.sizeBytes)}</small></span>
              <b>{entry.count}</b>
            </button>
          ))}
        </aside>

        <div className="project-library-browser">
          <div className="project-library-toolbar">
            <label className="project-library-search">
              <Search aria-hidden="true" size={15} />
              <input
                type="search"
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setVisibleLimit(INITIAL_LIMIT);
                }}
                placeholder="Search file names, paths, guides, SQL, or tools"
                aria-label="Search complete project library"
              />
            </label>
            <div className="project-library-file-filters" role="group" aria-label="Filter project files by type">
              {fileFilters.map((filter) => (
                <button
                  key={filter.id}
                  type="button"
                  className={fileFilter === filter.id ? "is-active" : ""}
                  aria-pressed={fileFilter === filter.id}
                  onClick={() => applyFileFilter(filter.id)}
                >
                  {filter.label}
                </button>
              ))}
            </div>
            <p><strong>{filteredFiles.length}</strong> matching files <span>Manifest commit {index.sourceCommit.slice(0, 8)}</span></p>
          </div>

          <div className="project-library-table" role="table" aria-label="Hosted project files">
            <div className="project-library-table-head" role="row">
              <span role="columnheader">File</span>
              <span role="columnheader">Section</span>
              <span role="columnheader">Size</span>
              <span role="columnheader">Integrity</span>
              <span role="columnheader">Actions</span>
            </div>
            <div className="project-library-table-body">
              {visibleFiles.map((file) => (
                <div className="project-library-file-row" role="row" key={file.path}>
                  <span className="project-library-file-main" role="cell">
                    <i><FileKindIcon file={file} /></i>
                    <span>
                      <strong>{file.name}</strong>
                      <small title={file.path}>{file.path}</small>
                    </span>
                  </span>
                  <span className="project-library-file-category" role="cell">
                    {categoryMap.get(file.category)?.label ?? file.category}
                    <small>{file.kind}</small>
                  </span>
                  <span className="project-library-file-size" role="cell">{formatBytes(file.sizeBytes)}</span>
                  <code role="cell" title={file.sha256}>{file.sha256.slice(0, 10)}</code>
                  <span className="project-library-file-actions" role="cell">
                    <a href={projectFileUrl(file.path)} target="_blank" rel="noreferrer" title={`Open ${file.name}`}>
                      <ExternalLink aria-hidden="true" size={14} /><span>Open</span>
                    </a>
                    <a href={projectFileUrl(file.path)} download title={`Download ${file.name}`}>
                      <Download aria-hidden="true" size={14} /><span>Download</span>
                    </a>
                  </span>
                </div>
              ))}
              {visibleFiles.length === 0 && (
                <div className="project-library-empty">
                  <Search aria-hidden="true" size={20} />
                  <strong>No files match this view</strong>
                  <span>Clear the search or select another section.</span>
                </div>
              )}
            </div>
          </div>

          {visibleFiles.length < filteredFiles.length && (
            <button
              className="project-library-load-more"
              type="button"
              onClick={() => setVisibleLimit((current) => current + INITIAL_LIMIT)}
            >
              Show next {Math.min(INITIAL_LIMIT, filteredFiles.length - visibleFiles.length)} files
            </button>
          )}
        </div>
      </div>
    </section>
  );
}
