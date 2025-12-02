/**
 * @vitest-environment jsdom
 */
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import PostCard from "../components/PostCard.jsx";

describe("PostCard component", () => {
  test("renders username, title, excerpt, likes, and comments", () => {
    render(
      <MemoryRouter>
        <PostCard
          username="Bob"
          title="Test Card"
          excerpt="A short description"
          likes={7}
          comments={3}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Bob")).toBeInTheDocument();
    expect(screen.getByText("Test Card")).toBeInTheDocument();
    expect(screen.getByText("A short description")).toBeInTheDocument();
    expect(screen.getByText("❤️ 7")).toBeInTheDocument();
    expect(screen.getByText("💬 3")).toBeInTheDocument();
  });

  test("renders View link", () => {
    render(
      <MemoryRouter>
        <PostCard
          username="Bob"
          title="Test Card"
          excerpt="A short description"
          likes={7}
          comments={3}
        />
      </MemoryRouter>
    );

    const link = screen.getByRole("link", { name: /view/i });
    expect(link).toBeInTheDocument();
    expect(link.getAttribute("href")).toBe("/explore");
  });
});
