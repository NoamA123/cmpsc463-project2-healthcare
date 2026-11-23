import type { PolicyResult } from "../api/types";

const pct = (x: number) => `${(x * 100).toFixed(1)}%`;

/** Rank disagreement (normalized inversions) vs arrival and urgency order, overall and per group. */
export function FairnessSummary({ results, groups }: { results: PolicyResult[]; groups: string[] }) {
  return (
    <table>
      <thead>
        <tr>
          <th rowSpan={2}>Policy</th>
          <th colSpan={2}>Overall</th>
          {groups.map((g) => (
            <th key={g} colSpan={3}>
              {g}
            </th>
          ))}
        </tr>
        <tr>
          <th>vs arrival</th>
          <th>vs urgency</th>
          {groups.map((g) => [
            <th key={`${g}-a`}>vs arrival</th>,
            <th key={`${g}-u`}>vs urgency</th>,
            <th key={`${g}-w`}>p90 wait</th>,
          ])}
        </tr>
      </thead>
      <tbody>
        {results.map((r) => (
          <tr key={r.policy}>
            <td>{r.policy}</td>
            <td>{pct(r.metrics.fairness.disagreement_vs_arrival)}</td>
            <td>{pct(r.metrics.fairness.disagreement_vs_urgency)}</td>
            {groups.map((g) => {
              const m = r.metrics.per_group.find((x) => x.group === g);
              return m
                ? [
                    <td key={`${g}-a`}>{pct(m.fairness.disagreement_vs_arrival)}</td>,
                    <td key={`${g}-u`}>{pct(m.fairness.disagreement_vs_urgency)}</td>,
                    <td key={`${g}-w`}>{m.waits.p90}</td>,
                  ]
                : null;
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
