import atlasSnapshot from "@/schema-pack/generated/atlas.json";
import controlTowerSnapshot from "@/schema-pack/generated/control-tower-requirements.json";
import controlTowerEvidenceSnapshot from "@/schema-pack/generated/control-tower-evidence.json";
import controlTowerFidelitySnapshot from "@/schema-pack/generated/control-tower-fidelity.json";
import controlTowerModelSnapshot from "@/schema-pack/generated/control-tower-model.json";
import controlTowerPresentationSnapshot from "@/schema-pack/generated/control-tower-presentation.json";
import projectPackSnapshot from "@/schema-pack/generated/project-pack-index.json";
import workspaceSnapshot from "@/schema-pack/generated/workspace.json";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "../app/globals.css";
import { AtlasWorkspace } from "../app/components/AtlasWorkspace";
import { EmbeddedControlTowerPortal } from "../app/components/EmbeddedControlTowerPortal";
import type { AtlasData } from "../app/lib/atlas-types";
import type { ControlTowerRequirements } from "../app/lib/control-tower-types";
import type { ControlTowerEvidence } from "../app/lib/control-tower-evidence-types";
import type { ControlTowerFidelity } from "../app/lib/control-tower-fidelity-types";
import type { ProjectPackIndex } from "../app/lib/project-pack-types";
import type {
  ControlTowerModel,
  ControlTowerPresentation,
} from "../app/lib/control-tower-presentation-types";
import type { WorkspaceSeed } from "../app/lib/workspace-types";

const root = document.getElementById("root");
if (!root) throw new Error("ABNAH workbench root was not found.");

const isPortalRoute = /\/portal\/?$/.test(globalThis.location.pathname);

createRoot(root).render(
  <StrictMode>
    {isPortalRoute ? (
      <EmbeddedControlTowerPortal standalone />
    ) : (
      <AtlasWorkspace
        atlas={atlasSnapshot as AtlasData}
        controlTower={controlTowerSnapshot as ControlTowerRequirements}
        controlTowerEvidence={controlTowerEvidenceSnapshot as ControlTowerEvidence}
        controlTowerFidelity={controlTowerFidelitySnapshot as ControlTowerFidelity}
        controlTowerModel={controlTowerModelSnapshot as ControlTowerModel}
        controlTowerPresentation={controlTowerPresentationSnapshot as ControlTowerPresentation}
        projectPack={projectPackSnapshot as ProjectPackIndex}
        workspaceSeed={workspaceSnapshot as WorkspaceSeed}
        persistenceMode="browser"
      />
    )}
  </StrictMode>,
);
