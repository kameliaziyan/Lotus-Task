import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import TreeVisualizer from "./components/TreeVisualizer";
import { AppProvider } from "./context/AppContext";

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <div className="app">
          <header>
            <div className="header-inner">
              <div className="header-title">
                <h1>Burnout Predictor</h1>
                <p>Decision tree powered burnout risk assessment</p>
              </div>
            </div>
          </header>

          <main className="page-content">
            <Routes>
              <Route path="/predict" element={<Dashboard />} />
              <Route path="/tree" element={<TreeVisualizer />} />
              <Route path="*" element={<Navigate to="/predict" replace />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AppProvider>
  );
}
