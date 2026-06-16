import { useEffect, useState } from 'react';
import TopAppBar from './components/layout/TopAppBar';
import BottomNavigation, { TabId } from './components/layout/BottomNavigation';
import TodayPMScreen from './components/today/TodayPMScreen';
import FleetScreen from './components/fleet/FleetScreen';
import WorkRecordsScreen from './components/records/WorkRecordsScreen';
import AlertsScreen from './components/alerts/AlertsScreen';
import PMBotButton from './components/bot/PMBotButton';
import PMBotSheet from './components/bot/PMBotSheet';
import { buildPolicyContext, deriveTodayPMTasksFromSchedule, loadOfficialPolicyContext } from './selectors/dataLoader';
import type { PolicyId } from './policies/types';

function App() {
  const [activeTab, setActiveTab] = useState<TabId>('today');
  const [selectedPolicy, setSelectedPolicy] = useState<PolicyId>('h3_cost_weighted');
  const [policyContext, setPolicyContext] = useState(buildPolicyContext());
  const [botOpen, setBotOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    loadOfficialPolicyContext().then(context => {
      if (context) setPolicyContext(context);
    });
  }, []);

  const { trucks, componentHealth, pmSchedule, workRecords, alerts } = policyContext;
  const todayTasks = deriveTodayPMTasksFromSchedule(pmSchedule, selectedPolicy);
  const unreadAlerts = alerts.filter(a => !a.read).length;

  const renderScreen = () => {
    switch (activeTab) {
      case 'today':
        return (
          <TodayPMScreen
            tasks={todayTasks}
            summary={pmSchedule.summary}
            pmSchedule={pmSchedule}
            selectedPolicy={selectedPolicy}
            onPolicyChange={setSelectedPolicy}
          />
        );
      case 'fleet':
        return (
          <FleetScreen
            trucks={trucks}
            componentHealth={componentHealth}
            workRecordsPreviousPM={workRecords.previousPMByTruck}
            selectedPolicy={selectedPolicy}
            policyContext={policyContext}
          />
        );
      case 'records':
        return <WorkRecordsScreen workRecords={workRecords} />;
      case 'alerts':
        return <AlertsScreen alerts={alerts} />;
    }
  };

  // Toggle dark class on body for CSS overrides
  useEffect(() => {
    document.body.classList.toggle('dark', darkMode);
  }, [darkMode]);

  return (
    <div className={`flex flex-col h-[844px] relative ${darkMode ? 'dark-app' : ''}`}>
      <TopAppBar
        unreadAlerts={unreadAlerts}
        onAlertClick={() => setActiveTab(activeTab === 'alerts' ? 'today' : 'alerts')}
        darkMode={darkMode}
        onDarkModeToggle={() => setDarkMode(d => !d)}
      />
      {renderScreen()}
      <BottomNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      <PMBotButton onClick={() => setBotOpen(true)} />
      <PMBotSheet
        open={botOpen}
        onClose={() => setBotOpen(false)}
        selectedPolicy={selectedPolicy}
        policyContext={policyContext}
      />
    </div>
  );
}

export default App;
