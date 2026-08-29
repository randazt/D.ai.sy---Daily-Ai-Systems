import type { ReactNode } from "react";

import type { SurfaceKey } from "../../app/App";
import { Sidebar } from "./Sidebar";

interface AppShellProps {
  activeSurface: SurfaceKey;
  children: ReactNode;
  onNavigate: (surface: SurfaceKey) => void;
}

export function AppShell({
  activeSurface,
  children,
  onNavigate,
}: AppShellProps) {
  return (
    <div className="app-shell">
      <Sidebar activeSurface={activeSurface} onNavigate={onNavigate} />
      <main className="main-content" id="main-content" tabIndex={-1}>
        {children}
      </main>
    </div>
  );
}
