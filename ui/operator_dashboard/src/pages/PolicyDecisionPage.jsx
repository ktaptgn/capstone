import { useState } from 'react';
import { FileText, CheckCircle, PauseCircle, XCircle, Download, Clock } from 'lucide-react';
import Card from '../components/Card';
import SectionHeader from '../components/SectionHeader';

const statusConfig = {
  approved: { label: '승인', icon: CheckCircle, color: '#16A34A', bg: '#DCFCE7', darkBg: 'rgba(22,163,74,0.15)' },
  hold:     { label: '보류', icon: PauseCircle, color: '#D97706', bg: '#FEF3C7', darkBg: 'rgba(217,119,6,0.15)' },
  rejected: { label: '거절', icon: XCircle,     color: '#DC2626', bg: '#FEE2E2', darkBg: 'rgba(220,38,38,0.15)' },
};

export default function PolicyDecisionPage({ decisionLog = [], onAddReport }) {
  const [editingId, setEditingId] = useState(null);
  const [reportText, setReportText] = useState('');
  const [filter, setFilter] = useState('all');

  const filtered = filter === 'all'
    ? decisionLog
    : decisionLog.filter(d => d.decision === filter);

  const handleSaveReport = (id) => {
    if (onAddReport && reportText.trim()) {
      onAddReport(id, reportText.trim());
    }
    setEditingId(null);
    setReportText('');
  };

  const stats = {
    approved: decisionLog.filter(d => d.decision === 'approved').length,
    hold: decisionLog.filter(d => d.decision === 'hold').length,
    rejected: decisionLog.filter(d => d.decision === 'rejected').length,
  };

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Summary stats */}
      <div style={{ display: 'flex', gap: 16 }}>
        {Object.entries(statusConfig).map(([key, cfg]) => (
          <Card key={key} style={{ flex: 1, padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{
                width: 40, height: 40, borderRadius: 8,
                background: `${cfg.color}14`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <cfg.icon size={20} color={cfg.color} />
              </div>
              <div>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  {cfg.label}
                </div>
                <div style={{ fontSize: 24, fontWeight: 700, color: cfg.color }}>{stats[key]}</div>
              </div>
            </div>
          </Card>
        ))}
        <Card style={{ flex: 1, padding: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 40, height: 40, borderRadius: 8,
              background: '#8A493114',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <FileText size={20} color="#8A4931" />
            </div>
            <div>
              <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                총 결정
              </div>
              <div style={{ fontSize: 24, fontWeight: 700, color: '#8A4931' }}>{decisionLog.length}</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Filter + content */}
      <Card style={{ padding: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <SectionHeader title="정책 결정 내역" />
          <div style={{ display: 'flex', gap: 4, border: '1px solid var(--border)', borderRadius: 8, padding: 2 }}>
            {[
              { key: 'all', label: '전체' },
              { key: 'approved', label: '승인' },
              { key: 'hold', label: '보류' },
              { key: 'rejected', label: '거절' },
            ].map(f => (
              <button
                key={f.key}
                onClick={() => setFilter(f.key)}
                style={{
                  padding: '4px 10px', borderRadius: 6, border: 'none',
                  fontSize: 11, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
                  background: filter === f.key ? '#8A4931' : 'transparent',
                  color: filter === f.key ? '#fff' : 'var(--text-sub)',
                }}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {filtered.length === 0 ? (
          <div style={{
            textAlign: 'center', padding: '48px 0', color: 'var(--text-muted)',
          }}>
            <FileText size={40} style={{ margin: '0 auto 12px', opacity: 0.3 }} />
            <div style={{ fontSize: 14, fontWeight: 600 }}>결정 내역이 없습니다</div>
            <div style={{ fontSize: 12, marginTop: 4 }}>
              전체 현황 페이지의 Recommended Actions에서 승인/보류/거절하면 기록됩니다.
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {filtered.map((entry) => {
              const cfg = statusConfig[entry.decision] || statusConfig.hold;
              const CfgIcon = cfg.icon;
              return (
                <div key={entry.id} style={{
                  border: '1px solid var(--border)', borderRadius: 10, overflow: 'hidden',
                }}>
                  {/* Decision header */}
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: 12,
                    padding: '12px 16px', background: `${cfg.color}08`,
                    borderBottom: '1px solid var(--border)',
                  }}>
                    <CfgIcon size={18} color={cfg.color} />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-main)' }}>
                        Action #{entry.actionId}: {entry.actionText}
                      </div>
                      <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
                        <span style={{
                          fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 4,
                          background: cfg.bg, color: cfg.color,
                        }}>
                          {cfg.label}
                        </span>
                        <span style={{ fontSize: 10, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 3 }}>
                          <Clock size={10} /> {entry.timestamp}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Policy values at decision time */}
                  <div style={{ padding: '10px 16px', borderBottom: '1px solid var(--divider)' }}>
                    <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                      결정 시점 정책 값
                    </div>
                    <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                      {entry.policyValues && Object.entries(entry.policyValues).map(([k, v]) => (
                        <div key={k} style={{ fontSize: 11 }}>
                          <span style={{ color: 'var(--text-sub)' }}>{k}: </span>
                          <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{v}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Report / notes */}
                  <div style={{ padding: '10px 16px' }}>
                    {entry.report ? (
                      <div>
                        <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>
                          운영자 보고서 <span style={{ fontSize: 9, color: '#8A4931', fontWeight: 400 }}>(정책 학습 데이터)</span>
                        </div>
                        <div style={{
                          fontSize: 12, color: 'var(--text-body)', lineHeight: 1.6,
                          padding: '8px 12px', background: 'var(--divider)', borderRadius: 6,
                          borderLeft: '3px solid #8A4931',
                        }}>
                          {entry.report}
                        </div>
                      </div>
                    ) : editingId === entry.id ? (
                      <div>
                        <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>
                          보고서 작성 <span style={{ fontSize: 9, color: '#8A4931', fontWeight: 400 }}>(정책 학습 데이터로 사용됩니다)</span>
                        </div>
                        <textarea
                          value={reportText}
                          onChange={e => setReportText(e.target.value)}
                          placeholder="이 정책을 선택/거절한 이유를 간략히 기록하세요. 이 데이터는 향후 정책 학습에 활용됩니다."
                          rows={3}
                          style={{
                            width: '100%', padding: '8px 10px', borderRadius: 6,
                            border: '1px solid var(--border)', fontSize: 12, fontFamily: 'inherit',
                            color: 'var(--text-body)', resize: 'vertical', background: 'var(--bg-page)',
                            boxSizing: 'border-box',
                          }}
                        />
                        <div style={{ display: 'flex', gap: 8, marginTop: 8, justifyContent: 'flex-end' }}>
                          <button
                            onClick={() => { setEditingId(null); setReportText(''); }}
                            style={{
                              padding: '6px 14px', borderRadius: 6, border: '1px solid var(--border)',
                              background: 'var(--bg-card)', color: 'var(--text-sub)',
                              fontSize: 11, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
                            }}
                          >
                            취소
                          </button>
                          <button
                            onClick={() => handleSaveReport(entry.id)}
                            disabled={!reportText.trim()}
                            style={{
                              padding: '6px 14px', borderRadius: 6, border: 'none',
                              background: reportText.trim() ? '#8A4931' : 'var(--border)',
                              color: '#fff', fontSize: 11, fontWeight: 600,
                              cursor: reportText.trim() ? 'pointer' : 'default',
                              fontFamily: 'inherit',
                            }}
                          >
                            저장
                          </button>
                        </div>
                      </div>
                    ) : (
                      <button
                        onClick={() => setEditingId(entry.id)}
                        style={{
                          width: '100%', padding: '8px 0', borderRadius: 6,
                          border: '1px dashed var(--border)', background: 'transparent',
                          color: 'var(--text-sub)', fontSize: 11, fontWeight: 600,
                          cursor: 'pointer', fontFamily: 'inherit',
                        }}
                      >
                        + 보고서 작성 (정책 학습 데이터)
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>
    </div>
  );
}
