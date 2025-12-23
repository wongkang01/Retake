import { render, screen, fireEvent } from "@testing-library/react";
import { ResultCard, MatchResult } from "../result-card";
import { describe, it, expect, vi } from "vitest";
import React from "react";

const mockResult: MatchResult = {
  id: "test-1",
  team_a: "Sentinels",
  team_b: "LOUD",
  score_a: 13,
  score_b: 11,
  map_name: "Ascent",
  date: "2024-01-01",
  summary: "Great retake on A site.",
  vod_timestamp: 120,
  tags: ["Win", "Retake"]
};

describe("ResultCard", () => {
  it("renders match information correctly", () => {
    const mockAnalyze = vi.fn();
    const mockPlay = vi.fn();

    render(
      <ResultCard 
        result={mockResult} 
        onAnalyze={mockAnalyze} 
        onPlay={mockPlay} 
      />
    );

    expect(screen.getByText("Sentinels")).toBeDefined();
    expect(screen.getByText("LOUD")).toBeDefined();
    expect(screen.getByText("Ascent")).toBeDefined();
    expect(screen.getByText(/Great retake on A site/)).toBeDefined(); // Summary check
  });

  it("calls onPlay when Watch VOD is clicked", () => {
    const mockAnalyze = vi.fn();
    const mockPlay = vi.fn();

    render(
      <ResultCard 
        result={mockResult} 
        onAnalyze={mockAnalyze} 
        onPlay={mockPlay} 
      />
    );

    const playButton = screen.getByText("Watch VOD");
    fireEvent.click(playButton);
    expect(mockPlay).toHaveBeenCalledWith(120);
  });
});
