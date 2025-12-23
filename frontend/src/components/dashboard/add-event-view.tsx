import * as React from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PlusCircle, Globe, Terminal, Loader2 } from "lucide-react";
import axios from "axios";

export function AddEventView() {
  const [url, setUrl] = React.useState("");
  const [isIngesting, setIsIngesting] = React.useState(false);
  const [status, setStatus] = React.useState<{message: string, type: 'success' | 'error' | 'info'} | null>(null);

  const handleIngest = async () => {
    if (!url.includes("rib.gg/events")) {
      setStatus({ message: "Invalid rib.gg event URL.", type: "error" });
      return;
    }

    setIsIngesting(true);
    setStatus({ message: "Crawling and Indexing tournament... this may take several minutes.", type: "info" });

    const apiBase = import.meta.env.VITE_API_URL || "http://localhost:8000";
    try {
      const response = await axios.post(`${apiBase}/api/v1/admin/ingest-event`, {
        event_url: url
      }, {
        headers: { "X-API-Key": import.meta.env.VITE_BACKEND_API_KEY || "dev_key" }
      });

      setStatus({ message: response.data.message, type: "success" });
      setUrl("");
    } catch (error: any) {
      console.error("Ingestion failed:", error);
      setStatus({ 
        message: error.response?.data?.detail || "Ingestion failed. Check backend logs.", 
        type: "error" 
      });
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex flex-col gap-1">
        <h2 className="text-2xl font-bold tracking-tighter uppercase italic">Event Management</h2>
        <p className="text-muted-foreground text-sm">Add new tournaments to the global tactical library.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <Card className="border-2 border-primary/20">
          <CardHeader>
            <CardTitle className="text-sm font-bold uppercase tracking-widest flex items-center gap-2">
              <PlusCircle className="size-4 text-primary" />
              New Ingestion
            </CardTitle>
            <CardDescription>Enter a rib.gg event URL to start the bulk crawler.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Input
                placeholder="https://www.rib.gg/events/..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isIngesting}
                className="font-mono text-xs h-10"
              />
            </div>
            <Button 
              className="w-full font-bold tracking-wider" 
              onClick={handleIngest}
              disabled={isIngesting || !url}
            >
              {isIngesting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  PROCESSING...
                </>
              ) : "START BULK INGESTION"}
            </Button>

            {status && (
              <div className={`p-3 rounded border text-[11px] font-mono ${
                status.type === 'success' ? 'bg-green-500/10 border-green-500/30 text-green-400' :
                status.type === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-400' :
                'bg-primary/10 border-primary/30 text-primary animate-pulse'
              }`}>
                [{status.type.toUpperCase()}] {status.message}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="bg-muted/20 border-dashed">
          <CardHeader>
            <CardTitle className="text-sm font-bold uppercase tracking-widest flex items-center gap-2">
              <Terminal className="size-4 text-muted-foreground" />
              Ingestion Protocol
            </CardTitle>
          </CardHeader>
          <CardContent className="text-[11px] space-y-3 text-muted-foreground leading-relaxed">
            <div className="flex gap-2">
              <Badge variant="outline" className="h-4 px-1 text-[8px]">STEP 1</Badge>
              <span>Crawler identifies all unique Series IDs in the event.</span>
            </div>
            <div className="flex gap-2">
              <Badge variant="outline" className="h-4 px-1 text-[8px]">STEP 2</Badge>
              <span>Playwright extracts raw Match Data and VOD links.</span>
            </div>
            <div className="flex gap-2">
              <Badge variant="outline" className="h-4 px-1 text-[8px]">STEP 3</Badge>
              <span>Gemini generates semantic tactical vectors for every round.</span>
            </div>
            <div className="pt-4 border-t border-primary/10">
              <p className="italic text-[10px]">Note: Bulk ingestion is idempotent. Duplicate matches will be ignored automatically.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
