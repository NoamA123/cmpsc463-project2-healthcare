import type { Dataset, PolicyResult } from "../api/types";
import { colorFor } from "./colors";

const ROW_H = 28;
const LABEL_W = 90;
const WIDTH = 900;

/** One row per provider; each bar is an appointment, colored by patient group. */
export function GanttChart({ dataset, result }: { dataset: Dataset; result: PolicyResult }) {
  const patients = new Map(dataset.patients.map((p) => [p.id, p]));
  const groups = dataset.meta.groups;
  const end = Math.max(dataset.meta.horizon, result.metrics.makespan);
  const x = (t: number) => LABEL_W + (t / end) * (WIDTH - LABEL_W - 10);
  const height = dataset.providers.length * ROW_H + 24;
  const ticks = Array.from({ length: Math.floor(end / 60) + 1 }, (_, i) => i * 60);

  return (
    <div>
      <svg width={WIDTH} height={height} className="gantt">
        {ticks.map((t) => (
          <g key={t}>
            <line x1={x(t)} x2={x(t)} y1={0} y2={height - 20} stroke="#ddd" />
            <text x={x(t)} y={height - 6} fontSize={10} textAnchor="middle">
              {t}m
            </text>
          </g>
        ))}
        {dataset.providers.map((pr, row) => (
          <g key={pr.id} transform={`translate(0, ${row * ROW_H})`}>
            <text x={4} y={ROW_H / 2 + 4} fontSize={12}>
              {pr.name}
            </text>
            {result.schedule.appointments
              .filter((a) => a.provider_id === pr.id)
              .map((a) => {
                const p = patients.get(a.patient_id)!;
                return (
                  <rect
                    key={a.patient_id}
                    x={x(a.start)}
                    y={4}
                    width={Math.max(1, x(a.end) - x(a.start) - 1)}
                    height={ROW_H - 8}
                    fill={colorFor(p.group, groups)}
                    opacity={0.4 + 0.12 * p.urgency}
                  >
                    <title>
                      {`${p.id} (${p.group}, urgency ${p.urgency})\narrived ${p.arrival_time}, ${a.start}–${a.end}, waited ${a.wait}m`}
                    </title>
                  </rect>
                );
              })}
          </g>
        ))}
      </svg>
      <div className="legend">
        {groups.map((g) => (
          <span key={g}>
            <i style={{ background: colorFor(g, groups) }} /> {g}
          </span>
        ))}
        <span className="muted">darker = more urgent</span>
        {result.schedule.unserved.length > 0 && (
          <span className="warn">{result.schedule.unserved.length} unserved</span>
        )}
      </div>
    </div>
  );
}
