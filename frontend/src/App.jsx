import React, { useState } from 'react';
import AppLayout from './layouts/AppLayout';
import DashboardPage from './pages/DashboardPage';
import DatasetsPage from './pages/DatasetsPage';
import DatasetVersionsPage from './pages/DatasetVersionsPage';
import DataQualityPage from './pages/DataQualityPage';
import ModelsPage from './pages/ModelsPage';
import ModelVersionsPage from './pages/ModelVersionsPage';
import EvaluationsPage from './pages/EvaluationsPage';
import ComparisonPage from './pages/ComparisonPage';
import DriftPage from './pages/DriftPage';
import ReliabilityPage from './pages/ReliabilityPage';
import AboutPage from './pages/AboutPage';

export default function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [selectedDatasetId, setSelectedDatasetId] = useState(null);
  const [selectedModelId, setSelectedModelId] = useState(null);
  const [selectedModelVersionId, setSelectedModelVersionId] = useState(null);
  const [selectedEvaluationId, setSelectedEvaluationId] = useState(null);
  const [showLaunchEvalModal, setShowLaunchEvalModal] = useState(false);

  const handleNavigate = (tab) => {
    setCurrentTab(tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectDataset = (id) => {
    setSelectedDatasetId(id);
  };

  const handleSelectModel = (id) => {
    setSelectedModelId(id);
  };

  const handleLaunchEvaluation = (modelVersionId) => {
    setSelectedModelVersionId(modelVersionId);
    setShowLaunchEvalModal(true);
    setCurrentTab('evaluations');
  };

  const handleSelectEvaluation = (id) => {
    setSelectedEvaluationId(id);
  };

  return (
    <AppLayout
      currentTab={currentTab}
      onSelectTab={handleNavigate}
      onOpenUpload={() => {
        setCurrentTab('datasets');
      }}
      onOpenEvalModal={() => {
        setShowLaunchEvalModal(true);
        setCurrentTab('evaluations');
      }}
    >
      {currentTab === 'dashboard' && (
        <DashboardPage
          onNavigate={handleNavigate}
          onSelectEvaluation={handleSelectEvaluation}
        />
      )}

      {currentTab === 'datasets' && (
        <DatasetsPage
          onSelectDataset={handleSelectDataset}
          onNavigate={handleNavigate}
        />
      )}

      {currentTab === 'dataset-versions' && (
        <DatasetVersionsPage
          selectedDatasetId={selectedDatasetId}
          onNavigate={handleNavigate}
        />
      )}

      {currentTab === 'data-quality' && (
        <DataQualityPage />
      )}

      {currentTab === 'models' && (
        <ModelsPage
          onSelectModel={handleSelectModel}
          onNavigate={handleNavigate}
        />
      )}

      {currentTab === 'model-versions' && (
        <ModelVersionsPage
          selectedModelId={selectedModelId}
          onNavigate={handleNavigate}
          onLaunchEvaluation={handleLaunchEvaluation}
        />
      )}

      {currentTab === 'evaluations' && (
        <EvaluationsPage
          initialEvaluationId={selectedEvaluationId}
          preselectedModelVersionId={selectedModelVersionId}
          showLaunchModal={showLaunchEvalModal}
          onCloseLaunchModal={() => setShowLaunchEvalModal(false)}
          onNavigate={handleNavigate}
        />
      )}

      {currentTab === 'comparison' && (
        <ComparisonPage />
      )}

      {currentTab === 'drift' && (
        <DriftPage />
      )}

      {currentTab === 'reliability' && (
        <ReliabilityPage />
      )}

      {currentTab === 'about' && (
        <AboutPage />
      )}
    </AppLayout>
  );
}
