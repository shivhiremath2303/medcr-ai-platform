"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X, ShieldAlert } from "lucide-react";
import { cn } from "@/core/utils/cn";
import { navItems } from "./nav-config";
import { ThemeToggle } from "../theme/theme-toggle";
import { useAuth } from "@/features/auth/hooks/use-auth";

export function MobileNav() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <div className="md:hidden">
      <button
        onClick={() => setIsOpen(true)}
        className="p-2 text-muted-foreground hover:text-foreground"
      >
        <Menu className="h-6 w-6" />
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="fixed inset-y-0 left-0 w-3/4 max-w-sm bg-card border-r shadow-xl animate-in slide-in-from-left duration-300">
            <div className="flex items-center justify-between p-4 border-b">
              <Link href="/dashboard" className="flex items-center" onClick={() => setIsOpen(false)}>
                <ShieldAlert className="h-6 w-6 text-primary mr-2" />
                <span className="font-bold text-lg">LEGAL AI</span>
              </Link>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 text-muted-foreground hover:text-foreground"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="overflow-y-auto h-full pb-20 px-4 py-6">
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
                            onClick={() => !item.comingSoon && setIsOpen(false)}
                            className={cn(
                              "flex items-center rounded-lg px-3 py-3 text-base font-medium transition-colors group",
                              pathname === item.href
                                ? "bg-primary text-primary-foreground"
                                : "text-muted-foreground hover:bg-accent",
                              item.comingSoon && "opacity-50 cursor-not-allowed"
                            )}
                          >
                            <item.icon className="h-5 w-5 mr-4" />
                            <span>{item.name}</span>
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            <div className="absolute bottom-0 left-0 w-full p-4 border-t bg-card flex items-center justify-between">
              <ThemeToggle />
              <button
                onClick={() => {
                  setIsOpen(false);
                  logout();
                }}
                className="flex items-center gap-2 hover:bg-accent p-2 rounded-lg transition-colors text-left"
              >
                <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold text-xs">
                  {user?.username.slice(0, 2).toUpperCase()}
                </div>
                <div>
                  <p className="text-sm font-medium">{user?.full_name}</p>
                  <p className="text-xs text-muted-foreground">Sign out</p>
                </div>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
