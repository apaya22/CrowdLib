/**
 * @vitest-environment jsdom
 */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";
import Explore from "../pages/Explore.jsx";

beforeEach(() => {
  vi.restoreAllMocks();
});

// Simplified helper
function mockFetch(data, ok = true) {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
    ok,
    json: async () => data,
    text: async () => "error",
  }));
}

describe("Explore (simple, stable tests)", () => {
  test("shows list of madlibs after initial load", async () => {
    mockFetch([
      { id: 1, title: "Alpha", author: { username: "Bob" } },
      { id: 2, title: "Beta", author: { username: "Alice" } },
    ]);

    render(
      <MemoryRouter>
        <Explore />
      </MemoryRouter>
    );

    // Wait for fetched items to appear
    await screen.findByText("Alpha");
    expect(screen.getByText("Beta")).toBeInTheDocument();
  });

  test("search submits to the server and shows results", async () => {
    // 1️⃣ Initial fetch
    mockFetch([
      { id: 1, title: "Alpha" }
    ]);

    render(
      <MemoryRouter>
        <Explore />
      </MemoryRouter>
    );

    await screen.findByText("Alpha");

    // 2️⃣ Search fetch
    mockFetch([
      { id: 2, title: "Cat Tale", author: { username: "Eve" } }
    ]);

    // Fill input
    fireEvent.change(screen.getByLabelText(/search/i), {
      target: { value: "cat" }
    });

    // Submit search
    fireEvent.submit(screen.getByRole("button", { name: /search/i }));

    // Result should appear
    await waitFor(() =>
      expect(screen.getByText("Cat Tale")).toBeInTheDocument()
    );
  });

  test("shows error UI when initial fetch fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      text: async () => "Server broke",
    }));

    render(
      <MemoryRouter>
        <Explore />
      </MemoryRouter>
    );

    await screen.findByText(/couldn’t load madlibs/i);
  });
});
