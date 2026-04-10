from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, FileResponse
from pydantic import BaseModel
import asyncio
import json
import threading
from pathlib import Path

from scanner import PortScanner
from database import init_db, save_scan, get_scans, get_scan_detail, delete_scan
from reports import generate_pdf

app = FastAPI(title="NETSCOPE", version="1.0.0")

# Init DB on startup
init_db()

# ── Active scanners registry ───────────────────────────────────────────────────
active_scanners: dict[str, PortScanner] = {}

# ── REST endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/scans")
def list_scans():
    return get_scans(limit=50)

@app.get("/api/scans/{scan_id}")
def get_scan(scan_id: int):
    data = get_scan_detail(scan_id)
    if not data:
        raise HTTPException(status_code=404, detail="Scan not found")
    return data

@app.delete("/api/scans/{scan_id}")
def remove_scan(scan_id: int):
    delete_scan(scan_id)
    return {"ok": True}

@app.get("/api/scans/{scan_id}/pdf")
def download_pdf(scan_id: int):
    data = get_scan_detail(scan_id)
    if not data:
        raise HTTPException(status_code=404, detail="Scan not found")
    pdf_bytes = generate_pdf(data)
    filename = f"netscope_{data['scan']['target'].replace('.','_')}_{scan_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ── WebSocket scan endpoint ────────────────────────────────────────────────────

@app.websocket("/ws/scan")
async def websocket_scan(ws: WebSocket):
    await ws.accept()
    scanner = None
    ws_id = id(ws)

    try:
        # Receive config
        data = await ws.receive_json()
        target      = data.get("target", "").strip()
        port_from   = int(data.get("port_from", 1))
        port_to     = int(data.get("port_to", 1024))
        threads     = min(int(data.get("threads", 150)), 500)
        timeout     = float(data.get("timeout", 1.0))

        if not target:
            await ws.send_json({"type": "error", "msg": "No target specified"})
            return

        await ws.send_json({"type": "start", "target": target,
                            "port_from": port_from, "port_to": port_to})

        scanner = PortScanner()
        active_scanners[ws_id] = scanner
        loop = asyncio.get_event_loop()
        result_holder = {}

        def run_scan():
            def on_progress(done, total):
                asyncio.run_coroutine_threadsafe(
                    ws.send_json({"type": "progress", "done": done, "total": total}),
                    loop
                )

            def on_port_found(port_result):
                asyncio.run_coroutine_threadsafe(
                    ws.send_json({
                        "type": "port",
                        "port":     port_result.port,
                        "state":    port_result.state,
                        "service":  port_result.service,
                        "banner":   port_result.banner,
                        "cve":      port_result.cve,
                        "severity": port_result.severity,
                        "cve_desc": port_result.cve_desc,
                    }),
                    loop
                )

            try:
                r = scanner.scan(
                    target=target,
                    port_range=(port_from, port_to),
                    threads=threads,
                    timeout=timeout,
                    on_progress=on_progress,
                    on_port_found=on_port_found,
                )
                result_holder["result"] = r
            except Exception as e:
                asyncio.run_coroutine_threadsafe(
                    ws.send_json({"type": "error", "msg": str(e)}),
                    loop
                )

        thread = threading.Thread(target=run_scan, daemon=True)
        thread.start()

        # Wait for thread with stop support
        while thread.is_alive():
            try:
                msg = await asyncio.wait_for(ws.receive_json(), timeout=0.3)
                if msg.get("type") == "stop":
                    scanner.stop()
                    break
            except asyncio.TimeoutError:
                pass
            except Exception:
                scanner.stop()
                break

        thread.join(timeout=5)

        if "result" in result_holder:
            scan_result = result_holder["result"]
            scan_id = save_scan(scan_result)
            await ws.send_json({
                "type":       "done",
                "scan_id":    scan_id,
                "target":     scan_result.target,
                "hostname":   scan_result.hostname,
                "duration":   scan_result.duration,
                "open_count": len(scan_result.open_ports),
                "total":      scan_result.total_scanned,
            })

    except WebSocketDisconnect:
        if scanner:
            scanner.stop()
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "msg": str(e)})
        except Exception:
            pass
    finally:
        active_scanners.pop(ws_id, None)

# ── Static files ───────────────────────────────────────────────────────────────
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)