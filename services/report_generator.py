# ============================================================
# services/report_generator.py — PDF Report Generator
# Generates professional medical AI analysis reports
# ============================================================

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from models.patient import CombinedAnalysisResult, Severity
from config.settings import MEDICAL_DISCLAIMER, SEVERITY_LEVELS


class ReportGenerator:
    """Generates professional PDF medical analysis reports."""

    COLORS = {
        "primary":    colors.HexColor("#1a237e"),
        "secondary":  colors.HexColor("#0d47a1"),
        "accent":     colors.HexColor("#1565c0"),
        "critical":   colors.HexColor("#c62828"),
        "high":       colors.HexColor("#e53935"),
        "moderate":   colors.HexColor("#f57c00"),
        "low":        colors.HexColor("#388e3c"),
        "normal":     colors.HexColor("#2e7d32"),
        "bg_light":   colors.HexColor("#e3f2fd"),
        "bg_warn":    colors.HexColor("#fff3e0"),
        "bg_critical":colors.HexColor("#ffebee"),
        "text_dark":  colors.HexColor("#1a1a2e"),
        "text_muted": colors.HexColor("#546e7a"),
        "border":     colors.HexColor("#90a4ae"),
    }

    def generate(
        self,
        result: CombinedAnalysisResult,
        output_path: Optional[str] = None,
    ) -> str:
        """Generate PDF report and return file path."""
        os.makedirs("reports", exist_ok=True)
        if not output_path:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = result.patient.name.replace(" ", "_") or "Patient"
            output_path = f"reports/MedicalAI_Report_{name}_{ts}.pdf"

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        )

        styles = self._build_styles()
        story  = []

        # Build sections
        story.extend(self._build_header(result, styles))
        story.extend(self._build_disclaimer(styles))
        story.extend(self._build_patient_info(result, styles))

        sev = result.severity_overall
        story.extend(self._build_severity_banner(sev, styles))

        if result.executive_summary:
            story.extend(self._build_executive_summary(result, styles))

        if result.final_diagnosis:
            story.extend(self._build_diagnosis(result, styles))

        if result.image_result:
            story.extend(self._build_image_findings(result.image_result, styles))

        if result.report_result:
            story.extend(self._build_report_findings(result.report_result, styles))

        if result.comprehensive_plan:
            story.extend(self._build_action_plan(result, styles))

        if result.patient_counseling:
            story.extend(self._build_patient_counseling(result, styles))

        story.extend(self._build_footer(styles))

        doc.build(story)
        return output_path

    # ─── Styles ──────────────────────────────────────────────

    def _build_styles(self):
        base = getSampleStyleSheet()
        C    = self.COLORS

        styles = {
            "title": ParagraphStyle("title",
                fontSize=22, fontName="Helvetica-Bold",
                textColor=C["primary"], alignment=TA_CENTER,
                spaceAfter=6),
            "subtitle": ParagraphStyle("subtitle",
                fontSize=12, fontName="Helvetica",
                textColor=C["text_muted"], alignment=TA_CENTER,
                spaceAfter=12),
            "section": ParagraphStyle("section",
                fontSize=13, fontName="Helvetica-Bold",
                textColor=C["primary"], spaceBefore=14, spaceAfter=6,
                borderPad=4),
            "body": ParagraphStyle("body",
                fontSize=9.5, fontName="Helvetica",
                textColor=C["text_dark"], leading=14,
                alignment=TA_JUSTIFY, spaceAfter=4),
            "bold": ParagraphStyle("bold",
                fontSize=9.5, fontName="Helvetica-Bold",
                textColor=C["text_dark"], spaceAfter=3),
            "critical": ParagraphStyle("critical",
                fontSize=10, fontName="Helvetica-Bold",
                textColor=C["critical"], spaceAfter=4),
            "muted": ParagraphStyle("muted",
                fontSize=8.5, fontName="Helvetica",
                textColor=C["text_muted"], spaceAfter=3),
            "mono": ParagraphStyle("mono",
                fontSize=8.5, fontName="Courier",
                textColor=C["text_dark"], leading=12, spaceAfter=3),
        }
        return styles

    def _hr(self, color=None):
        return HRFlowable(
            width="100%", thickness=1,
            color=color or self.COLORS["border"],
            spaceAfter=8, spaceBefore=4,
        )

    def _section_header(self, title: str, styles: dict, icon: str = ""):
        C = self.COLORS
        return [
            Spacer(1, 8),
            Paragraph(f"{icon} {title}" if icon else title, styles["section"]),
            self._hr(C["accent"]),
        ]

    # ─── Report Sections ─────────────────────────────────────

    def _build_header(self, result: CombinedAnalysisResult, styles: dict):
        C = self.COLORS
        items = [
            Paragraph("🏥 MEDICAL AI ANALYSIS REPORT", styles["title"]),
            Paragraph("Powered by Claude AI · For Clinical Decision Support Only",
                      styles["subtitle"]),
            self._hr(C["primary"]),
            Spacer(1, 6),
        ]
        return items

    def _build_disclaimer(self, styles: dict):
        C = self.COLORS
        text = ("⚠️  DISCLAIMER: This AI-generated report is for EDUCATIONAL and "
                "RESEARCH purposes only. It is NOT a substitute for professional "
                "medical diagnosis. Always consult a qualified healthcare professional.")

        data = [[Paragraph(text, ParagraphStyle("disc",
                    fontSize=8, fontName="Helvetica-Bold",
                    textColor=C["critical"], leading=12))]]
        table = Table(data, colWidths=[16*cm])
        table.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,-1), C["bg_critical"]),
            ("BORDER",      (0,0), (-1,-1), 1, C["critical"]),
            ("TOPPADDING",  (0,0), (-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
            ("RIGHTPADDING",(0,0), (-1,-1), 10),
            ("ROWBACKGROUNDS",(0,0),(-1,-1),[C["bg_critical"]]),
        ]))
        return [table, Spacer(1, 10)]

    def _build_patient_info(self, result: CombinedAnalysisResult, styles: dict):
        C = self.COLORS
        p = result.patient
        items = self._section_header("PATIENT INFORMATION", styles, "👤")

        data = [
            ["Patient Name",    p.name or "Anonymous",
             "Report Date",     datetime.now().strftime("%Y-%m-%d %H:%M")],
            ["Age / Gender",    f"{p.age or '?'} yrs / {p.gender}",
             "Patient ID",      p.patient_id or "N/A"],
            ["Chief Complaint", p.chief_complaint or "Not specified",
             "Referring Doctor",p.referring_doctor or "N/A"],
            ["Clinical History",p.clinical_history or "Not provided",
             "Urgency",         result.urgency],
        ]

        col_widths = [3.5*cm, 4.5*cm, 3.5*cm, 4.5*cm]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ("FONTNAME",    (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTNAME",    (2,0), (2,-1), "Helvetica-Bold"),
            ("FONTSIZE",    (0,0), (-1,-1), 9),
            ("BACKGROUND",  (0,0), (0,-1), C["bg_light"]),
            ("BACKGROUND",  (2,0), (2,-1), C["bg_light"]),
            ("GRID",        (0,0), (-1,-1), 0.5, C["border"]),
            ("TOPPADDING",  (0,0), (-1,-1), 5),
            ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
        ]))
        items.append(table)
        items.append(Spacer(1, 8))
        return items

    def _build_severity_banner(self, severity: str, styles: dict):
        C    = self.COLORS
        cfg  = SEVERITY_LEVELS.get(severity, SEVERITY_LEVELS["NORMAL"])
        icon = cfg["icon"]
        bg   = {
            "CRITICAL": C["bg_critical"],
            "HIGH":     C["bg_critical"],
            "MODERATE": C["bg_warn"],
            "LOW":      colors.HexColor("#e8f5e9"),
            "NORMAL":   colors.HexColor("#e8f5e9"),
        }.get(severity, colors.white)
        tc   = {
            "CRITICAL": C["critical"],
            "HIGH":     C["high"],
            "MODERATE": C["moderate"],
            "LOW":      C["normal"],
            "NORMAL":   C["normal"],
        }.get(severity, C["text_dark"])

        text = f"{icon}  OVERALL SEVERITY: {severity}  |  {cfg['action']}"
        style = ParagraphStyle("banner",
            fontSize=11, fontName="Helvetica-Bold",
            textColor=tc, alignment=TA_CENTER)

        data  = [[Paragraph(text, style)]]
        table = Table(data, colWidths=[16*cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), bg),
            ("BORDER",     (0,0), (-1,-1), 1.5, tc),
            ("TOPPADDING", (0,0), (-1,-1), 10),
            ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ]))
        return [table, Spacer(1, 10)]

    def _build_executive_summary(self, result: CombinedAnalysisResult, styles: dict):
        C     = self.COLORS
        items = self._section_header("EXECUTIVE SUMMARY", styles, "📋")
        items.append(Paragraph(result.executive_summary, styles["body"]))
        if result.prognosis:
            items.append(Spacer(1, 4))
            items.append(Paragraph(f"<b>Prognosis:</b> {result.prognosis}", styles["body"]))
        return items

    def _build_diagnosis(self, result: CombinedAnalysisResult, styles: dict):
        C     = self.COLORS
        items = self._section_header("DIAGNOSIS", styles, "🔬")
        fd    = result.final_diagnosis

        if fd.get("primary"):
            primary_text = (f"<b>Primary Diagnosis:</b> {fd['primary']} "
                          f"(ICD-10: {fd.get('icd_code','N/A')}) "
                          f"— Confidence: {fd.get('confidence',0)}%")
            items.append(Paragraph(primary_text, styles["bold"]))

        if fd.get("secondary"):
            items.append(Paragraph(
                "<b>Secondary Conditions:</b> " + ", ".join(fd["secondary"]),
                styles["body"]
            ))
        if fd.get("differential"):
            items.append(Paragraph(
                "<b>Differential Diagnoses:</b> " + ", ".join(fd["differential"]),
                styles["body"]
            ))

        # Image differential
        if result.image_result and result.image_result.differential_diagnosis:
            items.append(Spacer(1, 6))
            items.append(Paragraph("<b>Differential Diagnosis (from imaging):</b>", styles["bold"]))
            rows = [["Rank", "Diagnosis", "ICD-10", "Probability", "Confidence"]]
            for d in result.image_result.differential_diagnosis[:5]:
                rows.append([
                    str(d.rank), d.diagnosis, d.icd_code or "—",
                    d.probability, f"{d.confidence}%",
                ])
            t = Table(rows, colWidths=[1*cm, 5*cm, 2.5*cm, 2.5*cm, 2*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND",   (0,0), (-1,0), C["primary"]),
                ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
                ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",     (0,0), (-1,-1), 8.5),
                ("GRID",         (0,0), (-1,-1), 0.5, C["border"]),
                ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, C["bg_light"]]),
                ("TOPPADDING",   (0,0), (-1,-1), 4),
                ("BOTTOMPADDING",(0,0), (-1,-1), 4),
                ("LEFTPADDING",  (0,0), (-1,-1), 5),
            ]))
            items.append(t)
        return items

    def _build_image_findings(self, img_result, styles: dict):
        C     = self.COLORS
        items = self._section_header("IMAGING FINDINGS", styles, "🩻")

        # Impression
        if img_result.impression:
            items.append(Paragraph("<b>Radiological Impression:</b>", styles["bold"]))
            items.append(Paragraph(img_result.impression, styles["body"]))
            items.append(Spacer(1, 6))

        # Critical findings
        if img_result.critical_findings:
            items.append(Paragraph("🚨 CRITICAL FINDINGS:", styles["critical"]))
            for cf in img_result.critical_findings:
                items.append(Paragraph(f"• {cf}", styles["critical"]))
            items.append(Spacer(1, 6))

        # Findings table
        if img_result.findings:
            items.append(Paragraph("<b>Detailed Findings:</b>", styles["bold"]))
            rows = [["#", "Region", "Finding", "Severity", "Confidence"]]
            for f in img_result.findings:
                sev_color_map = {
                    "CRITICAL": C["critical"], "HIGH": C["high"],
                    "MODERATE": C["moderate"], "LOW": C["low"],
                    "NORMAL": C["normal"],
                }
                rows.append([
                    str(f.id), f.region,
                    Paragraph(f.finding[:120], styles["body"]),
                    f.severity.value if hasattr(f.severity, 'value') else str(f.severity),
                    f"{f.confidence}%",
                ])
            t = Table(rows, colWidths=[0.6*cm, 2.5*cm, 7*cm, 2*cm, 1.8*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND",   (0,0), (-1,0), C["secondary"]),
                ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
                ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",     (0,0), (-1,-1), 8.5),
                ("GRID",         (0,0), (-1,-1), 0.5, C["border"]),
                ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, C["bg_light"]]),
                ("VALIGN",       (0,0), (-1,-1), "TOP"),
                ("TOPPADDING",   (0,0), (-1,-1), 4),
                ("BOTTOMPADDING",(0,0), (-1,-1), 4),
                ("LEFTPADDING",  (0,0), (-1,-1), 5),
            ]))
            items.append(t)
            items.append(Spacer(1, 6))

        # Normal findings
        if img_result.normal_findings:
            items.append(Paragraph("<b>Normal Findings:</b>", styles["bold"]))
            nf_text = " • ".join(img_result.normal_findings[:8])
            items.append(Paragraph(nf_text, styles["body"]))

        return items

    def _build_report_findings(self, rpt_result, styles: dict):
        C     = self.COLORS
        items = self._section_header("MEDICAL REPORT ANALYSIS", styles, "📄")

        if rpt_result.diagnosis_summary:
            items.append(Paragraph(f"<b>Clinical Summary:</b> {rpt_result.diagnosis_summary}",
                                   styles["body"]))
            items.append(Spacer(1, 6))

        # Critical values
        if rpt_result.critical_values:
            items.append(Paragraph("🚨 CRITICAL VALUES:", styles["critical"]))
            for cv in rpt_result.critical_values:
                items.append(Paragraph(f"• {cv}", styles["critical"]))
            items.append(Spacer(1, 6))

        # Key findings table
        if rpt_result.key_findings:
            items.append(Paragraph("<b>Key Parameters:</b>", styles["bold"]))
            rows = [["Parameter", "Value", "Normal Range", "Status", "Significance"]]
            for kf in rpt_result.key_findings[:12]:
                status = kf.get("status", "")
                status_color = (C["critical"] if status == "Critical" else
                               C["high"]     if status == "Abnormal" else C["normal"])
                rows.append([
                    kf.get("parameter", ""),
                    kf.get("value", ""),
                    kf.get("normal_range", ""),
                    Paragraph(f'<font color="#{status_color.hexval()[1:] if hasattr(status_color,"hexval") else "000000"}">{status}</font>',
                              styles["body"]),
                    Paragraph(kf.get("clinical_significance", "")[:80], styles["body"]),
                ])
            t = Table(rows, colWidths=[3*cm, 2*cm, 2.5*cm, 2*cm, 6.5*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND",   (0,0), (-1,0), C["secondary"]),
                ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
                ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",     (0,0), (-1,-1), 8),
                ("GRID",         (0,0), (-1,-1), 0.5, C["border"]),
                ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, C["bg_light"]]),
                ("VALIGN",       (0,0), (-1,-1), "TOP"),
                ("TOPPADDING",   (0,0), (-1,-1), 4),
                ("BOTTOMPADDING",(0,0), (-1,-1), 4),
                ("LEFTPADDING",  (0,0), (-1,-1), 5),
            ]))
            items.append(t)
        return items

    def _build_action_plan(self, result: CombinedAnalysisResult, styles: dict):
        C     = self.COLORS
        items = self._section_header("PHYSICIAN ACTION PLAN", styles, "📋")
        plan  = result.comprehensive_plan

        sections = [
            ("Immediate Actions (Next 24h)", "immediate_24h", C["critical"]),
            ("Short-term (Week 1)",           "week1",         C["moderate"]),
            ("Long-term Management",          "ongoing",       C["normal"]),
            ("Specialist Referrals Needed",   "specialist_team",C["secondary"]),
            ("Additional Investigations",     "investigations_needed", C["accent"]),
            ("Monitoring Parameters",         "monitoring_parameters", C["text_muted"]),
        ]

        for label, key, color in sections:
            vals = plan.get(key, [])
            if not vals:
                continue
            items.append(Paragraph(f"<b>{label}:</b>", styles["bold"]))
            for v in (vals if isinstance(vals, list) else [vals]):
                items.append(Paragraph(f"  ▸  {v}", styles["body"]))
            items.append(Spacer(1, 4))

        if plan.get("treatment_approach"):
            items.append(Paragraph(
                f"<b>Treatment Approach:</b> {plan['treatment_approach']}", styles["body"]
            ))

        return items

    def _build_patient_counseling(self, result: CombinedAnalysisResult, styles: dict):
        C        = self.COLORS
        items    = self._section_header("PATIENT COUNSELING GUIDE", styles, "💬")
        counsel  = result.patient_counseling

        if counsel.get("diagnosis_explanation"):
            items.append(Paragraph("<b>Explain to Patient:</b>", styles["bold"]))
            items.append(Paragraph(counsel["diagnosis_explanation"], styles["body"]))
            items.append(Spacer(1, 4))

        if counsel.get("lifestyle_modifications"):
            items.append(Paragraph("<b>Lifestyle Modifications:</b>", styles["bold"]))
            for lm in counsel["lifestyle_modifications"]:
                items.append(Paragraph(f"  ✓  {lm}", styles["body"]))
            items.append(Spacer(1, 4))

        if counsel.get("warning_signs"):
            items.append(Paragraph("<b>⚠️ Go to ER Immediately If:</b>", styles["critical"]))
            for ws in counsel["warning_signs"]:
                items.append(Paragraph(f"  🚨  {ws}", styles["body"]))

        return items

    def _build_footer(self, styles: dict):
        C = self.COLORS
        items = [
            Spacer(1, 16),
            self._hr(C["primary"]),
            Paragraph(
                f"Generated by Medical AI Analysis System · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · "
                "For research and educational purposes only · Not for clinical use without physician review",
                ParagraphStyle("footer", fontSize=7.5, fontName="Helvetica",
                              textColor=C["text_muted"], alignment=TA_CENTER)
            ),
        ]
        return items
