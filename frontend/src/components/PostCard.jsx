import { Link } from "react-router-dom";

export default function PostCard({ username, title, excerpt, likes, comments }) {
  return (
    <article className="card post-card">
      <div className="post-card__image img-placeholder" aria-hidden>
        <span>Post Image</span>
      </div>
      <div className="post-card__body">
        <div className="post-card__meta">
          <span className="post-card__user">{username}</span>
        </div>
        <h3 className="post-card__title">{title}</h3>
        <p className="post-card__excerpt">{excerpt}</p>
      </div>
      <div className="post-card__footer">
        <div className="post-card__stats" aria-label="Engagement">
          <span>❤️ {likes}</span>
          <span>💬 {comments}</span>
        </div>
        <Link className="btn btn--tiny" to="/login">View</Link>
      </div>
    </article>
  );
}
