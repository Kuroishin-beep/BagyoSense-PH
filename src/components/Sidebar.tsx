'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV = [
  { href: '/', label: 'Dashboard' },
  { href: '/analysis', label: 'Analysis' },
  { href: '/predictor', label: 'Predictor' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <div className="brand">BagyoSense</div>
      <div className="brand-sub">Philippines 2014 &ndash; 2024</div>
      <nav className="nav">
        {NAV.map(({ href, label }) => (
          <Link
            key={href}
            href={href}
            className={`nav-link ${pathname === href ? 'nav-link-active' : ''}`}
          >
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
