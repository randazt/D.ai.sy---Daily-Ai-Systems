interface StatusBadgeProps {
  children: string;
  tone?: "preview" | "current" | "complete";
}

export function StatusBadge({ children, tone = "preview" }: StatusBadgeProps) {
  return <span className={`status-badge ${tone}`}>{children}</span>;
}
