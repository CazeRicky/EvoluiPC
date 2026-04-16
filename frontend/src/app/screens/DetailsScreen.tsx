import { ArrowLeft, ExternalLink, CheckCircle2, AlertTriangle, TrendingUp } from 'lucide-react';
import { useNavigate, useParams } from 'react-router';
import { useState, useEffect } from 'react';
import { apiService, UpgradeStep, CatalogItem } from '../services/api';

export function DetailsScreen() {
  const navigate = useNavigate();
  const { stepId } = useParams<{ stepId: string }>();
  const [upgradeRoute, setUpgradeRoute] = useState<UpgradeStep[]>([]);
  const [catalog, setCatalog] = useState<CatalogItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [routeData, catalogData] = await Promise.all([
          apiService.getUpgradeRoute(),
          apiService.getCatalog(),
        ]);
        setUpgradeRoute(routeData.route);
        setCatalog(catalogData.catalog);
      } catch (error) {
        console.error('Error loading details:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const step = upgradeRoute.find(s => s.step === Number(stepId));
  const relatedProducts = catalog.filter(item =>
    item.name.toLowerCase().includes(step?.component.toLowerCase().split(' ')[0] || '')
  );

  if (isLoading) {
    return (
      <div className="p-4 space-y-5 pb-24 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
          <p className="text-muted-foreground">Carregando detalhes...</p>
        </div>
      </div>
    );
  }

  if (!step) {
    return (
      <div className="p-4">
        <p className="text-muted-foreground">Upgrade não encontrado</p>
      </div>
    );
  }

  return (
    <div className="size-full bg-background overflow-y-auto pb-24">
      <div className="sticky top-0 bg-background/80 backdrop-blur-sm z-10 border-b border-border p-4">
        <button
          onClick={() => navigate('/route')}
          className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Voltar</span>
        </button>
      </div>

      <div className="p-4 space-y-5">
        <div className="bg-gradient-to-br from-[#0b7a75] to-[#0d9087] rounded-2xl p-5 text-white">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center font-mono">
              {step.step}
            </div>
            <div>
              <h1 className="text-xl">{step.action}</h1>
              <p className="text-sm text-white/80 font-mono">{step.component}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 mt-4">
            <TrendingUp className="w-5 h-5" />
            <span className="text-lg">{step.impact}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="bg-card border border-border rounded-xl p-4">
            <p className="text-sm text-muted-foreground mb-1">Investimento</p>
            <p className="text-xl font-mono text-foreground">
              R$ {step.estimated_cost.toLocaleString('pt-BR')}
            </p>
          </div>
          <div className="bg-card border border-border rounded-xl p-4">
            <p className="text-sm text-muted-foreground mb-1">Ganho de Performance</p>
            <p className="text-xl font-mono text-primary">
              {step.impact_percentage > 0 ? `+${step.impact_percentage}%` : 'Estabilidade'}
            </p>
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <h2 className="text-foreground mb-4">Por que este upgrade?</h2>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-foreground mb-1">Alto Impacto</h3>
                <p className="text-sm text-muted-foreground">
                  Este componente oferece {step.impact_percentage > 30 ? 'um dos maiores' : 'um bom'} ganhos
                  de performance para o seu sistema.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-foreground mb-1">Compatibilidade Garantida</h3>
                <p className="text-sm text-muted-foreground">
                  100% compatível com seu setup atual sem necessidade de outros upgrades.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-foreground mb-1">Custo-Benefício</h3>
                <p className="text-sm text-muted-foreground">
                  Melhor relação entre investimento e ganho de performance nesta categoria.
                </p>
              </div>
            </div>
          </div>
        </div>

        {step.component.includes('Placa-Mãe') && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-yellow-700 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-yellow-900 mb-1">Atenção</h3>
                <p className="text-sm text-yellow-800">
                  Este upgrade pode requerer atualização de BIOS. Certifique-se de seguir as
                  instruções do fabricante.
                </p>
              </div>
            </div>
          </div>
        )}

        <div>
          <h2 className="text-foreground mb-3">Produtos Recomendados</h2>
          <div className="space-y-3">
            {relatedProducts.map((product) => (
              <div
                key={product.id}
                className="bg-card border border-border rounded-xl p-4"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-foreground mb-1">{product.name}</h3>
                    <p className="text-xs text-muted-foreground">{product.source}</p>
                  </div>
                  <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700 border border-green-200">
                    {product.tag}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xl font-mono text-foreground">
                    R$ {product.price.toLocaleString('pt-BR')}
                  </span>
                  <a
                    href={product.affiliate_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg hover:opacity-90 transition-opacity"
                  >
                    <span className="text-sm">Ver Oferta</span>
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
