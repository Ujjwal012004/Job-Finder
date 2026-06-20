import React, { useState, useEffect } from 'react';
import { jobService, applicationService } from '../api/services';
import CyberCard from '../components/CyberCard';
import NeonButton from '../components/NeonButton';
import GlitchText from '../components/GlitchText';
import { Search, MapPin, Briefcase, Building, DollarSign } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(null);
  const { user } = useAuth();

  const fetchJobs = async (searchQuery = '') => {
    setLoading(true);
    try {
      const data = await jobService.searchJobs({ keyword: searchQuery, page_size: 20 });
      setJobs(data.results || []);
    } catch (err) {
      console.error("Failed to fetch jobs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchJobs(query);
  };

  const handleApply = async (jobId) => {
    if (!user) {
      alert("PLEASE INITIALIZE SESSION TO APPLY");
      return;
    }
    setApplying(jobId);
    try {
      await applicationService.apply(jobId, "Standard Nexus Application");
      // Update local state to reflect application
      setJobs(jobs.map(item => 
        item.job.id === jobId ? { ...item, has_applied: true } : item
      ));
    } catch (err) {
      alert(err.response?.data?.detail || "Application failed.");
    } finally {
      setApplying(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-10">
        <GlitchText text="NEXUS_QUERY" className="text-3xl mb-6" />
        <CyberCard glow="cyan" className="p-4">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="relative flex-grow">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-cyber-neonCyan" />
              </div>
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-3 border border-cyber-gray bg-cyber-black/50 rounded-md text-cyber-text focus:outline-none focus:ring-1 focus:ring-cyber-neonCyan focus:border-cyber-neonCyan transition-all font-mono"
                placeholder="INPUT QUERY: React, Python, Remote..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
            <NeonButton type="submit" variant="cyan" disabled={loading}>
              {loading ? 'SCANNING...' : 'EXECUTE'}
            </NeonButton>
          </form>
        </CyberCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Filters Sidebar (Mocked for visual aesthetic in Phase 5) */}
        <div className="hidden lg:block space-y-6">
          <CyberCard glow="purple" className="p-5 text-sm font-mono text-cyber-textMuted">
            <h3 className="text-white font-display text-lg mb-4 border-b border-cyber-gray pb-2">PARAMETERS</h3>
            <div className="space-y-3">
              <div>
                <span className="block text-cyber-neonPurple mb-1">&gt; STATUS</span>
                <label className="flex items-center space-x-2"><input type="checkbox" className="bg-cyber-black border-cyber-gray text-cyber-neonPurple focus:ring-cyber-neonPurple" checked readOnly/> <span>ACTIVE</span></label>
              </div>
              <div>
                <span className="block text-cyber-neonPurple mb-1">&gt; TYPE</span>
                <label className="flex items-center space-x-2"><input type="checkbox" className="bg-cyber-black" /> <span>FULL_TIME</span></label>
                <label className="flex items-center space-x-2"><input type="checkbox" className="bg-cyber-black" /> <span>CONTRACT</span></label>
              </div>
              <div>
                <span className="block text-cyber-neonPurple mb-1">&gt; LOCATION</span>
                <label className="flex items-center space-x-2"><input type="checkbox" className="bg-cyber-black" /> <span>REMOTE_ONLY</span></label>
              </div>
            </div>
          </CyberCard>
        </div>

        {/* Results */}
        <div className="lg:col-span-3 space-y-4">
          {loading ? (
            <div className="text-center py-20 font-mono text-cyber-neonCyan animate-pulse">
              RETRIEVING_DATA_FROM_NEXUS...
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-20 font-mono text-cyber-neonPink">
              NO_MATCHES_FOUND. Adjust parameters.
            </div>
          ) : (
            jobs.map((item) => (
              <CyberCard key={item.job.id} interactive className="group flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex-grow">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-xl font-display font-bold text-white group-hover:text-cyber-neonCyan transition-colors">
                      {item.job.title}
                    </h3>
                    {item.job.is_remote && (
                      <span className="px-2 py-0.5 text-xs font-mono border border-cyber-neonPurple text-cyber-neonPurple rounded">REMOTE</span>
                    )}
                  </div>
                  
                  <div className="flex flex-wrap items-center gap-4 text-sm font-mono text-cyber-textMuted mb-4">
                    <div className="flex items-center gap-1"><Building size={14} className="text-cyber-neonCyan"/> {item.job.company?.name || 'Unknown Entity'}</div>
                    <div className="flex items-center gap-1"><MapPin size={14} className="text-cyber-neonPink"/> {item.job.location}</div>
                    <div className="flex items-center gap-1"><Briefcase size={14} className="text-cyber-neonPurple"/> {item.job.employment_type?.replace('-', ' ').toUpperCase()}</div>
                    {item.job.salary_min && (
                      <div className="flex items-center gap-1"><DollarSign size={14} className="text-cyber-neonCyan"/> ${item.job.salary_min.toLocaleString()}</div>
                    )}
                  </div>
                  
                  <p className="text-sm text-cyber-textMuted line-clamp-2">
                    {item.job.description}
                  </p>
                </div>
                
                <div className="md:w-32 flex-shrink-0 flex flex-col gap-2">
                  {item.has_applied ? (
                    <div className="text-center py-2 text-sm font-mono border border-cyber-gray text-cyber-gray rounded bg-cyber-black">
                      APPLIED
                    </div>
                  ) : (
                    <NeonButton 
                      variant="cyan" 
                      onClick={() => handleApply(item.job.id)}
                      disabled={applying === item.job.id}
                    >
                      {applying === item.job.id ? '...' : 'APPLY'}
                    </NeonButton>
                  )}
                  <div className="text-xs text-right font-mono text-cyber-textMuted mt-2">
                    Score: {(item.relevance_score * 100).toFixed(0)}%
                  </div>
                </div>
              </CyberCard>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchPage;
