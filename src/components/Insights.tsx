import type { Insight } from '@/lib/insights';

/** Plain-language findings grid. */
export default function Insights({ items }: { items: Insight[] }) {
  if (!items.length) return null;
  return (
    <div className="insights-grid">
      {items.map((it, i) => (
        <div key={i} className="insight">
          <span className="insight-ico" aria-hidden>{it.icon}</span>
          <div>
            <div className="insight-title">{it.title}</div>
            <div className="insight-text">{it.text}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
