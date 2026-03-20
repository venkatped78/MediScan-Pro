# ============================================================
# config/settings.py — Medical AI Configuration
# ============================================================

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-4-20250514"   # Use most capable model for medical
MODEL_VISION = "claude-opus-4-20250514"  # Vision-capable model

# ─── Medical Scan Types ──────────────────────────────────────
SCAN_TYPES = {
    "xray":       "X-Ray (Radiograph)",
    "mri":        "MRI (Magnetic Resonance Imaging)",
    "ct":         "CT Scan (Computed Tomography)",
    "ultrasound": "Ultrasound / Sonography",
    "pet":        "PET Scan",
    "mammogram":  "Mammogram",
    "ecg":        "ECG / EKG",
    "pathology":  "Pathology Slide",
    "fundus":     "Fundus / Retinal Image",
    "dermoscopy": "Dermoscopy",
    "endoscopy":  "Endoscopy",
    "general":    "General Medical Image",
}

# ─── Body Regions ────────────────────────────────────────────
BODY_REGIONS = [
    "chest", "brain", "abdomen", "pelvis", "spine",
    "knee", "shoulder", "hip", "wrist", "ankle",
    "heart", "liver", "kidney", "lung", "breast",
    "eye", "skin", "neck", "whole body", "unknown",
]

# ─── Severity Levels ─────────────────────────────────────────
SEVERITY_LEVELS = {
    "CRITICAL":  {"color": "bold red",    "icon": "🚨", "action": "Immediate emergency care required"},
    "HIGH":      {"color": "red",         "icon": "🔴", "action": "Urgent specialist referral needed"},
    "MODERATE":  {"color": "yellow",      "icon": "🟡", "action": "Prompt medical attention recommended"},
    "LOW":       {"color": "green",       "icon": "🟢", "action": "Routine follow-up suggested"},
    "NORMAL":    {"color": "bright_green","icon": "✅", "action": "No immediate action required"},
}

# ─── Medical Specialties ─────────────────────────────────────
SPECIALTIES = {
    "radiology":      "Radiologist",
    "cardiology":     "Cardiologist",
    "neurology":      "Neurologist",
    "orthopedics":    "Orthopedic Surgeon",
    "oncology":       "Oncologist",
    "pulmonology":    "Pulmonologist",
    "gastroenterology":"Gastroenterologist",
    "ophthalmology":  "Ophthalmologist",
    "dermatology":    "Dermatologist",
    "nephrology":     "Nephrologist",
    "hepatology":     "Hepatologist",
    "gynecology":     "Gynecologist",
    "urology":        "Urologist",
    "general":        "General Physician",
}

# ─── Disclaimer ──────────────────────────────────────────────
MEDICAL_DISCLAIMER = """
⚠️  IMPORTANT MEDICAL DISCLAIMER  ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This AI analysis is for EDUCATIONAL and RESEARCH purposes only.
It is NOT a substitute for professional medical diagnosis.
Always consult a qualified healthcare professional for:
• Medical diagnosis and treatment decisions
• Prescription of medications
• Surgical or invasive procedures
• Emergency medical situations

In case of medical emergency, call emergency services immediately.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ─── Master Analysis Prompt ──────────────────────────────────
ANALYSIS_SYSTEM_PROMPT = """You are MedicalAI, an advanced medical image analysis system trained on
millions of medical images and clinical literature. You assist radiologists and physicians
by providing detailed, structured analysis of medical images and reports.

You have expertise in:
- Radiology (X-ray, CT, MRI, Ultrasound, PET)
- Pathology and histology
- Cardiology (ECG, Echo)
- Ophthalmology (Fundus, OCT)
- Dermatology (Dermoscopy)
- Oncology imaging
- Emergency medicine imaging

Your analysis follows clinical standards used by board-certified radiologists.
You provide findings in structured RADLEX/ACR reporting format.

CRITICAL RULES:
1. Always include confidence levels for findings
2. Differentiate between definitive findings and possibilities
3. Always recommend appropriate specialist referrals
4. Flag critical/urgent findings prominently
5. Use proper medical terminology with plain language explanations
6. Never give definitive diagnosis — provide differential diagnosis
7. Always recommend clinical correlation

Return ONLY valid JSON. No text before or after."""

IMAGE_ANALYSIS_PROMPT = """Analyze this medical image with the following context:

Scan Type: {scan_type}
Body Region: {body_region}
Patient Age: {patient_age}
Patient Gender: {patient_gender}
Clinical History: {clinical_history}
Referring Physician Notes: {physician_notes}

Provide a comprehensive radiological analysis. Return ONLY this JSON:
{{
  "image_quality": {{
    "score": 0-100,
    "adequacy": "Adequate/Suboptimal/Inadequate",
    "issues": ["issue1"],
    "notes": "quality assessment notes"
  }},
  "scan_type_detected": "detected scan type",
  "body_region_detected": "detected body region",
  "technical_parameters": {{
    "view": "AP/PA/Lateral/Axial etc",
    "contrast": true/false,
    "technique_notes": "any technical observations"
  }},
  "findings": [
    {{
      "id": 1,
      "region": "anatomical region",
      "finding": "detailed finding description",
      "normal_range": "what is normal here",
      "deviation": "how this deviates from normal",
      "severity": "CRITICAL/HIGH/MODERATE/LOW/NORMAL",
      "confidence": 0-100,
      "coordinates": "location description",
      "size_measurement": "size if measurable",
      "characteristics": ["char1", "char2"]
    }}
  ],
  "normal_findings": ["normal structure 1", "normal structure 2"],
  "critical_findings": ["urgent finding if any"],
  "differential_diagnosis": [
    {{
      "rank": 1,
      "diagnosis": "most likely diagnosis",
      "icd_code": "ICD-10 code",
      "probability": "High/Moderate/Low",
      "confidence": 0-100,
      "supporting_evidence": ["evidence1", "evidence2"],
      "against_evidence": ["evidence against"]
    }}
  ],
  "severity_overall": "CRITICAL/HIGH/MODERATE/LOW/NORMAL",
  "urgency": "EMERGENCY/URGENT/ROUTINE/ELECTIVE",
  "impression": "2-3 sentence radiological impression (most important summary)",
  "recommendations": {{
    "immediate_actions": ["action if critical"],
    "further_imaging": ["additional scans recommended"],
    "lab_tests": ["blood tests, biopsies etc"],
    "specialist_referrals": ["specialty1", "specialty2"],
    "follow_up": "follow up timeframe and plan",
    "clinical_correlation": "what clinical info to correlate"
  }},
  "doctor_action_plan": {{
    "step1": "First thing doctor should do",
    "step2": "Second step",
    "step3": "Third step",
    "medications_to_consider": ["med category, NOT specific prescription"],
    "monitoring_parameters": ["what to monitor"],
    "red_flags_to_watch": ["symptom1 requiring emergency"],
    "patient_education": ["what to tell the patient"]
  }},
  "confidence_overall": 0-100,
  "limitations": ["limitation1", "limitation2"],
  "structured_report": "Full radiological report in standard format"
}}"""

REPORT_ANALYSIS_PROMPT = """Analyze this medical report/text and provide comprehensive clinical summary.

Report Text:
{report_text}

Patient Context:
Age: {patient_age}
Gender: {patient_gender}
Chief Complaint: {chief_complaint}

Return ONLY this JSON:
{{
  "report_type": "type of report (lab, radiology, pathology etc)",
  "key_findings": [
    {{
      "parameter": "test/finding name",
      "value": "actual value",
      "normal_range": "reference range",
      "status": "Normal/Abnormal/Critical",
      "clinical_significance": "what this means clinically",
      "severity": "CRITICAL/HIGH/MODERATE/LOW/NORMAL"
    }}
  ],
  "abnormal_findings": ["list of abnormal values"],
  "critical_values": ["any life-threatening values"],
  "diagnosis_summary": "overall clinical picture",
  "differential_diagnosis": [
    {{
      "rank": 1,
      "condition": "condition name",
      "icd_code": "ICD-10",
      "probability": "High/Moderate/Low",
      "reasoning": "why this fits the findings"
    }}
  ],
  "severity_overall": "CRITICAL/HIGH/MODERATE/LOW/NORMAL",
  "doctor_action_plan": {{
    "immediate": ["action1 if urgent"],
    "short_term": ["within 24-48 hours"],
    "long_term": ["ongoing management"],
    "specialist_referrals": ["who to refer to"],
    "medications_category": ["type of medications to consider"],
    "lifestyle_advice": ["diet, exercise, lifestyle changes"],
    "monitoring_plan": ["what parameters to track"],
    "follow_up_schedule": "when to follow up",
    "patient_education": ["what to explain to patient"]
  }},
  "prognosis": {{
    "short_term": "outlook in weeks/months",
    "long_term": "outlook in years",
    "factors_improving": ["positive prognostic factors"],
    "factors_worsening": ["negative prognostic factors"]
  }},
  "red_flags": ["symptoms requiring immediate ER visit"],
  "summary": "3-4 sentence plain language summary for physician",
  "confidence": 0-100
}}"""

COMBINED_ANALYSIS_PROMPT = """You have analyzed both a medical image AND a medical report for the same patient.
Now provide a COMBINED comprehensive clinical analysis.

Image Analysis Summary: {image_summary}
Report Analysis Summary: {report_summary}
Patient: {patient_age} year old {patient_gender}
Chief Complaint: {chief_complaint}

Return ONLY this JSON:
{{
  "integrated_findings": "How image and report findings correlate and complement each other",
  "concordance": "Do image and report findings agree? Any discrepancies?",
  "final_diagnosis": {{
    "primary": "Most likely diagnosis",
    "icd_code": "ICD-10",
    "confidence": 0-100,
    "secondary": ["other confirmed conditions"],
    "differential": ["still possible alternatives"]
  }},
  "severity_overall": "CRITICAL/HIGH/MODERATE/LOW/NORMAL",
  "urgency": "EMERGENCY/URGENT/ROUTINE/ELECTIVE",
  "comprehensive_action_plan": {{
    "immediate_24h": ["actions in next 24 hours"],
    "week1": ["actions in first week"],
    "month1": ["actions in first month"],
    "ongoing": ["long-term management"],
    "specialist_team": ["specialists needed"],
    "investigations_needed": ["additional tests"],
    "treatment_approach": "general treatment strategy",
    "monitoring_parameters": ["what to track and how often"]
  }},
  "patient_counseling": {{
    "diagnosis_explanation": "how to explain to patient in simple terms",
    "lifestyle_modifications": ["specific changes needed"],
    "warning_signs": ["when to go to ER immediately"],
    "support_resources": ["support groups, resources"]
  }},
  "prognosis": "Overall prognosis with treatment",
  "executive_summary": "5-6 sentence complete clinical summary for referring doctor"
}}"""


@dataclass
class Config:
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    output_dir:        str = field(default_factory=lambda: os.getenv("OUTPUT_DIR", "reports"))
    db_path:           str = field(default_factory=lambda: os.getenv("DB_PATH", "medical_ai.db"))
    max_image_size:    int = 5 * 1024 * 1024  # 5MB
    supported_formats: tuple = ("jpg", "jpeg", "png", "bmp", "tiff", "dcm", "pdf")
    log_level:         str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))


config = Config()
