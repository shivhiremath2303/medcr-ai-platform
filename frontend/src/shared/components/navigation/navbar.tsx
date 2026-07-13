"use client";

import Link from "next/link";
import { MobileNav } from "./mobile-nav";
import { ThemeToggle } from "@/shared/components/theme/theme-toggle";
import { ShieldAlert, Bell, Search, Settings, Command } from "lucide-react";
import { useAuth } from "@/features/auth/hooks/use-auth";
import { cn } from "@/core/utils/cn";

export function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="fixed top-0 z-50 w-full border-b bg-card/80 backdrop-blur-md shadow-sm">
      <div className="px-4 h-16 flex items-center justify-between max-w-[1600px] mx-auto">
        <div className="flex items-center gap-4">
          <MobileNav />
          <Link href="/dashboard" className="flex items-center group">
            <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center mr-2 md:mr-3 transition-transform group-hover:scale-105">
              <ShieldAlert className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="self-center text-lg font-black sm:text-xl whitespace-nowrap tracking-tighter uppercase">
              MedCr <span className="text-primary">AI</span>
            </span>
          </Link>
        </div>

        {/* Global Search Trigger (Ctrl+K) */}
        <div className="hidden md:flex flex-1 max-w-xl mx-12">
          <button
            className="w-full flex items-center justify-between px-4 py-2 bg-muted/50 hover:bg-muted border border-transparent hover:border-primary/20 rounded-xl transition-all group outline-none"
            onClick={() => {
              // Trigger command palette
              const event = new KeyboardEvent('keydown', {
                key: 'k',
                ctrlKey: true,
                bubbles: true
              });
              document.dispatchEvent(event);
            }}
          >
            <div className="flex items-center gap-3">
              <Search className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
              <span className="text-sm font-medium text-muted-foreground group-hover:text-foreground">Global Search & Actions...</span>
            </div>
            <div className="flex items-center gap-1.5 opacity-60">
               <div className="flex gap-0.5">
                  <kbd className="px-1.5 py-0.5 rounded bg-card border text-[10px] font-bold">Ctrl</kbd>
                  <kbd className="px-1.5 py-0.5 rounded bg-card border text-[10px] font-bold">K</kbd>
               </div>
            </div>
          </button>
        </div>

        <div className="flex items-center space-x-1 md:space-x-3">
          <div className="hidden lg:flex items-center mr-2">
            <div className="h-2 w-2 rounded-full bg-green-500 mr-2 animate-pulse" />
            <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Production Engine</span>
          </div>

          <button className="p-2 text-muted-foreground hover:text-primary hover:bg-muted rounded-lg transition-all hidden sm:block relative">
            <Bell className="h-5 w-5" />
            <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-primary border-2 border-card" />
          </button>

          <Link href="/settings" className="p-2 text-muted-foreground hover:text-primary hover:bg-muted rounded-lg transition-all hidden sm:block">
            <Settings className="h-5 w-5" />
          </Link>

          <div className="h-6 w-px bg-border mx-1 hidden sm:block" />

          <div className="hidden md:block">
            <ThemeToggle />
          </div>

          <div className="flex items-center gap-3 pl-2">
             <div className="text-right hidden xl:block">
               <p className="text-[11px] font-bold text-foreground leading-none">{user?.full_name}</p>
               <p className="text-[9px] text-muted-foreground mt-1 uppercase tracking-widest">{user?.role}</p>
             </div>
             <button
               onClick={logout}
               className="h-9 w-9 rounded-xl bg-primary shadow-sm shadow-primary/20 flex items-center justify-center text-primary-foreground font-black text-sm cursor-pointer hover:scale-105 active:scale-95 transition-all"
               title="Sign Out"
             >
               {user?.username.slice(0, 2).toUpperCase()}
             </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
