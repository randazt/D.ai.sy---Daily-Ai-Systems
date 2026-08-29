import { StatusBadge } from "../../components/ui/StatusBadge";

const previewSteps = [
  {
    label: "Clarify what is making this difficult",
    state: "complete",
  },
  {
    label: "Understand the requirements",
    state: "current",
  },
  {
    label: "Break it into manageable steps",
    state: "upcoming",
  },
  {
    label: "Take the first step",
    state: "upcoming",
  },
  {
    label: "Reflect and adjust",
    state: "upcoming",
  },
];

const nextActions = [
  "Review certification requirements",
  "List what is already completed",
  "Identify what is still unclear",
];

export function PreviewPanel() {
  return (
    <aside className="context-panel" aria-labelledby="preview-heading">
      <div className="preview-card">
        <div className="section-heading-row compact">
          <div>
            <p className="eyebrow">Example workspace</p>
            <h2 id="preview-heading">Renew My Professional Certification</h2>
          </div>
          <StatusBadge tone="current">Preview</StatusBadge>
        </div>

        <div className="progress-summary">
          <span>Progress</span>
          <strong>Step 2 of 5</strong>
        </div>

        <ol className="step-list" aria-label="Example goal steps">
          {previewSteps.map((step, index) => (
            <li className={`step-item ${step.state}`} key={step.label}>
              <span className="step-number">{index + 1}</span>
              <span>{step.label}</span>
              <small>
                {step.state === "complete"
                  ? "complete"
                  : step.state === "current"
                    ? "current"
                    : "planned"}
              </small>
            </li>
          ))}
        </ol>

        <section className="next-actions" aria-labelledby="next-actions-heading">
          <h3 id="next-actions-heading">Suggested next actions</h3>
          <ul>
            {nextActions.map((action) => (
              <li key={action}>{action}</li>
            ))}
          </ul>
        </section>

        <p className="preview-disclaimer">
          Preview only. This is not persisted user data.
        </p>
      </div>
    </aside>
  );
}
