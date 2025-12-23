import * as React from "react"
import { HistoryIcon } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"
import { SidebarNav } from "./sidebar-nav"
import { WorkflowMode } from "./types"

interface DashboardShellProps {
  mode: WorkflowMode;
  setMode: (mode: WorkflowMode) => void;
  children: React.ReactNode;
}

export function DashboardShell({ mode, setMode, children }: DashboardShellProps) {
  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <SidebarNav mode={mode} setMode={setMode} />
      
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Top Header */}
        <header className="h-14 border-b flex items-center justify-between px-6 bg-card/50 backdrop-blur-md z-20 shrink-0">
           <div className="flex items-center gap-4">
              <Badge variant="outline" 
                className={cn(
                  "rounded-none text-[9px] font-bold transition-all cursor-pointer",
                  mode === "HOME" ? "border-white/20 text-muted-foreground" : "border-primary/40 text-primary"
                )}
                onClick={() => setMode("HOME")}
              >
                 {mode === "HOME" ? "DASHBOARD" : `${mode} SESSION #42`}
              </Badge>
              {mode !== "HOME" && (
                <>
                  <Separator orientation="vertical" className="h-4" />
                  <div className="flex items-center gap-1.5 opacity-60 hover:opacity-100 transition-opacity cursor-pointer text-muted-foreground">
                    <HistoryIcon className="size-3" />
                    <span className="text-[10px] font-bold uppercase">Recent</span>
                  </div>
                </>
              )}
           </div>
           <div className="flex items-center gap-3">
              <Badge className="rounded-none bg-emerald-500/10 text-emerald-500 border-emerald-500/20 text-[9px]">LIVE DATA SYNC</Badge>
              <div className="size-2 rounded-full bg-emerald-500 animate-pulse" />
           </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto relative z-10 custom-scrollbar">
          {/* Subtle Background Glow */}
          <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_-20%,var(--color-primary)_0%,transparent_40%)] opacity-[0.03] pointer-events-none" />
          
          <div className="max-w-5xl mx-auto p-6 lg:p-10">
            {children}
          </div>
        </div>
      </main>
    </div>
  )
}
