import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router';
import { SplashScreen } from './screens/SplashScreen';
import { LoginScreen } from './screens/LoginScreen';
import { RegisterScreen } from './screens/RegisterScreen';
import { HomeScreen } from './screens/HomeScreen';
import { DiagnosticsScreen } from './screens/DiagnosticsScreen';
import { RouteScreen } from './screens/RouteScreen';
import { MarketplaceScreen } from './screens/MarketplaceScreen';
import { DetailsScreen } from './screens/DetailsScreen';
import { BottomNav } from './components/BottomNav';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { useState } from 'react';
import { Cpu } from 'lucide-react';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="size-full bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
          <p className="text-muted-foreground">Carregando...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function AppLayout() {
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('home');
  const { user, logout } = useAuth();

  const hideNavRoutes = ['/', '/login', '/register'];
  const showNav = !hideNavRoutes.includes(location.pathname) && !location.pathname.startsWith('/details');

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    const routes: Record<string, string> = {
      home: '/home',
      analytics: '/diagnostics',
      wallet: '/route',
      settings: '/marketplace',
    };
    window.location.hash = routes[tab] || '/home';
  };

  const hideHeaderRoutes = ['/', '/login', '/register'];
  const showHeader = !hideHeaderRoutes.includes(location.pathname) && !location.pathname.startsWith('/details');

  return (
    <div className="size-full bg-background">
      {showHeader && (
        <div className="sticky top-0 bg-background/80 backdrop-blur-sm z-10 border-b border-border">
          <div className="max-w-md mx-auto p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Bem-vindo,</p>
                <h1 className="text-foreground">{user?.username || 'Usuário'}</h1>
              </div>
              <button
                onClick={logout}
                className="p-2 rounded-full hover:bg-accent transition-colors"
              >
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#0b7a75] to-[#0d9087] flex items-center justify-center text-white">
                  <Cpu className="w-5 h-5" />
                </div>
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-md mx-auto">
        <Routes>
          <Route path="/" element={<SplashScreen />} />
          <Route path="/login" element={<LoginScreen />} />
          <Route path="/register" element={<RegisterScreen />} />
          <Route path="/home" element={<ProtectedRoute><HomeScreen /></ProtectedRoute>} />
          <Route path="/diagnostics" element={<ProtectedRoute><DiagnosticsScreen /></ProtectedRoute>} />
          <Route path="/route" element={<ProtectedRoute><RouteScreen /></ProtectedRoute>} />
          <Route path="/marketplace" element={<ProtectedRoute><MarketplaceScreen /></ProtectedRoute>} />
          <Route path="/details/:stepId" element={<ProtectedRoute><DetailsScreen /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>

      {showNav && <BottomNav activeTab={activeTab} onTabChange={handleTabChange} />}
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppLayout />
      </AuthProvider>
    </BrowserRouter>
  );
}