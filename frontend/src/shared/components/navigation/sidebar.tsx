"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/core/utils/cn";
import {
  LayoutDashboard,
  FileText,
  MessageSquare,
  Search,
  Settings,
  ShieldCheck
} from "lucide-react";

import { navItems } from "./nav-config";

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r bg-card pt-16 transition-transform sm:translate-x-0 hidden md:block">
      <div className="h-full overflow-y-auto px-4 py-6">
        <div className="space-y-6">
          {navItems.map((section) => (
            <div key={section.title}>
              <h2 className="mb-2 px-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {section.title}
              </h2>
              <ul className="space-y-1">
                {section.items.map((item) => (
                  <li key={item.name}>
                    <Link
                      href={item.comingSoon ? "#" : item.href}
                      className={cn(
                        "flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors group relative",
                        pathname === item.href
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:bg-accent hover:text-foreground",
                        item.comingSoon && "opacity-60 cursor-not-allowed"
                      )}
                    >
                      <item.icon className={cn(
                        "h-4 w-4 mr-3 transition-colors",
                        pathname === item.href ? "text-primary-foreground" : "group-hover:text-foreground"
                      )} />
                      <span>{item.name}</span>
                      {item.comingSoon && (
                        <span className="ml-auto text-[10px] bg-muted px-1.5 py-0.5 rounded text-muted-foreground font-normal">
                          Soon
                        </span>
                      )}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}
