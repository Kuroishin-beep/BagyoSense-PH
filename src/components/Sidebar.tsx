'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV = [
  { href: '/', label: 'Dashboard', ico: '📊' },
  { href: '/analysis', label: 'Analysis', ico: '📈' },
  { href: '/predictor', label: 'Predictor', ico: '🎛️' },
];

function NavLinks({ pathname }: { pathname: string }) {
  return (
    <nav className="nav">
      {NAV.map(({ href, label, ico }) => (
        <Link
          key={href}
          href={href}
          className={`nav-link ${pathname === href ? 'nav-link-active' : ''}`}
        >
          <span className="nav-ico" aria-hidden>{ico}</span>
          {label}
        </Link>
      ))}
    </nav>
  );
}

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <>
      {/* Desktop sidebar */}
      <aside className="sidebar">
        <div className="brand-row">
          <span className="brand-mark" aria-hidden>🌀</span>
          <span className="brand">BagyoSense</span>
        </div>
        <div className="brand-sub">
          Philippines typhoon patterns,<br />explained simply · 2014–2026
        </div>
        <NavLinks pathname={pathname} />
        <div className="sidebar-foot">
          Learning demo.<br />Illustrative data only.
        </div>
      </aside>

      {/* Mobile top bar */}
      <header className="topbar">
        <span className="brand">🌀 BagyoSense</span>
        <NavLinks pathname={pathname} />
      </header>
    </>
  );
}
