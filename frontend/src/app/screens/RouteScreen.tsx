import { ArrowRight, TrendingUp, Zap } from 'lucide-react';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { apiService, UpgradeStep } from '../services/api';

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'high':
      return 'bg-red-100 text-red-700 border-red-200';
    case 'medium':
      return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    default:
      return 'bg-blue-100 text-blue-700 border-blue-200';
  }
};

const getPriorityLabel = (priority: string) => {
  switch (priority) {
    case 'high':
      return 'Alta';
    case 'medium':
      return 'Média';
    default:
      return 'Baixa';
  }
};

export function RouteScreen() {
  const navigate = useNavigate();
  const [upgradeRoute, setUpgradeRoute] = useState<UpgradeStep[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await apiService.getUpgradeRoute();
        setUpgradeRoute(data.route);
      } catch (error) {
        console.error('Error loading upgrade route:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const totalCost = upgradeRoute.reduce((sum, step) => sum + step.estimated_cost, 0);

  if (isLoading) {
    return <LoadingSpinner message="Carregando rota de upgrade..." />;
  }

  return (
    <div className="p-4 space-y-5 pb-24">
      <div>
        <h1 className="text-foreground mb-2">Rota de Upgrade</h1>
        <p className="text-muted-foreground">Caminho otimizado para melhor performance</p>
      </div>

      <div className="bg-gradient-to-br from-[#0b7a75] to-[#0d9087] rounded-2xl p-5 text-white">
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-sm text-white/80">Investimento Total</p>
            <h2 className="text-2xl mt-1 font-mono">R$ {totalCost.toLocaleString('pt-BR')}</h2>
          </div>
          <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
            <TrendingUp className="w-6 h-6" />
          </div>
        </div>
        <p className="text-sm text-white/80">
          Seguindo esta rota, você pode alcançar até <span className="font-bold">+95%</span> de performance
        </p>
      </div>

      <div className="space-y-3">
        {upgradeRoute.map((step, index) => (
          <div
            key={step.step}
            className="bg-card border border-border rounded-xl p-4 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => navigate(`/details/${step.step}`)}
          >
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-primary rounded-full flex items-center justify-center text-white font-mono">
                {step.step}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <h3 className="text-foreground mb-1">{step.action}</h3>
                    <p className="text-sm text-primary font-mono">{step.component}</p>
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded-full border ${getPriorityColor(step.priority)} flex-shrink-0`}
                  >
                    {getPriorityLabel(step.priority)}
                  </span>
                </div>

                <div className="flex items-center gap-4 text-sm mb-3">
                  <div className="flex items-center gap-1 text-muted-foreground">
                    <Zap className="w-4 h-4 text-primary" />
                    <span>{step.impact}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-lg font-mono text-foreground">
                    R$ {step.estimated_cost.toLocaleString('pt-BR')}
                  </span>
                  <button className="flex items-center gap-1 text-primary hover:gap-2 transition-all">
                    <span className="text-sm">Ver Detalhes</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {index < upgradeRoute.length - 1 && (
              <div className="ml-5 mt-3 mb-0 h-8 border-l-2 border-dashed border-border" />
            )}
          </div>
        ))}
      </div>

      <div className="bg-card border border-border rounded-xl p-5">
        <h3 className="text-foreground mb-3">Sobre a Rota</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Esta rota foi calculada com base em análise de compatibilidade, gargalos identificados e
          melhor custo-benefício. Os upgrades estão ordenados por impacto e prioridade.
        </p>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Total de etapas:</span>
            <span className="text-foreground font-mono">{upgradeRoute.length}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Ganho estimado:</span>
            <span className="text-foreground font-mono">+95% Performance</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Prioridades altas:</span>
            <span className="text-foreground font-mono">
              {upgradeRoute.filter(s => s.priority === 'high').length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
