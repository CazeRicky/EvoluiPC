import { LucideIcon } from 'lucide-react';

interface TransactionItemProps {
  icon: LucideIcon;
  title: string;
  date: string;
  amount: string;
  type: 'income' | 'expense';
  iconColor: string;
}

export function TransactionItem({ icon: Icon, title, date, amount, type, iconColor }: TransactionItemProps) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-xl hover:bg-accent transition-colors">
      <div className={`${iconColor} bg-opacity-10 p-2.5 rounded-lg shrink-0`}>
        <Icon className={`${iconColor.replace('bg-', 'text-')} w-5 h-5`} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-foreground truncate">{title}</p>
        <p className="text-sm text-muted-foreground">{date}</p>
      </div>
      <div className={`text-right ${type === 'income' ? 'text-green-500' : 'text-foreground'}`}>
        <p>{type === 'income' ? '+' : '-'}{amount}</p>
      </div>
    </div>
  );
}
