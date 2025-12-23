import * as React from "react";
import { Card } from "@/components/ui/card";
import { PlayIcon } from "lucide-react";

interface VodPlayerProps {
  timestamp?: number;
  videoId?: string;
}

export function VodPlayer({ timestamp = 0, videoId }: VodPlayerProps) {
  if (!videoId) {
    return (
      <div className="aspect-video bg-black border relative overflow-hidden flex items-center justify-center text-muted-foreground">
        <div className="flex flex-col items-center">
          <PlayIcon className="size-12 mb-2 opacity-20" />
          <p className="text-[10px] font-mono uppercase tracking-widest">Select a round to play VOD</p>
        </div>
      </div>
    );
  }

  // Construct the YouTube embed URL with the timestamp
  // Using start={timestamp} to auto-seek on load
  // and autoplay=1 to start immediately
  const embedUrl = `https://www.youtube.com/embed/${videoId}?start=${timestamp}&autoplay=1`;

  return (
    <div className="flex flex-col gap-2">
      <div className="aspect-video bg-black border relative group overflow-hidden">
         <iframe
            className="w-full h-full"
            src={embedUrl}
            title="YouTube video player"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowFullScreen
         ></iframe>
      </div>
      <div className="flex items-center justify-between px-1">
        <span className="text-[9px] font-mono text-muted-foreground uppercase">Live VOD Playback</span>
        <span className="text-[9px] font-mono text-primary uppercase">Timestamp: {timestamp}s</span>
      </div>
    </div>
  );
}