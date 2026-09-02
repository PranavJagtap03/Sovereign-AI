import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import StatusBar from './components/StatusBar';
import Dashboard from './pages/Dashboard';
import NewTask from './pages/NewTask';
import KnowledgePage from './pages/KnowledgePage';
import AuditPage from './pages/AuditPage';
import SovereigntyPage from './pages/SovereigntyPage';
import ModelRouterPage from './pages/ModelRouterPage';
import { RiskCoverageProvider } from './context/RiskCoverageContext';

export default function App() {
  return (
    <RiskCoverageProvider>
      <BrowserRouter>
        <div className="flex flex-col h-screen overflow-hidden" style={{ background: '#0A1628' }}>
        {/* Top Status Bar */}
        <StatusBar />

        {/* Main layout */}
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <Sidebar />

          {/* Page content */}
          <main className="flex-1 overflow-y-auto p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/task" element={<NewTask />} />
              <Route path="/knowledge" element={<KnowledgePage />} />
              <Route path="/audit" element={<AuditPage />} />
              <Route path="/sovereignty" element={<SovereigntyPage />} />
              <Route path="/models" element={<ModelRouterPage />} />
            </Routes>
          </main>
        </div>

        {/* Fixed demo badge */}
        <div className="demo-badge">⚡ DEMO MODE</div>
      </div>
    </BrowserRouter>
  </RiskCoverageProvider>
  );
}
