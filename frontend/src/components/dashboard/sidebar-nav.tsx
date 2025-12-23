import * as React from "react"
import {
  SearchIcon,
  BarChart3Icon,
  MapPinnedIcon,
  HistoryIcon,
  PlusCircleIcon
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { WorkflowMode } from "./types"

interface SidebarNavProps {
  mode: WorkflowMode;
  setMode: (mode: WorkflowMode) => void;
}

export function SidebarNav({ mode, setMode }: SidebarNavProps) {
  const items = [
    { id: "FIND" as WorkflowMode, label: "Find", icon: SearchIcon, desc: "Search & Discovery" },
    { id: "ANALYZE" as WorkflowMode, label: "Analyze", icon: BarChart3Icon, desc: "Review & Insights", disabled: true },
    { id: "PLAN" as WorkflowMode, label: "Plan", icon: MapPinnedIcon, desc: "Opponent Countering", disabled: true },
  ];

  return (
    <div className="w-64 border-r flex flex-col gap-2 p-4 h-full hidden lg:flex bg-muted/10 shrink-0">
      <div className="mb-6 px-2 cursor-pointer group" onClick={() => setMode("HOME")}>
        <h1 className="text-xl font-bold tracking-tighter uppercase italic text-primary group-hover:text-foreground transition-colors">Retake //</h1>
        <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest">Coach Intelligence</p>
      </div>
      
      <div className="flex flex-col gap-1">
        {items.map((item) => (
          <Button
            key={item.id}
            variant={mode === item.id ? "secondary" : "ghost"}
            disabled={item.disabled}
            className={cn(
              "justify-start gap-3 h-12 rounded-none transition-all relative overflow-hidden",
              mode === item.id ? "border-l-2 border-primary pl-4" : "pl-4 opacity-60 hover:opacity-100",
              item.disabled && "opacity-40 grayscale"
            )}
            onClick={() => setMode(item.id)}
          >
            <item.icon className={cn("size-4", mode === item.id && "text-primary")} />
            <div className="flex flex-col items-start text-left">
              <span className="text-xs font-bold uppercase tracking-tight">{item.label}</span>
              <span className="text-[9px] opacity-70">{item.desc}</span>
            </div>
            {item.disabled && (
              <Badge variant="outline" className="absolute right-[-10px] top-1 rotate-12 scale-[0.6] bg-primary text-primary-foreground border-none px-4 py-0.5">SOON</Badge>
            )}
          </Button>
        ))}
      </div>

      <div className="mt-auto p-2">
        <div className="flex items-center gap-3 p-3 hover:bg-muted/50 transition-colors cursor-pointer group">
          <div className="size-8 rounded-full bg-primary/20 flex items-center justify-center border border-primary/30 group-hover:border-primary transition-colors">
            <span className="text-[10px] font-bold text-primary font-mono">TU</span>
          </div>
          <div className="flex flex-col overflow-hidden">
            <span className="text-[11px] font-bold truncate">Test User</span>
            <span className="text-[9px] text-muted-foreground uppercase tracking-widest font-bold">Head Coach</span>
          </div>
        </div>
      </div>
    </div>
  );
}