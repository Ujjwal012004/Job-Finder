import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Terminal, LogOut, User as UserIcon, LayoutDashboard, Search } from 'lucide-react';
import GlitchText from './GlitchText';

const Layout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 border-b border-cyber-gray bg-cyber-black/80 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Link to="/" className="flex items-center gap-2 group">
              <Terminal className="text-cyber-neonCyan group-hover:text-cyber-neonPurple transition-colors" />
              <GlitchText text="NEXUS_JOBS" className="text-xl" as="span" />
            </Link>

            <div className="flex items-center gap-6">
              <Link to="/search" className="text-cyber-textMuted hover:text-cyber-neonCyan transition-colors flex items-center gap-1">
                <Search size={18} /> <span className="hidden sm:inline">Search</span>
              </Link>
              
              {user ? (
                <>
                  <Link to="/dashboard" className="text-cyber-textMuted hover:text-cyber-neonPurple transition-colors flex items-center gap-1">
                    <LayoutDashboard size={18} /> <span className="hidden sm:inline">Dashboard</span>
                  </Link>
                  <div className="h-6 w-px bg-cyber-gray mx-2"></div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-cyber-text hidden md:inline">
                      <span className="text-cyber-textMuted">&lt;</span>
                      {user.full_name}
                      <span className="text-cyber-textMuted">/&gt;</span>
                    </span>
                    <button onClick={handleLogout} className="text-cyber-neonPink hover:text-white transition-colors" title="Logout">
                      <LogOut size={18} />
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <Link to="/login" className="text-cyber-text hover:text-cyber-neonCyan transition-colors">Login</Link>
                  <Link to="/register" className="border border-cyber-neonCyan text-cyber-neonCyan px-4 py-1.5 rounded hover:bg-cyber-neonCyan hover:text-cyber-black transition-all shadow-[0_0_10px_rgba(0,240,255,0.2)] hover:shadow-neon-cyan">
                    Initialize
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-grow">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-cyber-gray bg-cyber-black py-8 mt-auto">
        <div className="max-w-7xl mx-auto px-4 text-center text-cyber-textMuted text-sm font-mono">
          <p>© 2026 NEXUS_JOBS // DIGITAL FRONTIER</p>
          <p className="mt-1 opacity-50">SYSTEM.STATUS: ONLINE</p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
