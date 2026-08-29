import { StatusBadge } from "../../components/ui/StatusBadge";

interface PlannedSurfaceProps {
  description: string;
  plannedFor: string;
  title: string;
}

export function PlannedSurface({
  description,
  plannedFor,
  title,
}: PlannedSurfaceProps) {
  return (
    <section className="planned-surface" aria-labelledby="planned-title">
      <div className="planned-card">
        <StatusBadge>Planned Product Experience</StatusBadge>
        <h1 id="planned-title">{title}</h1>
        <p>{description}</p>
        <div className="planned-meta">
          <span>Planned phase</span>
          <strong>{plannedFor}</strong>
        </div>
        <p className="boundary-note">
          This shell does not fabricate stored user content, account state,
          notifications, activity history, integrations, or long-term memory.
        </p>
      </div>
    </section>
  );
}
