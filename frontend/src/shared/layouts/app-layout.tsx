import { Navbar } from "@/shared/components/navigation/navbar";
import { Sidebar } from "@/shared/components/navigation/sidebar";

export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <Sidebar />
      <div className="p-4 sm:ml-64 pt-20">
        <main className="mx-auto max-w-7xl">
          {children}
        </main>
      </div>
    </div>
  );
}
