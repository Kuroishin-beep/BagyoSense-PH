import dynamic from 'next/dynamic';

const PredictorContent = dynamic(() => import('@/components/PredictorContent'), {
  ssr: false,
  loading: () => <div className="loading">Loading...</div>,
});

export default function Page() {
  return <PredictorContent />;
}
