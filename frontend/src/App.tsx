import { useState, useEffect, useCallback } from 'react'
import type { PortResult, ScanStatus, ScanStats, WsProgress } from './types'
import { useWebSocket } from './hooks/useWebSocket'
import { useScans } from './hooks/useScans'
import { useToast } from './hooks/useToast'
import { Topbar } from './components/Topbar'
import { ScanForm } from './components/ScanForm'
import { HistoryPanel } from './components/HistoryPanel'
import { Welcome } from './components/Welcome'
import { Progress } from './components/Progress'
import { StatsGrid } from './components/StatsGrid'
import { PortTable } from './components/PortTable'
import { ToastContainer } from './components/ToastContainer'
import './App.css'

type View = 'welcome' | 'scanning' | 'results'

export default function App() {
  const [view, setView]           = useState<View>('welcome')
  const [scanStatus, setScanStatus] = useState<ScanStatus>('idle')
  const [statusText, setStatusText] = useState('Ready')
  const [currentScanId, setCurrentScanId] = useState<number | null>(null)
  const [scanTarget, setScanTarget] = useState('')
  const [ports, setPorts]         = useState<PortResult[]>([])
  const [progress, setProgress]   = useState<WsProgress>({ done: 0, total: 0 })
  const [stats, setStats]         = useState<ScanStats>({ open: 0, critical: 0, high: 0, duration: null, total: 0 })

  const { connect, stop } = useWebSocket()
  const { history, loadHistory, loadScan, deleteScan } = useScans()
  const { toasts, addToast } = useToast()

  useEffect(() => { loadHistory() }, [loadHistory])

  const handleStart = useCallback(({ target, portFrom, portTo, threads }: {
    target: string; portFrom: number; portTo: number; threads: number
  }) => {
    if (!target.trim()) { addToast('Enter a target IP or hostname', 'error'); return }
    if (portFrom > portTo) { addToast('Port range is invalid', 'error'); return }

    setPorts([])
    setProgress({ done: 0, total: 0 })
    setStats({ open: 0, critical: 0, high: 0, duration: null, total: 0 })
    setCurrentScanId(null)
    setScanTarget(target)
    setView('scanning')
    setScanStatus('scanning')
    setStatusText(`Scanning ${target}...`)

    let openCount = 0, critCount = 0, highCount = 0

    connect(
      { target, port_from: portFrom, port_to: portTo, threads, timeout: 1.0 },
      {
        onProgress: (p) => setProgress(p),

        onPort: (port) => {
          openCount++
          if (port.severity === 'CRITICAL') critCount++
          if (port.severity === 'HIGH') highCount++
          setPorts(prev => [...prev, port])
          setStats(prev => ({ ...prev, open: openCount, critical: critCount, high: highCount }))
        },

        onDone: (data) => {
          setCurrentScanId(data.scan_id)
          setStats({ open: data.open_count, critical: critCount, high: highCount, duration: data.duration, total: data.total })
          setProgress({ done: data.total, total: data.total })
          setScanStatus('done')
          setStatusText(`Scan complete — ${data.open_count} open ports`)
          addToast(`Scan complete. ${data.open_count} open ports found.`, 'success')
          setView('results')
          loadHistory()
        },

        onError: (msg) => {
          addToast(msg, 'error')
          setScanStatus('error')
          setStatusText('Error')
          setView(ports.length > 0 ? 'results' : 'welcome')
        },
      }
    )
  }, [connect, addToast, loadHistory])

  const handleStop = useCallback(() => {
    stop()
    setScanStatus('idle')
    setStatusText('Ready')
    setView(ports.length > 0 ? 'results' : 'welcome')
    addToast('Scan stopped', 'info')
  }, [stop, addToast, ports.length])

  const handleSelectScan = useCallback(async (id: number) => {
    const data = await loadScan(id)
    if (!data) { addToast('Scan not found', 'error'); return }

    let crit = 0, high = 0
    data.ports.forEach(p => {
      if (p.severity === 'CRITICAL') crit++
      if (p.severity === 'HIGH') high++
    })

    setCurrentScanId(id)
    setScanTarget(data.scan.target)
    setPorts(data.ports)
    setStats({
      open: data.scan.open_count,
      critical: crit,
      high,
      duration: data.scan.duration,
      total: data.scan.total_ports,
    })
    setScanStatus('done')
    setStatusText(`${data.scan.target} — ${data.scan.open_count} open ports`)
    setView('results')
  }, [loadScan, addToast])

  const handleDeleteScan = useCallback(async (id: number) => {
    await deleteScan(id)
    if (currentScanId === id) {
      setCurrentScanId(null)
      setView('welcome')
      setScanStatus('idle')
      setStatusText('Ready')
    }
    addToast('Scan deleted', 'info')
  }, [deleteScan, currentScanId, addToast])

  const handleExportPdf = useCallback(() => {
    if (currentScanId) window.open(`/api/scans/${currentScanId}/pdf`, '_blank')
  }, [currentScanId])

  return (
    <div className="app">
      <Topbar status={scanStatus} statusText={statusText} />

      <aside className="sidebar">
        <ScanForm
          scanning={scanStatus === 'scanning'}
          onStart={handleStart}
          onStop={handleStop}
        />
        <HistoryPanel
          history={history}
          activeScanId={currentScanId}
          onSelect={handleSelectScan}
          onDelete={handleDeleteScan}
        />
      </aside>

      <main className="main">
        {view === 'welcome' && <Welcome />}

        {view === 'scanning' && (
          <>
            <Progress target={scanTarget} progress={progress} openCount={ports.length} />
            <StatsGrid stats={stats} />
            <PortTable ports={ports} scanId={currentScanId} onExportPdf={handleExportPdf} />
          </>
        )}

        {view === 'results' && (
          <>
            <StatsGrid stats={stats} />
            <PortTable ports={ports} scanId={currentScanId} onExportPdf={handleExportPdf} />
          </>
        )}
      </main>

      <ToastContainer toasts={toasts} />
    </div>
  )
}
