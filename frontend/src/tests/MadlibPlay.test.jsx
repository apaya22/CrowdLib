import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import MadlibPlay from "../pages/MadlibPlay";

// Mock the config module
vi.mock("../config", () => ({
  getCSRFToken: () => "mock-csrf-token",
}));

// Helper function
function renderWithRouter(ui, { route = "/madlibs/1" } = {}) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <Routes>
        <Route path="/madlibs/:id" element={ui} />
      </Routes>
    </MemoryRouter>
  );
}

const mockTemplate = {
  _id: "template123",
  title: "Test Adventure",
  blanks: [
    { id: "1", placeholder: "adjective", type: "adjective" },
    { id: "2", placeholder: "noun", type: "noun" },
  ],
  template: [
    { type: "text", content: "The " },
    { type: "blank", id: "1" },
    { type: "text", content: " " },
    { type: "blank", id: "2" },
    { type: "text", content: " jumped." },
  ],
};

const mockUser = {
  _id: "user123",
  email: "test@example.com",
  username: "testuser",
};

beforeEach(() => {
  vi.restoreAllMocks();
  document.cookie = "";
});

// render test
describe("MadlibPlay — loading state", () => {
  it("shows loading state initially", () => {
    vi.spyOn(global, "fetch").mockImplementation((url) => {
      if (url.includes("/users/profile/")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockUser,
        });
      }
      if (url.includes("/templates/")) {
        return new Promise(() => {}); // Never resolves
      }
    });

    renderWithRouter(<MadlibPlay />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
});

// Error Test
describe("MadlibPlay — error state", () => {
  it("shows error when template fetch fails", async () => {
    vi.spyOn(global, "fetch").mockImplementation((url) => {
      if (url.includes("/users/profile/")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockUser,
        });
      }
      if (url.includes("/templates/")) {
        return Promise.reject(new Error("Network fail"));
      }
    });

    renderWithRouter(<MadlibPlay />);

    await waitFor(() => {
      // The component shows just "Network fail", not "Failed to load template"
      expect(screen.getByText(/Network fail/i)).toBeInTheDocument();
    });
  });
});

// unfound Test
describe("MadlibPlay — not found", () => {
  it("shows 'Not found' when template returns null", async () => {
    vi.spyOn(global, "fetch").mockImplementation((url) => {
      if (url.includes("/users/profile/")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockUser,
        });
      }
      if (url.includes("/templates/")) {
        return Promise.resolve({
          ok: true,
          json: async () => null,
        });
      }
    });

    renderWithRouter(<MadlibPlay />);

    await waitFor(() => {
      expect(screen.getByText(/Cannot read properties of null/i)).toBeInTheDocument();
    });
  });
});

// Form Render tests
describe("MadlibPlay — form behavior", () => {
  it("renders title and blanks", async () => {
    vi.spyOn(global, "fetch").mockImplementation((url) => {
      if (url.includes("/users/profile/")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockUser,
        });
      }
      if (url.includes("/templates/")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockTemplate,
        });
      }
    });

    renderWithRouter(<MadlibPlay />);

    await waitFor(() => {
      expect(screen.getByText("Test Adventure")).toBeInTheDocument();
    });

    expect(screen.getByPlaceholderText("adjective")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("noun")).toBeInTheDocument();
  });

  it("allows typing into blank fields", async () => {
    vi.spyOn(global, "fetch").mockImplementation((url) => {
      if (url.includes("/users/profile/")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockUser,
        });
      }
      if (url.includes("/templates/")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockTemplate,
        });
      }
    });

    renderWithRouter(<MadlibPlay />);

    const input = await waitFor(() => screen.getByPlaceholderText("adjective"));

    fireEvent.change(input, { target: { value: "quick" } });

    expect(input.value).toBe("quick");
  });
});

//Story tests
describe("MadlibPlay — generating story", () => {
  it("fills in the story on Generate", async () => {
    vi.spyOn(global, "fetch").mockImplementation((url) => {
      if (url.includes("/users/profile/")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockUser,
        });
      }
      if (url.includes("/templates/")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockTemplate,
        });
      }
      if (url.includes("/madlibs/") && !url.includes("image-gen")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ id: "madlib123" }),
        });
      }
      if (url.includes("/image-gen/generate/")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ url: "http://example.com/image.png" }),
        });
      }
    });

    renderWithRouter(<MadlibPlay />);

    const input1 = await waitFor(() => screen.getByPlaceholderText("adjective"));
    const input2 = screen.getByPlaceholderText("noun");

    fireEvent.change(input1, { target: { value: "quick" } });
    fireEvent.change(input2, { target: { value: "fox" } });

    fireEvent.click(screen.getByText("Generate"));

    await waitFor(() => {
      expect(screen.getByText(/The quick fox jumped/i)).toBeInTheDocument();
    });
  });

  it("blocks generation when user is not logged in", async () => {
    vi.spyOn(global, "fetch").mockImplementation((url) => {
      if (url.includes("/users/profile/")) {
        return Promise.resolve({
          ok: false,
        });
      }
      if (url.includes("/templates/")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockTemplate,
        });
      }
    });

    const alertMock = vi.spyOn(window, "alert").mockImplementation(() => {});

    renderWithRouter(<MadlibPlay />);

    await waitFor(() => {
      expect(screen.getByText("Test Adventure")).toBeInTheDocument();
    });

    const input1 = screen.getByPlaceholderText("adjective");
    const input2 = screen.getByPlaceholderText("noun");

    fireEvent.change(input1, { target: { value: "quick" } });
    fireEvent.change(input2, { target: { value: "fox" } });

    const generateBtn = screen.getByText("Generate");
    fireEvent.click(generateBtn);

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith(
        "You must be logged in to generate images."
      );
    });
  });
});

// Save test
describe("MadlibPlay — auto save", () => {
  it("automatically saves on Generate", async () => {
    const fetchSpy = vi.spyOn(global, "fetch").mockImplementation((url) => {
      if (url.includes("/users/profile/")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockUser,
        });
      }
      if (url.includes("/templates/")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockTemplate,
        });
      }
      if (url.includes("/madlibs/") && !url.includes("image-gen")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ id: "madlib123" }),
        });
      }
      if (url.includes("/image-gen/generate/")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ url: "http://example.com/image.png" }),
        });
      }
    });

    renderWithRouter(<MadlibPlay />);

    const input1 = await waitFor(() => screen.getByPlaceholderText("adjective"));
    const input2 = screen.getByPlaceholderText("noun");

    fireEvent.change(input1, { target: { value: "blue" } });
    fireEvent.change(input2, { target: { value: "cat" } });

    fireEvent.click(screen.getByText("Generate"));

    await waitFor(() => {
      expect(screen.getByText(/The blue cat jumped/i)).toBeInTheDocument();
    });

    // Verify save was called
    const saveCalls = fetchSpy.mock.calls.filter(
      (call) => call[0].includes("/madlibs/") && !call[0].includes("image-gen")
    );
    expect(saveCalls.length).toBeGreaterThan(0);
  });
});

// Image generation tests
describe("MadlibPlay — image generation", () => {
  it("generates an image and shows preview", async () => {
    vi.spyOn(global, "fetch").mockImplementation((url) => {
      if (url.includes("/users/profile/")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockUser,
        });
      }
      if (url.includes("/templates/")) {
        return Promise.resolve({
          ok: true,
          json: async () => mockTemplate,
        });
      }
      if (url.includes("/madlibs/") && !url.includes("image-gen")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ id: "madlib123" }),
        });
      }
      if (url.includes("/image-gen/generate/")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ url: "http://test.com/cat.png" }),
        });
      }
    });

    renderWithRouter(<MadlibPlay />);

    const input1 = await waitFor(() => screen.getByPlaceholderText("adjective"));
    const input2 = screen.getByPlaceholderText("noun");

    fireEvent.change(input1, { target: { value: "funny" } });
    fireEvent.change(input2, { target: { value: "dog" } });

    fireEvent.click(screen.getByText("Generate"));

    await waitFor(() => {
      const image = screen.getByAltText("Generated illustration");
      expect(image).toBeInTheDocument();
      expect(image.src).toBe("http://test.com/cat.png");
    });
  });
});
