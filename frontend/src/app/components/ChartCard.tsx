import { ReactNode } from 'react';

interface ChartCardProps {
  title: string;
  children: ReactNode;
}

export function ChartCard({ title, children }: ChartCardProps) {
  return (
    <div className="bg-card rounded-xl p-4 shadow-sm border border-border">
      <h3 className="text-foreground mb-4">{title}</h3>
      {children}
    </div>
  );
}
