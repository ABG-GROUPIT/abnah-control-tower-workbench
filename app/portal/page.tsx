import type { Metadata } from "next";
import { EmbeddedControlTowerPortal } from "../components/EmbeddedControlTowerPortal";

export const metadata: Metadata = {
  title: "ABNAH Supply Chain Control Tower",
  description:
    "Secured executive supply-chain control tower powered by governed Zoho Analytics views.",
};

export default function ControlTowerPortalPage() {
  return <EmbeddedControlTowerPortal standalone />;
}
