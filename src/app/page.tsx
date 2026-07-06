import dynamic from 'next/dynamic';

const Dashboard = dynamic(() => import('@/components/Dashboard'), {
  ssr: false,
  loading: () => <div className="loading">Loading...</div>,
});

export default function Page() {
  return <Dashboard />;
}
