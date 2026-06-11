import { useState, useRef, useEffect } from 'react';
import { Bell, Download, Thermometer, Moon, Sun, Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import { generateDaySnapshot, formatDate } from '../data/simulationData';
import SimulationControls from './SimulationControls';

const pageNames = {
  overview: '전체 현황',
  fleet: 'Fleet 및 PM 상태',
  policy: '정책 비교',
  decisions: '정책 결정 내역',
  analysis: '휴리스틱 분석',
  scenario: '시나리오 재생',
  transfer: '산업 확장성 (Cross-industry Transfer)',
};

const WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토'];
const MONTHS_KR = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월'];

function CalendarPopup({ selectedDate, onSelect, onClose }) {
  const [viewDate, setViewDate] = useState(new Date(selectedDate));
  const ref = useRef(null);

  useEffect(() => {
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) onClose();
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [onClose]);

  const year = viewDate.getFullYear();
  const month = viewDate.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  const cells = [];
  for (let i = 0; i < firstDay; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);

  const selStr = formatDate(selectedDate);
  const todayStr = formatDate(new Date());

  return (
    <div ref={ref} style={{
      position: 'absolute', top: '100%', right: 0, marginTop: 6, zIndex: 100,
      background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 10,
      boxShadow: '0 8px 24px rgba(0,0,0,0.15)', padding: 14, width: 280,
    }}>
      {/* Month nav */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <button onClick={() => setViewDate(new Date(year, month - 1, 1))} style={{
          background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: 'var(--text-sub)',
        }}><ChevronLeft size={16} /></button>
        <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-main)' }}>
          {year}년 {MONTHS_KR[month]}
        </span>
        <button onClick={() => setViewDate(new Date(year, month + 1, 1))} style={{
          background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: 'var(--text-sub)',
        }}><ChevronRight size={16} /></button>
      </div>

      {/* Weekday headers */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 2, marginBottom: 4 }}>
        {WEEKDAYS.map(w => (
          <div key={w} style={{ textAlign: 'center', fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', padding: '4px 0' }}>
            {w}
          </div>
        ))}
      </div>

      {/* Day cells */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 2 }}>
        {cells.map((day, i) => {
          if (!day) return <div key={`e${i}`} />;
          const cellDate = new Date(year, month, day);
          const cellStr = formatDate(cellDate);
          const isSelected = cellStr === selStr;
          const isToday = cellStr === todayStr;
          return (
            <button
              key={day}
              onClick={() => { onSelect(cellDate); onClose(); }}
              style={{
                width: '100%', aspectRatio: '1', border: 'none', borderRadius: 6,
                fontSize: 12, fontWeight: isSelected ? 700 : 400, cursor: 'pointer',
                fontFamily: 'inherit',
                background: isSelected ? '#8A4931' : isToday ? 'var(--primary-soft)' : 'transparent',
                color: isSelected ? '#fff' : isToday ? '#8A4931' : 'var(--text-body)',
                transition: 'background 0.1s',
              }}
            >
              {day}
            </button>
          );
        })}
      </div>

      {/* Today button */}
      <button
        onClick={() => { onSelect(new Date()); onClose(); }}
        style={{
          width: '100%', marginTop: 8, padding: '6px 0', borderRadius: 6,
          border: '1px solid var(--border)', background: 'var(--bg-page)',
          color: 'var(--text-sub)', fontSize: 11, fontWeight: 600, cursor: 'pointer',
          fontFamily: 'inherit',
        }}
      >
        오늘로 이동
      </button>
    </div>
  );
}

export default function Header({ activePage, timeSpeed = 1, darkMode = false, onDarkModeToggle, simDate, onSimDateChange, isLive, onSetLive, playing = true, onPlayPause, onStep, onSpeedChange, onReset }) {
  const [calendarOpen, setCalendarOpen] = useState(false);

  // Use simulation data for the selected date, or live data
  const currentDate = simDate || new Date();
  const snapshot = generateDaySnapshot(currentDate);
  const displayDate = isLive ? formatDate(new Date()) : snapshot.date;
  const temperature = snapshot.temperature;

  const handleDateSelect = (date) => {
    if (onSimDateChange) onSimDateChange(date);
    if (onSetLive) onSetLive(false);
  };

  const handleLiveClick = () => {
    if (onSetLive) onSetLive(true);
    if (onSimDateChange) onSimDateChange(new Date());
    if (onSpeedChange) onSpeedChange(1);
  };

  return (
    <header style={{
      height: 56, background: 'var(--bg-card)', borderBottom: '1px solid var(--border)',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 24px', flexShrink: 0,
    }}>
      <h1 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
        {pageNames[activePage]}
      </h1>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {/* Simulation transport controls (presentation recording) */}
        <SimulationControls
          playing={playing}
          speed={timeSpeed}
          onPlayPause={onPlayPause}
          onStep={onStep}
          onSpeedChange={onSpeedChange}
          onReset={onReset}
        />

        <span style={{
          fontSize: 11, fontWeight: 600, color: '#8A4931',
          background: 'var(--primary-soft)', padding: '4px 10px', borderRadius: 6,
        }}>
          근무조 {snapshot.shift}
        </span>

        {/* Date with calendar */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setCalendarOpen(v => !v)}
            style={{
              display: 'flex', alignItems: 'center', gap: 4,
              padding: '4px 10px', borderRadius: 6,
              border: '1px solid var(--border)', background: 'var(--bg-card)',
              fontSize: 12, color: 'var(--text-body)', cursor: 'pointer',
              fontFamily: 'inherit', fontWeight: 500,
            }}
          >
            <Calendar size={13} color="var(--text-sub)" />
            {displayDate}
            {isLive && (
              <span style={{
                width: 6, height: 6, borderRadius: '50%', background: '#16A34A',
                marginLeft: 2, animation: 'pulse 2s infinite',
              }} />
            )}
          </button>
          {calendarOpen && (
            <CalendarPopup
              selectedDate={currentDate}
              onSelect={handleDateSelect}
              onClose={() => setCalendarOpen(false)}
            />
          )}
        </div>

        <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: 'var(--text-sub)' }}>
          <Thermometer size={14} /> {temperature}°C
        </span>

        {/* Dark mode toggle */}
        <button
          onClick={onDarkModeToggle}
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            width: 32, height: 32, borderRadius: 8, border: '1px solid var(--border)',
            background: darkMode ? '#334155' : '#F8FAFC', cursor: 'pointer',
            transition: 'all 0.15s',
          }}
          title={darkMode ? '라이트 모드' : '다크 모드'}
        >
          {darkMode ? <Sun size={16} color="#F59E0B" /> : <Moon size={16} color="#64748B" />}
        </button>

        <div style={{ position: 'relative', cursor: 'pointer' }}>
          <Bell size={18} color="var(--text-sub)" />
          {snapshot.riskTrucks > 0 && (
            <span style={{
              position: 'absolute', top: -4, right: -6,
              background: '#DC2626', color: '#fff', fontSize: 9, fontWeight: 700,
              width: 16, height: 16, borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              {snapshot.riskTrucks}
            </span>
          )}
        </div>
        <button style={{
          display: 'flex', alignItems: 'center', gap: 6,
          padding: '6px 12px', borderRadius: 6,
          border: '1px solid var(--border)', background: 'var(--bg-card)',
          fontSize: 12, color: 'var(--text-body)', cursor: 'pointer',
          fontFamily: 'inherit',
        }}>
          <Download size={14} /> 내보내기
        </button>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
      `}</style>
    </header>
  );
}
