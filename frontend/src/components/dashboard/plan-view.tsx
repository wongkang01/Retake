import * as React from "react"
import {
  TargetIcon,
  ShieldCheckIcon
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card"

export function PlanView() {
  return (
    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex flex-col gap-1">
        <h2 className="text-lg font-bold uppercase tracking-tight">Strategic Counter-Planning</h2>
        <p className="text-xs text-muted-foreground italic">Proposing strategies based on <strong>A-Site Def. Analysis</strong>.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
         <div className="flex flex-col gap-4">
            <h3 className="text-[10px] font-bold uppercase tracking-widest flex items-center gap-2">
               <TargetIcon className="size-3 text-primary" /> Proposed Counter-Strat: "The Early Pinch"
            </h3>
            <Card className="border-primary/20">
               <CardHeader className="bg-muted/20 border-b">
                  <CardTitle className="text-xs uppercase">Objective: Punish A-Long Agression</CardTitle>
               </CardHeader>
               <CardContent className="pt-4 flex flex-col gap-4">
                  <div className="space-y-4">
                    <div className="flex gap-3">
                       <Badge className="h-5 w-5 p-0 flex items-center justify-center shrink-0">1</Badge>
                       <p className="text-[11px] text-muted-foreground">Fake pressure on B-Link to force their Sentinel to anchor.</p>
                    </div>
                    <div className="flex gap-3">
                       <Badge className="h-5 w-5 p-0 flex items-center justify-center shrink-0">2</Badge>
                       <p className="text-[11px] text-muted-foreground">Double Breach flash from Sewer into A-Long contact point.</p>
                    </div>
                  </div>
               </CardContent>
               <CardFooter className="bg-primary/5 py-2 border-t">
                  <span className="text-[10px] font-bold text-primary italic uppercase tracking-tighter">Predicted Success: 64% based on 18 similar scenarios</span>
               </CardFooter>
            </Card>
         </div>

         <div className="flex flex-col gap-4">
            <h3 className="text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 opacity-60">
               <ShieldCheckIcon className="size-3" /> Opponent Habit Checklist
            </h3>
            <div className="flex flex-col gap-2">
               {[
                 "Early Jett dash in Garage (80% frequency)",
                 "Sova dart A-Main at 1:32",
                 "No smoke used for mid-control on Eco"
               ].map((item, i) => (
                 <div key={i} className="flex items-center gap-3 p-3 border bg-muted/10 text-[11px] uppercase tracking-tight font-bold group hover:border-primary/40 transition-colors">
                    <div className="size-3 border border-primary group-hover:bg-primary transition-colors" />
                    {item}
                 </div>
               ))}
            </div>
         </div>
      </div>
    </div>
  );
}
