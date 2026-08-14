import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "./App";

describe("EvidencePilot dashboard", () => {
  it("renders the research workspace and evidence metrics", async () => {
    render(<App />);

    expect(screen.getByText("Direct a research department, not a chatbot.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Start research" })).toBeEnabled();
    expect(screen.getByText("Agent activity")).toBeInTheDocument();
    expect(screen.getByText("Sources found")).toBeInTheDocument();
  });
});
