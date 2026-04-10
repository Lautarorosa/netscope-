from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
import io

C_BG      = colors.HexColor("#0D1117")
C_SURFACE = colors.HexColor("#161B22")
C_BORDER  = colors.HexColor("#21262D")
C_CYAN    = colors.HexColor("#79C0FF")
C_CYAN2   = colors.HexColor("#388BFD")
C_TEXT    = colors.HexColor("#C9D1D9")
C_MUTED   = colors.HexColor("#8B949E")
C_WHITE   = colors.HexColor("#F0F6FC")

SEV_COLORS = {
    "CRITICAL": colors.HexColor("#FF4444"),
    "HIGH":     colors.HexColor("#FF8C00"),
    "MEDIUM":   colors.HexColor("#F0C040"),
    "LOW":      colors.HexColor("#4CAF50"),
    "NONE":     colors.HexColor("#8B949E"),
}

def sev_color(sev):
    return SEV_COLORS.get(sev, SEV_COLORS["NONE"])

def make_style(name, **kw):
    return ParagraphStyle(name, fontName="Helvetica", fontSize=10,
                          textColor=C_TEXT, leading=14, **kw)

def generate_pdf(scan_data: dict) -> bytes:
    buf  = io.BytesIO()
    scan  = scan_data["scan"]
    ports = scan_data["ports"]
    W     = A4[0] - 40*mm

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=18*mm,  bottomMargin=18*mm,
    )

    S_TITLE   = make_style("title",   fontSize=22, textColor=C_WHITE, fontName="Helvetica-Bold", leading=28)
    S_SECTION = make_style("section", fontSize=13, textColor=C_CYAN,  fontName="Helvetica-Bold", leading=18, spaceBefore=10)
    S_BODY    = make_style("body",    fontSize=9,  textColor=C_TEXT,  leading=13)
    S_MUTED   = make_style("muted",   fontSize=8,  textColor=C_MUTED, leading=12)
    S_MONO    = make_style("mono",    fontSize=8,  textColor=C_TEXT,  fontName="Courier", leading=12)

    critical = sum(1 for p in ports if p["severity"] == "CRITICAL")
    high     = sum(1 for p in ports if p["severity"] == "HIGH")
    medium   = sum(1 for p in ports if p["severity"] == "MEDIUM")
    low      = sum(1 for p in ports if p["severity"] == "LOW")
    vulns    = sum(1 for p in ports if p.get("cve"))

    def page_bg(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(C_BG)
        canvas.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
        canvas.setFillColor(C_CYAN2)
        canvas.rect(0, A4[1] - 2*mm, A4[0], 2*mm, stroke=0, fill=1)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(C_MUTED)
        canvas.drawString(20*mm, 10*mm, f"NETSCOPE  |  {scan['target']}  |  CONFIDENTIAL")
        canvas.drawRightString(A4[0] - 20*mm, 10*mm, f"Page {doc.page}")
        canvas.restoreState()

    story = []

    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("NETSCOPE", make_style("ns", fontSize=8, textColor=C_CYAN,
                                                   fontName="Helvetica-Bold", charSpace=4, leading=12)))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("Port Scan Report", S_TITLE))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        f"Target: <font color='#79C0FF'><b>{scan['target']}</b></font>"
        + (f"  ({scan['hostname']})" if scan.get('hostname') and scan['hostname'] != scan['target'] else ""),
        make_style("sub", fontSize=10, textColor=C_MUTED, leading=14)
    ))
    story.append(Paragraph(
        f"Completed: {str(scan.get('end_time',''))[:19].replace('T',' ')}  |  "
        f"Duration: {scan.get('duration', 0):.1f}s  |  "
        f"Ports scanned: {scan.get('total_ports', 0)}",
        make_style("meta", fontSize=8, textColor=C_MUTED, leading=12)
    ))
    story.append(Spacer(1, 5*mm))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 5*mm))

    # RESUMEN
    story.append(Paragraph("Risk Summary", S_SECTION))
    story.append(Spacer(1, 3*mm))
    col_w = W / 6
    summary = [
        ["Open Ports", "Vulnerabilities", "Critical", "High", "Medium", "Low"],
        [str(len(ports)), str(vulns), str(critical), str(high), str(medium), str(low)],
    ]
    tbl = Table(summary, colWidths=[col_w]*6, rowHeights=[16, 28])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), C_SURFACE),
        ("BACKGROUND",    (0,1), (-1,1), C_BORDER),
        ("TEXTCOLOR",     (0,0), (-1,0), C_MUTED),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0), 7),
        ("FONTNAME",      (0,1), (-1,1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,1), (-1,1), 16),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TEXTCOLOR",     (0,1), (1,1),  C_WHITE),
        ("TEXTCOLOR",     (2,1), (2,1),  SEV_COLORS["CRITICAL"]),
        ("TEXTCOLOR",     (3,1), (3,1),  SEV_COLORS["HIGH"]),
        ("TEXTCOLOR",     (4,1), (4,1),  SEV_COLORS["MEDIUM"]),
        ("TEXTCOLOR",     (5,1), (5,1),  SEV_COLORS["LOW"]),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LINEBELOW",     (0,0), (-1,0),  0.5, C_BORDER),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6*mm))

    # TABLA DE PUERTOS
    story.append(Paragraph("Port Findings", S_SECTION))
    story.append(Spacer(1, 3*mm))

    if not ports:
        story.append(Paragraph("No open ports discovered.", S_MUTED))
    else:
        col_widths = [18*mm, 22*mm, 22*mm, 32*mm, W - 94*mm]
        rows = [["PORT", "SERVICE", "SEVERITY", "CVE", "DESCRIPTION"]]
        for p in sorted(ports, key=lambda x: (
            -["CRITICAL","HIGH","MEDIUM","LOW","NONE"].index(x["severity"])
            if x["severity"] in ["CRITICAL","HIGH","MEDIUM","LOW","NONE"] else 0,
            x["port"]
        )):
            sev  = p.get("severity", "NONE")
            desc = p.get("cve_desc", "") or p.get("banner", "") or "-"
            if len(desc) > 80:
                desc = desc[:80] + "..."
            rows.append([str(p["port"]), p.get("service","") or "-", sev,
                         p.get("cve","") or "-", desc])

        tbl2 = Table(rows, colWidths=col_widths, repeatRows=1)
        cmds = [
            ("BACKGROUND",    (0,0),  (-1,0),  C_SURFACE),
            ("TEXTCOLOR",     (0,0),  (-1,0),  C_MUTED),
            ("FONTNAME",      (0,0),  (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0,0),  (-1,0),  7),
            ("FONTNAME",      (0,1),  (-1,-1), "Helvetica"),
            ("FONTSIZE",      (0,1),  (-1,-1), 8),
            ("TEXTCOLOR",     (0,1),  (-1,-1), C_TEXT),
            ("ALIGN",         (0,0),  (2,-1),  "CENTER"),
            ("ALIGN",         (3,0),  (-1,-1), "LEFT"),
            ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS",(0,1),  (-1,-1), [C_BG, C_SURFACE]),
            ("LINEBELOW",     (0,0),  (-1,0),  0.5, C_BORDER),
            ("TOPPADDING",    (0,0),  (-1,-1), 4),
            ("BOTTOMPADDING", (0,0),  (-1,-1), 4),
            ("LEFTPADDING",   (0,0),  (-1,-1), 5),
            ("RIGHTPADDING",  (0,0),  (-1,-1), 5),
        ]
        for i, row in enumerate(rows[1:], start=1):
            cmds.append(("TEXTCOLOR", (2,i), (2,i), sev_color(row[2])))
            cmds.append(("FONTNAME",  (2,i), (2,i), "Helvetica-Bold"))
            cmds.append(("TEXTCOLOR", (0,i), (0,i), C_CYAN))
        tbl2.setStyle(TableStyle(cmds))
        story.append(tbl2)

    story.append(Spacer(1, 8*mm))

    # DETALLE DE VULNERABILIDADES
    vuln_ports = [p for p in ports if p.get("cve")]
    if vuln_ports:
        story.append(HRFlowable(width=W, thickness=0.5, color=C_BORDER))
        story.append(Paragraph("Vulnerability Detail", S_SECTION))
        story.append(Spacer(1, 3*mm))
        for p in sorted(vuln_ports, key=lambda x: x["port"]):
            sev = p.get("severity", "NONE")
            block = [
                Paragraph(
                    f"<font color='#79C0FF'><b>Port {p['port']}</b></font>"
                    f"  <font color='#8B949E'>{p.get('service','')}</font>"
                    f"  <b>[{sev}]</b>",
                    make_style("vh", fontSize=10, textColor=sev_color(sev),
                               fontName="Helvetica-Bold", leading=15)
                ),
                Paragraph(f"<b>CVE:</b> {p.get('cve','')}  -  {p.get('cve_desc','')}", S_BODY),
            ]
            if p.get("banner"):
                block.append(Paragraph(f"<b>Banner:</b> {p['banner'][:120]}", S_MONO))
            block.append(Spacer(1, 6*mm))
            story.append(KeepTogether(block))

    # PIE
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Generated by NETSCOPE for authorized security assessment purposes only. "
        "Unauthorized port scanning may violate local laws.",
        make_style("disc", fontSize=7, textColor=C_MUTED, leading=11)
    ))

    doc.build(story, onFirstPage=page_bg, onLaterPages=page_bg)
    return buf.getvalue()