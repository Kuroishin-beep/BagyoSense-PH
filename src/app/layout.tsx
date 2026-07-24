import type { Metadata } from 'next';
import Sidebar from '@/components/Sidebar';
import './globals.css';

export const metadata: Metadata = {
  title: 'BagyoSense — Philippine typhoon patterns, explained simply',
  description: 'An educational dashboard exploring how typhoons hit the Philippines and how a simple forecasting model works. Built on illustrative data — not an official forecast.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="layout">
          <Sidebar />
          <main className="main">{children}</main>
        </div>
      </body>
    </html>
  );
}
