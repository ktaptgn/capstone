import { Play, Pause, SkipForward, RotateCcw } from 'lucide-react';

const SPEEDS = [1, 2, 4];

// Presentation transport controls for the operation map / replay.
// playing + speed drive the map animation; Step nudges one frame while paused;
// Reset re-seeds truck positions.
export default function SimulationControls({
  playing = true,
  speed = 1,
  onPlayPause,
  onStep,
  onSpeedChange,
  onReset,
}) {
  const iconBtn = (extra = {}) => ({
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    width: 28, height: 26, borderRadius: 6, border: 'none', cursor: 'pointer',
    background: 'transparent', color: 'var(--text-sub)', fontFamily: 'inherit',
    ...extra,
  });

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 2,
      border: '1px solid var(--border)', borderRadius: 8, padding: 2,
      background: '#F8FAFC',
    }}>
      {/* Reset */}
      <button onClick={onReset} style={iconBtn()} title="Reset scenario">
        <RotateCcw size={13} />
      </button>
      {/* Play / Pause */}
      <button
        onClick={onPlayPause}
        style={iconBtn({ background: '#8A4931', color: '#fff', width: 30 })}
        title={playing ? 'Pause' : 'Play'}
      >
        {playing ? <Pause size={14} /> : <Play size={14} />}
      </button>
      {/* Step forward (only meaningful while paused) */}
      <button
        onClick={onStep}
        disabled={playing}
        style={iconBtn({ opacity: playing ? 0.35 : 1, cursor: playing ? 'default' : 'pointer' })}
        title="Step forward"
      >
        <SkipForward size={13} />
      </button>

      <span style={{ width: 1, height: 16, background: 'var(--border)', margin: '0 2px' }} />

      {/* Speed */}
      {SPEEDS.map(s => {
        const active = speed === s && playing;
        return (
          <button
            key={s}
            onClick={() => onSpeedChange(s)}
            style={{
              padding: '3px 8px', borderRadius: 6, border: 'none',
              fontSize: 10, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit',
              background: active ? '#8A4931' : 'transparent',
              color: active ? '#fff' : 'var(--text-sub)',
            }}
            title={`Speed x${s}`}
          >
            x{s}
          </button>
        );
      })}
    </div>
  );
}
