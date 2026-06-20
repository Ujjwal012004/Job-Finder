import React from 'react';
import { Link } from 'react-router-dom';
import GlitchText from '../components/GlitchText';
import NeonButton from '../components/NeonButton';
import { Search, Zap, Shield, Database } from 'lucide-react';

const LandingPage = () => {
  return (
    <div className="relative overflow-hidden">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center">
        <GlitchText text="FIND YOUR NEXT UPGRADE" className="text-5xl md:text-7xl mb-6" />
        <p className="max-w-2xl mx-auto text-xl text-cyber-textMuted font-mono mb-10">
          Jack into the premier tech employment nexus. High-speed matching, encrypted applications, and real-time analytics for the modern digital warrior.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link to="/search">
            <NeonButton variant="cyan" className="px-8 py-3 text-lg">
              <Search className="mr-2" size={20} />
              INITIATE_SEARCH
            </NeonButton>
          </Link>
          <Link to="/register">
            <NeonButton variant="purple" className="px-8 py-3 text-lg">
              CREATE_PROFILE
            </NeonButton>
          </Link>
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-cyber-gray bg-cyber-black/50">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass-panel p-8 text-center hover:-translate-y-2 transition-transform">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-cyber-neonCyan/10 text-cyber-neonCyan mb-6 shadow-neon-cyan">
              <Zap size={32} />
            </div>
            <h3 className="text-xl font-display font-bold text-white mb-3">LIGHTNING FAST</h3>
            <p className="text-cyber-textMuted font-mono text-sm">
              Instantaneous search algorithms matching your skills to the perfect corporate entity.
            </p>
          </div>
          
          <div className="glass-panel p-8 text-center hover:-translate-y-2 transition-transform">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-cyber-neonPurple/10 text-cyber-neonPurple mb-6 shadow-neon-purple">
              <Shield size={32} />
            </div>
            <h3 className="text-xl font-display font-bold text-white mb-3">SECURE PIPELINE</h3>
            <p className="text-cyber-textMuted font-mono text-sm">
              End-to-end encrypted application tracking. Keep your career movements classified.
            </p>
          </div>

          <div className="glass-panel p-8 text-center hover:-translate-y-2 transition-transform">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-cyber-neonPink/10 text-cyber-neonPink mb-6 shadow-neon-pink">
              <Database size={32} />
            </div>
            <h3 className="text-xl font-display font-bold text-white mb-3">DATA DRIVEN</h3>
            <p className="text-cyber-textMuted font-mono text-sm">
              Comprehensive analytics on your application pipeline to optimize your success rate.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
