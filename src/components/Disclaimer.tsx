/** Honesty banner — this is a learning demo, not an official forecast. */
export default function Disclaimer({ dataThrough }: { dataThrough?: string }) {
  return (
    <div className="disclaimer">
      <span className="d-ico">⚠️</span>
      <span>
        <b>Educational demo.</b> Built on illustrative climate data to show how
        typhoon patterns and forecasting models work. It is <b>not</b> an official
        PAGASA or NOAA forecast — don&rsquo;t use it for planning or safety decisions.
        {dataThrough && <> Data runs through {dataThrough}.</>}
      </span>
    </div>
  );
}
