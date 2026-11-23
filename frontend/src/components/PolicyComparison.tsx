import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { PolicyResult } from "../api/types";

/** Side-by-side efficiency numbers for every policy that was run. */
export function PolicyComparison({ results }: { results: PolicyResult[] }) {
  const data = results.map((r) => ({
    policy: r.policy,
    mean: r.metrics.waits.mean,
    median: r.metrics.waits.median,
    p90: r.metrics.waits.p90,
    max: r.metrics.waits.max,
  }));

  return (
    <div>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="policy" />
          <YAxis label={{ value: "wait (min)", angle: -90, position: "insideLeft" }} />
          <Tooltip formatter={(v) => Number(v).toFixed(1)} />
          <Legend />
          <Bar dataKey="mean" fill="#4e79a7" />
          <Bar dataKey="median" fill="#76b7b2" />
          <Bar dataKey="p90" fill="#f28e2b" />
          <Bar dataKey="max" fill="#e15759" />
        </BarChart>
      </ResponsiveContainer>

      <table>
        <thead>
          <tr>
            <th>Policy</th>
            <th>Served</th>
            <th>Unserved</th>
            <th>Mean wait</th>
            <th>Weighted wait</th>
            <th>Makespan</th>
            <th>Engine</th>
            <th>Runtime</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r) => (
            <tr key={r.policy}>
              <td>{r.policy}</td>
              <td>{r.metrics.served}</td>
              <td>{r.metrics.unserved}</td>
              <td>{r.metrics.waits.mean.toFixed(1)}</td>
              <td>{r.metrics.total_weighted_wait.toFixed(0)}</td>
              <td>{r.metrics.makespan}</td>
              <td className="muted">
                {r.engine.scheduler}/{r.engine.analytics}
              </td>
              <td>{r.runtime_ms.toFixed(1)} ms</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
