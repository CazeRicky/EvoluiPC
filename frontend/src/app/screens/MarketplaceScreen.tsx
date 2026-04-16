import { ExternalLink, Cpu, HardDrive, Zap, Filter } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { apiService, CatalogItem } from '../services/api';

const getComponentIcon = (type: string) => {
  switch (type) {
    case 'cpu':
    case 'gpu':
      return <Cpu className="w-5 h-5" />;
    case 'ram':
    case 'storage':
      return <HardDrive className="w-5 h-5" />;
    case 'psu':
      return <Zap className="w-5 h-5" />;
    default:
      return <Cpu className="w-5 h-5" />;
  }
};

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    cpu: 'Processador',
    gpu: 'Placa de Vídeo',
    ram: 'Memória RAM',
    storage: 'Armazenamento',
    psu: 'Fonte',
    motherboard: 'Placa-Mãe',
  };
  return labels[type] || type;
};

export function MarketplaceScreen() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<string>('all');
  const [catalog, setCatalog] = useState<CatalogItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await apiService.getCatalog();
        setCatalog(data.catalog);
      } catch (error) {
        console.error('Error loading catalog:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const filteredCatalog = filter === 'all'
    ? catalog
    : catalog.filter(item => item.type === filter);

  if (isLoading) {
    return (
      <div className="p-4 space-y-5 pb-24 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
          <p className="text-muted-foreground">Carregando marketplace...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-5 pb-24">
      <div>
        <h1 className="text-foreground mb-2">Marketplace</h1>
        <p className="text-muted-foreground">Melhores ofertas de hardware compatível</p>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-xl flex-shrink-0 transition-colors ${
            filter === 'all'
              ? 'bg-primary text-white'
              : 'bg-card border border-border text-foreground'
          }`}
        >
          Todos
        </button>
        <button
          onClick={() => setFilter('gpu')}
          className={`px-4 py-2 rounded-xl flex-shrink-0 transition-colors ${
            filter === 'gpu'
              ? 'bg-primary text-white'
              : 'bg-card border border-border text-foreground'
          }`}
        >
          GPU
        </button>
        <button
          onClick={() => setFilter('cpu')}
          className={`px-4 py-2 rounded-xl flex-shrink-0 transition-colors ${
            filter === 'cpu'
              ? 'bg-primary text-white'
              : 'bg-card border border-border text-foreground'
          }`}
        >
          CPU
        </button>
        <button
          onClick={() => setFilter('ram')}
          className={`px-4 py-2 rounded-xl flex-shrink-0 transition-colors ${
            filter === 'ram'
              ? 'bg-primary text-white'
              : 'bg-card border border-border text-foreground'
          }`}
        >
          RAM
        </button>
        <button
          onClick={() => setFilter('storage')}
          className={`px-4 py-2 rounded-xl flex-shrink-0 transition-colors ${
            filter === 'storage'
              ? 'bg-primary text-white'
              : 'bg-card border border-border text-foreground'
          }`}
        >
          Storage
        </button>
      </div>

      <div className="space-y-3">
        {filteredCatalog.map((item) => (
          <div
            key={item.id}
            className="bg-card border border-border rounded-xl p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary">
                {getComponentIcon(item.type)}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <h3 className="text-foreground mb-1">{item.name}</h3>
                    <p className="text-xs text-muted-foreground">{getTypeLabel(item.type)}</p>
                  </div>
                  <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700 border border-green-200 flex-shrink-0">
                    {item.tag}
                  </span>
                </div>

                <div className="flex items-center gap-4 text-sm mb-3">
                  <div className="flex items-center gap-1">
                    <span className="text-muted-foreground">Compatibilidade:</span>
                    <span className="text-foreground font-mono">{item.compatibility}%</span>
                  </div>
                  {item.performance_gain > 0 && (
                    <div className="flex items-center gap-1">
                      <span className="text-muted-foreground">Ganho:</span>
                      <span className="text-primary font-mono">+{item.performance_gain}%</span>
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-2xl font-mono text-foreground">
                      R$ {item.price.toLocaleString('pt-BR')}
                    </span>
                    <p className="text-xs text-muted-foreground mt-1">{item.source}</p>
                  </div>
                  <a
                    href={item.affiliate_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg hover:opacity-90 transition-opacity"
                  >
                    <span className="text-sm">Ver na Loja</span>
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredCatalog.length === 0 && (
        <div className="text-center py-12">
          <Filter className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
          <p className="text-muted-foreground">Nenhum produto encontrado nesta categoria</p>
        </div>
      )}
    </div>
  );
}
