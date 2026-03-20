# 🏥 Medical Image Analysis AI — Clinical Decision Support System

> **Production-grade AI Medical Analysis System** powered by Claude AI.
> Analyzes medical scans (X-Ray, MRI, CT, Ultrasound), lab reports, and
> pathology results — providing radiologist-level analysis, differential diagnosis,
> and step-by-step doctor action plans.

![Python](https://img.shields.io/badge/Python-3.10+-3776ab)
![Claude](https://img.shields.io/badge/AI-Claude%20Opus-2dd4bf)
![Medical](https://img.shields.io/badge/Medical-AI%20Analysis-red)
![License](https://img.shields.io/badge/license-MIT-green)

> ⚠️ **DISCLAIMER:** For educational and research purposes ONLY.
> Not a substitute for professional medical diagnosis.

---

## 🎯 What It Does

```
Medical Image / Lab Report
           ↓
┌──────────────────────────────────────────────────┐
│  MedicalAgent (Claude AI)                         │
│  ├── Image Analysis (Vision AI)                   │
│  │   ├── Detect abnormalities in X-ray/MRI/CT     │
│  │   ├── Measure lesion sizes, locations           │
│  │   ├── Assess image quality                      │
│  │   └── Generate radiological impression          │
│  ├── Report Analysis (NLP)                        │
│  │   ├── Parse lab values vs normal ranges         │
│  │   ├── Flag critical values                      │
│  │   ├── Identify patterns across results          │
│  │   └── Generate clinical summary                 │
│  └── Combined Analysis                            │
│      ├── Correlate image + report findings         │
│      ├── Final differential diagnosis (ICD-10)     │
│      ├── Severity: CRITICAL/HIGH/MODERATE/LOW      │
│      ├── Urgency: EMERGENCY/URGENT/ROUTINE         │
│      └── Step-by-step Doctor Action Plan           │
└──────────────────────────────────────────────────┘
           ↓
📊 Rich Terminal Report + 📄 Professional PDF
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🩻 **Medical Image Analysis** | X-Ray, MRI, CT, Ultrasound, PET, Mammogram |
| 📄 **Report Analysis** | Lab results, CBC, metabolic panel, LFT, lipid panel |
| 🔬 **Differential Diagnosis** | Ranked diagnoses with ICD-10 codes + confidence % |
| 🚨 **Critical Value Detection** | Immediately flags life-threatening values |
| 📋 **Doctor Action Plan** | Step-by-step: immediate/week1/long-term actions |
| 💊 **Treatment Guidance** | Medication categories, monitoring parameters |
| 💬 **Q&A Mode** | Ask follow-up clinical questions interactively |
| 📁 **DICOM Support** | Read .dcm files with full metadata extraction |
| 📊 **PDF Reports** | Professional A4 medical reports with tables |
| 🎯 **Severity Scoring** | 5-level severity: CRITICAL → NORMAL |
| 👤 **Patient Counseling** | What to tell patients, warning signs |
| 📈 **Prognosis** | Short-term and long-term outlook |

---

## 🚀 Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Configure
Create `.env` file:
```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### 3. Run Demo
```bash
python main.py demo
```

This runs a full analysis of a sample patient with:
- Severe anemia (Hb: 9.2)
- Kidney failure (eGFR: 18)
- Uncontrolled diabetes (HbA1c: 9.2%)
- Elevated liver enzymes

---

## 🎮 Usage

### Interactive Menu
```bash
python main.py menu
```

### Analyze Medical Image
```bash
# Basic
python main.py analyze-image chest_xray.jpg

# With patient details
python main.py analyze-image brain_mri.jpg \
  --scan-type mri \
  --body-region brain \
  --age 45 \
  --gender Male \
  --complaint "Severe headache and vision changes"

# Skip PDF
python main.py analyze-image scan.jpg --no-pdf
```

### Analyze Medical Report
```bash
python main.py analyze-report lab_results.txt \
  --age 55 \
  --gender Male \
  --complaint "Fatigue and shortness of breath"
```

### Full Combined Analysis (Image + Report)
```bash
python main.py analyze-both \
  chest_xray.jpg \
  lab_report.txt \
  --scan-type xray \
  --body-region chest \
  --age 60 \
  --gender Female \
  --complaint "Cough and chest pain"
```

---

## 📁 Project Structure

```
medical-ai/
│
├── main.py                      ← CLI entry point + all commands
│
├── agents/
│   └── medical_agent.py         ← Core AI engine
│       ├── analyze_image()      → Vision AI scan analysis
│       ├── analyze_report()     → NLP report parsing
│       ├── analyze_combined()   → Multi-modal synthesis
│       └── ask_doctor()         → Interactive Q&A
│
├── services/
│   ├── image_processor.py       ← Image loading + preprocessing
│   │   ├── Standard images (JPG/PNG/TIFF)
│   │   ├── DICOM files (.dcm) with metadata
│   │   └── PDF → image extraction
│   └── report_generator.py      ← Professional PDF generation
│
├── models/
│   └── patient.py               ← Data models
│       ├── PatientInfo
│       ├── Finding, Diagnosis
│       ├── ImageAnalysisResult
│       ├── ReportAnalysisResult
│       └── CombinedAnalysisResult
│
├── config/
│   └── settings.py              ← All prompts, constants, config
│
├── display.py                   ← Rich terminal UI
├── requirements.txt
├── .env                         ← API key
└── README.md
```

---

## 🔬 Medical Analysis Capabilities

### Image Analysis Output
```
✅ Image quality assessment (0-100%)
✅ Scan type and body region detection
✅ Detailed findings per anatomical region
✅ Severity per finding (CRITICAL/HIGH/MODERATE/LOW/NORMAL)
✅ Lesion size measurements
✅ Normal structures confirmed
✅ Critical findings flagged immediately
✅ Differential diagnosis (top 5, ranked)
✅ ICD-10 codes for each diagnosis
✅ Radiological impression (standard format)
✅ Recommendations: further imaging, labs, referrals
```

### Report Analysis Output
```
✅ Key parameters vs normal ranges
✅ Critical values detection
✅ Pattern recognition across multiple tests
✅ Clinical significance of each abnormality
✅ Differential diagnosis with reasoning
✅ Prognosis (short-term and long-term)
✅ Red flags requiring ER visit
✅ Confidence score for analysis
```

### Doctor Action Plan
```
📋 Immediate Actions (Next 24 hours)
📋 Week 1 Actions
📋 Long-term Management
📋 Specialist Referrals needed
📋 Additional Investigations
📋 Monitoring Parameters (what + how often)
📋 Medication categories to consider
📋 Lifestyle modifications
📋 Patient counseling guide
📋 Warning signs for emergency
```

---

## 🩻 Supported Scan Types

| Scan | Code |
|------|------|
| X-Ray | `xray` |
| MRI | `mri` |
| CT Scan | `ct` |
| Ultrasound | `ultrasound` |
| PET Scan | `pet` |
| Mammogram | `mammogram` |
| ECG/EKG | `ecg` |
| Pathology | `pathology` |
| Fundus/Retinal | `fundus` |
| Dermoscopy | `dermoscopy` |

---

## 📊 Severity System

| Level | Icon | Meaning | Action |
|-------|------|---------|--------|
| CRITICAL | 🚨 | Life-threatening | Immediate emergency care |
| HIGH | 🔴 | Serious | Urgent specialist referral |
| MODERATE | 🟡 | Significant | Prompt medical attention |
| LOW | 🟢 | Minor | Routine follow-up |
| NORMAL | ✅ | No concern | No immediate action |

---

## 🎯 AI/ML Engineer Interview Talking Points

This project demonstrates:

1. **Multi-modal AI** — Claude Vision for images + NLP for text reports
2. **Structured Output** — Complex nested JSON schema enforcement
3. **Prompt Engineering** — Clinical-grade system prompts with medical context
4. **Domain Adaptation** — AI adapted to medical terminology and standards
5. **Data Modeling** — Pydantic-like dataclasses for medical data structures
6. **PDF Generation** — Professional ReportLab document generation
7. **DICOM Processing** — Medical imaging standard file format
8. **Image Preprocessing** — PIL/Pillow pipeline for medical scan enhancement
9. **Error Handling** — Production-grade exception handling
10. **CLI Design** — Click with multiple subcommands

---

## 🛠 Tech Stack

| Library | Purpose |
|---------|---------|
| `anthropic` | Claude AI (Vision + NLP) |
| `Pillow` | Image processing |
| `pydicom` | DICOM medical image files |
| `reportlab` | PDF report generation |
| `rich` | Terminal UI |
| `click` | CLI framework |
| `numpy` | Numerical processing |
| `opencv-python` | Advanced image ops |

---

## ⚠️ Important Notes

- API uses Claude Opus (most capable) for medical accuracy
- Each analysis costs ~$0.05-0.15 per scan
- Results are AI-generated — always verify with qualified physician
- DICOM files may contain patient data — handle with care (HIPAA/GDPR)

---

## 📄 License
MIT — For educational and research use.

---
**Built by an AI/ML Engineer · Demonstrates advanced multi-modal LLM application development**
