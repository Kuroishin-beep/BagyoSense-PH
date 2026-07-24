interface Props {
  value: string | number;
  label: string;
  hint?: string;
  variant?: 'default' | 'amber' | 'blue' | 'red';
}

export default function KPICard({ value, label, hint, variant = 'default' }: Props) {
  return (
    <div className={`card kpi-card ${variant === 'default' ? '' : variant}`}>
      <div className="kpi-top">
        <span className="kpi-dot" />
        <span className="kpi-label">{label}</span>
      </div>
      <div className="kpi-value">{value}</div>
      {hint && <div className="kpi-hint">{hint}</div>}
    </div>
  );
}
