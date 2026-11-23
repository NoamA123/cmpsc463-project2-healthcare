import type { Dataset, PolicyInfo, PolicyName, WeightConfig } from "../api/types";

interface Props {
  dataset: Dataset | null;
  policies: PolicyInfo[];
  selected: PolicyName[];
  onSelected: (p: PolicyName[]) => void;
  weights: WeightConfig;
  onWeights: (w: WeightConfig) => void;
  onRun: () => void;
  running: boolean;
}

export function PolicyPanel({ dataset, policies, selected, onSelected, weights, onWeights, onRun, running }: Props) {
  const n = dataset?.patients.length ?? 0;
  const toggle = (p: PolicyName) =>
    onSelected(selected.includes(p) ? selected.filter((x) => x !== p) : [...selected, p]);
  const tooBig = (p: PolicyInfo) => p.max_patients !== null && n > p.max_patients;

  return (
    <section className="panel">
      <h2>2. Policies &amp; weights</h2>
      {policies.map((p) => (
        <label key={p.name} className="row" title={p.description}>
          <input
            type="checkbox"
            checked={selected.includes(p.name) && !tooBig(p)}
            disabled={tooBig(p)}
            onChange={() => toggle(p.name)}
          />
          <b>{p.name}</b> <span className="muted">{p.description}</span>
        </label>
      ))}

      <fieldset>
        <legend>Weight function</legend>
        <p className="muted">
          weight = urgency<sup>power</sup> × group multiplier + aging × minutes waited
        </p>
        <label>
          Urgency power {weights.urgency_power.toFixed(1)}
          <input
            type="range" min={0} max={4} step={0.1} value={weights.urgency_power}
            onChange={(e) => onWeights({ ...weights, urgency_power: Number(e.target.value) })}
          />
        </label>
        <label>
          Aging rate {weights.aging_rate.toFixed(2)}
          <input
            type="range" min={0} max={1} step={0.01} value={weights.aging_rate}
            onChange={(e) => onWeights({ ...weights, aging_rate: Number(e.target.value) })}
          />
        </label>
        {dataset?.meta.groups.map((g) => (
          <label key={g}>
            {g} multiplier
            <input
              type="number" min={0} step={0.1} value={weights.group_multipliers[g] ?? 1}
              onChange={(e) =>
                onWeights({ ...weights, group_multipliers: { ...weights.group_multipliers, [g]: Number(e.target.value) } })
              }
            />
          </label>
        ))}
      </fieldset>

      <button
        className="primary"
        disabled={!dataset || running || selected.filter((p) => !tooBig(policies.find((x) => x.name === p)!)).length === 0}
        onClick={onRun}
      >
        {running ? "Running…" : "Run simulation"}
      </button>
    </section>
  );
}
