import * as React from "react"
import {
  BarChart3Icon,
  LayersIcon,
  TrendingUpIcon,
  DatabaseIcon
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card"

export function AnalyzeView() {
  return (
    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex items-center justify-between border-b pb-4">
         <div>
            <h2 className="text-lg font-bold uppercase tracking-tight">Review & Insight Synthesis</h2>
            <p className="text-xs text-muted-foreground italic">Synthesizing data from rib.gg, VLR, and 12 referenced VOD clips.</p>
         </div>
         <Button size="sm" className="gap-2 uppercase font-bold text-[10px]">
            <LayersIcon className="size-3" /> Generate Visualization
         </Button>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
         <Card className="lg:col-span-2">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 border-b mb-4">
              <CardTitle className="text-xs font-bold uppercase tracking-widest">Tendency Visualization: A-Site Def. (Haven)</CardTitle>
              <BarChart3Icon className="size-4 text-muted-foreground" />
            </CardHeader>
            <CardContent className="h-64 flex items-end justify-between gap-2 px-6 pb-8">
               {/* Mock Bar Chart */}
               {[65, 40, 85, 30, 95, 50].map((h, i) => (
                 <div key={i} className="w-full bg-muted/20 relative group overflow-hidden" style={{ height: '100%' }}>
                    <div className="absolute bottom-0 w-full bg-primary/60 transition-all group-hover:bg-primary" style={{ height: `${h}%` }} />
                    <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[9px] font-bold opacity-50 uppercase italic">T{i+1}</span>
                 </div>
               ))}
            </CardContent>
            <CardFooter className="text-[10px] text-muted-foreground uppercase font-bold tracking-tight py-2 bg-muted/10 border-t">
               Showing success rate delta vs global average across selected timeframe
            </CardFooter>
         </Card>

         <div className="flex flex-col gap-4">
            <Card className="border-primary/40 bg-primary/5">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-bold uppercase tracking-widest text-primary flex items-center gap-2">
                  <TrendingUpIcon className="size-3" /> Critical Trend
                </CardTitle>
              </CardHeader>
              <CardContent className="text-[11px] leading-relaxed">
                 Talon has switched to a <strong>Low-Utility / High-Contact</strong> hold on A-Long during rounds 3-7. Success rate increased by 22% compared to previous VCT Pacific Split.
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2 border-b">
                <CardTitle className="text-[10px] uppercase font-bold opacity-70 flex items-center gap-2">
                  <DatabaseIcon className="size-3" /> VLR/RIB Sync
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-3 text-[10px] flex flex-col gap-3 font-mono">
                 <div className="flex justify-between"><span>Econ Rating</span> <span className="text-foreground font-bold">+1.2</span></div>
                 <div className="flex justify-between"><span>Post-Plant %</span> <span className="text-foreground font-bold">72%</span></div>
                 <div className="flex justify-between"><span>Retake Speed</span> <span className="text-foreground font-bold">14.2s</span></div>
              </CardContent>
            </Card>
         </div>
      </div>
    </div>
  );
}
