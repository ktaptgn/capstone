import versionResultsRaw from '../../data/version_results.json';

interface VersionPolicy {
  id: string;
  name: string;
  color: string;
  demandFulfill: number | null;
  pmCost: number | null;
  downtime: number | null;
  failures: number | null;
  totalCost: number | null;
  useCase: string;
}
interface VersionData {
  label: string;
  title: string;
  subtitle: string;
  costLabel: string;
  costUnit: string;
  recommended: string;
  headline: string;
  source: string;
  policies: VersionPolicy[];
}
interface VersionResults {
  versions: string[];
  default: string;
  data: Record<string, VersionData>;
}

const versionResults = versionResultsRaw as unknown as VersionResults;

const fmt = (v: number | null) =>
  v === null || v === undefined ? '—' : Number(v).toLocaleString('ko-KR', { maximumFractionDigits: 1 });

// Shows the selected capstone version's policy-comparison result values. The version is
// chosen in the top app bar; switching it swaps every number shown here.
export default function VersionResultsCard({ selectedVersion }: { selectedVersion: string }) {
  const v = versionResults.data[selectedVersion] ?? versionResults.data[versionResults.default];
  return (
    <div className="mx-4 mt-3 rounded-xl border border-border bg-white p-3">
      <div className="flex items-center justify-between">
        <span className="text-[12px] font-bold text-text-main">{v.title}</span>
        <span className="text-[10px] font-bold text-white bg-sanguine rounded-full px-2 py-0.5">{v.label}</span>
      </div>
      <p className="text-[11px] text-text-sub mt-1 leading-snug">{v.subtitle}</p>
      <div className="mt-2 text-[11px] text-text-main">
        추천 정책 <b className="text-sanguine">{v.recommended}</b> — {v.headline}
      </div>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {v.policies.map(p => {
          const best = p.id === v.recommended;
          return (
            <span
              key={p.id}
              className={`text-[10px] px-2 py-1 rounded ${best ? 'font-bold ring-1' : ''}`}
              style={{ background: `${p.color}1A`, color: p.color }}
              title={`${p.name} · ${p.useCase}`}
            >
              {p.id}: {fmt(p.totalCost)}
            </span>
          );
        })}
      </div>
      <div className="mt-2 text-[9px] text-text-muted">
        {v.costLabel} ({v.costUnit}) · 출처: {v.source}
      </div>
    </div>
  );
}
