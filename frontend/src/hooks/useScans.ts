import { useState, useCallback } from 'react'
import type { ScanSummary, ScanDetail } from '../types'

export function useScans() {
  const [history, setHistory] = useState<ScanSummary[]>([])

  const loadHistory = useCallback(async () => {
    try {
      const res = await fetch('/api/scans')
      if (!res.ok) return
      setHistory(await res.json())
    } catch { /* silent */ }
  }, [])

  const loadScan = useCallback(async (id: number): Promise<ScanDetail | null> => {
    try {
      const res = await fetch(`/api/scans/${id}`)
      if (!res.ok) return null
      return await res.json()
    } catch {
      return null
    }
  }, [])

  const deleteScan = useCallback(async (id: number): Promise<boolean> => {
    try {
      await fetch(`/api/scans/${id}`, { method: 'DELETE' })
      setHistory(prev => prev.filter(s => s.id !== id))
      return true
    } catch {
      return false
    }
  }, [])

  return { history, loadHistory, loadScan, deleteScan }
}
