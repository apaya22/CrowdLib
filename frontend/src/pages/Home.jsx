import { Link } from "react-router-dom";
import FeatureCard from "../components/FeatureCard.jsx";
import PostCard from "../components/PostCard.jsx";

export default function Home() {
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
            <Link className="btn btn--primary" to="/login">Log In</Link>
            <Link className="btn btn--ghost" to="/explore">Explore</Link>
          </div>
          <p className="hero__footnote">
            New here? <Link to="/signup">Create an account</Link>
          </p>
        </div>

        {/* Replace this with a real image later */}
        <div className="hero__image">
          <div className="img-placeholder">
            <span>Hero Image Placeholder</span>
          </div>
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
          <div className="img-placeholder img-placeholder--wide"><span>Image 1</span></div>
          <div className="img-placeholder"><span>Image 2</span></div>
          <div className="img-placeholder"><span>Image 3</span></div>
          <div className="img-placeholder"><span>Image 4</span></div>
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
            <Link className="btn btn--primary" to="/login">Log In</Link>
            <Link className="btn btn--ghost" to="/signup">Sign Up</Link>
          </div>
        </div>
      </section>
    </div>
  );
}
