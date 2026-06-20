import React, { useState, useEffect } from 'react';
import { dashboardService } from '../api/services';
import CyberCard from '../components/CyberCard';
import GlitchText from '../components/GlitchText';
import { Activity, Target, CheckCircle2, XCircle, Clock } from 'lucide-react';

const DashboardPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const result = await dashboardService.getDashboard();
        setData(result);
      } catch (err) {
        console.error("Failed to load dashboard:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center font-mono text-cyber-neonCyan animate-pulse">
        CALCULATING_TRAJECTORIES...
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center font-mono text-cyber-neonPink">
        ERROR: FAILED TO FETCH TELEMETRY
      </div>
    );
  }

  const { pipeline, recent_activity } = data;

  const StatusIcon = ({ status }) => {
    switch (status.toLowerCase()) {
      case 'applied': return <Clock size={16} className="text-cyber-neonCyan" />;
      case 'interviewing': return <Activity size={16} className="text-cyber-neonPurple" />;
      case 'offered': return <CheckCircle2 size={16} className="text-[#00ff88]" />;
      case 'rejected': return <XCircle size={16} className="text-cyber-neonPink" />;
      default: return <Target size={16} className="text-cyber-textMuted" />;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="flex items-center justify-between border-b border-cyber-gray pb-4">
        <GlitchText text="COMMAND_CENTER" className="text-3xl" />
        <div className="font-mono text-sm text-cyber-textMuted">
          UPTIME: {new Date().toISOString().split('T')[1].substring(0, 8)}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <CyberCard glow="cyan" className="flex flex-col">
          <span className="text-cyber-textMuted font-mono text-sm mb-2">&gt; TOTAL_APPLICATIONS</span>
          <span className="text-4xl font-display font-bold text-cyber-neonCyan">{pipeline.total}</span>
        </CyberCard>
        
        <CyberCard glow="purple" className="flex flex-col">
          <span className="text-cyber-textMuted font-mono text-sm mb-2">&gt; SUCCESS_RATE</span>
          <span className="text-4xl font-display font-bold text-cyber-neonPurple">
            {(pipeline.success_rate * 100).toFixed(1)}%
          </span>
        </CyberCard>

        <CyberCard glow="pink" className="flex flex-col">
          <span className="text-cyber-textMuted font-mono text-sm mb-2">&gt; ACTIVE_PIPELINE</span>
          <span className="text-4xl font-display font-bold text-cyber-neonPink">
            {(pipeline.active_rate * 100).toFixed(1)}%
          </span>
        </CyberCard>

        <CyberCard glow="cyan" className="flex flex-col">
          <span className="text-cyber-textMuted font-mono text-sm mb-2">&gt; RECENT_ACTIVITY</span>
          <span className="text-4xl font-display font-bold text-white">
            {pipeline.this_week}
          </span>
        </CyberCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Activity Feed */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="font-display text-xl text-white border-b border-cyber-gray pb-2 mb-4">RECENT_TELEMETRY</h3>
          {recent_activity.length === 0 ? (
            <p className="font-mono text-cyber-textMuted p-4 border border-dashed border-cyber-gray text-center">
              NO ACTIVITY LOGGED
            </p>
          ) : (
            recent_activity.map((item) => (
              <CyberCard key={item.application_id} className="p-4 flex items-center justify-between" glow="purple">
                <div>
                  <h4 className="font-display font-bold text-white text-lg">{item.job_title}</h4>
                  <div className="font-mono text-sm text-cyber-textMuted">{item.company_name}</div>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <div className="flex items-center gap-1 font-mono text-xs px-2 py-1 border border-cyber-gray rounded bg-cyber-black uppercase">
                    <StatusIcon status={item.status} />
                    <span className="ml-1">{item.status}</span>
                  </div>
                  <div className="font-mono text-[10px] text-cyber-textMuted">
                    {item.applied_on ? item.applied_on.split('T')[0] : 'UNKNOWN_DATE'}
                  </div>
                </div>
              </CyberCard>
            ))
          )}
        </div>

        {/* Breakdown */}
        <div>
          <h3 className="font-display text-xl text-white border-b border-cyber-gray pb-2 mb-4">STATUS_DISTRIBUTION</h3>
          <CyberCard className="p-6">
            <div className="space-y-4">
              {Object.entries(pipeline.by_status).map(([status, count]) => (
                <div key={status}>
                  <div className="flex justify-between font-mono text-sm mb-1 uppercase">
                    <span className="text-cyber-text">{status}</span>
                    <span className="text-cyber-neonCyan">{count}</span>
                  </div>
                  <div className="w-full bg-cyber-black h-2 rounded overflow-hidden">
                    <div 
                      className="bg-cyber-neonCyan h-full shadow-neon-cyan" 
                      style={{ width: `${(count / pipeline.total) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
              {Object.keys(pipeline.by_status).length === 0 && (
                <p className="font-mono text-sm text-cyber-textMuted text-center">INSUFFICIENT DATA</p>
              )}
            </div>
          </CyberCard>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
