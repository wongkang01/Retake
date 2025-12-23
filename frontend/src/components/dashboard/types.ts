export type WorkflowMode = "HOME" | "FIND" | "ANALYZE" | "PLAN" | "ADMIN_INGEST";

export interface VodResult {
  id: string;
  map: string;
  round: number;
  team: string;
  condition: string;
  type: string;
  timestamp: string;
  text: string;
  vodUrl: string;
}

export const MOCK_RESULTS: VodResult[] = [
  {
    id: "3268099",
    map: "Haven",
    round: 1,
    team: "TALON",
    condition: "bomb",
    type: "pistol",
    timestamp: "3962s",
    text: "On Haven, round 1, TALON won the pistol round by bomb plant. Paper Rex attempted a retake from A link but were stalled by utility.",
    vodUrl: "https://www.youtube.com/watch?v=XJTlVgaeY3U&t=3962s"
  },
  {
    id: "3268111",
    map: "Haven",
    round: 13,
    team: "TALON",
    condition: "kills",
    type: "flawless",
    timestamp: "5397s",
    text: "Pistol round 13 on Haven: TALON secured a flawless victory via elimination. Exceptional entry timing on C site.",
    vodUrl: "https://www.youtube.com/watch?v=XJTlVgaeY3U&t=5397s"
  }
];
