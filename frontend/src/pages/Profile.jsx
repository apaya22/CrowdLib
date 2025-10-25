import { useParams } from "react-router-dom";
export default function Profile() {
  const { username } = useParams();
  return (
    <section>
      <h1>@{username}</h1>
      <p>User profile, posts, followers (placeholder).</p>
    </section>
  );
}