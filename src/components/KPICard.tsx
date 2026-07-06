interface Props {
  value: string | number;
  label: string;
  variant?: 'default' | 'amber' | 'red';
}

export default function KPICard({ value, label, variant = 'default' }: Props) {
  return (
    <div className={`card kpi-card ${variant === 'default' ? '' : variant}`}>
      <div className="kpi-value">{value}</div>
      <div className="kpi-label">{label}</div>
    </div>
  );
}
