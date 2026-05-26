import { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, CheckCircle2, Info, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';
import Card from '../components/Card';
import SectionHeader from '../components/SectionHeader';
import StatusBadge from '../components/StatusBadge';
import { loadDashboardSnapshots } from '../data/c5Snapshots';

const DATA_NONE = '데이터 없음';
const policyColors = {
  H0: '#64748B',
  H1: '#2563EB',
  H2: '#7C3AED',
  H3: '#16A34A',
  H4: '#0891B2',
};

function isNumber(value) {
  return value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value));
}

function formatNumber(value, digits = 2) {
  if (!isNumber(value)) return DATA_NONE;
  return Number(value).toLocaleString('ko-KR', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function formatPercent(value, digits = 2) {
  if (!isNumber(value)) return DATA_NONE;
  return `${formatNumber(value, digits)}%`;
}

function formatRate(value) {
  if (!isNumber(value)) return DATA_NONE;
  return `${formatNumber(Number(value) * 100, 2)}%`;
}

function formatDeltaPoint(value) {
  if (!isNumber(value)) return DATA_NONE;
  const sign = Number(value) > 0 ? '+' : '';
  return `${sign}${formatNumber(Number(value) * 100, 2)}%p`;
}

function directionKo(direction) {
  return direction === 'higher_is_better' ? '높을수록 좋음' : '낮을수록 좋음';
}

function policyLabel(item) {
  if (!item) return DATA_NONE;
  return item.is_tie ? `${item.best_policy} 공동 1위` : item.best_policy;
}

function kpiValue(item) {
  if (!item) return DATA_NONE;
  if (item.kpi === 'demand_fulfillment_rate') return formatRate(item.value);
  return formatNumber(item.value, item.kpi === 'queue_time' ? 3 : 2);
}

function FallbackPanel() {
  return (
    <Card style={{ padding: 24, borderLeft: '4px solid #F59E0B' }}>
      <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
        <AlertTriangle size={22} color="#B45309" />
        <div>
          <h2 style={{ fontSize: 16, margin: 0, color: '#1E293B' }}>분석 결과 파일을 찾을 수 없습니다.</h2>
          <p style={{ margin: '6px 0 0', color: '#64748B', fontSize: 13 }}>
            policy sweep과 heuristic analysis를 실행한 뒤 UI snapshot을 다시 생성하세요.
          </p>
        </div>
      </div>
    </Card>
  );
}

function RecommendedPanel({ recommended, seedCount }) {
  return (
    <Card style={{ padding: 20, borderLeft: '4px solid #16A34A' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-start' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <CheckCircle2 size={20} color="#16A34A" />
            <span style={{ fontSize: 12, color: '#64748B', fontWeight: 700 }}>추천 정책</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 12 }}>
            <span style={{ fontSize: 34, lineHeight: 1, fontWeight: 800, color: '#166534' }}>
              {recommended?.policy_id || DATA_NONE}
            </span>
            <StatusBadge status="available" label="현재 KPI 가중치 기준 추천" size="md" />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(120px, 1fr))', gap: 12, marginTop: 18 }}>
            <div>
              <div style={{ fontSize: 11, color: '#94A3B8', fontWeight: 700 }}>가중 순위 점수</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: '#1E293B' }}>{formatNumber(recommended?.weighted_rank_score, 3)}</div>
            </div>
            <div>
              <div style={{ fontSize: 11, color: '#94A3B8', fontWeight: 700 }}>분석 기준</div>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#334155' }}>{recommended?.basis_ko || '현재 KPI 가중 순위 점수'}</div>
            </div>
            <div>
              <div style={{ fontSize: 11, color: '#94A3B8', fontWeight: 700 }}>Seed 수</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: '#1E293B' }}>{seedCount || DATA_NONE}</div>
            </div>
          </div>
        </div>
        <div style={{
          minWidth: 190,
          border: '1px solid #FDE68A',
          background: '#FFFBEB',
          borderRadius: 8,
          padding: 12,
          color: '#92400E',
          fontSize: 12,
          fontWeight: 700,
        }}>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <AlertTriangle size={16} />
            <span>주의</span>
          </div>
          <div style={{ marginTop: 6 }}>전역 최적해가 아님</div>
        </div>
      </div>
    </Card>
  );
}

function BestByKpi({ items }) {
  return (
    <Card style={{ padding: 20 }}>
      <SectionHeader title="KPI별 우수 정책" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
        {items.map(item => (
          <div key={item.kpi} style={{
            border: '1px solid #E2E8F0',
            borderRadius: 8,
            padding: 12,
            background: '#FFFFFF',
            minHeight: 112,
          }}>
            <div style={{ fontSize: 12, color: '#64748B', fontWeight: 700 }}>{item.label_ko}</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8 }}>
              <span style={{
                width: 10,
                height: 10,
                borderRadius: 3,
                background: policyColors[item.best_policies?.[0]] || '#64748B',
                flexShrink: 0,
              }} />
              <span style={{ fontSize: 17, fontWeight: 800, color: '#1E293B' }}>{policyLabel(item)}</span>
            </div>
            <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between', gap: 10, color: '#64748B', fontSize: 11 }}>
              <span>{directionKo(item.direction)}</span>
              <strong style={{ color: '#334155' }}>{kpiValue(item)}</strong>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

function ImprovementTable({ rows }) {
  const chartData = rows.map(row => ({
    policy_id: row.policy_id,
    totalCost: Number(row.total_cost_improvement_pct || 0),
    downtime: Number(row.downtime_reduction_pct || 0),
  }));

  return (
    <Card style={{ padding: 20 }}>
      <SectionHeader title="H0 대비 개선율" />
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(360px, 1fr) minmax(320px, 0.9fr)', gap: 18, alignItems: 'stretch' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #E2E8F0' }}>
                {['정책', '총 운영비용 개선율', '수요 충족률 변화', '대기시간 감소율', '다운타임 감소율'].map((header, index) => (
                  <th key={header} style={{
                    padding: '10px 8px',
                    textAlign: index === 0 ? 'left' : 'right',
                    color: '#64748B',
                    fontSize: 11,
                    fontWeight: 800,
                  }}>
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map(row => (
                <tr key={row.policy_id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                  <td style={{ padding: '10px 8px', fontWeight: 800, color: policyColors[row.policy_id] || '#334155' }}>{row.policy_id}</td>
                  <td style={{ padding: '10px 8px', textAlign: 'right' }}>{formatPercent(row.total_cost_improvement_pct)}</td>
                  <td style={{ padding: '10px 8px', textAlign: 'right' }}>{formatDeltaPoint(row.demand_fulfillment_delta)}</td>
                  <td style={{ padding: '10px 8px', textAlign: 'right' }}>{formatPercent(row.queue_time_reduction_pct)}</td>
                  <td style={{ padding: '10px 8px', textAlign: 'right' }}>{formatPercent(row.downtime_reduction_pct)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData} margin={{ left: 8, right: 16, top: 8, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
            <XAxis dataKey="policy_id" tick={{ fontSize: 11, fill: '#64748B', fontWeight: 700 }} />
            <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} />
            <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E2E8F0' }} />
            <ReferenceLine y={0} stroke="#94A3B8" />
            <Bar dataKey="totalCost" name="총 운영비용 개선율" radius={[4, 4, 0, 0]}>
              {chartData.map(entry => <Cell key={entry.policy_id} fill={entry.totalCost >= 0 ? '#16A34A' : '#DC2626'} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

function StabilityTable({ rows }) {
  return (
    <Card style={{ padding: 20 }}>
      <SectionHeader title="Seed 안정성" />
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #E2E8F0' }}>
              {['정책', '총 운영비용 평균', '총 운영비용 표준편차', '수요 충족률 평균', '수요 충족률 표준편차', '안정성 해석'].map((header, index) => (
                <th key={header} style={{
                  padding: '10px 8px',
                  textAlign: index === 0 || index === 5 ? 'left' : 'right',
                  color: '#64748B',
                  fontSize: 11,
                  fontWeight: 800,
                }}>
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => {
              const highlighted = index === 0;
              return (
                <tr key={row.policy_id} style={{ borderBottom: '1px solid #F1F5F9', background: highlighted ? '#F0FDF4' : 'transparent' }}>
                  <td style={{ padding: '10px 8px', fontWeight: 800, color: policyColors[row.policy_id] || '#334155' }}>{row.policy_id}</td>
                  <td style={{ padding: '10px 8px', textAlign: 'right' }}>{formatNumber(row.total_cost_mean)}</td>
                  <td style={{ padding: '10px 8px', textAlign: 'right' }}>{formatNumber(row.total_cost_std)}</td>
                  <td style={{ padding: '10px 8px', textAlign: 'right' }}>{formatRate(row.demand_fulfillment_rate_mean)}</td>
                  <td style={{ padding: '10px 8px', textAlign: 'right' }}>{formatRate(row.demand_fulfillment_rate_std)}</td>
                  <td style={{ padding: '10px 8px', fontWeight: highlighted ? 800 : 600, color: highlighted ? '#166534' : '#334155' }}>
                    {row.stability_label_ko || DATA_NONE}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

function NotesPanel({ notes, missingKpis, limitations }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1.1fr) minmax(280px, 0.9fr)', gap: 20 }}>
      <Card style={{ padding: 20 }}>
        <SectionHeader title="Trade-off 해석" />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {notes.map((note, index) => (
            <div key={`${note}-${index}`} style={{
              display: 'flex',
              gap: 10,
              alignItems: 'flex-start',
              padding: 10,
              borderRadius: 8,
              background: '#F8FAFC',
              border: '1px solid #E2E8F0',
            }}>
              <TrendingUp size={16} color="#2563EB" style={{ marginTop: 1, flexShrink: 0 }} />
              <span style={{ fontSize: 12, color: '#334155', lineHeight: 1.55 }}>{note}</span>
            </div>
          ))}
        </div>
      </Card>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        {missingKpis.length > 0 && (
          <Card style={{ padding: 18, borderLeft: '4px solid #F59E0B', background: '#FFFBEB' }}>
            <SectionHeader title="누락 KPI" />
            {missingKpis.map(item => (
              <div key={item.kpi} style={{ color: '#92400E', fontSize: 12, lineHeight: 1.6 }}>
                <strong>{item.label_ko}</strong>는 현재 생성된 C5.1 결과 데이터에 포함되지 않았습니다.
                <br />
                따라서 {item.label_ko}는 이번 순위 계산에서 제외했습니다.
              </div>
            ))}
          </Card>
        )}

        <Card style={{ padding: 18 }}>
          <details>
            <summary style={{ cursor: 'pointer', fontSize: 14, fontWeight: 800, color: '#1E293B', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Info size={16} color="#64748B" />
              분석 한계
            </summary>
            <ul style={{ margin: '12px 0 0 18px', color: '#64748B', fontSize: 12, lineHeight: 1.7 }}>
              {limitations.map(item => <li key={item}>{item}</li>)}
            </ul>
          </details>
        </Card>
      </div>
    </div>
  );
}

export default function HeuristicAnalysisPage() {
  const [analysis, setAnalysis] = useState(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    loadDashboardSnapshots().then(snapshot => {
      setAnalysis(snapshot.dashboardAnalysis);
      setLoaded(true);
    });
  }, []);

  const content = useMemo(() => ({
    recommended: analysis?.recommended_policy,
    bestByKpi: analysis?.best_by_kpi || [],
    improvement: analysis?.h0_improvement || [],
    stability: analysis?.stability || [],
    notes: analysis?.tradeoff_notes_ko || [],
    missing: analysis?.missing_kpis || [],
    limitations: analysis?.limitations_ko || [],
  }), [analysis]);

  if (!loaded) {
    return (
      <div style={{ padding: 24 }}>
        <Card style={{ padding: 24, color: '#64748B' }}>불러오는 중</Card>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
        <FallbackPanel />
      </div>
    );
  }

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
      <RecommendedPanel recommended={content.recommended} seedCount={analysis.seed_count} />
      <BestByKpi items={content.bestByKpi} />
      <ImprovementTable rows={content.improvement} />
      <StabilityTable rows={content.stability} />
      <NotesPanel notes={content.notes} missingKpis={content.missing} limitations={content.limitations} />
    </div>
  );
}
