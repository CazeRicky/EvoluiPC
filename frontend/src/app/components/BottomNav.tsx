import { Home, Activity, Route, ShoppingBag } from 'lucide-react';

interface BottomNavProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export function BottomNav({ activeTab, onTabChange }: BottomNavProps) {
  const tabs = [
    { id: 'home', icon: Home, label: 'Home' },
    { id: 'analytics', icon: Activity, label: 'Diagnóstico' },
    { id: 'wallet', icon: Route, label: 'Rota' },
    { id: 'settings', icon: ShoppingBag, label: 'Loja' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-card border-t border-border z-20">
      <nav className="flex items-center justify-around px-2 py-3 max-w-md mx-auto">
        {tabs.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => onTabChange(id)}
            className={`flex flex-col items-center gap-1 px-4 py-1 rounded-lg transition-colors ${
              activeTab === id
                ? 'text-primary'
                : 'text-muted-foreground'
            }`}
          >
            <Icon className="w-6 h-6" />
            <span className="text-xs">{label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}
