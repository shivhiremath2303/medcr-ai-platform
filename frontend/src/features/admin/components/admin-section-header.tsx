import React from "react";

interface AdminSectionHeaderProps {
  title: string;
  description?: string;
  rightElement?: React.ReactNode;
}

export function AdminSectionHeader({ title, description, rightElement }: AdminSectionHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-foreground">{title}</h2>
        {description && (
          <p className="text-sm text-muted-foreground mt-1">{description}</p>
        )}
      </div>
      {rightElement && <div>{rightElement}</div>}
    </div>
  );
}
