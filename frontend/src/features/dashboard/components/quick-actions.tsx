import {
  FilePlus,
  MessageSquarePlus,
  Upload,
  Zap
} from "lucide-react";
import Link from "next/link";

const actions = [
  {
    title: "New Investigation",
    description: "Start a new legal analysis",
    icon: Zap,
    href: "/chat",
    color: "text-blue-500",
    bg: "bg-blue-500/10"
  },
  {
    title: "Upload Evidence",
    description: "Add documents for analysis",
    icon: Upload,
    href: "/documents",
    color: "text-purple-500",
    bg: "bg-purple-500/10"
  },
  {
    title: "AI Research",
    description: "Search legal knowledge base",
    icon: MessageSquarePlus,
    href: "/chat",
    color: "text-green-500",
    bg: "bg-green-500/10"
  },
  {
    title: "Generate Report",
    description: "Draft case summaries",
    icon: FilePlus,
    href: "/evidence",
    color: "text-orange-500",
    bg: "bg-orange-500/10"
  }
];

export function QuickActions() {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {actions.map((action) => (
        <Link
          key={action.title}
          href={action.href}
          className="group relative flex flex-col items-start rounded-xl border bg-card p-6 shadow-sm transition-all hover:shadow-md hover:-translate-y-1"
        >
          <div className={`rounded-lg p-2 ${action.bg} ${action.color} group-hover:scale-110 transition-transform`}>
            <action.icon className="h-6 w-6" />
          </div>
          <h3 className="mt-4 font-semibold text-foreground">{action.title}</h3>
          <p className="mt-1 text-sm text-muted-foreground">{action.description}</p>
        </Link>
      ))}
    </div>
  );
}
