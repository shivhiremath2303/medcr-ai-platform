"use client";

import { MobileNav } from "./mobile-nav";
import { ThemeToggle } from "@/shared/components/theme/theme-toggle";
import { ShieldAlert, Bell, Search } from "lucide-react";

import { useAuth } from "@/features/auth/hooks/use-auth";

export function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="fixed top-0 z-50 w-full border-b bg-card/80 backdrop-blur-md">
      <div className="px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <MobileNav />
          <Link href="/dashboard" className="flex items-center">
            <ShieldAlert className="h-7 w-7 text-primary mr-2 md:mr-3" />
            <span className="self-center text-lg font-bold sm:text-xl whitespace-nowrap tracking-tight">
              LEGAL AI
            </span>
          </Link>
        </div>

        <div className="hidden md:flex flex-1 max-w-md mx-8">
          <div className="relative w-full">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="search"
              placeholder="Search legal records..."
              className="w-full bg-muted/50 border-none rounded-lg pl-9 pr-4 py-2 text-sm focus:ring-1 focus:ring-ring outline-none"
            />
          </div>
        </div>

        <div className="flex items-center space-x-2 md:space-x-4">
          <button className="p-2 text-muted-foreground hover:text-foreground hidden sm:block">
            <Bell className="h-5 w-5" />
          </button>
          <div className="hidden md:block">
            <ThemeToggle />
          </div>

          <div className="flex items-center gap-3">
             <div className="text-right hidden sm:block">
               <p className="text-sm font-semibold text-foreground leading-none">{user?.full_name}</p>
               <p className="text-xs text-muted-foreground mt-1 capitalize">{user?.role}</p>
             </div>
             <button
               onClick={logout}
               className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold text-xs cursor-pointer hover:opacity-90 transition-opacity"
               title="Click to Logout"
             >
               {user?.username.slice(0, 2).toUpperCase()}
             </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
