import { Cpu, TrendingUp, Shield, DollarSign, Sparkles, Search, Upload, MonitorUp, MessageCircle } from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { ChartCard } from '../components/ChartCard';
import { QuickAction } from '../components/QuickAction';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';
import { useNavigate } from 'react-router';
import { useState, useEffect } from 'react';
import { apiService, MachineSnapshot } from '../services/api';

const performanceData = [
  { name: 'Atual', value: 42 },
  { name: 'RAM +8GB', value: 58 },
  { name: '+GPU', value: 78 },
  { name: '+CPU', value: 92 },
  { name: '+SSD', value: 95 },
];

export function HomeScreen() {
  const navigate = useNavigate();
  const [machine, setMachine] = useState<MachineSnapshot | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await apiService.getMachineData();
        setMachine(data.machine);
      } catch (error) {
        console.error('Error loading machine data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  if (isLoading) {
    return <LoadingSpinner message="Carregando dados..." />;
  }

  if (!machine) {
    return (
      <div className="p-4 space-y-5 pb-24 flex items-center justify-center min-h-screen">
        <p className="text-muted-foreground">Erro ao carregar dados do sistema.</p>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-5 pb-24">
      <div className="bg-gradient-to-br from-[#0b7a75] to-[#0d9087] rounded-2xl p-5 text-white shadow-lg">
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-sm text-white/80">Seu Setup Atual</p>
            <h2 className="text-xl mt-1 font-mono">{machine.cpu} • {machine.gpu.replace('NVIDIA ', '')}</h2>
          </div>
          <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
            <Cpu className="w-6 h-6" />
          </div>
        </div>
        <div className="flex items-center gap-2 mt-4">
          <div className="flex-1 bg-white/20 rounded-full h-2 overflow-hidden">
            <div
              className="bg-white h-full rounded-full transition-all duration-500"
              style={{ width: `${machine.performance_score}%` }}
            />
          </div>
          <span className="text-sm font-mono">{machine.performance_score}% Performance</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <StatCard
          title="Performance"
          value={`${machine.performance_score}%`}
          change="+35% possível"
          trend="up"
          icon={TrendingUp}
          iconColor="bg-blue-500"
        />
        <StatCard
          title="Compatibilidade"
          value={`${machine.compatibility_score}%`}
          change="Boa"
          trend="up"
          icon={Shield}
          iconColor="bg-green-500"
        />
        <StatCard
          title="Economia"
          value="R$ 450"
          change="vs Novo"
          trend="up"
          icon={DollarSign}
          iconColor="bg-emerald-500"
        />
        <StatCard
          title="Upgrades"
          value="3"
          change="Recomendados"
          trend="up"
          icon={Sparkles}
          iconColor="bg-purple-500"
        />
      </div>

      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-foreground">Ações Rápidas</h2>
        </div>
        <div className="grid grid-cols-4 gap-2">
          <QuickAction
            icon={Search}
            label="Buscar"
            color="bg-blue-500"
            onClick={() => navigate('/marketplace')}
          />
          <QuickAction
            icon={Upload}
            label="Upload"
            color="bg-purple-500"
          />
          <QuickAction
            icon={MonitorUp}
            label="Upgrade"
            color="bg-[#0b7a75]"
            onClick={() => navigate('/route')}
          />
          <QuickAction
            icon={MessageCircle}
            label="Suporte"
            color="bg-orange-500"
          />
        </div>
      </div>

      <ChartCard title="Rota de Performance">
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={performanceData}>
            <defs>
              <linearGradient id="colorPerf" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0b7a75" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#0b7a75" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#dad2c1" opacity={0.5} />
            <XAxis
              dataKey="name"
              stroke="#5a5a5a"
              style={{ fontSize: '11px' }}
              tickLine={false}
            />
            <YAxis
              stroke="#5a5a5a"
              style={{ fontSize: '12px' }}
              tickLine={false}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#0b7a75"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorPerf)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </ChartCard>

      <div className="bg-card rounded-xl border border-border p-5">
        <h3 className="text-foreground mb-3">Componentes do Sistema</h3>
        <div className="space-y-3 font-mono text-sm">
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">CPU</span>
            <span className="text-foreground">{machine.cpu}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">GPU</span>
            <span className="text-foreground">{machine.gpu}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">RAM</span>
            <span className="text-foreground">{machine.ram}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">Placa-Mãe</span>
            <span className="text-foreground">{machine.motherboard}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">Armazenamento</span>
            <span className="text-foreground">{machine.storage}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">Fonte</span>
            <span className="text-foreground">{machine.psu}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
