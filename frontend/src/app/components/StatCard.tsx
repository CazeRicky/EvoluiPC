import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down';
  icon: LucideIcon;
  iconColor: string;
}

export function StatCard({ title, value, change, trend, icon: Icon, iconColor }: StatCardProps) {
  return (
    <div className="bg-card rounded-xl p-4 shadow-sm border border-border">
      <div className="flex items-start justify-between mb-3">
        <div className={`${iconColor} bg-opacity-10 p-2.5 rounded-lg`}>
          <Icon className={`${iconColor.replace('bg-', 'text-')} w-5 h-5`} />
        </div>
      </div>
      <h3 className="text-muted-foreground mb-1">{title}</h3>
      <div className="flex items-end justify-between">
        <p className="text-3xl text-foreground">{value}</p>
        <div className={`flex items-center gap-1 ${trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>
          <span className="text-sm">{change}</span>
        </div>
      </div>
    </div>
  );
}
