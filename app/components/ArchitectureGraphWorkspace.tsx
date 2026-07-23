"use client";

import {
  AlertTriangle,
  ArrowRight,
  BadgeCheck,
  Boxes,
  CircleDot,
  Database,
  ExternalLink,
  GitBranch,
  Layers3,
  LocateFixed,
  Maximize2,
  MousePointer2,
  Network,
  PanelRightClose,
  RotateCcw,
  Search,
  ShieldCheck,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type PointerEvent as ReactPointerEvent,
} from "react";
import type {
  ArchitectureLayerId,
  ArchitectureNode,
  ControlTowerArchitecture,
} from "../lib/architecture-types";
import type {
  ControlTowerKpi,
  ControlTowerPage,
  ControlTowerRequirements,
} from "../lib/control-tower-types";

interface ArchitectureGraphWorkspaceProps {
  architecture: ControlTowerArchitecture;
  requirements: ControlTowerRequirements;
  onOpenReport: (reportId: string) => void;
}

type GraphMode = "route" | "engineering";

interface GraphNode {
  id: string;
  layerId: ArchitectureLayerId;
  groupId: string;
  label: string;
  description: string;
  status: string;
  role: string;
  pages: string[];
  dataPoints: string[];
  logic: string;
  alternatives: string[];
  reportId?: string;
  source?: ArchitectureNode;
  kpi?: ControlTowerKpi;
  page?: ControlTowerPage;
  members?: GraphNode[];
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
}

interface Position {
  x: number;
  y: number;
}

const NODE_WIDTH = 208;
const NODE_HEIGHT = 66;
const LANE_WIDTH = 252;
const LANE_GAP = 24;
const NODE_GAP = 18;
const SCENE_TOP = 84;

const humanize = (value: string) => value.replaceAll("_", " ");

function graphFromContracts(
  architecture: ControlTowerArchitecture,
  requirements: ControlTowerRequirements,
) {
  const staticNodes: GraphNode[] = [...architecture.sourceNodes, ...architecture.modelNodes].map((node) => ({
    id: node.id,
    layerId: node.layerId,
    groupId: node.groupId,
    label: node.label,
    description: node.description,
    status: node.status,
    role: node.role,
    pages: node.pages,
    dataPoints: node.dataPoints,
    logic: node.logic,
    alternatives: node.alternatives,
    reportId: node.reportId,
    source: node,
  }));

  const kpiNodes: GraphNode[] = requirements.kpis.map((kpi) => ({
    id: kpi.id,
    layerId: "kpi",
    groupId: kpi.pageId,
    label: kpi.name,
    description: kpi.businessDefinition,
    status: kpi.approvalStatus === "approved" ? "definition_ready" : "planned",
    role: "Draft business KPI",
    pages: requirements.pages.filter((page) => page.kpiIds.includes(kpi.id)).map((page) => page.id),
    dataPoints: [kpi.grain, kpi.formula],
    logic: kpi.formula,
    alternatives: kpi.caveats,
    kpi,
  }));

  const pageNodes: GraphNode[] = requirements.pages.map((page) => ({
    id: `experience:${page.id}`,
    layerId: "experience",
    groupId: page.id,
    label: page.name,
    description: page.purpose,
    status: "definition_ready",
    role: `Control Tower Page ${page.number}`,
    pages: [page.id],
    dataPoints: page.visualModules.map((module) => module.name),
    logic: page.decisionFlow.join(" -> "),
    alternatives: [],
    page,
  }));

  const edges: GraphEdge[] = [];
  for (const node of architecture.modelNodes) {
    for (const input of node.inputs) {
      edges.push({ id: `${input}->${node.id}`, source: input, target: node.id });
    }
  }
  for (const route of architecture.kpiRoutes) {
    for (const kpiId of route.kpiIds) {
      edges.push({ id: `${route.summaryNodeId}->${kpiId}`, source: route.summaryNodeId, target: kpiId });
    }
  }
  for (const page of requirements.pages) {
    for (const kpiId of page.kpiIds) {
      edges.push({ id: `${kpiId}->experience:${page.id}`, source: kpiId, target: `experience:${page.id}` });
    }
  }

  return { nodes: [...staticNodes, ...kpiNodes, ...pageNodes], edges };
}

function traceConnected(selectedId: string, edges: GraphEdge[]) {
  if (!selectedId) return new Set<string>();
  const upstream = new Map<string, string[]>();
  const downstream = new Map<string, string[]>();
  for (const edge of edges) {
    upstream.set(edge.target, [...(upstream.get(edge.target) ?? []), edge.source]);
    downstream.set(edge.source, [...(downstream.get(edge.source) ?? []), edge.target]);
  }
  const found = new Set<string>([selectedId]);
  const visit = (start: string, adjacency: Map<string, string[]>) => {
    const queue = [start];
    while (queue.length) {
      const current = queue.shift()!;
      for (const next of adjacency.get(current) ?? []) {
        if (found.has(next)) continue;
        found.add(next);
        queue.push(next);
      }
    }
  };
  visit(selectedId, upstream);
  visit(selectedId, downstream);
  return found;
}

function edgePath(source: Position, target: Position) {
  const sourceX = source.x + NODE_WIDTH;
  const sourceY = source.y + NODE_HEIGHT / 2;
  const targetY = target.y + NODE_HEIGHT / 2;
  if (target.x > source.x) {
    const distance = Math.max(42, (target.x - sourceX) * 0.52);
    return `M ${sourceX} ${sourceY} C ${sourceX + distance} ${sourceY}, ${target.x - distance} ${targetY}, ${target.x} ${targetY}`;
  }
  const loopX = source.x + NODE_WIDTH + 46;
  return `M ${sourceX} ${sourceY} C ${loopX} ${sourceY}, ${loopX} ${targetY}, ${target.x + NODE_WIDTH} ${targetY}`;
}

function RouteOverview({
  architecture,
  nodes,
  focusedKpi,
  focusedPage,
  selectedId,
  onSelect,
  onOpenReport,
}: {
  architecture: ControlTowerArchitecture;
  nodes: GraphNode[];
  focusedKpi?: ControlTowerKpi;
  focusedPage?: ControlTowerPage;
  selectedId: string;
  onSelect: (node: GraphNode) => void;
  onOpenReport: (reportId: string) => void;
}) {
  const byLayer = new Map<ArchitectureLayerId, GraphNode[]>();
  for (const node of nodes) {
    byLayer.set(node.layerId, [...(byLayer.get(node.layerId) ?? []), node]);
  }
  const sources = nodes.filter(
    (node) => node.source?.kind === "report" || node.source?.kind === "master",
  );
  const modelSteps = nodes.filter((node) => node.source?.kind === "table");

  return (
    <div className="architecture-route-overview">
      <section className="architecture-route-summary">
        <div>
          <span className="section-kicker">
            {focusedPage ? `Page ${focusedPage.number} / ${focusedPage.name}` : "Complete architecture"}
          </span>
          <h2>{focusedKpi?.name ?? "Eight-layer Control Tower architecture"}</h2>
          <p>
            {focusedKpi?.businessDefinition
              ?? "Select a Control Tower page to trace one KPI from captured Restroworks evidence to its final decision surface."}
          </p>
        </div>
        {focusedKpi ? (
          <dl>
            <div><dt>Formula</dt><dd><code>{focusedKpi.formula}</code></dd></div>
            <div><dt>Grain</dt><dd>{focusedKpi.grain}</dd></div>
            <div><dt>Owner</dt><dd>{focusedKpi.owner}</dd></div>
            <div><dt>Evidence</dt><dd>{sources.length} sources / {modelSteps.length} model steps</dd></div>
          </dl>
        ) : (
          <div className="architecture-system-counts">
            {architecture.layers.map((layer) => (
              <span key={layer.id} data-layer={layer.id}>
                <i />
                <b>{nodes.filter((node) => node.layerId === layer.id).length}</b>
                <small>{layer.shortLabel}</small>
              </span>
            ))}
          </div>
        )}
      </section>

      <section className="architecture-route-stages" aria-label="Ordered KPI architecture route">
        {architecture.layers.map((layer, layerNumber) => {
          const layerNodes = byLayer.get(layer.id) ?? [];
          return (
            <article key={layer.id} className="architecture-route-stage" data-layer={layer.id}>
              <header>
                <b>{layerNumber + 1}</b>
                <span><strong>{layer.shortLabel}</strong><small>{layer.description}</small></span>
                <em>{layerNodes.length}</em>
              </header>
              <div>
                {layerNodes.slice(0, 6).map((node) => (
                  <button
                    key={node.id}
                    type="button"
                    className={node.id === selectedId ? "is-selected" : ""}
                    onClick={() => onSelect(node)}
                  >
                    <i />
                    <span><strong>{node.label}</strong><small>{node.role}</small></span>
                    <ArrowRight aria-hidden="true" size={12} />
                  </button>
                ))}
                {!layerNodes.length ? <p>No node is required for this selected route.</p> : null}
                {layerNodes.length > 6 ? <p>+ {layerNodes.length - 6} additional engineering nodes</p> : null}
              </div>
            </article>
          );
        })}
      </section>

      {focusedKpi ? (
        <section className="architecture-route-source-matrix">
          <header>
            <span><Database aria-hidden="true" size={15} /><strong>Exact source evidence for this KPI</strong></span>
            <small>{sources.length} contributing report and master sources</small>
          </header>
          <div className="architecture-route-source-grid">
            {sources.map((source) => (
              <article key={source.id}>
                <div>
                  <span data-layer="source"><i /></span>
                  <p><strong>{source.label}</strong><small>{source.role}</small></p>
                  {source.reportId ? (
                    <button type="button" title={`Open ${source.label} schema`} onClick={() => onOpenReport(source.reportId!)}>
                      <ExternalLink aria-hidden="true" size={13} />
                    </button>
                  ) : null}
                </div>
                <ul>{source.dataPoints.map((point) => <li key={`${source.id}:${point}`}>{point}</li>)}</ul>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <section className="architecture-route-gate">
        <ShieldCheck aria-hidden="true" size={17} />
        <span>
          <strong>{focusedKpi ? "Route isolated and presentation-ready" : "Architecture coverage at first glance"}</strong>
          <small>
            {focusedKpi
              ? `${focusedKpi.formula} Production publication still follows the source, UOM, reconciliation and business-definition gates shown in the inspector.`
              : "The complete system is summarized by layer. Choose a page and KPI for its exact source-to-decision route."}
          </small>
        </span>
      </section>
    </div>
  );
}

export function ArchitectureGraphWorkspace({
  architecture,
  requirements,
  onOpenReport,
}: ArchitectureGraphWorkspaceProps) {
  const initialPage = requirements.pages[0];
  const initialKpiId = initialPage?.kpiIds[0] ?? "";
  const [mode, setMode] = useState<GraphMode>("route");
  const [pageFocus, setPageFocus] = useState(initialPage?.id ?? "all");
  const [kpiFocus, setKpiFocus] = useState(initialKpiId);
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(initialKpiId);
  const [zoom, setZoom] = useState(0.82);
  const [pan, setPan] = useState<Position>({ x: 24, y: 18 });
  const [offsets, setOffsets] = useState<Record<string, Position>>({});
  const [inspectorOpen, setInspectorOpen] = useState(true);
  const viewportRef = useRef<HTMLDivElement>(null);
  const panSession = useRef<{ pointerId: number; x: number; y: number; pan: Position } | null>(null);
  const nodeSession = useRef<{ pointerId: number; id: string; x: number; y: number; offset: Position; moved: boolean } | null>(null);
  const suppressClick = useRef(false);

  const completeGraph = useMemo(
    () => graphFromContracts(architecture, requirements),
    [architecture, requirements],
  );
  const focusedPage = useMemo(
    () => requirements.pages.find((page) => page.id === pageFocus),
    [pageFocus, requirements.pages],
  );
  const pageKpis = useMemo(
    () => focusedPage
      ? focusedPage.kpiIds
        .map((kpiId) => requirements.kpis.find((kpi) => kpi.id === kpiId))
        .filter((kpi): kpi is ControlTowerKpi => Boolean(kpi))
      : [],
    [focusedPage, requirements.kpis],
  );
  const focusedKpi = useMemo(
    () => requirements.kpis.find((kpi) => kpi.id === kpiFocus),
    [kpiFocus, requirements.kpis],
  );
  const scopedCompleteGraph = useMemo(() => {
    if (focusedKpi) {
      const routeIds = traceConnected(focusedKpi.id, completeGraph.edges);
      const selectedExperienceId = focusedPage ? `experience:${focusedPage.id}` : "";
      const nodes = completeGraph.nodes.filter((node) => (
        routeIds.has(node.id)
        && (node.layerId !== "experience" || !selectedExperienceId || node.id === selectedExperienceId)
      ));
      const nodeIds = new Set(nodes.map((node) => node.id));
      return {
        nodes,
        edges: completeGraph.edges.filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target)),
      };
    }
    if (focusedPage) {
      const nodes = completeGraph.nodes.filter((node) => node.pages.includes(focusedPage.id));
      const nodeIds = new Set(nodes.map((node) => node.id));
      return {
        nodes,
        edges: completeGraph.edges.filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target)),
      };
    }
    return completeGraph;
  }, [completeGraph, focusedKpi, focusedPage]);
  const graph = scopedCompleteGraph;
  const visibleNodes = graph.nodes;
  const visibleIds = useMemo(() => new Set(visibleNodes.map((node) => node.id)), [visibleNodes]);
  const visibleEdges = useMemo(
    () => graph.edges.filter((edge) => visibleIds.has(edge.source) && visibleIds.has(edge.target)),
    [graph.edges, visibleIds],
  );

  const layerIndex = useMemo(
    () => new Map(architecture.layers.map((layer, index) => [layer.id, index])),
    [architecture.layers],
  );
  const groupIndex = useMemo(
    () => new Map(architecture.groups.map((group, index) => [group.id, index])),
    [architecture.groups],
  );
  const basePositions = useMemo(() => {
    const positions: Record<string, Position> = {};
    const byLayer = new Map<ArchitectureLayerId, GraphNode[]>();
    for (const node of visibleNodes) byLayer.set(node.layerId, [...(byLayer.get(node.layerId) ?? []), node]);
    for (const layer of architecture.layers) {
      const items = (byLayer.get(layer.id) ?? []).sort((a, b) => {
        const groupDifference = (groupIndex.get(a.groupId) ?? 99) - (groupIndex.get(b.groupId) ?? 99);
        return groupDifference || a.label.localeCompare(b.label);
      });
      items.forEach((node, row) => {
        positions[node.id] = {
          x: 32 + (layerIndex.get(layer.id) ?? 0) * (LANE_WIDTH + LANE_GAP),
          y: SCENE_TOP + row * (NODE_HEIGHT + NODE_GAP),
        };
      });
    }
    return positions;
  }, [architecture.layers, groupIndex, layerIndex, visibleNodes]);
  const positions = useMemo(() => Object.fromEntries(
    Object.entries(basePositions).map(([id, position]) => [
      id,
      { x: position.x + (offsets[id]?.x ?? 0), y: position.y + (offsets[id]?.y ?? 0) },
    ]),
  ), [basePositions, offsets]);

  const maxRows = useMemo(() => Math.max(
    1,
    ...architecture.layers.map((layer) => visibleNodes.filter((node) => node.layerId === layer.id).length),
  ), [architecture.layers, visibleNodes]);
  const scene = {
    width: 32 + architecture.layers.length * (LANE_WIDTH + LANE_GAP),
    height: Math.max(760, SCENE_TOP + maxRows * (NODE_HEIGHT + NODE_GAP) + 72),
  };

  const selectedNode = visibleNodes.find((node) => node.id === selectedId);
  const connected = useMemo(
    () => focusedKpi
      ? new Set(visibleNodes.map((node) => node.id))
      : traceConnected(selectedNode?.id ?? "", visibleEdges),
    [focusedKpi, selectedNode?.id, visibleEdges, visibleNodes],
  );
  const normalizedQuery = query.trim().toLowerCase();
  const queryMatches = useMemo(() => new Set(
    normalizedQuery
      ? visibleNodes.filter((node) => `${node.label} ${node.description} ${node.dataPoints.join(" ")}`.toLowerCase().includes(normalizedQuery)).map((node) => node.id)
      : [],
  ), [normalizedQuery, visibleNodes]);

  const fitGraph = useCallback(() => {
    const viewport = viewportRef.current;
    if (!viewport || !visibleNodes.length) return;
    const rect = viewport.getBoundingClientRect();
    const values = visibleNodes.map((node) => basePositions[node.id]).filter(Boolean);
    const minX = Math.min(...values.map((position) => position.x));
    const maxX = Math.max(...values.map((position) => position.x + NODE_WIDTH));
    const minY = Math.min(...values.map((position) => position.y - 44));
    const maxY = Math.max(...values.map((position) => position.y + NODE_HEIGHT));
    const nextZoom = Math.max(0.28, Math.min(1.05, (rect.width - 54) / (maxX - minX), (rect.height - 54) / (maxY - minY)));
    setZoom(nextZoom);
    setPan({
      x: (rect.width - (maxX - minX) * nextZoom) / 2 - minX * nextZoom,
      y: (rect.height - (maxY - minY) * nextZoom) / 2 - minY * nextZoom,
    });
  }, [basePositions, visibleNodes]);

  useEffect(() => {
    if (mode !== "engineering") return;
    const frame = requestAnimationFrame(() => fitGraph());
    return () => cancelAnimationFrame(frame);
  }, [fitGraph, mode]);

  const changeMode = (nextMode: GraphMode) => {
    setMode(nextMode);
    setOffsets({});
    if (focusedKpi) {
      setSelectedId(focusedKpi.id);
    } else {
      setSelectedId("");
    }
  };

  const changePageFocus = (pageId: string) => {
    setPageFocus(pageId);
    setOffsets({});
    if (pageId === "all") {
      setKpiFocus("");
      setSelectedId("");
      setMode("route");
      return;
    }
    const page = requirements.pages.find((candidate) => candidate.id === pageId);
    const nextKpiId = page?.kpiIds[0] ?? "";
    setKpiFocus(nextKpiId);
    setSelectedId(nextKpiId);
    setMode("route");
    setInspectorOpen(true);
  };

  const activateKpiRoute = (kpiId: string, preferredPageId?: string) => {
    const kpi = requirements.kpis.find((candidate) => candidate.id === kpiId);
    if (!kpi) return;
    const page = requirements.pages.find((candidate) => (
      candidate.id === preferredPageId && candidate.kpiIds.includes(kpiId)
    )) ?? requirements.pages.find((candidate) => candidate.kpiIds.includes(kpiId));
    setPageFocus(page?.id ?? kpi.pageId);
    setKpiFocus(kpiId);
    setMode("route");
    setOffsets({});
    setSelectedId(kpiId);
    setInspectorOpen(true);
  };

  const openMember = (member: GraphNode) => {
    if (member.kpi) {
      activateKpiRoute(member.kpi.id, pageFocus);
      return;
    }
    setSelectedId(member.id);
  };

  const zoomBy = (factor: number) => {
    const viewport = viewportRef.current;
    if (!viewport) return;
    const rect = viewport.getBoundingClientRect();
    const next = Math.max(0.28, Math.min(1.45, zoom * factor));
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    setPan((current) => ({
      x: centerX - (centerX - current.x) * (next / zoom),
      y: centerY - (centerY - current.y) * (next / zoom),
    }));
    setZoom(next);
  };

  const handleWheel = useCallback((event: WheelEvent) => {
    event.preventDefault();
    const viewport = viewportRef.current;
    if (!viewport) return;
    const rect = viewport.getBoundingClientRect();
    const pointerX = event.clientX - rect.left;
    const pointerY = event.clientY - rect.top;
    const next = Math.max(0.28, Math.min(1.45, zoom * (event.deltaY > 0 ? 0.9 : 1.1)));
    setPan((current) => ({
      x: pointerX - (pointerX - current.x) * (next / zoom),
      y: pointerY - (pointerY - current.y) * (next / zoom),
    }));
    setZoom(next);
  }, [zoom]);

  useEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport || mode !== "engineering") return;
    viewport.addEventListener("wheel", handleWheel, { passive: false });
    return () => viewport.removeEventListener("wheel", handleWheel);
  }, [handleWheel, mode]);

  const beginPan = (event: ReactPointerEvent<HTMLDivElement>) => {
    const target = event.target as HTMLElement;
    if (event.button !== 0 || target.closest(".architecture-node, button, input")) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    panSession.current = { pointerId: event.pointerId, x: event.clientX, y: event.clientY, pan };
  };
  const movePan = (event: ReactPointerEvent<HTMLDivElement>) => {
    const session = panSession.current;
    if (!session || session.pointerId !== event.pointerId) return;
    setPan({ x: session.pan.x + event.clientX - session.x, y: session.pan.y + event.clientY - session.y });
  };
  const endPan = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (panSession.current?.pointerId === event.pointerId) panSession.current = null;
  };

  const beginNodeDrag = (event: ReactPointerEvent<HTMLButtonElement>, nodeId: string) => {
    if (event.button !== 0) return;
    event.stopPropagation();
    event.currentTarget.setPointerCapture(event.pointerId);
    nodeSession.current = {
      pointerId: event.pointerId,
      id: nodeId,
      x: event.clientX,
      y: event.clientY,
      offset: offsets[nodeId] ?? { x: 0, y: 0 },
      moved: false,
    };
  };
  const moveNode = (event: ReactPointerEvent<HTMLButtonElement>) => {
    const session = nodeSession.current;
    if (!session || session.pointerId !== event.pointerId) return;
    const dx = (event.clientX - session.x) / zoom;
    const dy = (event.clientY - session.y) / zoom;
    if (Math.abs(dx) + Math.abs(dy) > 3) session.moved = true;
    setOffsets((current) => ({ ...current, [session.id]: { x: session.offset.x + dx, y: session.offset.y + dy } }));
  };
  const endNodeDrag = (event: ReactPointerEvent<HTMLButtonElement>) => {
    const session = nodeSession.current;
    if (!session || session.pointerId !== event.pointerId) return;
    suppressClick.current = session.moved;
    nodeSession.current = null;
    requestAnimationFrame(() => { suppressClick.current = false; });
  };

  const resetView = () => {
    setOffsets({});
    setZoom(0.82);
    setPan({ x: 24, y: 18 });
    requestAnimationFrame(() => fitGraph());
  };

  const sourceMembers = (selectedNode?.members ?? (selectedNode ? [selectedNode] : []))
    .filter((member) => member.source?.kind === "report" || member.source?.kind === "master");
  const selectedPage = selectedNode?.page;
  const selectedKpi = selectedNode?.kpi ?? selectedNode?.members?.find((member) => member.kpi)?.kpi;
  const routeSources = focusedKpi
    ? scopedCompleteGraph.nodes.filter((node) => node.source?.kind === "report" || node.source?.kind === "master")
    : [];
  const routeModelNodeCount = focusedKpi
    ? scopedCompleteGraph.nodes.filter((node) => node.source?.kind === "table").length
    : 0;
  const reportCount = architecture.sourceNodes.filter((node) => node.kind === "report").length;
  const masterCount = architecture.sourceNodes.filter((node) => node.kind === "master").length;

  return (
    <section className="architecture-surface">
      <header className="architecture-header">
        <div>
          <span className="section-kicker">Planned architecture / feasibility validation in progress</span>
          <h1>Supply chain intelligence map</h1>
          <p>Select a control-tower page and KPI to isolate its exact route from Restroworks fields through RAW, standardized, dimensional, fact and summary layers.</p>
        </div>
        <div className="architecture-header-metrics" aria-label="Architecture coverage">
          <span><b>{reportCount}</b> reports</span>
          <span><b>{masterCount}</b> masters</span>
          <span><b>{architecture.modelNodes.length}</b> model nodes</span>
          <span><b>{requirements.kpis.length}</b> KPIs</span>
        </div>
        <div className="architecture-phase">
          <CircleDot aria-hidden="true" size={14} />
          <span><strong>{architecture.currentPhase.label}</strong><small>{architecture.currentPhase.nextGate}</small></span>
        </div>
      </header>

      <div className={`architecture-workbench mode-${mode}${inspectorOpen ? "" : " inspector-closed"}`}>
        <aside className="architecture-controls">
          <div className="architecture-control-section">
            <span className="architecture-control-label">Presentation depth</span>
            <div className="architecture-mode-switch" role="group" aria-label="Graph detail level">
              <button type="button" className={mode === "route" ? "is-active" : ""} onClick={() => changeMode("route")}><Boxes aria-hidden="true" size={14} /> KPI route</button>
              <button type="button" className={mode === "engineering" ? "is-active" : ""} onClick={() => changeMode("engineering")}><GitBranch aria-hidden="true" size={14} /> Engineering</button>
            </div>
            <p>{mode === "route" ? "One KPI, eight ordered layers, exact reports and source fields." : "Every source and table in the selected route with movable nodes and exact edges."}</p>
          </div>

          <div className="architecture-control-section">
            <span className="architecture-control-label">Page focus</span>
            <button type="button" className={`architecture-page-filter${pageFocus === "all" ? " is-active" : ""}`} onClick={() => changePageFocus("all")}>
              <Network aria-hidden="true" size={15} /><span><strong>Complete system</strong><small>All four pages</small></span><b>{requirements.kpis.length}</b>
            </button>
            {requirements.pages.map((page) => (
              <button key={page.id} type="button" className={`architecture-page-filter${pageFocus === page.id ? " is-active" : ""}`} onClick={() => changePageFocus(page.id)}>
                <span className="architecture-page-number">{page.number}</span><span><strong>{page.name}</strong><small>{page.kpiIds.length} KPI routes</small></span><ArrowRight aria-hidden="true" size={13} />
              </button>
            ))}
            {focusedPage && (
              <label className="architecture-route-picker">
                <span><GitBranch aria-hidden="true" size={13} /> KPI / chart route</span>
                <select value={kpiFocus} onChange={(event) => activateKpiRoute(event.target.value, focusedPage.id)}>
                  {pageKpis.map((kpi) => <option key={kpi.id} value={kpi.id}>{kpi.name}</option>)}
                </select>
                {focusedKpi && (
                  <small>
                    <strong>{routeSources.length} sources</strong>
                    <span>{routeModelNodeCount} model steps</span>
                  </small>
                )}
              </label>
            )}
          </div>

          <div className="architecture-control-section architecture-layer-key">
            <span className="architecture-control-label">Architecture layers</span>
            {architecture.layers.map((layer) => (
              <div key={layer.id}><i data-layer={layer.id} /><span><strong>{layer.shortLabel}</strong><small>{visibleNodes.filter((node) => node.layerId === layer.id).length} visible</small></span></div>
            ))}
          </div>

          <div className="architecture-assurance-note">
            <ShieldCheck aria-hidden="true" size={16} />
            <p><strong>Evidence boundary</strong>The three-month synthetic route passes its reconciliation controls. Production promotion still requires populated Restroworks evidence and business sign-off.</p>
          </div>
        </aside>

        {mode === "route" ? (
          <RouteOverview
            architecture={architecture}
            nodes={scopedCompleteGraph.nodes}
            focusedKpi={focusedKpi}
            focusedPage={focusedPage}
            selectedId={selectedId}
            onSelect={(node) => {
              setSelectedId(node.id);
              setInspectorOpen(true);
            }}
            onOpenReport={onOpenReport}
          />
        ) : (
        <div className="architecture-graph-shell">
          <div className="architecture-graph-toolbar">
            <label className="architecture-search">
              <Search aria-hidden="true" size={14} />
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Find report, table, KPI or data point" />
              {normalizedQuery && <span>{queryMatches.size}</span>}
            </label>
            <div className="architecture-tool-group">
              <button type="button" onClick={() => zoomBy(1.15)} title="Zoom in" aria-label="Zoom in"><ZoomIn aria-hidden="true" size={16} /></button>
              <button type="button" onClick={() => zoomBy(0.87)} title="Zoom out" aria-label="Zoom out"><ZoomOut aria-hidden="true" size={16} /></button>
              <button type="button" onClick={fitGraph} title="Fit architecture" aria-label="Fit architecture"><Maximize2 aria-hidden="true" size={16} /></button>
              <button type="button" onClick={resetView} title="Reset moved nodes" aria-label="Reset moved nodes"><RotateCcw aria-hidden="true" size={16} /></button>
              <button type="button" onClick={() => setInspectorOpen((current) => !current)} title={inspectorOpen ? "Hide inspector" : "Show inspector"} aria-label={inspectorOpen ? "Hide inspector" : "Show inspector"}><PanelRightClose aria-hidden="true" size={16} /></button>
            </div>
          </div>
          <div className="architecture-graph-caption">
            {focusedKpi && focusedPage ? (
              <>
                <GitBranch aria-hidden="true" size={13} />
                <strong>Page {focusedPage.number} / {focusedKpi.name}</strong>
                <span>{visibleNodes.length} nodes in this isolated route. Drag or zoom without losing it.</span>
              </>
            ) : (
              <><MousePointer2 aria-hidden="true" size={13} /> Complete architecture overview. Choose a page and KPI to isolate one route.</>
            )}
          </div>
          <div
            ref={viewportRef}
            className="architecture-viewport"
            onPointerDown={beginPan}
            onPointerMove={movePan}
            onPointerUp={endPan}
            onPointerCancel={endPan}
          >
            <div
              className="architecture-scene"
              style={{ width: scene.width, height: scene.height, transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})` }}
            >
              {architecture.layers.map((layer) => (
                <div
                  key={layer.id}
                  className="architecture-lane"
                  data-layer={layer.id}
                  style={{ left: 18 + (layerIndex.get(layer.id) ?? 0) * (LANE_WIDTH + LANE_GAP), width: LANE_WIDTH, height: scene.height - 30 }}
                >
                  <span>{layer.shortLabel}</span><small>{layer.description}</small>
                </div>
              ))}
              <svg className="architecture-edges" width={scene.width} height={scene.height} aria-hidden="true">
                <defs>
                  <marker id="architecture-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 8 4 L 0 8 z" /></marker>
                  <marker id="architecture-arrow-active" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 8 4 L 0 8 z" /></marker>
                </defs>
                {visibleEdges.map((edge) => {
                  const source = positions[edge.source];
                  const target = positions[edge.target];
                  if (!source || !target) return null;
                  const isActive = selectedNode ? connected.has(edge.source) && connected.has(edge.target) : false;
                  return <path key={edge.id} className={isActive ? "is-active" : selectedNode ? "is-muted" : ""} d={edgePath(source, target)} markerEnd={`url(#architecture-arrow${isActive ? "-active" : ""})`} />;
                })}
              </svg>
              {visibleNodes.map((node) => {
                const position = positions[node.id];
                const isSelected = selectedNode?.id === node.id;
                const isConnected = connected.has(node.id);
                const isQueryMatch = queryMatches.has(node.id);
                const isMuted = (selectedNode && !isConnected) || (normalizedQuery && !isQueryMatch);
                const count = node.members?.length ?? 1;
                return (
                  <button
                    key={node.id}
                    type="button"
                    className={`architecture-node${isSelected ? " is-selected" : ""}${isConnected && !isSelected ? " is-connected" : ""}${isQueryMatch ? " is-query-match" : ""}${isMuted ? " is-muted" : ""}`}
                    data-layer={node.layerId}
                    data-status={node.status}
                    style={{ left: position.x, top: position.y }}
                    onPointerDown={(event) => beginNodeDrag(event, node.id)}
                    onPointerMove={moveNode}
                    onPointerUp={endNodeDrag}
                    onPointerCancel={endNodeDrag}
                    onClick={() => {
                      if (suppressClick.current) return;
                      if (node.kpi) {
                        activateKpiRoute(node.kpi.id, pageFocus);
                      } else {
                        setSelectedId(node.id);
                        setInspectorOpen(true);
                      }
                    }}
                  >
                    <span className="architecture-node-top"><i />{humanize(node.status)}{count > 1 && <b>{count}</b>}</span>
                    <strong>{node.label}</strong>
                    <small>{node.role}</small>
                  </button>
                );
              })}
            </div>
          </div>
          <div className="architecture-zoom-readout">{Math.round(zoom * 100)}%</div>
        </div>
        )}

        {inspectorOpen && (
          <aside className="architecture-inspector">
            {selectedNode ? (
              <>
                <header>
                  <span className="architecture-inspector-layer" data-layer={selectedNode.layerId}>{architecture.layers.find((layer) => layer.id === selectedNode.layerId)?.label}</span>
                  <h2>{selectedNode.label}</h2>
                  <p>{selectedNode.description}</p>
                  <div><span className={`architecture-status status-${selectedNode.status}`}>{humanize(selectedNode.status)}</span><span>{selectedNode.role}</span></div>
                </header>

                {selectedKpi && (
                  <section>
                    <h3><BadgeCheck aria-hidden="true" size={14} /> KPI definition</h3>
                    <dl>
                      <div><dt>Formula</dt><dd><code>{selectedKpi.formula}</code></dd></div>
                      <div><dt>Grain</dt><dd>{selectedKpi.grain}</dd></div>
                      <div><dt>Owner</dt><dd>{selectedKpi.owner}</dd></div>
                      <div><dt>Validation</dt><dd>{humanize(selectedKpi.validationStatus)}</dd></div>
                    </dl>
                  </section>
                )}

                {selectedPage && (
                  <section>
                    <h3><Layers3 aria-hidden="true" size={14} /> Page composition</h3>
                    <p>{selectedPage.audiences.join(" / ")}</p>
                    <ol className="architecture-module-list">
                      {selectedPage.visualModules.map((module) => <li key={`${selectedPage.id}:${module.order}`}><b>{module.order}</b><span><strong>{module.name}</strong><small>{module.question}</small></span></li>)}
                    </ol>
                  </section>
                )}

                {focusedKpi && (
                  <section className="architecture-route-evidence">
                    <h3><GitBranch aria-hidden="true" size={14} /> Contributing source fields</h3>
                    <p>{routeSources.length} report and master sources feed this isolated KPI route.</p>
                    {selectedKpi?.id !== focusedKpi.id && (
                      <dl>
                        <div><dt>Selected route</dt><dd>{focusedKpi.name}</dd></div>
                        <div><dt>Formula</dt><dd><code>{focusedKpi.formula}</code></dd></div>
                        <div><dt>Grain</dt><dd>{focusedKpi.grain}</dd></div>
                      </dl>
                    )}
                    <div className="architecture-route-source-list">
                      {routeSources.map((source, index) => (
                        <details key={source.id} open={index === 0 ? true : undefined}>
                          <summary>
                            <span><strong>{source.label}</strong><small>{source.role}</small></span>
                            <b>{source.dataPoints.length} field groups</b>
                          </summary>
                          <div className="architecture-chip-list">
                            {source.dataPoints.map((point) => <span key={`${source.id}:${point}`}>{point}</span>)}
                          </div>
                        </details>
                      ))}
                    </div>
                  </section>
                )}

                <section>
                  <h3><Database aria-hidden="true" size={14} /> Data contract</h3>
                  <div className="architecture-chip-list">
                    {selectedNode.dataPoints.map((point) => <span key={point}>{point}</span>)}
                  </div>
                </section>

                <section>
                  <h3><GitBranch aria-hidden="true" size={14} /> Transformation or decision logic</h3>
                  <p>{selectedNode.logic}</p>
                </section>

                {!!selectedNode.alternatives.length && (
                  <section>
                    <h3><AlertTriangle aria-hidden="true" size={14} /> Fallbacks and gates</h3>
                    <ul>{selectedNode.alternatives.map((alternative) => <li key={alternative}>{alternative}</li>)}</ul>
                  </section>
                )}

                {!!selectedNode.members?.length && (
                  <section>
                    <h3><Boxes aria-hidden="true" size={14} /> Cluster members</h3>
                    <div className="architecture-member-list">
                      {selectedNode.members.map((member) => (
                        <button key={member.id} type="button" onClick={() => openMember(member)}>
                          <span><strong>{member.label}</strong><small>{member.role}</small></span><ArrowRight aria-hidden="true" size={13} />
                        </button>
                      ))}
                    </div>
                  </section>
                )}

                {!!sourceMembers.length && (
                  <section>
                    <h3><ExternalLink aria-hidden="true" size={14} /> Source records</h3>
                    <div className="architecture-source-links">
                      {sourceMembers.map((member) => member.reportId ? (
                        <button key={member.id} type="button" onClick={() => onOpenReport(member.reportId!)}><span>{member.label}</span><ExternalLink aria-hidden="true" size={13} /></button>
                      ) : (
                        <div key={member.id}><span>{member.label}</span><small>{member.source?.catalogState === "external_reference" ? "Captured outside current catalogue" : "Master extract required"}</small></div>
                      ))}
                    </div>
                  </section>
                )}
              </>
            ) : (
              <>
                <header className="architecture-inspector-empty">
                  <LocateFixed aria-hidden="true" size={20} />
                  <h2>Select any node</h2>
                  <p>The map will isolate its complete upstream evidence path and downstream KPI or page impact.</p>
                </header>
                <section>
                  <h3><ShieldCheck aria-hidden="true" size={14} /> Current phase</h3>
                  <p>{architecture.currentPhase.description}</p>
                </section>
                <section>
                  <h3><GitBranch aria-hidden="true" size={14} /> Architecture decisions</h3>
                  <div className="architecture-decision-list">
                    {architecture.decisions.map((decision) => (
                      <article key={decision.id}>
                        <span className={`architecture-status status-${decision.status}`}>{humanize(decision.status)}</span>
                        <strong>{decision.title}</strong>
                        <p>{decision.decision}</p>
                        <small>{decision.rationale}</small>
                      </article>
                    ))}
                  </div>
                </section>
              </>
            )}
          </aside>
        )}
      </div>
    </section>
  );
}
