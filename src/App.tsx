import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <div className="min-h-screen bg-surface">
      <Navbar />
      <Dashboard />
    </div>
  );
}
