import type { SurfaceKey } from "../../app/App";
import { DaisyMark } from "../ui/DaisyMark";

interface NavItem {
  key: SurfaceKey;
  label: string;
}

const primaryNavItems: NavItem[] = [
  { key: "home", label: "Home" },
  { key: "conversations", label: "Conversations" },
  { key: "goals", label: "Goals" },
  { key: "workflows", label: "Workflows" },
  { key: "tasks", label: "Tasks" },
  { key: "decisions", label: "Decisions" },
  { key: "growth-passport", label: "Growth Passport" },
  { key: "activity", label: "Activity" },
  { key: "integrations", label: "Integrations" },
];

const toolNavItems: NavItem[] = [
  { key: "templates", label: "Templates" },
  { key: "resources", label: "Resources" },
  { key: "knowledge-base", label: "Knowledge Base" },
];

interface SidebarProps {
  activeSurface: SurfaceKey;
  onNavigate: (surface: SurfaceKey) => void;
}

export function Sidebar({ activeSurface, onNavigate }: SidebarProps) {
  return (
    <aside className="sidebar" aria-label="D.AI.SY navigation">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>

      <div className="brand-lockup">
        <DaisyMark />
        <div>
          <p className="brand-name">D.AI.SY</p>
          <p className="brand-subtitle">Human agency platform</p>
        </div>
      </div>

      <nav className="nav-groups" aria-label="Primary">
        <NavGroup
          label="Primary"
          items={primaryNavItems}
          activeSurface={activeSurface}
          onNavigate={onNavigate}
        />
        <NavGroup
          label="Tools"
          items={toolNavItems}
          activeSurface={activeSurface}
          onNavigate={onNavigate}
        />
      </nav>

      <div className="sidebar-bottom">
        <button
          className={`nav-item ${activeSurface === "settings" ? "active" : ""}`}
          type="button"
          aria-current={activeSurface === "settings" ? "page" : undefined}
          onClick={() => onNavigate("settings")}
        >
          Settings
        </button>

        <section className="principle-card" aria-labelledby="principle-title">
          <p id="principle-title" className="principle-title">
            AI assists. Humans decide.
          </p>
          <p>You stay in control.</p>
        </section>
      </div>
    </aside>
  );
}

interface NavGroupProps {
  activeSurface: SurfaceKey;
  items: NavItem[];
  label: string;
  onNavigate: (surface: SurfaceKey) => void;
}

function NavGroup({ activeSurface, items, label, onNavigate }: NavGroupProps) {
  return (
    <section className="nav-group" aria-labelledby={`${label}-nav-heading`}>
      <h2 id={`${label}-nav-heading`} className="nav-heading">
        {label}
      </h2>
      <div className="nav-list">
        {items.map((item) => (
          <button
            className={`nav-item ${activeSurface === item.key ? "active" : ""}`}
            type="button"
            key={item.key}
            aria-current={activeSurface === item.key ? "page" : undefined}
            onClick={() => onNavigate(item.key)}
          >
            {item.label}
          </button>
        ))}
      </div>
    </section>
  );
}
