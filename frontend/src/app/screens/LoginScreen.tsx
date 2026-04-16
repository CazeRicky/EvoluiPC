import { useState } from 'react';
import { motion } from 'motion/react';
import { Cpu, Mail, Lock, ArrowRight, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router';
import { useAuth } from '../contexts/AuthContext';

export function LoginScreen() {
  const navigate = useNavigate();
  const { login, isLoading: authLoading } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(formData.username, formData.password);
      navigate('/home');
    } catch (error) {
      alert('Erro no login. Verifique suas credenciais.');
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="size-full bg-background overflow-y-auto">
      <div className="max-w-md mx-auto min-h-full flex flex-col">
        <div className="flex-1 flex flex-col justify-center p-6">
          <motion.div
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="text-center mb-8"
          >
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary rounded-2xl mb-4">
              <Cpu className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-foreground mb-2">Bem-vindo de volta</h1>
            <p className="text-muted-foreground">Entre para acessar seu setup</p>
          </motion.div>

          <motion.form
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.1 }}
            onSubmit={handleSubmit}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm mb-2 text-foreground">Usuário ou Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full pl-11 pr-4 py-3 bg-input-background border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-foreground"
                  placeholder="Digite seu usuário"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm mb-2 text-foreground">Senha</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full pl-11 pr-4 py-3 bg-input-background border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-foreground"
                  placeholder="Digite sua senha"
                  required
                />
              </div>
            </div>

            <button
              type="button"
              className="text-sm text-primary hover:underline"
            >
              Esqueceu sua senha?
            </button>

            <button
              type="submit"
              disabled={isLoading || authLoading}
              className="w-full bg-primary text-white py-3 rounded-xl hover:opacity-90 transition-opacity flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Entrando...
                </>
              ) : (
                <>
                  Entrar
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </motion.form>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="mt-6 text-center"
          >
            <p className="text-muted-foreground">
              Não tem uma conta?{' '}
              <button
                onClick={() => navigate('/register')}
                className="text-primary hover:underline"
              >
                Cadastre-se
              </button>
            </p>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
