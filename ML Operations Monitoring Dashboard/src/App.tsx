import { Activity, Bell, Database, RefreshCcw, Search } from "lucide-react";
import { DecisionMix } from "./components/DecisionMix";
import { DriftTable } from "./components/DriftTable";
import { KpiCard } from "./components/KpiCard";
import { LineChart } from "./components/LineChart";
import { ModelRegistry } from "./components/ModelRegistry";
import { PredictionTable } from "./components/PredictionTable";
import { ScoreConsole } from "./components/ScoreConsole";
import { decisionMetrics, driftMetrics, kpis, modelMetadata, predictionLogs, timeSeries } from "./data/mockData";

export function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Activity size={23} />
          <div>
            <strong>RiskOps</strong>
            <span>ML Monitoring</span>
          </div>
        </div>
        <nav>
          <a className="active" href="#overview">Overview</a>
          <a href="#predictions">Predictions</a>
          <a href="#drift">Feature Drift</a>
          <a href="#registry">Model Registry</a>
          <a href="#probe">Scoring Probe</a>
        </nav>
      </aside>

      <main>
        <header className="topbar">
          <div>
            <h1>ML Operations Monitoring Dashboard</h1>
            <p>Production risk model health, decisions, drift, and prediction audit trail</p>
          </div>
          <div className="topbar-actions">
            <div className="search-box">
              <Search size={16} />
              <span>Search request ID</span>
            </div>
            <button type="button" title="Refresh dashboard"><RefreshCcw size={17} /> Refresh</button>
            <button type="button" title="View alerts"><Bell size={17} /> Alerts</button>
          </div>
        </header>

        <section className="kpi-grid" id="overview">
          {kpis.map((item) => <KpiCard key={item.label} item={item} />)}
        </section>

        <section className="dashboard-grid">
          <LineChart data={timeSeries} />
          <DecisionMix data={decisionMetrics} />
          <ModelRegistry metadata={modelMetadata} />
          <DriftTable rows={driftMetrics} />
          <PredictionTable rows={predictionLogs} />
          <ScoreConsole />
        </section>

        <footer>
          <Database size={16} />
          Connected target: Production ML Risk Scoring API at <code>http://127.0.0.1:8000</code>
        </footer>
      </main>
    </div>
  );
}
