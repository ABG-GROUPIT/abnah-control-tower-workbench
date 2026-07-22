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
  type WheelEvent as ReactWheelEvent,
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

type GraphMode = "executive" | "engineering";

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

const statusPriority: Record<string, number> = {
  required_gap: 6,
  conditional: 5,
  selected_for_validation: 4,
  planned: 3,
  control_only: 2,
  definition_ready: 1,
};

const humanize = (value: string) => value.replaceAll("_", " ");

function unique(values: string[]) {
  return [...new Set(values)];
}

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

function executiveGraph(
  nodes: GraphNode[],
  edges: GraphEdge[],
  architecture: ControlTowerArchitecture,
  requirements: ControlTowerRequirements,
) {
  const groupById = new Map(architecture.groups.map((group) => [group.id, group]));
  const pageById = new Map(requirements.pages.map((page) => [page.id, page]));
  const groupKey = (node: GraphNode) => {
    if (node.layerId === "experience") return node.id;
    if (node.layerId === "kpi") return `cluster:kpi:${node.groupId}`;
    return `cluster:${node.layerId}:${node.groupId}`;
  };

  const grouped = new Map<string, GraphNode[]>();
  for (const node of nodes) {
    const key = groupKey(node);
    grouped.set(key, [...(grouped.get(key) ?? []), node]);
  }

  const clusterNodes: GraphNode[] = [...grouped.entries()].map(([id, members]) => {
    if (members.length === 1 && members[0].layerId === "experience") {
      return { ...members[0], members };
    }
    const first = members[0];
    const architectureGroup = groupById.get(first.groupId);
    const page = pageById.get(first.groupId);
    const status = [...members]
      .sort((a, b) => (statusPriority[b.status] ?? 0) - (statusPriority[a.status] ?? 0))[0]?.status ?? "planned";
    const label = first.layerId === "kpi"
      ? `${page ? `Page ${page.number}` : "Page"} KPI definitions`
      : architectureGroup?.label ?? first.label;
    return {
      id,
      layerId: first.layerId,
      groupId: first.groupId,
      label,
      description: first.layerId === "kpi"
        ? `${members.length} business definitions routed into this control-tower page.`
        : architectureGroup?.description ?? first.description,
      status,
      role: `${members.length} ${first.layerId === "source" ? "selected sources" : "architecture nodes"}`,
      pages: unique(members.flatMap((member) => member.pages)),
      dataPoints: unique(members.flatMap((member) => member.dataPoints)).slice(0, 10),
      logic: `Open the inspector to review the ${members.length} members represented by this cluster.`,
      alternatives: unique(members.flatMap((member) => member.alternatives)).slice(0, 6),
      members,
    };
  });

  const nodeToCluster = new Map(nodes.map((node) => [node.id, groupKey(node)]));
  const edgeKeys = new Set<string>();
  const clusterEdges: GraphEdge[] = [];
  for (const edge of edges) {
    const source = nodeToCluster.get(edge.source);
    const target = nodeToCluster.get(edge.target);
    if (!source || !target || source === target) continue;
    const key = `${source}->${target}`;
    if (edgeKeys.has(key)) continue;
    edgeKeys.add(key);
    clusterEdges.push({ id: key, source, target });
  }
  return { nodes: clusterNodes, edges: clusterEdges };
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

export function ArchitectureGraphWorkspace({
  architecture,
  requirements,
  onOpenReport,
}: ArchitectureGraphWorkspaceProps) {
  const [mode, setMode] = useState<GraphMode>("executive");
  const [pageFocus, setPageFocus] = useState("all");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState("");
  const [zoom, setZoom] = useState(0.82);
  const [pan, setPan] = useState<Position>({ x: 24, y: 18 });
  const [offsets, setOffsets] = useState<Record<string, Position>>({});
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const viewportRef = useRef<HTMLDivElement>(null);
  const panSession = useRef<{ pointerId: number; x: number; y: number; pan: Position } | null>(null);
  const nodeSession = useRef<{ pointerId: number; id: string; x: number; y: number; offset: Position; moved: boolean } | null>(null);
  const suppressClick = useRef(false);

  const completeGraph = useMemo(
    () => graphFromContracts(architecture, requirements),
    [architecture, requirements],
  );
  const graph = useMemo(
    () => mode === "executive"
      ? executiveGraph(completeGraph.nodes, completeGraph.edges, architecture, requirements)
      : completeGraph,
    [architecture, completeGraph, mode, requirements],
  );
  const visibleNodes = useMemo(
    () => pageFocus === "all" ? graph.nodes : graph.nodes.filter((node) => node.pages.includes(pageFocus)),
    [graph.nodes, pageFocus],
  );
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
  const connected = useMemo(() => traceConnected(selectedNode?.id ?? "", visibleEdges), [selectedNode?.id, visibleEdges]);
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
    const frame = requestAnimationFrame(() => fitGraph());
    return () => cancelAnimationFrame(frame);
  }, [fitGraph, inspectorOpen, mode, pageFocus]);

  const changeMode = (nextMode: GraphMode) => {
    setMode(nextMode);
    setOffsets({});
    setSelectedId("");
  };

  const changePageFocus = (pageId: string) => {
    setPageFocus(pageId);
    setOffsets({});
    setSelectedId("");
  };

  const openMember = (member: GraphNode) => {
    if (mode === "executive") {
      setMode("engineering");
      setOffsets({});
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

  const handleWheel = (event: ReactWheelEvent<HTMLDivElement>) => {
    event.preventDefault();
    const rect = event.currentTarget.getBoundingClientRect();
    const pointerX = event.clientX - rect.left;
    const pointerY = event.clientY - rect.top;
    const next = Math.max(0.28, Math.min(1.45, zoom * (event.deltaY > 0 ? 0.9 : 1.1)));
    setPan((current) => ({
      x: pointerX - (pointerX - current.x) * (next / zoom),
      y: pointerY - (pointerY - current.y) * (next / zoom),
    }));
    setZoom(next);
  };

  const beginPan = (event: ReactPointerEvent<HTMLDivElement>) => {
    const target = event.target as HTMLElement;
    if (event.button !== 0 || target.closest(".architecture-node, button, input")) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    panSession.current = { pointerId: event.pointerId, x: event.clientX, y: event.clientY, pan };
    setSelectedId("");
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
  const selectedKpi = selectedNode?.kpi;

  return (
    <section className="architecture-surface">
      <header className="architecture-header">
        <div>
          <span className="section-kicker">Planned architecture / feasibility validation in progress</span>
          <h1>Supply chain intelligence map</h1>
          <p>Trace the selected source set through RAW, standardized, dimensional, fact and summary layers into all 35 KPIs and four ABNAH control-tower pages.</p>
        </div>
        <div className="architecture-header-metrics" aria-label="Architecture coverage">
          <span><b>21</b> reports</span>
          <span><b>2</b> masters</span>
          <span><b>{architecture.modelNodes.length}</b> model nodes</span>
          <span><b>{requirements.kpis.length}</b> KPIs</span>
        </div>
        <div className="architecture-phase">
          <CircleDot aria-hidden="true" size={14} />
          <span><strong>{architecture.currentPhase.label}</strong><small>{architecture.currentPhase.nextGate}</small></span>
        </div>
      </header>

      <div className={`architecture-workbench${inspectorOpen ? "" : " inspector-closed"}`}>
        <aside className="architecture-controls">
          <div className="architecture-control-section">
            <span className="architecture-control-label">View depth</span>
            <div className="architecture-mode-switch" role="group" aria-label="Graph detail level">
              <button type="button" className={mode === "executive" ? "is-active" : ""} onClick={() => changeMode("executive")}><Boxes aria-hidden="true" size={14} /> Executive</button>
              <button type="button" className={mode === "engineering" ? "is-active" : ""} onClick={() => changeMode("engineering")}><GitBranch aria-hidden="true" size={14} /> Engineering</button>
            </div>
            <p>{mode === "executive" ? "Grouped domains for presentation and decision tracing." : "Every source, table, KPI and page shown individually."}</p>
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
          </div>

          <div className="architecture-control-section architecture-layer-key">
            <span className="architecture-control-label">Architecture layers</span>
            {architecture.layers.map((layer) => (
              <div key={layer.id}><i data-layer={layer.id} /><span><strong>{layer.shortLabel}</strong><small>{visibleNodes.filter((node) => node.layerId === layer.id).length} visible</small></span></div>
            ))}
          </div>

          <div className="architecture-assurance-note">
            <ShieldCheck aria-hidden="true" size={16} />
            <p><strong>Evidence boundary</strong>This is the feasible planned route. Reviewed lineage remains empty until local CSV checks prove the joins and values.</p>
          </div>
        </aside>

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
            <MousePointer2 aria-hidden="true" size={13} /> Drag the canvas to pan. Move any node. Scroll to zoom. Select a node to trace both directions.
          </div>
          <div
            ref={viewportRef}
            className="architecture-viewport"
            onWheel={handleWheel}
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
                    onClick={() => { if (!suppressClick.current) { setSelectedId(node.id); setInspectorOpen(true); } }}
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
