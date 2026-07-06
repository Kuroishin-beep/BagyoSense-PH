import dynamic from 'next/dynamic';

const AnalysisContent = dynamic(() => import('@/components/AnalysisContent'), {
  ssr: false,
  loading: () => <div className="loading">Loading...</div>,
});

export default function Page() {
  return <AnalysisContent />;
}
