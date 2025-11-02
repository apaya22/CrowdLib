export default function FeatureCard({ title, desc }) {
  return (
    <article className="card feature-card">
      <h3 className="feature-card__title">{title}</h3>
      <p className="feature-card__desc">{desc}</p>
    </article>
  );
}
