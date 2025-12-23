import * as React from "react"
import { WorkflowMode } from "./dashboard/types"
import { DashboardShell } from "./dashboard/dashboard-shell"
import { HomeView } from "./dashboard/home-view"
import { FindView } from "./dashboard/find-view"
import { AnalyzeView } from "./dashboard/analyze-view"
import { PlanView } from "./dashboard/plan-view"
import { AddEventView } from "./dashboard/add-event-view"

export function CoachDashboard() {
  const [mode, setMode] = React.useState<WorkflowMode>("HOME");

  // Hidden developer shortcut: Shift + A to access Ingestion
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.shiftKey && e.key === "A") {
        setMode("ADMIN_INGEST");
        console.log("Admin mode activated via shortcut");
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <DashboardShell mode={mode} setMode={setMode}>
      {mode === "HOME" && <HomeView setMode={setMode} />}
      {mode === "FIND" && <FindView />}
      {mode === "ADMIN_INGEST" && <AddEventView />}
      {mode === "ANALYZE" && <AnalyzeView />}
      {mode === "PLAN" && <PlanView />}
    </DashboardShell>
  )
}