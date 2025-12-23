import * as React from "react";
import { SearchIcon, MicIcon } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ResultCard, MatchResult } from "./result-card";
import { VodPlayer } from "./vod-player";
import axios from "axios";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function FindView() {
  const [searchQuery, setSearchQuery] = React.useState("");
  const [activeVodTimestamp, setActiveVodTimestamp] = React.useState<number>(0);
  const [activeVideoId, setActiveVideoId] = React.useState<string | undefined>(undefined);
  const [results, setResults] = React.useState<MatchResult[]>([]);
  const [isSearching, setIsSearching] = React.useState(false);
  const [discoveryLog, setDiscoveryLog] = React.useState<{type: 'info' | 'error' | 'success', message: string}[]>([]);
  const [detectedIntent, setDetectedIntent] = React.useState<{team?: string, map?: string, round_type?: string} | null>(null);
  
  const [availableEvents, setAvailableEvents] = React.useState<any[]>([]);
  const [selectedEventId, setSelectedEventId] = React.useState<string>("all");

  // Fetch events on mount
  React.useEffect(() => {
    const fetchEvents = async () => {
      const apiBase = import.meta.env.VITE_API_URL || "http://localhost:8000";
      try {
        const resp = await axios.get(`${apiBase}/api/v1/events`, {
            headers: { "X-API-Key": import.meta.env.VITE_BACKEND_API_KEY || "dev_key" }
        });
        setAvailableEvents(resp.data);
        if (resp.data.length > 0) {
            setSelectedEventId(resp.data[0].id); // Default to first event
        }
      } catch (err) {
        console.error("Failed to fetch events:", err);
      }
    };
    fetchEvents();
  }, []);

  const addLog = (message: string, type: 'info' | 'error' | 'success' = 'info') => {
    setDiscoveryLog(prev => [...prev, { message, type }]);
  };

  const extractVideoId = (url?: string) => {
    if (!url) return undefined;
    const match = url.match(/(?:v=|\[0-9A-Za-z_-]{11}).*/);
    return match ? match[1] : undefined;
  };

  const handleSearch = async () => {
    if (!searchQuery) return;
    
    setIsSearching(true);
    setResults([]);
    setDiscoveryLog([]);
    setDetectedIntent(null);
    
    const apiBase = import.meta.env.VITE_API_URL || "http://localhost:8000";
    const eventName = availableEvents.find(e => e.id === selectedEventId)?.name || "Library";
    addLog(`Targeting Library: ${eventName}`);
    
    try {
      addLog("Querying Semantic Index...");
      
      const response = await axios.post(`${apiBase}/api/v1/query`, {
        query_text: searchQuery,
        n_results: 12,
        filters: selectedEventId !== "all" ? { event_id: selectedEventId } : undefined,
        jit_index: false 
      }, {
        headers: { "X-API-Key": import.meta.env.VITE_BACKEND_API_KEY || "dev_key" }
      });

      if (response.data.intent) {
        setDetectedIntent(response.data.intent);
      }

      if (response.data.results && response.data.results.length > 0) {
        addLog(`Retrieved ${response.data.results.length} relevant tactical moments.`, "success");
        
        try {
          const mapped = response.data.results.map((r: any) => {
              const metadata = r.metadata || {};
              const vId = extractVideoId(metadata.vod_url);
              // Calculate similarity percentage for the UI
              const similarity = Math.round((1 - (r.distance || 0)) * 100);
              
              return {
                  id: r.id || Math.random().toString(),
                  team_a: metadata.team_a || "Unknown",
                  team_b: metadata.team_b || "Unknown",
                  score_a: metadata.score_a || 0,
                  score_b: metadata.score_b || 0,
                  map_name: metadata.map_name || "Unknown",
                  round_num: metadata.round_num || 0,
                  winning_team: metadata.winning_team || "",
                  round_type: metadata.round_type || "default",
                  date: metadata.date || "2025",
                  summary: r.document || "No summary available.",
                  vod_timestamp: metadata.vod_timestamp,
                  video_id: vId,
                  tags: ["Champions 2025", `${similarity}% Match`]
              };
          });
          setResults(mapped);
        } catch (mapError) {
          console.error("Mapping results failed:", mapError);
          addLog("Error processing match data.", "error");
        }
      } else {
        addLog("No matches found in Champions 2025 library.", "error");
      }

    } catch (error: any) {
      console.error("FULL SEARCH ERROR:", error);
      if (axios.isAxiosError(error)) {
        console.error("Axios Detail:", error.response?.data);
        const msg = error.response?.data?.detail || error.message || "Search Service Offline.";
        addLog(msg, "error");
      } else {
        addLog("Internal Client Error.", "error");
      }
    } finally {
      setIsSearching(false);
    }
  };

  const handleAnalyze = (id: string) => {
    console.log("Analyze match:", id);
  };

  const handlePlay = (timestamp: number, videoId?: string) => {
    setActiveVodTimestamp(timestamp);
    setActiveVideoId(videoId);
  };

  return (
    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {/* Search Bar Section */}      <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between">
                 <div className="flex items-center gap-3">
                    <h2 className="text-xl font-bold tracking-tighter uppercase italic text-primary">Tactical Library</h2>
                    <Separator orientation="vertical" className="h-4" />
                    <Select value={selectedEventId} onValueChange={setSelectedEventId}>
                      <SelectTrigger className="w-[240px] h-8 bg-muted/20 border-primary/20 text-[11px] font-bold uppercase tracking-wider">
                        <SelectValue placeholder="Select Event" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Global Search (All Events)</SelectItem>
                        {availableEvents.map(event => (
                          <SelectItem key={event.id} value={event.id}>
                            {event.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                 </div>
                 <Badge variant="outline" className="text-[10px] border-primary/30 text-primary uppercase font-mono">
                    {availableEvents.length} Events Indexed
                 </Badge>
              </div>
        <div className="relative group">
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            <SearchIcon className="size-5" />
          </div>
          <Input
            className="h-14 pl-11 pr-24 text-base bg-muted/20 border-2 focus-visible:ring-0 focus-visible:border-primary transition-all rounded-none"
            placeholder="Search Champions 2025 (e.g., 'Sentinels retakes on Sunset')..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
            <Button size="icon" variant="ghost" className="h-8 w-8 hover:text-primary">
              <MicIcon className="size-4" />
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <Button 
              size="sm" 
              className="font-bold tracking-wider"
              onClick={handleSearch}
              disabled={isSearching}
            >
              {isSearching ? "..." : "FIND"}
            </Button>
          </div>
        </div>

        {/* Detected Intent Badges */}
        {detectedIntent && (detectedIntent.team || detectedIntent.map || detectedIntent.round_type) && (
            <div className="flex gap-2 animate-in fade-in slide-in-from-top-1 duration-300">
                {detectedIntent.team && (
                    <Badge className="bg-primary/10 text-primary border-primary/30 uppercase text-[10px] font-mono">
                        Team: {detectedIntent.team}
                    </Badge>
                )}
                {detectedIntent.map && (
                    <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/30 uppercase text-[10px] font-mono">
                        Map: {detectedIntent.map}
                    </Badge>
                )}
                {detectedIntent.round_type && (
                    <Badge className="bg-yellow-500/10 text-yellow-400 border-yellow-500/30 uppercase text-[10px] font-mono">
                        Type: {detectedIntent.round_type}
                    </Badge>
                )}
            </div>
        )}
      </div>

      <div className="grid lg:grid-cols-12 gap-8">
        {/* Results Column */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          <div className="flex items-center justify-between">
            <h3 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
              Tactical Moments {results.length > 0 && `(${results.length})`}
            </h3>
          </div>
          
          <div className="grid sm:grid-cols-1 gap-4">
            {isSearching ? (
              <div className="p-12 flex flex-col items-center justify-center gap-4 border border-dashed rounded-lg bg-muted/10">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <p className="text-sm font-mono text-muted-foreground animate-pulse">Querying Library...</p>
              </div>
            ) : results.length > 0 ? (
              results.map((result) => (
                <ResultCard
                  key={result.id}
                  result={result}
                  onAnalyze={handleAnalyze}
                  onPlay={() => handlePlay(result.vod_timestamp || 0, result.video_id)}
                />
              ))
            ) : (
              <div className="p-20 text-center border border-dashed rounded-lg bg-muted/5">
                <SearchIcon className="mx-auto h-12 w-12 text-muted-foreground/20 mb-4" />
                <h3 className="text-lg font-semibold text-muted-foreground/50">Champions 2025 Library</h3>
                <p className="text-sm text-muted-foreground/40 max-w-xs mx-auto mt-2">
                  Query the entire tournament for specific tactical patterns, executes, or retakes.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Player & Log Column */}
        <div className="lg:col-span-5 border-l pl-8 flex flex-col gap-4 sticky top-4 h-fit">
          <VodPlayer timestamp={activeVodTimestamp} videoId={activeVideoId} />
          
          <Card className="bg-muted/30 border-none rounded-none">
            <CardHeader className="py-3">
              <CardTitle className="text-[10px] uppercase tracking-widest flex items-center justify-between">
                <span>Discovery Log</span>
                <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20 text-[9px]">
                    LIVE
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="text-[10px] flex flex-col gap-2 font-mono pb-3 max-h-[200px] overflow-y-auto">
              {discoveryLog.length === 0 ? (
                <div className="text-muted-foreground italic">Waiting for query...</div>
              ) : (
                discoveryLog.map((log, i) => (
                  <div key={i} className="flex gap-2">
                    <span className={
                      log.type === 'success' ? "text-green-500" : 
                      log.type === 'error' ? "text-red-500" : 
                      "text-primary"
                    }>
                      [{log.type === 'success' ? 'OK' : log.type === 'error' ? 'ERR' : 'INFO'}]
                    </span>
                    {log.message}
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
