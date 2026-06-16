import { Plane, Wind, Atom, Ship, Trees, ArrowRight } from 'lucide-react';
import Card from '../components/Card';
import SectionHeader from '../components/SectionHeader';

const INDUSTRIES = [
  {
    icon: Plane,
    color: '#DC2626',
    title: '소방 · 군용 헬기 정비',
    asset: '기체 / 엔진',
    degrade: '비행시간·사이클 기반 부품 열화',
    demand: '출동·임무 대기 가용성',
    note: '안전 임계가 높아 사후 정비 불가 → 상태 기반 예방 정비 의사결정이 직접 전이.',
  },
  {
    icon: Wind,
    color: '#0891B2',
    title: '풍력 터빈 정비',
    asset: '기어박스 / 블레이드 / 베어링',
    degrade: '진동·온도 기반 건강지수(HI) 저하',
    demand: '발전량(MWh) 목표',
    note: '해상 접근 비용이 커 PM 윈도우·큐 최적화가 핵심 — H3/H4 휴리스틱과 동일 구조.',
  },
  {
    icon: Atom,
    color: '#7C3AED',
    title: '원자력 · 발전소 핵심 설비',
    asset: '펌프 / 밸브 / 열교환기',
    degrade: '마모·부식 누적, 안전 임계',
    demand: '안정 출력 + 규제 가동률',
    note: '정비 슬롯이 제한적 → "지금 정비 vs 가동 유지" 트레이드오프가 본 과제와 동형.',
  },
  {
    icon: Ship,
    color: '#2563EB',
    title: '선박 · 해양 플랜트',
    asset: '추진 엔진 / 크레인 / 펌프',
    degrade: '운항시간·하중 기반 열화',
    demand: '운항 스케줄 · 하역 처리량',
    note: '항해 중 정비 불가 → 입항 윈도우에 PM 배치, 큐·비용 균형 의사결정 전이.',
  },
  {
    icon: Trees,
    color: '#16A34A',
    title: '임업 · 건설 중장비',
    asset: '오프로드 차량 / 유압 장비',
    degrade: '가혹 노면·먼지 기반 빠른 마모',
    demand: '작업 물량 · 가동률',
    note: '광산 트럭과 가장 유사 — 노면 마모·타이어 HI 모델이 거의 그대로 적용.',
  },
];

export default function CrossIndustryPage() {
  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Common structure */}
      <Card style={{ padding: 20 }}>
        <SectionHeader title="공통 구조 (Transfer Mapping)" />
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginTop: 12 }}>
          {['자산 열화(HI)', '수요/임무 목표', '정비 용량(큐·Bay)', '비용·위험 가중', '정책 추천(H0–H4)', '운영자 승인/보류/거절'].map((step, i, arr) => (
            <div key={step} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{
                fontSize: 12, fontWeight: 700, color: '#8A4931', background: 'var(--primary-soft)',
                padding: '6px 12px', borderRadius: 8,
              }}>{step}</span>
              {i < arr.length - 1 && <ArrowRight size={16} color="var(--text-muted)" />}
            </div>
          ))}
        </div>
      </Card>

      {/* Industries */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 16 }}>
        {INDUSTRIES.map(ind => {
          const Icon = ind.icon;
          return (
            <Card key={ind.title} style={{ padding: 18, borderTop: `3px solid ${ind.color}` }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <div style={{
                  width: 36, height: 36, borderRadius: 8, background: `${ind.color}15`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <Icon size={20} color={ind.color} />
                </div>
                <h3 style={{ margin: 0, fontSize: 14, fontWeight: 800, color: 'var(--text-main)' }}>{ind.title}</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 12 }}>
                {[
                  ['자산 (= 트럭)', ind.asset],
                  ['열화 (= HI)', ind.degrade],
                  ['수요 (= loads)', ind.demand],
                ].map(([k, v]) => (
                  <div key={k} style={{ display: 'flex', gap: 8 }}>
                    <span style={{ color: 'var(--text-muted)', fontWeight: 700, width: 96, flexShrink: 0 }}>{k}</span>
                    <span style={{ color: 'var(--text-body)' }}>{v}</span>
                  </div>
                ))}
              </div>
              <div style={{
                marginTop: 12, fontSize: 11, color: 'var(--text-sub)', lineHeight: 1.55,
                background: 'var(--divider)', borderRadius: 8, padding: '8px 10px',
              }}>
                {ind.note}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
