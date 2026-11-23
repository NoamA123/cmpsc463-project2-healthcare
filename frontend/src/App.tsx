import { useCallback, useEffect, useState } from "react";
import { api } from "./api/client";
import type { Dataset, PolicyInfo, PolicyName, SimulationResponse, WeightConfig } from "./api/types";
import { DatasetPanel } from "./components/DatasetPanel";
import { FairnessSummary } from "./components/FairnessSummary";
import { GanttChart } from "./components/GanttChart";
import { GroupWaitChart } from "./components/GroupWaitChart";
import { PolicyComparison } from "./components/PolicyComparison";
import { PolicyPanel } from "./components/PolicyPanel";

const DEFAULT_WEIGHTS: WeightConfig = { urgency_power: 1, group_multipliers: {}, aging_rate: 0 };

export default function App() {
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [policies, setPolicies] = useState<PolicyInfo[]>([]);
  const [selected, setSelected] = useState<PolicyName[]>(["fifo", "sjf", "urgency", "wspt"]);
  const [weights, setWeights] = useState<WeightConfig>(DEFAULT_WEIGHTS);
  const [response, setResponse] = useState<SimulationResponse | null>(null);
  const [ganttPolicy, setGanttPolicy] = useState<PolicyName | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.policies().then(setPolicies).catch((e) => setError(String(e)));
  }, []);

  const onDataset = useCallback((d: Dataset) => {
    setDataset(d);
    setResponse(null);
    setError(null);
  }, []);

  const run = async () => {
    if (!dataset) return;
    const runnable = selected.filter((p) => {
      const info = policies.find((x) => x.name === p);
      return !info?.max_patients || dataset.patients.length <= info.max_patients;
    });
    setRunning(true);
    setError(null);
    try {
      const res = await api.simulate({ dataset, policies: runnable, weights });
      setResponse(res);
      setGanttPolicy(res.results[0]?.policy ?? null);
    } catch (e) {
      setError(String(e));
    } finally {
      setRunning(false);
    }
  };

  const ganttResult = response?.results.find((r) => r.policy === ganttPolicy);
  const groups = dataset?.meta.groups ?? [];

  return (
    <main>
      <header>
        <h1>Fair Appointment Scheduler</h1>
        <p className="muted">Schedule a simulated clinic under several policies and compare efficiency and fairness.</p>
      </header>

      {error && <div className="error">{error}</div>}

      <div className="controls">
        <DatasetPanel dataset={dataset} onDataset={onDataset} onError={setError} />
        <PolicyPanel
          dataset={dataset}
          policies={policies}
          selected={selected}
          onSelected={setSelected}
          weights={weights}
          onWeights={setWeights}
          onRun={run}
          running={running}
        />
      </div>

      {response && dataset && (
        <>
          <section className="panel">
            <h2>Schedule timeline</h2>
            <div className="tabs">
              {response.results.map((r) => (
                <button key={r.policy} className={r.policy === ganttPolicy ? "active" : ""} onClick={() => setGanttPolicy(r.policy)}>
                  {r.policy}
                </button>
              ))}
            </div>
            {ganttResult && <GanttChart dataset={dataset} result={ganttResult} />}
          </section>

          <section className="panel">
            <h2>Policy comparison</h2>
            <PolicyComparison results={response.results} />
          </section>

          <section className="panel">
            <h2>Average wait by group</h2>
            <GroupWaitChart results={response.results} groups={groups} />
          </section>

          <section className="panel">
            <h2>Fairness summary</h2>
            <p className="muted">
              Rank disagreement = inversions between the service order and a reference order, divided by n(n−1)/2. 0% means
              the policy served patients exactly in that order.
            </p>
            <FairnessSummary results={response.results} groups={groups} />
          </section>
        </>
      )}
    </main>
  );
}
