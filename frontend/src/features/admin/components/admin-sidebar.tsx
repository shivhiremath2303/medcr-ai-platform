import { Settings, Shield, Activity, Database, Lock, Terminal } from "lucide-react";
import { cn } from "@/core/utils/cn";

export function AdminSidebar() {
  const links = [
    { name: "System Dashboard", icon: Activity, active: true },
    { name: "User Management", icon: Shield, planned: true },
    { name: "Storage & Indices", icon: Database, planned: true },
    { name: "Security Policies", icon: Lock, planned: true },
    { name: "Audit Logs", icon: Terminal, planned: true },
    { name: "System Settings", icon: Settings, planned: true },
  ];

  return (
    <aside className="w-64 border-r bg-card hidden xl:flex flex-col">
      <div className="p-4 border-b">
        <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Admin Workspace</h3>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {links.map((link) => (
          <button
            key={link.name}
            disabled={link.planned}
            className={cn(
              "w-full flex items-center justify-between px-3 py-2 text-sm font-medium rounded-md transition-colors",
              link.active
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
              link.planned && "opacity-50 cursor-not-allowed"
            )}
          >
            <div className="flex items-center gap-3">
              <link.icon className="h-4 w-4" />
              <span>{link.name}</span>
            </div>
            {link.planned && (
               <span className="text-[9px] bg-muted px-1 rounded font-bold uppercase">PLANNED</span>
            )}
          </button>
        ))}
      </nav>
      <div className="p-4 border-t bg-muted/10">
          <div className="text-[10px] text-muted-foreground leading-relaxed uppercase font-bold text-center">
            Enterprise Admin v1.0
          </div>
      </div>
    </aside>
  );
}
