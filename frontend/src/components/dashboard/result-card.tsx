import * as React from "react";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PlayCircle, PlusCircle } from "lucide-react";

export interface MatchResult {
  id: string;
  team_a: string;
  team_b: string;
  score_a: number;
  score_b: number;
  map_name: string;
  round_num: number;
  winning_team: string;
  round_type: string;
  date: string;
  summary: string;
  vod_timestamp?: number;
  video_id?: string;
  tags: string[];
}

interface ResultCardProps {
  result: MatchResult;
  onAnalyze: (id: string) => void;
  onPlay: (timestamp: number, videoId?: string) => void;
}

export function ResultCard({ result, onAnalyze, onPlay }: ResultCardProps) {
  return (
    <Card className="overflow-hidden hover:border-primary/50 transition-colors">
      <CardHeader className="p-4 pb-2 flex flex-row items-center justify-between space-y-0">
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs uppercase font-bold tracking-wider">
            {result.map_name}
          </Badge>
          <Badge variant="secondary" className="text-[10px] uppercase h-5 px-1 bg-primary/20 text-primary border-primary/20">
            R{result.round_num} • {result.round_type}
          </Badge>
          <span className="text-xs text-muted-foreground">{result.date}</span>
        </div>
      </CardHeader>
      
      <CardContent className="p-4 pt-2 space-y-3">
        {/* Teams and Score */}
        <div className="flex items-center justify-between font-mono">
          <div className="flex flex-col">
            <span className={result.team_a === result.winning_team ? "text-primary font-bold" : "text-muted-foreground"}>
              {result.team_a}
            </span>
            <span className="text-2xl font-bold">{result.score_a}</span>
          </div>
          <div className="text-muted-foreground text-sm">VS</div>
          <div className="flex flex-col items-end">
            <span className={result.team_b === result.winning_team ? "text-primary font-bold" : "text-muted-foreground"}>
              {result.team_b}
            </span>
            <span className="text-2xl font-bold">{result.score_b}</span>
          </div>
        </div>

        {/* Semantic Snippet */}
        <div className="bg-muted/50 p-3 rounded-md">
            <p className="text-sm italic text-muted-foreground line-clamp-2">
                "{result.summary}"
            </p>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1">
            {result.tags.map(tag => (
                <Badge key={tag} variant="secondary" className="text-[10px] px-1 h-5">
                    {tag}
                </Badge>
            ))}
        </div>
      </CardContent>

      <CardFooter className="p-3 bg-muted/20 flex gap-2">
        <Button 
            className="flex-1" 
            size="sm" 
            variant="default"
            onClick={() => onPlay(result.vod_timestamp || 0, result.video_id)}
        >
            <PlayCircle className="mr-2 h-4 w-4" />
            Watch VOD
        </Button>
        <Button 
            className="flex-1" 
            size="sm" 
            variant="outline"
            onClick={() => onAnalyze(result.id)}
        >
            <PlusCircle className="mr-2 h-4 w-4" />
            Analyze
        </Button>
      </CardFooter>
    </Card>
  );
}
