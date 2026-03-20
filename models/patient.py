# ============================================================
# models/patient.py — Medical Data Models
# ============================================================

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    MALE    = "Male"
    FEMALE  = "Female"
    OTHER   = "Other"
    UNKNOWN = "Unknown"


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH     = "HIGH"
    MODERATE = "MODERATE"
    LOW      = "LOW"
    NORMAL   = "NORMAL"


class Urgency(str, Enum):
    EMERGENCY = "EMERGENCY"
    URGENT    = "URGENT"
    ROUTINE   = "ROUTINE"
    ELECTIVE  = "ELECTIVE"


@dataclass
class PatientInfo:
    name:             str           = "Anonymous"
    age:              int           = 0
    gender:           Gender        = Gender.UNKNOWN
    patient_id:       str           = ""
    date_of_birth:    Optional[str] = None
    chief_complaint:  str           = ""
    clinical_history: str           = ""
    current_medications: List[str]  = field(default_factory=list)
    allergies:        List[str]     = field(default_factory=list)
    physician_notes:  str           = ""
    referring_doctor: str           = ""


@dataclass
class Finding:
    id:               int
    region:           str
    finding:          str
    normal_range:     str           = ""
    deviation:        str           = ""
    severity:         Severity      = Severity.NORMAL
    confidence:       int           = 0
    coordinates:      str           = ""
    size_measurement: str           = ""
    characteristics:  List[str]     = field(default_factory=list)


@dataclass
class Diagnosis:
    rank:               int
    diagnosis:          str
    icd_code:           str           = ""
    probability:        str           = "Low"
    confidence:         int           = 0
    supporting_evidence:List[str]     = field(default_factory=list)
    against_evidence:   List[str]     = field(default_factory=list)
    reasoning:          str           = ""


@dataclass
class DoctorActionPlan:
    immediate_24h:          List[str] = field(default_factory=list)
    week1:                  List[str] = field(default_factory=list)
    long_term:              List[str] = field(default_factory=list)
    specialist_referrals:   List[str] = field(default_factory=list)
    medications_category:   List[str] = field(default_factory=list)
    monitoring_parameters:  List[str] = field(default_factory=list)
    lifestyle_advice:       List[str] = field(default_factory=list)
    follow_up_schedule:     str       = ""
    patient_education:      List[str] = field(default_factory=list)
    red_flags:              List[str] = field(default_factory=list)


@dataclass
class ImageAnalysisResult:
    scan_type:           str
    body_region:         str
    image_quality_score: int           = 0
    image_quality_notes: str           = ""
    findings:            List[Finding] = field(default_factory=list)
    normal_findings:     List[str]     = field(default_factory=list)
    critical_findings:   List[str]     = field(default_factory=list)
    differential_diagnosis: List[Diagnosis] = field(default_factory=list)
    severity_overall:    Severity      = Severity.NORMAL
    urgency:             Urgency       = Urgency.ROUTINE
    impression:          str           = ""
    recommendations:     Dict[str, Any]= field(default_factory=dict)
    doctor_action_plan:  Dict[str, Any]= field(default_factory=dict)
    confidence_overall:  int           = 0
    limitations:         List[str]     = field(default_factory=list)
    structured_report:   str           = ""
    raw_data:            Dict          = field(default_factory=dict)
    analyzed_at:         datetime      = field(default_factory=datetime.now)


@dataclass
class ReportAnalysisResult:
    report_type:         str
    key_findings:        List[Dict]    = field(default_factory=list)
    abnormal_findings:   List[str]     = field(default_factory=list)
    critical_values:     List[str]     = field(default_factory=list)
    diagnosis_summary:   str           = ""
    differential_diagnosis: List[Dict] = field(default_factory=list)
    severity_overall:    str           = "NORMAL"
    doctor_action_plan:  Dict[str, Any]= field(default_factory=dict)
    prognosis:           Dict[str, str]= field(default_factory=dict)
    red_flags:           List[str]     = field(default_factory=list)
    summary:             str           = ""
    confidence:          int           = 0
    raw_data:            Dict          = field(default_factory=dict)
    analyzed_at:         datetime      = field(default_factory=datetime.now)


@dataclass
class CombinedAnalysisResult:
    patient:              PatientInfo
    image_result:         Optional[ImageAnalysisResult]   = None
    report_result:        Optional[ReportAnalysisResult]  = None
    combined_data:        Dict                            = field(default_factory=dict)
    final_diagnosis:      Dict                            = field(default_factory=dict)
    severity_overall:     str                            = "NORMAL"
    urgency:              str                            = "ROUTINE"
    comprehensive_plan:   Dict                            = field(default_factory=dict)
    patient_counseling:   Dict                            = field(default_factory=dict)
    prognosis:            str                            = ""
    executive_summary:    str                            = ""
    analyzed_at:          datetime                       = field(default_factory=datetime.now)
    report_path:          Optional[str]                  = None
