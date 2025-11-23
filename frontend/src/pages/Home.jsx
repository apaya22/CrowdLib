import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BACKEND } from "../config"; 
import FeatureCard from "../components/FeatureCard.jsx";
import PostCard from "../components/PostCard.jsx";
import heroImg from "../assets/madlibhero.png";
import img1 from "../assets/bear.jpeg";
import img2 from "../assets/ducky.jpeg";
import img3 from "../assets/creature.jpeg";
import img4 from "../assets/dog.jpeg";

export default function Home() {
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    async function checkLogin() {
      try {
        const res = await fetch(`${BACKEND}/api/users/profile/`, {
          method: "GET",
          credentials: "include",
        });

        setLoggedIn(res.ok);
      } catch {
        setLoggedIn(false);
      }
    }

    checkLogin();
  }, []);

  return (
    <div className="home">
      {/* Intro */}
      <section className="hero">
        <div className="hero__text">
          <h1 className="hero__title">CrowdLib — Create & Share Madlibs</h1>
          <p className="hero__subtitle">
            Fill in playful prompts, generate AI images for your stories, and
            explore creations from the community. Post, like and comment with all of your friends.
          </p>
          <div className="hero__actions">

            {/* Hide login button when logged in */}
            {!loggedIn && (
              <Link className="btn btn--primary" to="/login">Log In</Link>
            )}

            <Link className="btn btn--ghost" to="/explore">Explore</Link>
          </div>
        </div>

        <div className="hero__image">
          <img src={heroImg} alt="CrowdLib hero" className="hero-img" />
        </div>
      </section>

      {/* Features */}
      <section className="section">
        <h2 className="section__title">What you can do!</h2>

        <div className="grid grid--3">
          <FeatureCard
            title="Like"
            desc="Show love for funny or clever entries."
          />
          <FeatureCard
            title="Comment"
            desc="Discuss, suggest, and joke with friends’ Madlibs."
          />
          <FeatureCard
            title="AI Image"
            desc="Generate images that match your completed Madlib story."
          />
        </div>
      </section>

      {/* AI images */}
      <section className="section">
        <h2 className="section__title">Gallery</h2>
        <p className="section__subtitle">Drop in eye-catching visuals alongside your stories.</p>

        <div className="gallery">
          <img src={img1} alt="Gallery 1" className="gallery-img gallery-img--wide" />
          <img src={img2} alt="Gallery 2" className="gallery-img" />
          <img src={img3} alt="Gallery 3" className="gallery-img" />
          <img src={img4} alt="Gallery 4" className="gallery-img" />
        </div>
      </section>

      {/* Trending posts */}
      <section className="section">
        <h2 className="section__title">Trending Madlibs</h2>
        <p className="section__subtitle">Find the most popular madlibs.</p>

        <div className="grid grid--3">
          <PostCard
            username="@john"
            title="A Day at the [NOUN]"
            excerpt="Today I saw a [ADJECTIVE] [ANIMAL] who loved to [VERB]..."
            likes={128}
            comments={23}
          />
          <PostCard
            username="@jane"
            title="Space Pirates and [PLURAL NOUN]"
            excerpt="Our ship ran on [SUBSTANCE] and bad decisions..."
            likes={94}
            comments={11}
          />
          <PostCard
            username="@67"
            title="Grandma’s Secret [NOUN]"
            excerpt="Turns out the secret ingredient was [SILLY WORD]!"
            likes={53}
            comments={7}
          />
        </div>

        <div className="section__actions">
          <Link className="btn btn--secondary" to="/explore">See more</Link>
        </div>
      </section>

      {/* How it works */}
      <section className="section section--muted">
        <h2 className="section__title">How it works</h2>
        <ol className="steps">
          <li><strong>Pick or create</strong> a Madlib template.</li>
          <li><strong>Fill the blanks,</strong> add a caption, and generate an AI image.</li>
          <li><strong>Share & react:</strong> get likes and comments from the community.</li>
        </ol>
        <div className="section__actions">
          <Link className="btn btn--primary" to="/create">Create a Madlib</Link>
        </div>
      </section>

      {/* Footer */}
      <section className="section">
        <div className="footer">
          <h3>Ready to join the fun?</h3>
          <p>Create, explore, and collaborate on endless stories.</p>

          <div className="footer__actions">
            {/* Hide login in footer if already logged in */}
            {!loggedIn && (
              <Link className="btn btn--primary" to="/login">Log In</Link>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
