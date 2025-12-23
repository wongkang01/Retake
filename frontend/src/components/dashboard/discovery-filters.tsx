import * as React from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { VCT_REGIONS, VCT_TEAMS, VALORANT_MAPS } from "@/lib/constants";
import { X } from "lucide-react";

interface DiscoveryFiltersProps {
  onFilterChange: (filters: FilterState) => void;
}

export interface FilterState {
  region: string | null;
  team: string | null;
  map: string | null;
  timeframe: string | null;
}

export function DiscoveryFilters({ onFilterChange }: DiscoveryFiltersProps) {
  const [filters, setFilters] = React.useState<FilterState>({
    region: null,
    team: null,
    map: null,
    timeframe: null,
  });

  const handleFilterChange = (key: keyof FilterState, value: string | null) => {
    const newFilters = { ...filters, [key]: value === "all" ? null : value };
    
    // Reset team if region changes
    if (key === "region") {
        newFilters.team = null;
    }
    
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const clearFilters = () => {
    const emptyFilters = { region: null, team: null, map: null, timeframe: null };
    setFilters(emptyFilters);
    onFilterChange(emptyFilters);
  };

  // Derived state for teams based on selected region
  const availableTeams = filters.region 
    ? VCT_TEAMS[filters.region as keyof typeof VCT_TEAMS] || []
    : Object.values(VCT_TEAMS).flat().sort();

  return (
    <div className="flex flex-col gap-4 p-4 border rounded-lg bg-card/50">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-sm text-muted-foreground">Filters</h3>
        {(filters.region || filters.team || filters.map || filters.timeframe) && (
             <Button variant="ghost" size="sm" onClick={clearFilters} className="h-8 px-2 lg:px-3">
                <span className="text-xs">Reset</span>
                <X className="ml-2 h-4 w-4" />
             </Button>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Region Filter */}
        <div className="space-y-2">
          <Label className="text-xs">Region</Label>
          <Select
            value={filters.region || "all"}
            onValueChange={(val) => handleFilterChange("region", val)}
          >
            <SelectTrigger>
              <SelectValue placeholder="All Regions" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Regions</SelectItem>
              {VCT_REGIONS.map((region) => (
                <SelectItem key={region.id} value={region.id}>
                  {region.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Team Filter */}
        <div className="space-y-2">
          <Label className="text-xs">Team</Label>
          <Select
            value={filters.team || "all"}
            onValueChange={(val) => handleFilterChange("team", val)}
            disabled={availableTeams.length === 0}
          >
            <SelectTrigger>
              <SelectValue placeholder="All Teams" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Teams</SelectItem>
              {availableTeams.map((team) => (
                <SelectItem key={team} value={team}>
                  {team}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Map Filter */}
        <div className="space-y-2">
          <Label className="text-xs">Map</Label>
          <Select
            value={filters.map || "all"}
            onValueChange={(val) => handleFilterChange("map", val)}
          >
            <SelectTrigger>
              <SelectValue placeholder="All Maps" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Maps</SelectItem>
              {VALORANT_MAPS.map((map) => (
                <SelectItem key={map} value={map}>
                  {map}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Timeframe Filter */}
        <div className="space-y-2">
          <Label className="text-xs">Timeframe</Label>
          <Select
            value={filters.timeframe || "all"}
            onValueChange={(val) => handleFilterChange("timeframe", val)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Any Time" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Any Time</SelectItem>
              <SelectItem value="7d">Last 7 Days</SelectItem>
              <SelectItem value="30d">Last 30 Days</SelectItem>
              <SelectItem value="3m">Last 3 Months</SelectItem>
              <SelectItem value="ytd">Year to Date</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}
