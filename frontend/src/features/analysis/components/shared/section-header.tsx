interface SectionHeaderProps {
  title: string;
}

export function SectionHeader({ title }: SectionHeaderProps) {
  return (
    <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
      {title}
    </h3>
  );
}
