import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Machines from './pages/Machines';
import MachineDetail from './pages/MachineDetail';
import Components from './pages/Components';
import Downtime from './pages/Downtime';
import Alerts from './pages/Alerts';
import Recommendations from './pages/Recommendations';
import Analytics from './pages/Analytics';
import MaintenanceHistory from './pages/MaintenanceHistory';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/machines" element={<Machines />} />
            <Route path="/machines/:id" element={<MachineDetail />} />
            <Route path="/components" element={<Components />} />
            <Route path="/downtime" element={<Downtime />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/recommendations" element={<Recommendations />} />
            <Route path="/maintenance-history" element={<MaintenanceHistory />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
