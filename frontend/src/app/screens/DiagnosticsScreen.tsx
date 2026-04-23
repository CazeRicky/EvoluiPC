import { AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { ChartCard } from '../components/ChartCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';
import { useState, useEffect } from 'react';
import { apiService, Diagnostic } from '../services/api';

const compatibilityData = [
  { name: 'CPU', value: 85 },
  { name: 'GPU', value: 92 },
  { name: 'RAM', value: 100 },
  { name: 'Mobo', value: 78 },
  { name: 'PSU', value: 88 },
  { name: 'Cooler', value: 95 },
];

const getSeverityIcon = (severity: string) => {
  switch (severity) {
    case 'critical':
      return <AlertCircle className="w-5 h-5 text-red-500" />;
    case 'warning':
      return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    default:
      return <Info className="w-5 h-5 text-blue-500" />;
  }
};

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'critical':
      return 'bg-red-50 border-red-200';
    case 'warning':
      return 'bg-yellow-50 border-yellow-200';
    default:
      return 'bg-blue-50 border-blue-200';
  }
};

export function DiagnosticsScreen() {
  const [diagnostics, setDiagnostics] = useState<Diagnostic[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await apiService.getMachineData();
        setDiagnostics(data.diagnostics);
      } catch (error) {
        console.error('Error loading diagnostics:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  if (isLoading) {
    return <LoadingSpinner message="Carregando diagnósticos..." />;
  }

  return (
    <div className="p-4 space-y-5 pb-24">
      <div>
        <h1 className="text-foreground mb-2">Diagnóstico do Sistema</h1>
        <p className="text-muted-foreground">Análise detalhada do seu hardware</p>
      </div>

      <ChartCard title="Compatibilidade de Componentes">
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={compatibilityData}>
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
            <Bar dataKey="value" fill="#0b7a75" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <div>
        <h2 className="text-foreground mb-3">Análises Detectadas</h2>
        <div className="space-y-3">
          {diagnostics.map((diagnostic) => (
            <div
              key={diagnostic.id}
              className={`p-4 rounded-xl border ${getSeverityColor(diagnostic.severity)}`}
            >
              <div className="flex items-start gap-3">
                <div className="mt-0.5">{getSeverityIcon(diagnostic.severity)}</div>
                <div className="flex-1">
                  <h3 className="text-foreground mb-1 capitalize">{diagnostic.component}</h3>
                  <p className="text-sm text-muted-foreground">{diagnostic.message}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gradient-to-br from-[#0b7a75] to-[#0d9087] rounded-2xl p-5 text-white">
        <h3 className="mb-2">Resumo Geral</h3>
        <p className="text-sm text-white/80 mb-4">
          Seu sistema apresenta {diagnostics.filter(d => d.severity === 'critical').length} problema
          {diagnostics.filter(d => d.severity === 'critical').length !== 1 ? 's' : ''} crítico
          {diagnostics.filter(d => d.severity === 'critical').length !== 1 ? 's' : ''} e{' '}
          {diagnostics.filter(d => d.severity === 'warning').length} aviso
          {diagnostics.filter(d => d.severity === 'warning').length !== 1 ? 's' : ''}.
        </p>
        <button className="w-full bg-white text-[#0b7a75] py-3 rounded-xl hover:bg-white/90 transition-colors">
          Ver Soluções Recomendadas
        </button>
      </div>
    </div>
  );
}
