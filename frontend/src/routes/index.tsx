import { createFileRoute } from "@tanstack/react-router";
import { CoachDashboard } from "@/components/coach-dashboard";

export const Route = createFileRoute("/")({ component: App });

function App() {
  return (
    <CoachDashboard />
  );
}