import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authService } from '../api/services';
import CyberCard from '../components/CyberCard';
import NeonButton from '../components/NeonButton';
import GlitchText from '../components/GlitchText';
import { Terminal, Lock, Mail, User as UserIcon } from 'lucide-react';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // 1. Register the user
      await authService.register(formData);
      // 2. Automatically log them in after registration
      const loginData = await authService.login(formData.email, formData.password);
      login(loginData.access_token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. System rejected entity creation.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <Terminal className="mx-auto h-12 w-12 text-cyber-neonPurple" />
          <GlitchText text="ENTITY_CREATION" className="mt-6 text-3xl" />
          <p className="mt-2 text-sm text-cyber-textMuted font-mono">
            Register for a new access token in the nexus.
          </p>
        </div>
        
        <CyberCard glow="purple">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="p-3 border border-cyber-neonPink/50 bg-cyber-neonPink/10 text-cyber-neonPink text-sm rounded font-mono">
                [ERROR]: {error}
              </div>
            )}
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-cyber-textMuted font-mono mb-1">
                  &gt; DESIGNATION (FULL NAME)
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <UserIcon className="h-5 w-5 text-cyber-neonPurple" />
                  </div>
                  <input
                    name="full_name"
                    type="text"
                    required
                    className="block w-full pl-10 pr-3 py-2 border border-cyber-gray bg-cyber-black/50 rounded-md text-cyber-text focus:outline-none focus:ring-1 focus:ring-cyber-neonPurple focus:border-cyber-neonPurple sm:text-sm transition-all"
                    placeholder="John Doe"
                    value={formData.full_name}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-cyber-textMuted font-mono mb-1">
                  &gt; IDENTIFIER (EMAIL)
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-cyber-neonPurple" />
                  </div>
                  <input
                    name="email"
                    type="email"
                    required
                    className="block w-full pl-10 pr-3 py-2 border border-cyber-gray bg-cyber-black/50 rounded-md text-cyber-text focus:outline-none focus:ring-1 focus:ring-cyber-neonPurple focus:border-cyber-neonPurple sm:text-sm transition-all"
                    placeholder="user@nexus.com"
                    value={formData.email}
                    onChange={handleChange}
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-cyber-textMuted font-mono mb-1">
                  &gt; SECURITY_KEY (PASSWORD)
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-cyber-neonPurple" />
                  </div>
                  <input
                    name="password"
                    type="password"
                    required
                    className="block w-full pl-10 pr-3 py-2 border border-cyber-gray bg-cyber-black/50 rounded-md text-cyber-text focus:outline-none focus:ring-1 focus:ring-cyber-neonPurple focus:border-cyber-neonPurple sm:text-sm transition-all"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            <div>
              <NeonButton type="submit" variant="purple" fullWidth disabled={loading}>
                {loading ? 'PROCESSING...' : 'ALLOCATE_ENTITY'}
              </NeonButton>
            </div>
          </form>
          
          <div className="mt-6 text-center font-mono text-xs text-cyber-textMuted">
            Already registered?{' '}
            <Link to="/login" className="text-cyber-neonPurple hover:text-cyber-neonCyan transition-colors">
              Access Nexus
            </Link>
          </div>
        </CyberCard>
      </div>
    </div>
  );
};

export default RegisterPage;
