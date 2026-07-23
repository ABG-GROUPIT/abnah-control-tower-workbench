import atlasSnapshot from "@/schema-pack/generated/atlas.json";
import architectureSnapshot from "@/schema-pack/generated/control-tower-architecture.json";
import controlTowerSnapshot from "@/schema-pack/generated/control-tower-requirements.json";
import controlTowerEvidenceSnapshot from "@/schema-pack/generated/control-tower-evidence.json";
import controlTowerFidelitySnapshot from "@/schema-pack/generated/control-tower-fidelity.json";
import workspaceSnapshot from "@/schema-pack/generated/workspace.json";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "../app/globals.css";
import { AtlasWorkspace } from "../app/components/AtlasWorkspace";
import type { ControlTowerArchitecture } from "../app/lib/architecture-types";
import type { AtlasData } from "../app/lib/atlas-types";
import type { ControlTowerRequirements } from "../app/lib/control-tower-types";
import type { ControlTowerEvidence } from "../app/lib/control-tower-evidence-types";
import type { ControlTowerFidelity } from "../app/lib/control-tower-fidelity-types";
import type { WorkspaceSeed } from "../app/lib/workspace-types";

const root = document.getElementById("root");
if (!root) throw new Error("ABNAH workbench root was not found.");

createRoot(root).render(
  <StrictMode>
    <AtlasWorkspace
      atlas={atlasSnapshot as AtlasData}
      architecture={architectureSnapshot as ControlTowerArchitecture}
      controlTower={controlTowerSnapshot as ControlTowerRequirements}
      controlTowerEvidence={controlTowerEvidenceSnapshot as ControlTowerEvidence}
      controlTowerFidelity={controlTowerFidelitySnapshot as ControlTowerFidelity}
      workspaceSeed={workspaceSnapshot as WorkspaceSeed}
      persistenceMode="browser"
    />
  </StrictMode>,
);
