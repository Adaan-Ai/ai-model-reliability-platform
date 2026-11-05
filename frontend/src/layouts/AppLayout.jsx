import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  Database,
  Layers,
  CheckCircle2,
  BrainCircuit,
  GitBranch,
  PlayCircle,
  Activity,
  ShieldCheck,
  GitCompare,
  FileCode2,
  Server,
  RefreshCw,
  Plus,
  ExternalLink
} from 'lucide-react';
import { api } from '../services/api';

export default function AppLayout({ currentTab, onSelectTab, children, onOpenUpload, onOpenEvalModal }) {
  const [backendStatus, setBackendStatus] = useState('checking'); // 'connected' | 'disconnected' | 'checking'
  const [dbName, setDbName] = useState('MySQL 8.0');

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const res = await api.checkHealth();
      if (res && res.status === 'healthy') {
        setBackendStatus('connected');
        if (res.database) setDbName(res.database);
      } else {
        setBackendStatus('disconnected');
      }
    } catch (e) {
      setBackendStatus('disconnected');
    }
  };

  const navItems = [
    { id: 'dashboard', label: 'Overview', icon: LayoutDashboard, badge: null },
    { id: 'datasets', label: 'Datasets', icon: Database, badge: null },
    { id: 'dataset-versions', label: 'Dataset Versions', icon: Layers, badge: null },
    { id: 'data-quality', label: 'Data Quality', icon: CheckCircle2, badge: 'Quality Engine' },
    { id: 'models', label: 'AI Models', icon: BrainCircuit, badge: null },
    { id: 'model-versions', label: 'Model Versions', icon: GitBranch, badge: null },
    { id: 'evaluations', label: 'Evaluations', icon: PlayCircle, badge: 'Scikit-learn' },
    { id: 'comparison', label: 'Model Comparison', icon: GitCompare, badge: null },
    { id: 'drift', label: 'Drift Monitoring', icon: Activity, badge: 'PSI / KS' },
    { id: 'reliability', label: 'Reliability Reports', icon: ShieldCheck, badge: 'Signature Score' },
    { id: 'about', label: 'Architecture & DBMS', icon: FileCode2, badge: '12 Entities' },
  ];

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-800">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 shadow-xl fixed inset-y-0 left-0 z-30">
        {/* Brand / Logo */}
        <div className="p-5 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-brand-500/20">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-white tracking-tight leading-tight">ReliabilityOps</h1>
              <span className="text-[10px] font-semibold tracking-wider text-brand-400 uppercase">AI Data & Model Platform</span>
            </div>
          </div>
          <div className="mt-3 px-2 py-1.5 rounded-md bg-slate-800/80 border border-slate-700/60 text-[11px] text-slate-400 flex items-center justify-between">
            <span className="truncate">PES University • DBMS</span>
            <span className="font-mono text-[9px] bg-slate-700 px-1.5 py-0.5 rounded text-slate-300">279 / 307</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-brand-600 text-white shadow-md shadow-brand-600/30'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center space-x-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`text-[9px] px-1.5 py-0.5 rounded font-mono ${
                    isActive ? 'bg-brand-700 text-white' : 'bg-slate-800 text-slate-400 border border-slate-700'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Connection status footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/60">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2">
              <span className={`w-2 h-2 rounded-full ${backendStatus === 'connected' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
              <span className="text-slate-400 text-[11px]">
                {backendStatus === 'connected' ? `DB: ${dbName}` : 'Backend Offline'}
              </span>
            </div>
            <button
              onClick={checkHealth}
              title="Refresh connection status"
              className="text-slate-400 hover:text-slate-200 p-1 rounded hover:bg-slate-800"
            >
              <RefreshCw className="w-3 h-3" />
            </button>
          </div>
          <div className="mt-2 text-[10px] text-slate-500 flex items-center justify-between">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="hover:text-brand-400 flex items-center space-x-1"
            >
              <span>Swagger API Docs</span>
              <ExternalLink className="w-2.5 h-2.5" />
            </a>
            <span className="font-mono">v1.0.0</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 pl-64 flex flex-col min-h-screen">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-20 shadow-xs">
          <div className="flex items-center space-x-4">
            <h2 className="text-base font-semibold text-slate-800 capitalize">
              {navItems.find(i => i.id === currentTab)?.label || 'Dashboard'}
            </h2>
            <div className="h-4 w-px bg-slate-200" />
            <span className="text-xs text-slate-500 hidden md:inline">
              12 Core MySQL Entities • Scikit-learn Machine Learning • Population Stability Index
            </span>
          </div>

          {/* Action buttons */}
          <div className="flex items-center space-x-3">
            <button
              onClick={onOpenUpload}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium rounded-lg border border-slate-200 transition"
            >
              <Plus className="w-3.5 h-3.5 text-slate-500" />
              <span>Upload CSV</span>
            </button>
            <button
              onClick={onOpenEvalModal}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-brand-600 hover:bg-brand-700 text-white text-xs font-medium rounded-lg shadow-sm shadow-brand-600/20 transition"
            >
              <PlayCircle className="w-3.5 h-3.5" />
              <span>Run Evaluation</span>
            </button>

            {/* User avatar */}
            <div className="flex items-center pl-3 border-l border-slate-200 space-x-2">
              <div className="w-8 h-8 rounded-full bg-slate-800 text-white font-bold text-xs flex items-center justify-center">
                M
              </div>
              <div className="hidden lg:block text-left">
                <p className="text-xs font-semibold text-slate-800 leading-tight">Mohammed Adaan</p>
                <p className="text-[10px] text-slate-400 font-mono">PES2UG24CS279</p>
              </div>
            </div>
          </div>
        </header>

        {/* Dynamic Page Content */}
        <main className="flex-1 p-8">
          {children}
        </main>

        {/* Global Footer */}
        <footer className="border-t border-slate-200 bg-white px-8 py-4 text-xs text-slate-500 flex flex-col md:flex-row items-center justify-between gap-2">
          <div>
            <span className="font-semibold text-slate-700">AI Model Evaluation & Data Reliability Platform</span> — PES University DBMS Project
          </div>
          <div className="flex items-center space-x-4 text-[11px]">
            <span>Mohammed Adaan Hamad (<span className="font-mono">PES2UG24CS279</span>)</span>
            <span>•</span>
            <span>Navya Kishore Dash (<span className="font-mono">PES2UG24CS307</span>)</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
