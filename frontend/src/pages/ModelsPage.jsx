import React, { useState, useEffect } from 'react';
import {
  BrainCircuit,
  GitBranch,
  Plus,
  Search,
  User,
  Calendar,
  ChevronRight,
  PlayCircle
} from 'lucide-react';
import { api } from '../services/api';

export default function ModelsPage({ onSelectModel, onNavigate }) {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Create model modal
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [type, setType] = useState('Classification');
  const [description, setDescription] = useState('');
  const [ownerId, setOwnerId] = useState('');
  const [users, setUsers] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadModels();
    loadUsers();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      const res = await api.getModels();
      setModels(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      const u = await api.getUsers();
      setUsers(u);
      if (u.length > 0) setOwnerId(u[0].user_id);
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateModel = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.createModel({
        model_name: name,
        model_type: type,
        description,
        owner_id: Number(ownerId),
      });
      setShowModal(false);
      setName('');
      setDescription('');
      loadModels();
    } catch (err) {
      alert(`Failed to register model: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const filtered = models.filter((m) =>
    m.model_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (m.description && m.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">AI Model Registry</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Registered machine learning models, ownership, and algorithmic iterations (Core Entities 7 & 8).
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-xs transition self-start sm:self-auto"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Register New AI Model</span>
        </button>
      </div>

      {/* Search */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search AI models by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:outline-hidden"
          />
        </div>
        <span className="text-xs text-slate-500">
          {filtered.length} Models Registered
        </span>
      </div>

      {/* Model Grid */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center space-y-3">
          <div className="w-8 h-8 border-3 border-brand-200 border-t-brand-600 rounded-full animate-spin" />
          <p className="text-xs text-slate-500">Querying registered models from MySQL...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((model) => (
            <div
              key={model.model_id}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:border-slate-300 hover:shadow-md transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2.5">
                    <div className="p-2 rounded-lg bg-purple-50 text-purple-600">
                      <BrainCircuit className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">{model.model_name}</h3>
                      <span className="text-[10px] text-slate-400 font-mono">Model ID: #{model.model_id}</span>
                    </div>
                  </div>
                  <span className="px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200 font-semibold text-[10px]">
                    {model.model_type}
                  </span>
                </div>

                <p className="text-xs text-slate-600 mt-3 line-clamp-2 leading-relaxed">
                  {model.description || 'No description provided.'}
                </p>

                <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-2 gap-2 text-[11px] text-slate-500">
                  <div className="flex items-center space-x-1.5">
                    <User className="w-3.5 h-3.5 text-slate-400" />
                    <span className="truncate">{model.owner?.name || 'Owner ID ' + model.owner_id}</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <GitBranch className="w-3.5 h-3.5 text-slate-400" />
                    <span>{model.version_count} Algorithmic Versions</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>Created: {model.created_date}</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <span className="font-mono text-[10px] text-slate-400">Latest: v{model.latest_version || '1.0'}</span>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between">
                <button
                  onClick={() => {
                    if (onSelectModel) onSelectModel(model.model_id);
                    onNavigate('model-versions');
                  }}
                  className="text-xs font-semibold text-brand-600 hover:text-brand-800 flex items-center space-x-1"
                >
                  <span>Inspect Versions</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => onNavigate('evaluations')}
                  className="text-xs font-medium text-slate-600 hover:text-slate-900 flex items-center space-x-1"
                >
                  <PlayCircle className="w-3 h-3 text-brand-600" />
                  <span>Evaluate</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-sm font-bold text-slate-900">Register New AI Model</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600 text-lg leading-none">
                &times;
              </button>
            </div>

            <form onSubmit={handleCreateModel} className="mt-4 space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Model Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Credit Fraud Classifier"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Model Type</label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden"
                >
                  <option value="Classification">Classification</option>
                  <option value="Regression">Regression</option>
                  <option value="Risk Scoring">Risk Scoring</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Description</label>
                <textarea
                  rows={2}
                  placeholder="Intended business application, target variables..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Owner (User) *</label>
                <select
                  value={ownerId}
                  onChange={(e) => setOwnerId(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden"
                >
                  {users.map((u) => (
                    <option key={u.user_id} value={u.user_id}>
                      {u.name} ({u.role})
                    </option>
                  ))}
                </select>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg font-semibold shadow-xs disabled:opacity-50"
                >
                  {submitting ? 'Registering...' : 'Save AI Model'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
