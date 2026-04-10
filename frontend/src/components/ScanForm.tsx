import { useState } from 'react'
import './ScanForm.css'

interface Props {
  scanning: boolean
  onStart: (params: { target: string; portFrom: number; portTo: number; threads: number }) => void
  onStop: () => void
}

export function ScanForm({ scanning, onStart, onStop }: Props) {
  const [target, setTarget]     = useState('')
  const [portFrom, setPortFrom] = useState(1)
  const [portTo, setPortTo]     = useState(1024)
  const [speed, setSpeed]       = useState(150)

  function handleStart() {
    onStart({ target, portFrom, portTo, threads: speed })
  }

  return (
    <div className="sf-block">
      <div className="sf-label">
        New Scan
        <span className="sf-label-line" />
      </div>

      <div className="sf-field">
        <label>Target IP / Hostname</label>
        <input
          type="text"
          placeholder="192.168.1.1"
          autoComplete="off"
          spellCheck={false}
          value={target}
          onChange={e => setTarget(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !scanning && handleStart()}
          disabled={scanning}
        />
      </div>

      <div className="sf-row">
        <div className="sf-field">
          <label>Port From</label>
          <input
            type="number"
            min={1}
            max={65535}
            value={portFrom}
            onChange={e => setPortFrom(+e.target.value)}
            disabled={scanning}
          />
        </div>
        <div className="sf-field">
          <label>Port To</label>
          <input
            type="number"
            min={1}
            max={65535}
            value={portTo}
            onChange={e => setPortTo(+e.target.value)}
            disabled={scanning}
          />
        </div>
      </div>

      <div className="sf-field">
        <label>Speed</label>
        <select value={speed} onChange={e => setSpeed(+e.target.value)} disabled={scanning}>
          <option value={50}>Slow (stealth)</option>
          <option value={150}>Normal</option>
          <option value={300}>Fast</option>
          <option value={500}>Aggressive</option>
        </select>
      </div>

      {scanning ? (
        <button className="sf-btn sf-btn-stop" onClick={onStop}>
          <svg viewBox="0 0 24 24" width={13} height={13} fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round">
            <rect x="6" y="6" width="12" height="12"/>
          </svg>
          Stop
        </button>
      ) : (
        <button className="sf-btn sf-btn-start" onClick={handleStart}>
          <svg viewBox="0 0 24 24" width={13} height={13} fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round">
            <polygon points="5,3 19,12 5,21"/>
          </svg>
          Start Scan
        </button>
      )}
    </div>
  )
}
