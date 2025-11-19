import { useEffect, useState } from "react";

export const BACKEND = (import.meta.env.VITE_API_BASE || "http://localhost:8000/api").replace(/\/$/, "");

const Profile = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`${BACKEND}/users/profile/`, {
      method: "GET",
      credentials: "include", // VERY IMPORTANT
    })
      .then((res) => res.json())
      .then((json) => setData(json));
  }, []);

  return (
    <div>
      <h1>Profile</h1>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};

export default Profile;