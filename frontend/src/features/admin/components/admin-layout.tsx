import React from "react";
import { AdminToolbar } from "./admin-toolbar";

interface AdminLayoutProps {
  children: React.ReactNode;
  onRefresh: () => void;
  isRefreshing?: boolean;
}

export function AdminLayout({ children, onRefresh, isRefreshing }: AdminLayoutProps) {
  return (
    <div className="flex flex-col min-h-full">
      <AdminToolbar onRefresh={onRefresh} isRefreshing={isRefreshing} />
      <main className="flex-1 pb-12">
        {children}
      </main>
    </div>
  );
}
