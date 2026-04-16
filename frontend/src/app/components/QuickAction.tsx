import { LucideIcon } from 'lucide-react';

interface QuickActionProps {
  icon: LucideIcon;
  label: string;
  color: string;
  onClick?: () => void;
}

export function QuickAction({ icon: Icon, label, color, onClick }: QuickActionProps) {
  return (
    <button
      onClick={onClick}
      className="flex flex-col items-center gap-2 p-3 rounded-xl bg-card border border-border hover:bg-accent transition-colors"
    >
      <div className={`${color} bg-opacity-10 p-3 rounded-xl`}>
        <Icon className={`${color.replace('bg-', 'text-')} w-6 h-6`} />
      </div>
      <span className="text-sm text-foreground">{label}</span>
    </button>
  );
}
