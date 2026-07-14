import atlasSnapshot from "@/schema-pack/generated/atlas.json";
import lineageSnapshot from "@/schema-pack/generated/kpi-lineage.json";
import workspaceSnapshot from "@/schema-pack/generated/workspace.json";
import { AtlasWorkspace } from "./components/AtlasWorkspace";
import type { AtlasData } from "./lib/atlas-types";
import type { KpiLineageContract } from "./lib/lineage-types";
import type { WorkspaceSeed } from "./lib/workspace-types";

export default function Home() {
  return (
    <AtlasWorkspace
      atlas={atlasSnapshot as AtlasData}
      lineage={lineageSnapshot as KpiLineageContract}
      workspaceSeed={workspaceSnapshot as WorkspaceSeed}
    />
  );
}
