import * as React from "react"
import {
  SearchIcon,
  BarChart3Icon,
  MapPinnedIcon,
  TargetIcon
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { WorkflowMode } from "./types"

interface HomeViewProps {
  setMode: (mode: WorkflowMode) => void;
}

export function HomeView({ setMode }: HomeViewProps) {
  return (
    <div className="flex flex-col gap-12 py-10 animate-in fade-in zoom-in-95 duration-700">
      <section className="text-center space-y-4 max-w-2xl mx-auto">
        <Badge variant="outline" className="rounded-none border-primary/30 text-primary px-4 py-1 tracking-[0.2em] font-bold">ALPHA ACCESS</Badge>
        <h2 className="text-4xl lg:text-6xl font-bold tracking-tighter uppercase italic italic">Dominate the <span className="text-primary">Retake</span></h2>
        <p className="text-muted-foreground text-sm lg:text-base leading-relaxed">
          The all-in-one tactical intelligence platform for professional Valorant coaching. 
          Discover patterns, analyze tendencies, and plan the perfect counter.
        </p>
      </section>

      <div className="grid md:grid-cols-3 gap-6">
        {/* FIND CARD */}
        <Card 
          className="group relative h-[380px] flex flex-col justify-between overflow-hidden cursor-pointer border-primary/20 hover:border-primary/50 transition-all hover:translate-y-[-4px]"
          onClick={() => setMode("FIND")}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <CardHeader className="relative z-10">
            <div className="size-10 bg-primary/10 flex items-center justify-center mb-4">
              <SearchIcon className="size-5 text-primary" />
            </div>
            <CardTitle className="text-xl tracking-tight uppercase italic">Find</CardTitle>
            <CardDescription className="text-xs">
              Semantic VOD search across thousands of professional rounds.
            </CardDescription>
          </CardHeader>
          <CardContent className="relative z-10 flex-1 flex items-center justify-center opacity-40 group-hover:opacity-100 transition-all">
             <div className="grid grid-cols-3 gap-2 w-full">
                {[1, 2, 3, 4, 5, 6].map(i => (
                  <div key={i} className="aspect-square bg-muted/40 border-primary/10 border" />
                ))}
             </div>
          </CardContent>
          <CardFooter className="relative z-10 border-t bg-muted/5 group-hover:bg-primary transition-colors py-3">
             <span className="text-[10px] font-bold uppercase tracking-widest group-hover:text-primary-foreground">Launch Module</span>
          </CardFooter>
        </Card>

        {/* ANALYZE CARD */}
        <Card className="group relative h-[380px] flex flex-col justify-between overflow-hidden border-white/5 opacity-80 grayscale-[0.5]">
          <div className="absolute top-4 right-4 z-20">
             <Badge className="rounded-none uppercase text-[9px] font-bold px-3">Coming Soon</Badge>
          </div>
          <CardHeader>
            <div className="size-10 bg-white/5 flex items-center justify-center mb-4">
              <BarChart3Icon className="size-5 text-muted-foreground" />
            </div>
            <CardTitle className="text-xl tracking-tight uppercase italic">Analyze</CardTitle>
            <CardDescription className="text-xs">
              Automated tendency visualization and pattern recognition.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex items-end gap-1 px-8 pb-10 opacity-20">
             <div className="w-full h-8 bg-muted" />
             <div className="w-full h-20 bg-muted" />
             <div className="w-full h-12 bg-muted" />
             <div className="w-full h-24 bg-muted" />
          </CardContent>
          <CardFooter className="border-t bg-muted/5 py-3">
             <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Locked</span>
          </CardFooter>
        </Card>

        {/* PLAN CARD */}
        <Card className="group relative h-[380px] flex flex-col justify-between overflow-hidden border-white/5 opacity-80 grayscale-[0.5]">
          <div className="absolute top-4 right-4 z-20">
             <Badge className="rounded-none uppercase text-[9px] font-bold px-3">Coming Soon</Badge>
          </div>
          <CardHeader>
            <div className="size-10 bg-white/5 flex items-center justify-center mb-4">
              <MapPinnedIcon className="size-5 text-muted-foreground" />
            </div>
            <CardTitle className="text-xl tracking-tight uppercase italic">Plan</CardTitle>
            <CardDescription className="text-xs">
              AI-generated strategy playbooks for specific opponents.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex items-center justify-center opacity-20">
             <TargetIcon className="size-24 text-muted-foreground" />
          </CardContent>
          <CardFooter className="border-t bg-muted/5 py-3">
             <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Locked</span>
          </CardFooter>
        </Card>
      </div>

      <section className="border-t border-white/5 pt-12 flex flex-col md:flex-row justify-between gap-8">
         <div className="flex flex-col gap-2">
            <span className="text-[10px] font-bold uppercase tracking-widest text-primary">System Status</span>
            <div className="flex items-center gap-4">
               <div className="flex items-center gap-2">
                  <div className="size-1.5 rounded-full bg-emerald-500" />
                  <span className="text-[11px] font-mono opacity-60">Database: Online</span>
               </div>
               <div className="flex items-center gap-2">
                  <div className="size-1.5 rounded-full bg-emerald-500" />
                  <span className="text-[11px] font-mono opacity-60">Gemini 3 Pro: Ready</span>
               </div>
            </div>
         </div>
         <div className="flex flex-wrap gap-4 items-center">
            <div className="flex flex-col gap-1">
               <span className="text-[9px] font-bold uppercase text-muted-foreground">Scraped Rounds</span>
               <span className="text-lg font-bold font-mono tracking-tighter">12,482</span>
            </div>
            <Separator orientation="vertical" className="h-8 opacity-20" />
            <div className="flex flex-col gap-1">
               <span className="text-[9px] font-bold uppercase text-muted-foreground">VOD Metadata</span>
               <span className="text-lg font-bold font-mono tracking-tighter">100% Precision</span>
            </div>
         </div>
      </section>
    </div>
  )
}
