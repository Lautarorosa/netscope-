import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable, Optional
from datetime import datetime

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 111: "RPC", 135: "MSRPC", 139: "NetBIOS",
    143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS", 995: "POP3S",
    1433: "MSSQL", 1521: "Oracle", 3306: "MySQL", 3389: "RDP",
    5432: "PostgreSQL", 5900: "VNC", 6379: "Redis", 8080: "HTTP-Alt",
    8443: "HTTPS-Alt", 8888: "HTTP-Dev", 9200: "Elasticsearch",
    27017: "MongoDB", 6443: "Kubernetes"
}

CVE_SIGNATURES = {
    "OpenSSH_7.2": {"cve": "CVE-2016-6210", "severity": "HIGH",   "desc": "Username enumeration via timing attack"},
    "OpenSSH_7.4": {"cve": "CVE-2018-15473", "severity": "MEDIUM","desc": "Username enumeration vulnerability"},
    "OpenSSH_6":   {"cve": "CVE-2016-0778",  "severity": "HIGH",  "desc": "Buffer overflow in client-side roaming"},
    "vsftpd 2.3.4":{"cve": "CVE-2011-2523",  "severity": "CRITICAL","desc": "Backdoor command execution"},
    "ProFTPD 1.3.3":{"cve": "CVE-2010-4221", "severity": "CRITICAL","desc": "Remote code execution via TELNET IAC buffer"},
    "Apache/2.2":  {"cve": "CVE-2017-7679",  "severity": "CRITICAL","desc": "mod_mime buffer overread"},
    "Apache/2.4.49":{"cve": "CVE-2021-41773","severity": "CRITICAL","desc": "Path traversal and RCE"},
    "Apache/2.4.50":{"cve": "CVE-2021-42013","severity": "CRITICAL","desc": "Path traversal bypass"},
    "nginx/1.14":  {"cve": "CVE-2019-9511",  "severity": "HIGH",   "desc": "HTTP/2 DoS - Data Dribble"},
    "IIS/6.0":     {"cve": "CVE-2017-7269",  "severity": "CRITICAL","desc": "Buffer overflow in WebDAV"},
    "Microsoft-IIS/6": {"cve": "CVE-2017-7269", "severity": "CRITICAL", "desc": "Buffer overflow in WebDAV"},
    "MySQL 5.5":   {"cve": "CVE-2016-6662",  "severity": "CRITICAL","desc": "Remote code execution via config injection"},
    "MySQL 5.6":   {"cve": "CVE-2016-6662",  "severity": "CRITICAL","desc": "Remote code execution via config injection"},
    "Redis":       {"cve": "CVE-2022-0543",  "severity": "CRITICAL","desc": "Lua sandbox escape"},
    "3.0.20-Debian":{"cve": "CVE-2007-2447","severity": "CRITICAL","desc": "Samba username map script RCE"},
    "Telnet":      {"cve": "CVE-1999-0619",  "severity": "HIGH",   "desc": "Cleartext credential transmission"},
    "FTP":         {"cve": "CVE-1999-0082",  "severity": "MEDIUM", "desc": "Anonymous FTP enabled"},
}

SEVERITY_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}

@dataclass
class PortResult:
    port: int
    state: str
    service: str
    banner: str = ""
    cve: str = ""
    severity: str = "NONE"
    cve_desc: str = ""

@dataclass
class ScanResult:
    target: str
    start_time: str
    end_time: str = ""
    open_ports: list = field(default_factory=list)
    total_scanned: int = 0
    duration: float = 0.0
    hostname: str = ""

def grab_banner(host: str, port: int, timeout: float = 2.0) -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((host, port))
            probes = {
                80:   b"GET / HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n",
                443:  b"GET / HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n",
                8080: b"GET / HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n",
                8443: b"GET / HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n",
                21:   None,
                22:   None,
                25:   b"EHLO test\r\n",
                110:  None,
                143:  None,
            }
            probe = probes.get(port, b"\r\n")
            if probe is not None:
                s.send(probe)
            raw = s.recv(1024).decode("utf-8", errors="ignore").strip()
            lines = [l for l in raw.splitlines() if l.strip()]
            banner = lines[0][:120] if lines else raw[:120]
            return banner
    except Exception:
        return ""

def check_cve(banner: str, service: str) -> tuple[str, str, str]:
    if not banner:
        return "", "NONE", ""
    for sig, data in CVE_SIGNATURES.items():
        if sig.lower() in banner.lower():
            return data["cve"], data["severity"], data["desc"]
    if service == "Telnet":
        return CVE_SIGNATURES["Telnet"]["cve"], CVE_SIGNATURES["Telnet"]["severity"], CVE_SIGNATURES["Telnet"]["desc"]
    if service == "FTP" and "anonymous" in banner.lower():
        return CVE_SIGNATURES["FTP"]["cve"], CVE_SIGNATURES["FTP"]["severity"], CVE_SIGNATURES["FTP"]["desc"]
    return "", "NONE", ""

def scan_port(host: str, port: int, timeout: float = 1.0) -> Optional[PortResult]:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            if result == 0:
                service = COMMON_PORTS.get(port, "Unknown")
                banner = grab_banner(host, port)
                cve, severity, desc = check_cve(banner, service)
                return PortResult(
                    port=port,
                    state="open",
                    service=service,
                    banner=banner,
                    cve=cve,
                    severity=severity,
                    cve_desc=desc
                )
    except Exception:
        pass
    return None

class PortScanner:
    def __init__(self):
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def resolve_host(self, target: str) -> tuple[str, str]:
        try:
            hostname = socket.gethostbyname(target)
            try:
                resolved = socket.gethostbyaddr(hostname)[0]
            except Exception:
                resolved = target
            return hostname, resolved
        except socket.gaierror as e:
            raise ValueError(f"Cannot resolve host: {target} — {e}")

    def scan(
        self,
        target: str,
        port_range: tuple[int, int] = (1, 1024),
        threads: int = 100,
        timeout: float = 1.0,
        on_progress: Optional[Callable] = None,
        on_port_found: Optional[Callable] = None,
    ) -> ScanResult:
        self._stop_event.clear()
        ip, hostname = self.resolve_host(target)
        ports = list(range(port_range[0], port_range[1] + 1))
        total = len(ports)
        scanned = 0
        open_ports = []
        start = time.time()
        start_time = datetime.now().isoformat()

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(scan_port, ip, p, timeout): p for p in ports}
            for future in as_completed(futures):
                if self._stop_event.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                scanned += 1
                result = future.result()
                if result:
                    open_ports.append(result)
                    if on_port_found:
                        on_port_found(result)
                if on_progress:
                    on_progress(scanned, total)

        open_ports.sort(key=lambda x: x.port)
        duration = round(time.time() - start, 2)

        return ScanResult(
            target=ip,
            hostname=hostname,
            start_time=start_time,
            end_time=datetime.now().isoformat(),
            open_ports=open_ports,
            total_scanned=scanned,
            duration=duration
        )