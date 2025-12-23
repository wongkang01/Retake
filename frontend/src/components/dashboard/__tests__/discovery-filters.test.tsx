import { render, screen, fireEvent } from "@testing-library/react";
import { DiscoveryFilters } from "../discovery-filters";
import { describe, it, expect, vi } from "vitest";
import React from "react";

describe("DiscoveryFilters", () => {
  it("renders all filter dropdowns", () => {
    const mockOnChange = vi.fn();
    render(<DiscoveryFilters onFilterChange={mockOnChange} />);

    expect(screen.getByText("Region")).toBeDefined();
    expect(screen.getByText("Team")).toBeDefined();
    expect(screen.getByText("Map")).toBeDefined();
    expect(screen.getByText("Timeframe")).toBeDefined();
  });

  // Note: Testing actual Select interactions in Headless UI/Radix/Shadcn can be tricky 
  // without user-event setup, but basic rendering confirms component integrity.
});
