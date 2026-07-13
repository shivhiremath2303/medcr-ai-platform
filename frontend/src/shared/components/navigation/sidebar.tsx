"use client";

import { memo } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/core/utils/cn";
import { Command } from "lucide-react";
import { navItems } from "./nav-config";

export const Sidebar = memo(function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      className="fixed left-0 top-0 z-40 h-screen w-64 border-r bg-card pt-16 transition-transform sm:translate-x-0 hidden md:block shadow-sm"
      aria-label="Main Sidebar Navigation"
    >
      <nav className="flex flex-col h-full" aria-label="Sidebar Menu">
        <div className="flex-1 overflow-y-auto px-4 py-6 custom-scrollbar">
          <div className="space-y-6">
            {navItems.map((section) => (
              <section key={section.title} aria-labelledby={`nav-section-${section.title.toLowerCase()}`}>
                <h2
                  id={`nav-section-${section.title.toLowerCase()}`}
                  className="mb-2 px-2 text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/50"
                >
                  {section.title}
                </h2>
                <ul className="space-y-1">
                  {section.items.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                      <li key={item.name}>
                        <Link
                          href={item.comingSoon ? "#" : item.href}
                          aria-current={isActive ? "page" : undefined}
                          aria-disabled={item.comingSoon}
                          className={cn(
                            "flex items-center rounded-lg px-3 py-2.5 text-sm font-bold transition-all group relative",
                            isActive
                              ? "bg-primary text-primary-foreground shadow-md shadow-primary/20"
                              : "text-muted-foreground hover:bg-muted hover:text-foreground",
                            item.comingSoon && "opacity-50 cursor-not-allowed"
                          )}
                        >
                          <item.icon className={cn(
                            "h-4 w-4 mr-3 transition-colors",
                            isActive ? "text-primary-foreground" : "group-hover:text-primary"
                          )} aria-hidden="true" />
                          <span>{item.name}</span>
                          {item.comingSoon && (
                            <span className="ml-auto text-[8px] bg-muted px-1.5 py-0.5 rounded text-muted-foreground font-black uppercase tracking-tighter">
                              Soon
                            </span>
                          )}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </section>
            ))}
          </div>
        </div>

        <div className="p-4 border-t bg-muted/10">
          <button
            className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl border bg-background text-[10px] font-black text-muted-foreground hover:border-primary/50 hover:text-primary transition-all group shadow-sm"
            onClick={() => {
              const event = new KeyboardEvent('keydown', {
                key: 'k',
                ctrlKey: true,
                bubbles: true
              });
              document.dispatchEvent(event);
            }}
            aria-label="Open Command Palette (Ctrl+K)"
          >
            <div className="flex items-center gap-2">
               <Command className="h-3.5 w-3.5" />
               <span className="tracking-widest">COMMAND PALETTE</span>
            </div>
            <div className="flex gap-1">
               <kbd className="px-1.5 py-0.5 rounded-md bg-muted border text-[9px] font-bold shadow-inner">Ctrl</kbd>
               <kbd className="px-1.5 py-0.5 rounded-md bg-muted border text-[9px] font-bold shadow-inner">K</kbd>
            </div>
          </button>
        </div>
      </nav>
    </aside>
  );
});
