import React, { useState, useEffect } from 'react';
import {
  Database,
  BrainCircuit,
  PlayCircle,
  TrendingUp,
  ShieldCheck,
  AlertTriangle,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Layers,
  Sparkles,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { api } from '../services/api';

export default function DashboardPage({ onNavigate, onSelectEvaluation }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadOverview();
  }, []);

  const loadOverview = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getDashboardOverview();
      setData(res);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard statistics.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-4">
        <div className="w-10 h-10 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin" />
        <p className="text-sm font-medium text-slate-500">Querying MySQL analytical metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-rose-50 border border-rose-200 rounded-xl text-rose-800">
        <h3 className="text-sm font-semibold flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-rose-600" />
          <span>Error loading dashboard</span>
        </h3>
        <p className="text-xs mt-1 text-rose-600">{error}</p>
        <button
          onClick={loadOverview}
          className="mt-3 px-3 py-1.5 bg-rose-600 text-white rounded-lg text-xs font-medium hover:bg-rose-700"
        >
          Retry Query
        </button>
      </div>
    );
  }

  const COLORS = {
    HIGH: '#10b981',   // emerald-500
    MEDIUM: '#f59e0b', // amber-500
    LOW: '#ef4444',    // rose-500
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Hero Banner / Academic Header */}
      <div className="bg-gradient-to-r from-slate-900 via-brand-950 to-slate-900 rounded-2xl p-6 text-white shadow-xl relative overflow-hidden border border-slate-800">
        <div className="absolute right-0 top-0 w-96 h-full bg-radial from-brand-600/20 to-transparent pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-full bg-brand-500/20 border border-brand-400/30 text-brand-300 text-[11px] font-medium mb-2">
              <Sparkles className="w-3.5 h-3.5 text-brand-400" />
              <span>Full-Stack Enterprise DBMS & Machine Learning Platform</span>
            </div>
            <h1 className="text-xl md:text-2xl font-bold tracking-tight text-white">
              AI Model Evaluation & Data Reliability Platform
            </h1>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Centralized operational tracking across 12 relational entities in MySQL: monitoring dataset versions, automated data quality scoring, Scikit-learn model evaluation, Population Stability Index (PSI) drift detection, and composite reliability scoring.
            </p>
          </div>
          <div className="flex items-center space-x-2 self-start md:self-auto">
            <button
              onClick={() => onNavigate('evaluations')}
              className="px-3.5 py-2 bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold rounded-lg shadow-md transition"
            >
              Run Evaluation Pipeline
            </button>
          </div>
        </div>
      </div>

      {/* Top 4 Primary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Datasets */}
        <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs hover:border-slate-300 transition">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Datasets Registered</span>
            <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
              <Database className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-slate-900">{data.total_datasets}</span>
            <span className="text-xs text-slate-500 font-medium">({data.total_dataset_versions} versions)</span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <span className="text-slate-500">Avg Quality Score</span>
            <span className="font-semibold text-emerald-600">{data.avg_data_quality_score}%</span>
          </div>
        </div>

        {/* AI Models */}
        <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs hover:border-slate-300 transition">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">AI Models</span>
            <div className="p-2 rounded-lg bg-purple-50 text-purple-600">
              <BrainCircuit className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-slate-900">{data.total_models}</span>
            <span className="text-xs text-slate-500 font-medium">({data.total_model_versions} versions)</span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <span className="text-slate-500">Avg Test Accuracy</span>
            <span className="font-semibold text-brand-600">{data.avg_model_accuracy}%</span>
          </div>
        </div>

        {/* Evaluation Runs */}
        <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs hover:border-slate-300 transition">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Evaluations Executed</span>
            <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
              <PlayCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-slate-900">{data.total_evaluations}</span>
            <span className="text-xs text-emerald-600 font-medium font-mono">100% real ML</span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <span className="text-slate-500">Low Reliability Runs</span>
            <span className={`font-semibold ${data.low_reliability_count > 0 ? 'text-rose-600' : 'text-slate-600'}`}>
              {data.low_reliability_count}
            </span>
          </div>
        </div>

        {/* Drift Alerts */}
        <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs hover:border-slate-300 transition">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Drift Severity</span>
            <div className={`p-2 rounded-lg ${data.high_drift_count > 0 ? 'bg-amber-50 text-amber-600' : 'bg-slate-50 text-slate-600'}`}>
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-slate-900">{data.high_drift_count}</span>
            <span className="text-xs text-amber-600 font-medium">High Shift Flags</span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <span className="text-slate-500">Monitoring Metric</span>
            <span className="font-mono text-slate-600">PSI &ge; 0.25</span>
          </div>
        </div>
      </div>

      {/* Main Analytical Visualizations (Recharts) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Model Performance Trend Chart */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-800">Model Performance History</h3>
              <p className="text-xs text-slate-500">Historical Accuracy and F1-score across completed evaluation runs</p>
            </div>
            <span className="text-[11px] font-mono text-slate-400 bg-slate-50 px-2 py-1 rounded border border-slate-200">
              Scikit-learn
            </span>
          </div>
          <div className="h-64">
            {data.performance_trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.performance_trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="accGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0c8fe9" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#0c8fe9" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="f1Grad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#94a3b8" />
                  <YAxis domain={[50, 100]} tick={{ fontSize: 11 }} stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }} />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                  <Area type="monotone" dataKey="value" name="Accuracy (%)" stroke="#0c8fe9" fillOpacity={1} fill="url(#accGrad)" strokeWidth={2} />
                  <Area type="monotone" dataKey="secondary_value" name="F1-Score (%)" stroke="#8b5cf6" fillOpacity={1} fill="url(#f1Grad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No evaluation trend points available.
              </div>
            )}
          </div>
        </div>

        {/* Data Quality Trend Chart */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-800">Data Quality Trends by Dataset Version</h3>
              <p className="text-xs text-slate-500">Average quality check scores (missingness, uniqueness, ranges, types)</p>
            </div>
            <span className="text-[11px] font-mono text-slate-400 bg-slate-50 px-2 py-1 rounded border border-slate-200">
              0 - 100 Scale
            </span>
          </div>
          <div className="h-64">
            {data.quality_trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.quality_trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="label" tick={{ fontSize: 11 }} stroke="#94a3b8" />
                  <YAxis domain={[60, 100]} tick={{ fontSize: 11 }} stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }} />
                  <Line type="monotone" dataKey="value" name="Quality Score" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No data quality runs recorded.
              </div>
            )}
          </div>
        </div>

        {/* Population Stability Index (PSI) Drift Monitoring */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-800">Data Drift Score (PSI)</h3>
              <p className="text-xs text-slate-500">Distribution shift between evaluated dataset and reference baseline</p>
            </div>
            <div className="flex items-center space-x-2 text-[10px]">
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-500" /> &lt;0.10 Low
              <span className="inline-block w-2 h-2 rounded-full bg-amber-500" /> &lt;0.25 Med
              <span className="inline-block w-2 h-2 rounded-full bg-rose-500" /> &gt;0.25 High
            </div>
          </div>
          <div className="h-64">
            {data.drift_trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.drift_trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#94a3b8" />
                  <YAxis tick={{ fontSize: 11 }} stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }} />
                  <Bar dataKey="value" name="PSI Score" radius={[4, 4, 0, 0]}>
                    {data.drift_trends.map((entry, index) => {
                      const color = entry.value > 0.25 ? '#ef4444' : entry.value >= 0.10 ? '#f59e0b' : '#10b981';
                      return <Cell key={`cell-${index}`} fill={color} />;
                    })}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No drift metrics recorded.
              </div>
            )}
          </div>
        </div>

        {/* Reliability Score Distribution */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-800">Reliability Rating Distribution</h3>
              <p className="text-xs text-slate-500">Consolidated platform ratings (0.35 DQ + 0.45 Model + 0.20 Drift)</p>
            </div>
            <span className="text-[11px] font-mono text-slate-400 bg-slate-50 px-2 py-1 rounded border border-slate-200">
              Evaluations
            </span>
          </div>
          <div className="h-64 flex flex-col md:flex-row items-center justify-center gap-6">
            <div className="w-48 h-48">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data.reliability_distribution}
                    dataKey="count"
                    nameKey="rating"
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={75}
                    paddingAngle={4}
                  >
                    {data.reliability_distribution.map((entry) => (
                      <Cell key={`slice-${entry.rating}`} fill={COLORS[entry.rating] || '#94a3b8'} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Legend Breakdown */}
            <div className="space-y-3 text-xs w-full max-w-xs">
              {data.reliability_distribution.map((item) => (
                <div key={item.rating} className="flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-100">
                  <div className="flex items-center space-x-2">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[item.rating] }} />
                    <span className="font-semibold text-slate-700">{item.rating} Reliability</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-slate-900">{item.count}</span>
                    <span className="text-slate-400 text-[10px]">({item.percentage}%)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Evaluations Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-800">Recent Evaluation Runs</h3>
            <p className="text-xs text-slate-500">Live operational history of ML models evaluated against dataset versions</p>
          </div>
          <button
            onClick={() => onNavigate('evaluations')}
            className="text-xs font-medium text-brand-600 hover:text-brand-700 flex items-center space-x-1"
          >
            <span>View All Runs</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 text-slate-500 uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-6 font-semibold">Run ID</th>
                <th className="py-3 px-6 font-semibold">Model & Algorithm</th>
                <th className="py-3 px-6 font-semibold">Dataset Version</th>
                <th className="py-3 px-6 font-semibold">Accuracy</th>
                <th className="py-3 px-6 font-semibold">F1-Score</th>
                <th className="py-3 px-6 font-semibold">Drift Status</th>
                <th className="py-3 px-6 font-semibold">Reliability</th>
                <th className="py-3 px-6 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.recent_evaluations.length > 0 ? (
                data.recent_evaluations.map((run) => {
                  const relRating = run.reliability?.rating || 'N/A';
                  const driftStatus = run.drift?.drift_status || 'LOW';

                  return (
                    <tr key={run.evaluation_id} className="hover:bg-slate-50/70 transition">
                      <td className="py-3.5 px-6 font-mono font-medium text-slate-700">
                        #{run.evaluation_id}
                      </td>
                      <td className="py-3.5 px-6">
                        <div className="font-semibold text-slate-800">{run.model_name || 'Model'}</div>
                        <div className="text-[11px] text-slate-400 font-mono">
                          v{run.model_version_number} • {run.algorithm}
                        </div>
                      </td>
                      <td className="py-3.5 px-6">
                        <div className="text-slate-700">{run.dataset_name || 'Dataset'}</div>
                        <div className="text-[11px] text-slate-400 font-mono">v{run.dataset_version_number}</div>
                      </td>
                      <td className="py-3.5 px-6 font-semibold text-slate-800">
                        {run.result ? `${run.result.accuracy}%` : '—'}
                      </td>
                      <td className="py-3.5 px-6 font-semibold text-slate-800">
                        {run.result ? `${run.result.f1_score}%` : '—'}
                      </td>
                      <td className="py-3.5 px-6">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          driftStatus === 'HIGH' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                          driftStatus === 'MEDIUM' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                          'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        }`}>
                          {driftStatus} DRIFT
                        </span>
                      </td>
                      <td className="py-3.5 px-6">
                        {run.reliability ? (
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-slate-900">{run.reliability.overall_score}</span>
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              relRating === 'HIGH' ? 'bg-emerald-100 text-emerald-800' :
                              relRating === 'MEDIUM' ? 'bg-amber-100 text-amber-800' :
                              'bg-rose-100 text-rose-800'
                            }`}>
                              {relRating}
                            </span>
                          </div>
                        ) : '—'}
                      </td>
                      <td className="py-3.5 px-6 text-right">
                        <button
                          onClick={() => {
                            if (onSelectEvaluation) onSelectEvaluation(run.evaluation_id);
                            onNavigate('evaluations');
                          }}
                          className="text-brand-600 hover:text-brand-800 font-medium hover:underline inline-flex items-center space-x-1"
                        >
                          <span>Inspect</span>
                          <ChevronRight className="w-3 h-3" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-400">
                    No evaluation runs recorded.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
