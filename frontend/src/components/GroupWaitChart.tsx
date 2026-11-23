import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { PolicyResult } from "../api/types";
import { colorFor } from "./colors";

type Stat = "mean" | "median" | "p90" | "max";

/** Wait statistic per group (x axis), one bar per policy. */
export function GroupWaitChart({ results, groups, stat = "mean" }: { results: PolicyResult[]; groups: string[]; stat?: Stat }) {
  const policies = results.map((r) => r.policy);
  const data = groups.map((g) => {
    const row: Record<string, string | number> = { group: g };
    for (const r of results) {
      row[r.policy] = r.metrics.per_group.find((m) => m.group === g)?.waits[stat] ?? 0;
    }
    return row;
  });

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="group" />
        <YAxis label={{ value: `${stat} wait (min)`, angle: -90, position: "insideLeft" }} />
        <Tooltip formatter={(v) => Number(v).toFixed(1)} />
        <Legend />
        {policies.map((p) => (
          <Bar key={p} dataKey={p} fill={colorFor(p, policies)} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
