import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import OverviewPage from './pages/OverviewPage';
import FleetPage from './pages/FleetPage';
import PolicyPage from './pages/PolicyPage';
import ScenarioPage from './pages/ScenarioPage';
import C5OpsAssistant from './components/C5OpsAssistant';

function App() {
  const [page, setPage] = useState('overview');

  const renderPage = () => {
    switch (page) {
      case 'overview': return <OverviewPage />;
      case 'fleet': return <FleetPage />;
      case 'policy': return <PolicyPage />;
      case 'scenario': return <ScenarioPage />;
      default: return <OverviewPage />;
    }
  };

  return (
    <>
      <Sidebar activePage={page} onNavigate={setPage} />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'auto' }}>
        <Header activePage={page} />
        <main style={{ flex: 1, overflow: 'auto' }}>
          {renderPage()}
        </main>
      </div>
      <C5OpsAssistant />
    </>
  );
}

export default App;
