import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authService } from '../api/services';
import CyberCard from '../components/CyberCard';
import NeonButton from '../components/NeonButton';
import GlitchText from '../components/GlitchText';
import { Terminal, Lock, Mail } from 'lucide-react';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await authService.login(email, password);
      login(data.access_token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed. Access denied.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <Terminal className="mx-auto h-12 w-12 text-cyber-neonCyan" />
          <GlitchText text="SYSTEM_LOGIN" className="mt-6 text-3xl" />
          <p className="mt-2 text-sm text-cyber-textMuted font-mono">
            Enter credentials to access the nexus.
          </p>
        </div>
        
        <CyberCard glow="cyan">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="p-3 border border-cyber-neonPink/50 bg-cyber-neonPink/10 text-cyber-neonPink text-sm rounded font-mono">
                [ERROR]: {error}
              </div>
            )}
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-cyber-textMuted font-mono mb-1">
                  &gt; IDENTIFIER (EMAIL)
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-cyber-neonCyan" />
                  </div>
                  <input
                    type="email"
                    required
                    className="block w-full pl-10 pr-3 py-2 border border-cyber-gray bg-cyber-black/50 rounded-md text-cyber-text focus:outline-none focus:ring-1 focus:ring-cyber-neonCyan focus:border-cyber-neonCyan sm:text-sm transition-all"
                    placeholder="user@nexus.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-cyber-textMuted font-mono mb-1">
                  &gt; SECURITY_KEY (PASSWORD)
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-cyber-neonCyan" />
                  </div>
                  <input
                    type="password"
                    required
                    className="block w-full pl-10 pr-3 py-2 border border-cyber-gray bg-cyber-black/50 rounded-md text-cyber-text focus:outline-none focus:ring-1 focus:ring-cyber-neonCyan focus:border-cyber-neonCyan sm:text-sm transition-all"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </div>
            </div>

            <div>
              <NeonButton type="submit" fullWidth disabled={loading}>
                {loading ? 'AUTHENTICATING...' : 'INITIALIZE_SESSION'}
              </NeonButton>
            </div>
          </form>
          
          <div className="mt-6 text-center font-mono text-xs text-cyber-textMuted">
            Unregistered entity?{' '}
            <Link to="/register" className="text-cyber-neonCyan hover:text-cyber-neonPurple transition-colors">
              Request Access
            </Link>
          </div>
        </CyberCard>
      </div>
    </div>
  );
};

export default LoginPage;
