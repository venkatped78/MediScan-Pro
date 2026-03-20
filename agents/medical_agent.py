# ============================================================
# agents/medical_agent.py — Core Medical AI Analysis Agent
# ============================================================

import json
import re
from datetime import datetime
from typing import Optional, Dict
import anthropic

from config.settings import (
    config, MODEL_VISION, MODEL,
    ANALYSIS_SYSTEM_PROMPT,
    IMAGE_ANALYSIS_PROMPT,
    REPORT_ANALYSIS_PROMPT,
    COMBINED_ANALYSIS_PROMPT,
)
from models.patient import (
    PatientInfo, ImageAnalysisResult, ReportAnalysisResult,
    CombinedAnalysisResult, Finding, Diagnosis, Severity, Urgency,
)
from services.image_processor import ImageProcessor


class MedicalAgent:
    """
    AI Medical Analysis Agent powered by Claude.

    Capabilities:
    1. analyze_image()   — Analyze medical scans (X-ray, MRI, CT, etc.)
    2. analyze_report()  — Analyze medical reports (lab, radiology text)
    3. analyze_combined()— Combined image + report analysis
    4. ask_doctor()      — Interactive Q&A about findings
    """

    def __init__(self, api_key: str = None):
        self.client    = anthropic.Anthropic(api_key=api_key or config.anthropic_api_key)
        self.processor = ImageProcessor()

    # ─── Image Analysis ──────────────────────────────────────

    def analyze_image(
        self,
        image_path: str,
        patient:    PatientInfo,
        scan_type:  str = "general",
        body_region:str = "unknown",
    ) -> ImageAnalysisResult:
        """
        Analyze a medical image using Claude Vision.

        Args:
            image_path:  Path to image (.jpg, .png, .dcm, .pdf)
            patient:     Patient information
            scan_type:   Type of scan (xray, mri, ct, etc.)
            body_region: Body region being imaged

        Returns:
            ImageAnalysisResult with findings and recommendations
        """
        # Process and encode image
        b64_image, media_type, metadata = self.processor.load_and_encode(image_path)

        # Build prompt
        prompt = IMAGE_ANALYSIS_PROMPT.format(
            scan_type=scan_type,
            body_region=body_region,
            patient_age=patient.age or "Unknown",
            patient_gender=patient.gender.value if hasattr(patient.gender, 'value') else str(patient.gender),
            clinical_history=patient.clinical_history or "Not provided",
            physician_notes=patient.physician_notes or "None",
        )

        # Call Claude Vision
        response = self.client.messages.create(
            model=MODEL_VISION,
            max_tokens=4000,
            system=ANALYSIS_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type":  "image",
                            "source": {
                                "type":       "base64",
                                "media_type": media_type,
                                "data":       b64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
        )

        raw  = self._clean_json(response.content[0].text)
        data = json.loads(raw)

        return self._parse_image_result(data, scan_type, body_region)

    # ─── Report Analysis ─────────────────────────────────────

    def analyze_report(
        self,
        report_text: str,
        patient:     PatientInfo,
    ) -> ReportAnalysisResult:
        """
        Analyze a medical report (lab results, radiology report, etc.)

        Args:
            report_text: Full text of the medical report
            patient:     Patient information

        Returns:
            ReportAnalysisResult with clinical summary
        """
        prompt = REPORT_ANALYSIS_PROMPT.format(
            report_text=report_text,
            patient_age=patient.age or "Unknown",
            patient_gender=patient.gender.value if hasattr(patient.gender, 'value') else str(patient.gender),
            chief_complaint=patient.chief_complaint or "Not specified",
        )

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=3000,
            system=ANALYSIS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw  = self._clean_json(response.content[0].text)
        data = json.loads(raw)

        return self._parse_report_result(data)

    # ─── Combined Analysis ───────────────────────────────────

    def analyze_combined(
        self,
        patient:       PatientInfo,
        image_result:  Optional[ImageAnalysisResult] = None,
        report_result: Optional[ReportAnalysisResult]= None,
    ) -> CombinedAnalysisResult:
        """
        Combine image and report analysis for comprehensive diagnosis.
        """
        if not image_result and not report_result:
            raise ValueError("At least one of image_result or report_result required")

        image_summary  = image_result.impression  if image_result  else "No image analysis"
        report_summary = report_result.summary    if report_result else "No report analysis"

        prompt = COMBINED_ANALYSIS_PROMPT.format(
            image_summary=image_summary,
            report_summary=report_summary,
            patient_age=patient.age or "Unknown",
            patient_gender=patient.gender.value if hasattr(patient.gender, 'value') else str(patient.gender),
            chief_complaint=patient.chief_complaint or "Not specified",
        )

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=3000,
            system=ANALYSIS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw  = self._clean_json(response.content[0].text)
        data = json.loads(raw)

        return CombinedAnalysisResult(
            patient=patient,
            image_result=image_result,
            report_result=report_result,
            combined_data=data,
            final_diagnosis=data.get("final_diagnosis", {}),
            severity_overall=data.get("severity_overall", "NORMAL"),
            urgency=data.get("urgency", "ROUTINE"),
            comprehensive_plan=data.get("comprehensive_action_plan", {}),
            patient_counseling=data.get("patient_counseling", {}),
            prognosis=data.get("prognosis", ""),
            executive_summary=data.get("executive_summary", ""),
        )

    # ─── Doctor Q&A ──────────────────────────────────────────

    def ask_doctor(
        self,
        question:        str,
        analysis_result: CombinedAnalysisResult,
    ) -> str:
        """
        Ask follow-up clinical questions about the analysis.
        Acts as a virtual radiologist/physician assistant.
        """
        context = f"""
You have already analyzed this patient:
- Patient: {analysis_result.patient.age}yr {analysis_result.patient.gender}
- Chief Complaint: {analysis_result.patient.chief_complaint}
- Executive Summary: {analysis_result.executive_summary}
- Overall Severity: {analysis_result.severity_overall}
- Final Diagnosis: {json.dumps(analysis_result.final_diagnosis, indent=2)}
- Action Plan: {json.dumps(analysis_result.comprehensive_plan, indent=2)}

The physician asks: {question}

Respond as a knowledgeable medical consultant. Be specific, cite relevant findings.
Include appropriate clinical caveats. Plain text response (no JSON).
"""
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=1000,
            system=ANALYSIS_SYSTEM_PROMPT + "\nRespond in plain text, not JSON.",
            messages=[{"role": "user", "content": context}],
        )
        return response.content[0].text

    # ─── Parse Results ───────────────────────────────────────

    def _parse_image_result(self, data: dict, scan_type: str, body_region: str) -> ImageAnalysisResult:
        findings = []
        for f in data.get("findings", []):
            try:
                sev = Severity(f.get("severity", "NORMAL"))
            except ValueError:
                sev = Severity.NORMAL
            findings.append(Finding(
                id=f.get("id", 0),
                region=f.get("region", ""),
                finding=f.get("finding", ""),
                normal_range=f.get("normal_range", ""),
                deviation=f.get("deviation", ""),
                severity=sev,
                confidence=f.get("confidence", 0),
                coordinates=f.get("coordinates", ""),
                size_measurement=f.get("size_measurement", ""),
                characteristics=f.get("characteristics", []),
            ))

        diagnoses = []
        for d in data.get("differential_diagnosis", []):
            diagnoses.append(Diagnosis(
                rank=d.get("rank", 0),
                diagnosis=d.get("diagnosis", ""),
                icd_code=d.get("icd_code", ""),
                probability=d.get("probability", "Low"),
                confidence=d.get("confidence", 0),
                supporting_evidence=d.get("supporting_evidence", []),
                against_evidence=d.get("against_evidence", []),
            ))

        try:
            sev = Severity(data.get("severity_overall", "NORMAL"))
        except ValueError:
            sev = Severity.NORMAL
        try:
            urg = Urgency(data.get("urgency", "ROUTINE"))
        except ValueError:
            urg = Urgency.ROUTINE

        iq = data.get("image_quality", {})
        return ImageAnalysisResult(
            scan_type=data.get("scan_type_detected", scan_type),
            body_region=data.get("body_region_detected", body_region),
            image_quality_score=iq.get("score", 0),
            image_quality_notes=iq.get("notes", ""),
            findings=findings,
            normal_findings=data.get("normal_findings", []),
            critical_findings=data.get("critical_findings", []),
            differential_diagnosis=diagnoses,
            severity_overall=sev,
            urgency=urg,
            impression=data.get("impression", ""),
            recommendations=data.get("recommendations", {}),
            doctor_action_plan=data.get("doctor_action_plan", {}),
            confidence_overall=data.get("confidence_overall", 0),
            limitations=data.get("limitations", []),
            structured_report=data.get("structured_report", ""),
            raw_data=data,
        )

    def _parse_report_result(self, data: dict) -> ReportAnalysisResult:
        return ReportAnalysisResult(
            report_type=data.get("report_type", "Unknown"),
            key_findings=data.get("key_findings", []),
            abnormal_findings=data.get("abnormal_findings", []),
            critical_values=data.get("critical_values", []),
            diagnosis_summary=data.get("diagnosis_summary", ""),
            differential_diagnosis=data.get("differential_diagnosis", []),
            severity_overall=data.get("severity_overall", "NORMAL"),
            doctor_action_plan=data.get("doctor_action_plan", {}),
            prognosis=data.get("prognosis", {}),
            red_flags=data.get("red_flags", []),
            summary=data.get("summary", ""),
            confidence=data.get("confidence", 0),
            raw_data=data,
        )

    def _clean_json(self, text: str) -> str:
        text = re.sub(r"```json\n?", "", text)
        text = re.sub(r"```\n?", "", text)
        return text.strip()
