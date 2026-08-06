import atlasSnapshot from "@/schema-pack/generated/atlas.json";
import controlTowerSnapshot from "@/schema-pack/generated/control-tower-requirements.json";
import controlTowerEvidenceSnapshot from "@/schema-pack/generated/control-tower-evidence.json";
import controlTowerFidelitySnapshot from "@/schema-pack/generated/control-tower-fidelity.json";
import projectPackSnapshot from "@/schema-pack/generated/project-pack-index.json";
import workspaceSnapshot from "@/schema-pack/generated/workspace.json";
import { AtlasWorkspace } from "./components/AtlasWorkspace";
import type { AtlasData } from "./lib/atlas-types";
import type { ControlTowerRequirements } from "./lib/control-tower-types";
import type { ControlTowerEvidence } from "./lib/control-tower-evidence-types";
import type { ControlTowerFidelity } from "./lib/control-tower-fidelity-types";
import type { ProjectPackIndex } from "./lib/project-pack-types";
import type { WorkspaceSeed } from "./lib/workspace-types";

export default function Home() {
  return (
    <AtlasWorkspace
      atlas={atlasSnapshot as AtlasData}
      controlTower={controlTowerSnapshot as ControlTowerRequirements}
      controlTowerEvidence={controlTowerEvidenceSnapshot as ControlTowerEvidence}
      controlTowerFidelity={controlTowerFidelitySnapshot as ControlTowerFidelity}
      projectPack={projectPackSnapshot as ProjectPackIndex}
      workspaceSeed={workspaceSnapshot as WorkspaceSeed}
    />
  );
}
