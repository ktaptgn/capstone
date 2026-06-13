import { useState, useEffect, useRef } from 'react';
import { Cloud, Thermometer, Gauge } from 'lucide-react';
import { facilities, routes, truckMarkers } from '../data/mineMap';
import C5OperationMap3D from './map3d/C5OperationMap3D';

/* ── Colors matching 3D map ── */
const TERRAIN_BG = '#B35F44';
const ROAD_COLOR = '#36454F';
const GRID_COLOR = '#ffffff18';

const statusColors = {
  running: '#22C55E', warning: '#F97316', critical: '#EF4444',
  'in-progress': '#7C3AED', standby: '#3B82F6', normal: '#22C55E',
};

const facilityHeaderColors = {
  shovel: '#16A34A', crusher: '#2563EB', pm_bay: '#7C3AED',
  standby: '#6B7280', dispatch: '#8A4931',
};

/* ── 2D route interpolation ── */
function parseSVGPath(d) {
  const nums = d.match(/-?\d+\.?\d*/g);
  if (!nums || nums.length < 4) return [];
  const points = [];
  for (let i = 0; i < nums.length; i += 2) {
    points.push({ x: parseFloat(nums[i]), y: parseFloat(nums[i + 1]) });
  }
  return points;
}

function lerp2D(points, t) {
  if (points.length < 2) return points[0] || { x: 0, y: 0 };
  const clampT = Math.max(0, Math.min(1, t));
  const totalSeg = points.length - 1;
  const segFloat = clampT * totalSeg;
  const segIdx = Math.min(Math.floor(segFloat), totalSeg - 1);
  const localT = segFloat - segIdx;
  const a = points[segIdx];
  const b = points[segIdx + 1];
  return { x: a.x + (b.x - a.x) * localT, y: a.y + (b.y - a.y) * localT };
}

/* ── Compound routes: full shovel→crusher/PM paths via main road ── */
const COMPOUND_ROUTES = {
  full_sa_c1: [
    {x:60,y:55},{x:100,y:95},
    {x:120,y:95},{x:150,y:150},{x:280,y:155},{x:380,y:160},{x:420,y:130},
    {x:460,y:145},{x:500,y:195},
  ],
  full_sb_c2: [
    {x:80,y:155},{x:140,y:120},
    {x:150,y:150},{x:280,y:155},{x:380,y:160},{x:420,y:130},
    {x:520,y:120},{x:580,y:155},
  ],
  full_sc_c1: [
    {x:140,y:210},{x:200,y:155},
    {x:280,y:155},{x:380,y:160},{x:420,y:130},
    {x:460,y:145},{x:500,y:195},
  ],
  full_sa_c2: [
    {x:60,y:55},{x:100,y:95},
    {x:120,y:95},{x:150,y:150},{x:280,y:155},{x:380,y:160},{x:420,y:130},
    {x:520,y:120},{x:580,y:155},
  ],
  full_sb_c1: [
    {x:80,y:155},{x:140,y:120},
    {x:150,y:150},{x:280,y:155},{x:380,y:160},{x:420,y:130},
    {x:460,y:145},{x:500,y:195},
  ],
  full_sc_pm: [
    {x:140,y:210},{x:200,y:155},
    {x:280,y:155},{x:380,y:160},{x:420,y:130},{x:480,y:115},
    {x:520,y:55},
  ],
  full_sa_pm: [
    {x:60,y:55},{x:100,y:95},
    {x:120,y:95},{x:150,y:150},{x:280,y:155},{x:380,y:160},{x:420,y:130},{x:480,y:115},
    {x:520,y:55},
  ],
};

// All running trucks now traverse full compound routes (shovel→crusher/PM)
const TRUCK_ROUTE_MAP = {
  T01: 'full_sa_c1',
  T02: 'full_sb_c2',
  T03: 'full_sc_c1',
  T05: 'full_sa_c2',
  T07: 'full_sa_pm',
  T09: 'full_sc_pm',
  T13: 'full_sb_c1',
};

/* ── Virtual weather data for satellite view ── */
const WEATHER_DATA = {
  location: 'C5 Escondida Mine, Chile',
  lat: '-24.27°S', lon: '-69.07°W', alt: '3,100m',
  temperature: 34, tempUnit: '°C',
  humidity: 18,
  clouds: 12, cloudDesc: '맑음 (Clear)',
  pressure: 680, pressureUnit: 'hPa',
  wind: '12 km/h NW',
  visibility: '25 km',
  uvIndex: 11,
};

/* ── 2D SVG map content (shared between 2d and satellite modes) ── */
function Map2DSVG({ truckPositions }) {
  return (
    <svg viewBox="0 0 660 280" style={{ width: '100%', height: 'auto', borderRadius: 8 }}>
      <defs>
        <pattern id="grid2d" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M 20 0 L 0 0 0 20" fill="none" stroke={GRID_COLOR} strokeWidth="0.5" />
        </pattern>
      </defs>
      <rect width="660" height="280" fill={TERRAIN_BG} rx="4" />
      <rect width="660" height="280" fill="url(#grid2d)" />

      {routes.map(r => (
        <path key={r.id} d={r.path} fill="none"
          stroke={r.riskLevel === 'high' ? '#F59E0B' : ROAD_COLOR}
          strokeWidth={r.riskLevel === 'high' ? 4 : 3}
          strokeDasharray={r.riskLevel === 'high' ? '8 4' : 'none'}
          opacity={r.riskLevel === 'high' ? 0.7 : 0.85}
          strokeLinecap="round"
        />
      ))}

      <ellipse cx={290} cy={155} rx={60} ry={35} fill="none" stroke="#F3E7E2" strokeWidth={1.5} strokeDasharray="6 3" opacity={0.5} />
      <text x={290} y={140} textAnchor="middle" fontSize={8} fill="#F3E7E2" fontWeight={600} opacity={0.7}>Dispatch Zone</text>

      {facilities.map(f => {
        const hdrColor = facilityHeaderColors[f.type] || '#64748B';
        const w = f.type === 'standby' ? 70 : 60;
        const h = 36;
        const isDashed = f.type === 'standby';
        return (
          <g key={f.id}>
            <rect x={f.x - w/2} y={f.y - h/2} width={w} height={h} rx={4}
              fill="rgba(255,255,255,0.85)" stroke={isDashed ? '#9CA3B8' : hdrColor}
              strokeWidth={f.type === 'pm_bay' ? 2 : 1}
              strokeDasharray={isDashed ? '4 2' : 'none'}
            />
            <rect x={f.x - w/2} y={f.y - h/2} width={w} height={12} rx={0}
              fill={hdrColor} opacity={0.2}
            />
            <text x={f.x} y={f.y - h/2 + 9} textAnchor="middle" fontSize={7} fill={hdrColor} fontWeight={700}>
              {f.name}
            </text>
            <text x={f.x} y={f.y + 6} textAnchor="middle" fontSize={8} fill="#334155" fontWeight={600}>
              {f.type === 'pm_bay' ? `${f.occupied}/${f.capacity} occupied` :
               f.queue !== undefined && f.queue > 0 ? `Queue: ${f.queue}` :
               f.type === 'standby' ? '' : 'Queue: 0'}
            </text>
          </g>
        );
      })}

      {truckPositions.map(t => {
        const col = statusColors[t.status] || '#6B7280';
        return (
          <g key={t.truckId}>
            <circle cx={t.x} cy={t.y} r={10} fill="rgba(255,255,255,0.9)" stroke={col} strokeWidth={2.5} />
            <circle cx={t.x + 5} cy={t.y - 5} r={3} fill={col} />
            <text x={t.x} y={t.y + 3} textAnchor="middle" fontSize={6} fill={col} fontWeight={700}>
              {t.truckId}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

/* ── Weather overlay panel for satellite view ── */
function WeatherPanel({ onClose }) {
  const w = WEATHER_DATA;
  const cardStyle = {
    background: 'rgba(255,255,255,0.92)', borderRadius: 8, padding: '10px 14px',
    border: '1px solid #E2E8F0', flex: 1,
  };
  return (
    <div style={{
      position: 'absolute', top: 8, right: 8, width: 260, zIndex: 10,
      background: 'rgba(15,23,42,0.88)', borderRadius: 10, padding: 12,
      color: '#fff', backdropFilter: 'blur(8px)',
      boxShadow: '0 8px 24px rgba(0,0,0,0.3)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <div style={{ fontSize: 12, fontWeight: 700 }}>C5 Mine Weather</div>
        <button onClick={onClose} style={{
          background: 'rgba(255,255,255,0.2)', border: 'none', borderRadius: 4,
          color: '#fff', fontSize: 10, padding: '2px 6px', cursor: 'pointer',
        }}>
          Close
        </button>
      </div>
      <div style={{ fontSize: 9, color: '#94A3B8', marginBottom: 8 }}>
        {w.location} ({w.lat}, {w.lon}) Alt: {w.alt}
      </div>

      {/* Temperature */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
        <div style={cardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 4 }}>
            <Thermometer size={12} color="#DC2626" />
            <span style={{ fontSize: 9, color: '#64748B', fontWeight: 600 }}>기온</span>
          </div>
          <div style={{ fontSize: 20, fontWeight: 700, color: '#1E293B' }}>{w.temperature}{w.tempUnit}</div>
          <div style={{ fontSize: 9, color: '#64748B' }}>습도 {w.humidity}%</div>
        </div>
        <div style={cardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 4 }}>
            <Cloud size={12} color="#3B82F6" />
            <span style={{ fontSize: 9, color: '#64748B', fontWeight: 600 }}>구름</span>
          </div>
          <div style={{ fontSize: 20, fontWeight: 700, color: '#1E293B' }}>{w.clouds}%</div>
          <div style={{ fontSize: 9, color: '#64748B' }}>{w.cloudDesc}</div>
        </div>
      </div>

      {/* Pressure + Wind */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
        <div style={cardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 4 }}>
            <Gauge size={12} color="#8B5CF6" />
            <span style={{ fontSize: 9, color: '#64748B', fontWeight: 600 }}>기압</span>
          </div>
          <div style={{ fontSize: 16, fontWeight: 700, color: '#1E293B' }}>{w.pressure}</div>
          <div style={{ fontSize: 9, color: '#64748B' }}>{w.pressureUnit}</div>
        </div>
        <div style={cardStyle}>
          <div style={{ fontSize: 9, color: '#64748B', fontWeight: 600, marginBottom: 4 }}>바람 / 가시거리</div>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#1E293B' }}>{w.wind}</div>
          <div style={{ fontSize: 9, color: '#64748B' }}>가시 {w.visibility} | UV {w.uvIndex}</div>
        </div>
      </div>

      {/* Pressure map placeholder */}
      <div style={{
        background: 'linear-gradient(135deg, #1e3a5f 0%, #3b82f6 30%, #60a5fa 50%, #f59e0b 80%, #dc2626 100%)',
        borderRadius: 6, height: 56, display: 'flex', alignItems: 'center', justifyContent: 'center',
        position: 'relative', overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute', width: 10, height: 10, borderRadius: '50%',
          background: '#fff', border: '2px solid #DC2626',
          top: '50%', left: '45%', transform: 'translate(-50%,-50%)',
        }} />
        <span style={{ fontSize: 9, fontWeight: 700, color: '#fff', textShadow: '0 1px 3px rgba(0,0,0,0.5)', zIndex: 1 }}>
          기압 분포도 (C5 Mine)
        </span>
      </div>
    </div>
  );
}

export default function MineMap({ timeSpeed = 1 }) {
  const [mapMode, setMapMode] = useState('3d');
  const [showWeather, setShowWeather] = useState(false);
  const [truckPositions, setTruckPositions] = useState(() =>
    truckMarkers.map(t => ({ ...t, progress: Math.random() * 0.8 + 0.1, dir: 1 }))
  );
  const animRef = useRef(null);

  const routePoints = useRef({});
  useEffect(() => {
    const map = {};
    // Parse SVG routes (kept for rendering)
    routes.forEach(r => { map[r.id] = parseSVGPath(r.path); });
    // Add compound routes (for truck animation)
    Object.entries(COMPOUND_ROUTES).forEach(([id, pts]) => { map[id] = pts; });
    routePoints.current = map;
  }, []);

  // 2D truck animation loop — runs for both '2d' and 'satellite' modes
  useEffect(() => {
    if (mapMode === '3d') return;

    let lastTime = performance.now();
    const animate = (now) => {
      const delta = (now - lastTime) / 1000;
      lastTime = now;

      setTruckPositions(prev => prev.map(t => {
        if (t.status === 'standby' || t.status === 'in-progress') return t;

        const routeId = TRUCK_ROUTE_MAP[t.truckId];
        const pts = routeId && routePoints.current[routeId];
        if (!pts || pts.length < 2) return t;

        const speed = 0.02 * timeSpeed;
        let newProgress = t.progress + speed * delta * t.dir;
        let newDir = t.dir;
        if (newProgress >= 1) { newProgress = 1; newDir = -1; }
        else if (newProgress <= 0) { newProgress = 0; newDir = 1; }

        const pos = lerp2D(pts, newProgress);
        return { ...t, x: pos.x, y: pos.y, progress: newProgress, dir: newDir };
      }));

      animRef.current = requestAnimationFrame(animate);
    };
    animRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animRef.current);
  }, [mapMode, timeSpeed]);

  const MAP_MODES = [
    { key: '2d', label: '2D Map' },
    { key: '3d', label: '3D Map' },
    { key: 'satellite', label: 'Satellite' },
  ];

  return (
    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 12, boxShadow: 'var(--shadow)', padding: 16, overflow: 'hidden', position: 'relative' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-main)' }}>Mine Operation Map</h3>
          <span style={{ fontSize: 11, color: '#8A4931', fontWeight: 600, background: 'var(--primary-soft)', padding: '3px 8px', borderRadius: 4 }}>
            Policy: H3 Cost-weighted
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', padding: 2, border: '1px solid var(--border)', borderRadius: 7, background: 'var(--divider)' }}>
          {MAP_MODES.map(mode => {
            const active = mapMode === mode.key;
            return (
              <button
                key={mode.key}
                type="button"
                onClick={() => { setMapMode(mode.key); setShowWeather(false); }}
                style={{
                  border: 0, borderRadius: 5,
                  background: active ? '#8A4931' : 'transparent',
                  color: active ? '#fff' : 'var(--text-sub)',
                  padding: '4px 9px', fontSize: 11, fontWeight: 700, cursor: 'pointer',
                }}
              >
                {mode.label}
              </button>
            );
          })}
        </div>
      </div>

      {mapMode === '3d' ? (
        <C5OperationMap3D timeSpeed={timeSpeed} />
      ) : (
        <div style={{ position: 'relative' }}>
          <Map2DSVG truckPositions={truckPositions} />

          {/* Satellite mode: weather button */}
          {mapMode === 'satellite' && (
            <button
              onClick={() => setShowWeather(v => !v)}
              style={{
                position: 'absolute', top: 8, left: 8, zIndex: 5,
                display: 'flex', alignItems: 'center', gap: 4,
                padding: '5px 10px', borderRadius: 6,
                border: 'none', background: 'rgba(15,23,42,0.75)',
                color: '#fff', fontSize: 11, fontWeight: 700, cursor: 'pointer',
                backdropFilter: 'blur(4px)',
              }}
            >
              <Cloud size={14} /> 기후 정보
            </button>
          )}

          {/* Weather overlay */}
          {mapMode === 'satellite' && showWeather && (
            <WeatherPanel onClose={() => setShowWeather(false)} />
          )}

          <div style={{ display: 'flex', gap: 16, marginTop: 10, justifyContent: 'center' }}>
            {[['Running','#22C55E'],['Warning','#F97316'],['Critical','#EF4444'],['PM','#7C3AED'],['Standby','#3B82F6']].map(([label, color]) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 10, color: 'var(--text-sub)' }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: color }} /> {label}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
