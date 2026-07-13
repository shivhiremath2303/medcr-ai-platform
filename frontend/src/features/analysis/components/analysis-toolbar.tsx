import { cn } from "@/core/utils/cn";
import { Clock, Copy, AlertTriangle, Download, Share2 } from "lucide-react";

interface AnalysisToolbarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export function AnalysisToolbar({ activeTab, onTabChange }: AnalysisToolbarProps) {
  const tabs = [
    { id: "timeline", label: "Timeline", icon: Clock },
    { id: "comparison", label: "Clause Comparison", icon: Copy },
    { id: "conflicts", label: "Conflict Viewer", icon: AlertTriangle },
  ];

  return (
    <div className="flex items-center justify-between px-4 py-2 border-b bg-card">
      <div className="flex space-x-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors",
              activeTab === tab.id
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            )}
          >
            <tab.icon className="w-4 h-4 mr-2" />
            {tab.label}
          </button>
        ))}
      </div>

      <div className="flex items-center space-x-2">
        <button className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-md transition-colors">
          <Share2 className="w-4 h-4" />
        </button>
        <button className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-md transition-colors">
          <Download className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
