import { useState, useCallback } from 'react';
import { getHIColor } from '../../utils/statusColors';
import type { TireComponent } from '../../policies/types';
import TruckModel3D from './TruckModel3D';

interface EquipmentViewerProps {
  tires: TireComponent[];
}

function SVGFallback({ tires }: { tires: TireComponent[] }) {
  const fl = tires.find(t => t.position === 'FL');
  const fr = tires.find(t => t.position === 'FR');
  const rl = tires.find(t => t.position === 'RL');
  const rr = tires.find(t => t.position === 'RR');

  const renderTire = (tire: TireComponent | undefined, x: number, y: number) => {
    if (!tire) return null;
    const color = getHIColor(tire.healthIndex);
    return (
      <g>
        <circle cx={x} cy={y} r={22} fill="none" stroke={color} strokeWidth={5} opacity={0.3} />
        <circle cx={x} cy={y} r={22} fill="none" stroke={color} strokeWidth={5}
          strokeDasharray={`${(tire.healthIndex / 100) * 138} 138`}
          transform={`rotate(-90 ${x} ${y})`}
        />
        <text x={x} y={y - 4} textAnchor="middle" fill={color} fontSize={11} fontWeight="bold">
          {tire.healthIndex}%
        </text>
        <text x={x} y={y + 10} textAnchor="middle" fill="#64748B" fontSize={8}>
          {tire.position}
        </text>
      </g>
    );
  };

  return (
    <div className="bg-gray-50 rounded-lg p-2" style={{ backgroundImage: 'radial-gradient(circle, #e5e7eb 1px, transparent 1px)', backgroundSize: '16px 16px' }}>
      <svg viewBox="0 0 280 200" className="w-full">
        <rect x={90} y={30} width={100} height={140} rx={8} fill="#F3E7E2" stroke="#8A4931" strokeWidth={1.5} opacity={0.6} />
        <rect x={105} y={15} width={70} height={30} rx={5} fill="#F3E7E2" stroke="#8A4931" strokeWidth={1.5} opacity={0.6} />
        <path d="M95 55 L185 55 L190 165 L85 165 Z" fill="none" stroke="#8A4931" strokeWidth={1} opacity={0.3} strokeDasharray="4 2" />
        <text x={140} y={115} textAnchor="middle" fill="#8A4931" fontSize={10} fontWeight="600" opacity={0.5}>
          797F
        </text>
        {renderTire(fl, 55, 50)}
        {renderTire(fr, 225, 50)}
        {renderTire(rl, 55, 155)}
        {renderTire(rr, 225, 155)}
      </svg>
    </div>
  );
}

export default function EquipmentViewer({ tires }: EquipmentViewerProps) {
  const [viewMode, setViewMode] = useState<'3d' | '2d'>('3d');
  const handleWebGLError = useCallback(() => setViewMode('2d'), []);

  const hasTires = tires.length > 0;

  return (
    <div className="bg-white rounded-xl p-3 shadow-sm border border-border">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-text-main">장비 상태 보기</h3>
        {hasTires && (
          <button
            onClick={() => setViewMode(v => v === '3d' ? '2d' : '3d')}
            className="text-[10px] px-2 py-0.5 rounded-full border border-border text-text-sub hover:bg-gray-50 transition-colors"
          >
            {viewMode === '3d' ? '2D 보기' : '3D 보기'}
          </button>
        )}
      </div>

      {viewMode === '3d' && hasTires ? (
        <TruckModel3D tires={tires} onError={handleWebGLError} />
      ) : (
        <SVGFallback tires={tires} />
      )}

      <div className="flex justify-center gap-3 mt-2">
        {[
          { label: '긴급', color: '#DC2626' },
          { label: '주의', color: '#F59E0B' },
          { label: '관찰', color: '#F97316' },
          { label: '정상', color: '#16A34A' },
        ].map(item => (
          <div key={item.label} className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
            <span className="text-[9px] text-text-sub">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
