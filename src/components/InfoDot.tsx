/** A small "?" that reveals a plain-language explanation on hover/focus. */
interface Props {
  title?: string;
  children: React.ReactNode;
}

export default function InfoDot({ title, children }: Props) {
  return (
    <span className="info" tabIndex={0}>
      <span className="info-dot" aria-hidden>?</span>
      <span className="info-pop" role="tooltip">
        {title && <b>{title}</b>}
        {title && <br />}
        {children}
      </span>
    </span>
  );
}
