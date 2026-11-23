import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Dataset, GeneratorParams } from "../api/types";

interface Props {
  dataset: Dataset | null;
  onDataset: (d: Dataset) => void;
  onError: (msg: string) => void;
}

export function DatasetPanel({ dataset, onDataset, onError }: Props) {
  const [samples, setSamples] = useState<string[]>([]);
  const [gen, setGen] = useState<GeneratorParams>({ n_patients: 50, n_providers: 3, horizon: 480, seed: 42 });

  useEffect(() => {
    api.listDatasets().then(setSamples).catch((e) => onError(String(e)));
  }, [onError]);

  const load = (p: Promise<Dataset>) => p.then(onDataset).catch((e) => onError(String(e)));

  const upload = async (file: File) => {
    try {
      onDataset(JSON.parse(await file.text()) as Dataset);
    } catch (e) {
      onError(`Could not read ${file.name}: ${e}`);
    }
  };

  const num = (key: keyof GeneratorParams) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setGen({ ...gen, [key]: Number(e.target.value) });

  return (
    <section className="panel">
      <h2>1. Dataset</h2>

      <label>
        Sample:{" "}
        <select defaultValue="" onChange={(e) => e.target.value && load(api.getDataset(e.target.value))}>
          <option value="" disabled>
            choose…
          </option>
          {samples.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
      </label>

      <fieldset>
        <legend>Generate</legend>
        <label>
          Patients <input type="number" min={1} value={gen.n_patients} onChange={num("n_patients")} />
        </label>
        <label>
          Providers <input type="number" min={1} value={gen.n_providers} onChange={num("n_providers")} />
        </label>
        <label>
          Day length (min) <input type="number" min={1} value={gen.horizon} onChange={num("horizon")} />
        </label>
        <label>
          Seed <input type="number" value={gen.seed ?? 0} onChange={num("seed")} />
        </label>
        <button onClick={() => load(api.generateDataset(gen))}>Generate</button>
      </fieldset>

      <label>
        Upload JSON: <input type="file" accept=".json" onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} />
      </label>

      {dataset && (
        <p className="muted">
          Loaded <b>{dataset.meta.name}</b>: {dataset.patients.length} patients, {dataset.providers.length} providers,
          groups {dataset.meta.groups.join(", ")}
        </p>
      )}
    </section>
  );
}
