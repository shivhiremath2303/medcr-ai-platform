import {
  LayoutDashboard,
  FileText,
  MessageSquare,
  Search,
  Scale,
  Settings,
  ShieldCheck,
  FileSearch,
  BookOpen
} from "lucide-react";

export const navItems = [
  {
    title: "Main",
    items: [
      { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
      { name: "Documents", href: "/documents", icon: FileText },
      { name: "Legal Chat", href: "/chat", icon: MessageSquare },
    ]
  },
  {
    title: "Analysis",
    items: [
      { name: "Evidence Explorer", href: "/evidence", icon: Search },
      { name: "Legal Analysis", href: "/analysis", icon: Scale },
      { name: "Citation Engine", href: "/citations", icon: BookOpen, comingSoon: true },
    ]
  },
  {
    title: "System",
    items: [
      { name: "Administration", href: "/admin", icon: ShieldCheck },
      { name: "Settings", href: "/settings", icon: Settings },
    ]
  }
];
