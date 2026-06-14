import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import OverviewPage from './pages/OverviewPage';
import FleetPage from './pages/FleetPage';
import PolicyPage from './pages/PolicyPage';
import ScenarioPage from './pages/ScenarioPage';
import HeuristicAnalysisPage from './pages/HeuristicAnalysisPage';
import PolicyDecisionPage from './pages/PolicyDecisionPage';
import C5OpsAssistant from './components/C5OpsAssistant';
import { dashboardKpis } from './data/dashboardKpis';
import versionResults from './data/version_results.json';

function App() {
  const [page, setPage] = useState('overview');
  const [timeSpeed, setTimeSpeed] = useState(1);
  const [darkMode, setDarkMode] = useState(false);
  const [simDate, setSimDate] = useState(new Date());
  const [isLive, setIsLive] = useState(true);
  const [selectedVersion, setSelectedVersion] = useState(versionResults.default);

  /* ── Decision log (lifted from DecisionPanel) ── */
  const [decisionLog, setDecisionLog] = useState([]);

  const handleDecision = (actionId, actionText, decision) => {
    setDecisionLog(prev => [
      {
        id: `${actionId}_${Date.now()}`,
        actionId,
        actionText,
        decision,
        timestamp: new Date().toLocaleString('ko-KR'),
        policyValues: {
          'Policy': dashboardKpis.currentPolicy,
          'Demand': `${dashboardKpis.demandFulfillment}%`,
          'PM Cost': `M₩${dashboardKpis.pmCostMKRW}`,
          'Total Cost': `M₩${dashboardKpis.totalCostMKRW}`,
          'Risk Trucks': `${dashboardKpis.riskTrucks}`,
          'Available': `${dashboardKpis.availableTrucks}/${dashboardKpis.totalTrucks}`,
        },
        report: null,
      },
      ...prev,
    ]);
  };

  const handleAddReport = (entryId, report) => {
    setDecisionLog(prev => prev.map(d =>
      d.id === entryId ? { ...d, report } : d
    ));
  };

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
  }, [darkMode]);

  const renderPage = () => {
    switch (page) {
      case 'overview': return <OverviewPage timeSpeed={timeSpeed} onDecision={handleDecision} simDate={simDate} isLive={isLive} />;
      case 'fleet': return <FleetPage />;
      case 'policy': return <PolicyPage version={selectedVersion} />;
      case 'decisions': return <PolicyDecisionPage decisionLog={decisionLog} onAddReport={handleAddReport} />;
      case 'analysis': return <HeuristicAnalysisPage />;
      case 'scenario': return <ScenarioPage />;
      default: return <OverviewPage timeSpeed={timeSpeed} onDecision={handleDecision} simDate={simDate} isLive={isLive} />;
    }
  };

  return (
    <>
      <Sidebar activePage={page} onNavigate={setPage} />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'auto' }}>
        <Header
          activePage={page}
          selectedVersion={selectedVersion}
          onVersionChange={setSelectedVersion}
          timeSpeed={timeSpeed}
          onTimeSpeedChange={setTimeSpeed}
          darkMode={darkMode}
          onDarkModeToggle={() => setDarkMode(d => !d)}
          simDate={simDate}
          onSimDateChange={setSimDate}
          isLive={isLive}
          onSetLive={setIsLive}
        />
        <main style={{ flex: 1, overflow: 'auto' }}>
          {renderPage()}
        </main>
      </div>
      <C5OpsAssistant />
    </>
  );
}

export default App;
