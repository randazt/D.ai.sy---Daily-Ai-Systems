import { useMemo, useState } from "react";

import { AppShell } from "../components/layout/AppShell";
import { Conversation } from "../features/conversation/Conversation";
import { Home } from "../features/home/Home";
import { PlannedSurface } from "../features/planned/PlannedSurface";

export type SurfaceKey =
  | "home"
  | "conversations"
  | "goals"
  | "workflows"
  | "tasks"
  | "decisions"
  | "growth-passport"
  | "activity"
  | "integrations"
  | "templates"
  | "resources"
  | "knowledge-base"
  | "settings";

const plannedSurfaceCopy: Record<
  Exclude<SurfaceKey, "home" | "conversations">,
  {
    title: string;
    description: string;
    plannedFor: string;
  }
> = {
  goals: {
    title: "Goals",
    description:
      "A planned workspace for goals and projects. This checkpoint does not show stored user goals.",
    plannedFor: "Phase 5C",
  },
  workflows: {
    title: "Workflows",
    description:
      "A planned surface for turning human direction into structured workflows and visible state.",
    plannedFor: "Phase 5C",
  },
  tasks: {
    title: "Tasks",
    description:
      "A planned view for task status, execution, observations, and bounded continuation.",
    plannedFor: "Phase 5C",
  },
  decisions: {
    title: "Decisions",
    description:
      "A planned human-authority surface for clarification, approval boundaries, and AI-vs-human decision states.",
    plannedFor: "Phase 5D",
  },
  "growth-passport": {
    title: "Growth Passport",
    description:
      "A planned user-owned record of helpful strategies, accomplishments, decisions, preferences, and growth.",
    plannedFor: "Phase 5F",
  },
  activity: {
    title: "Activity",
    description:
      "A planned durable activity view. No persistent activity history exists in this shell.",
    plannedFor: "Phase 5E",
  },
  integrations: {
    title: "Integrations",
    description:
      "A planned production integrations area. This checkpoint does not connect external tools.",
    plannedFor: "Future product work",
  },
  templates: {
    title: "Templates",
    description:
      "A planned tool surface for reusable structures that help people start without a blank page.",
    plannedFor: "Future product work",
  },
  resources: {
    title: "Resources",
    description:
      "A planned support library for user-controlled learning and workflow references.",
    plannedFor: "Future product work",
  },
  "knowledge-base": {
    title: "Knowledge Base",
    description:
      "A planned place for accessible reference material. It is not connected to backend retrieval yet.",
    plannedFor: "Future product work",
  },
  settings: {
    title: "Settings",
    description:
      "A planned control area for preferences and configuration. No account or profile persistence exists yet.",
    plannedFor: "Phase 5E",
  },
};

export function App() {
  const [activeSurface, setActiveSurface] = useState<SurfaceKey>("home");

  const activeContent = useMemo(() => {
    if (activeSurface === "home") {
      return <Home />;
    }

    if (activeSurface === "conversations") {
      return <Conversation />;
    }

    return <PlannedSurface {...plannedSurfaceCopy[activeSurface]} />;
  }, [activeSurface]);

  return (
    <AppShell activeSurface={activeSurface} onNavigate={setActiveSurface}>
      {activeContent}
    </AppShell>
  );
}