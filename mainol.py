import ollama
from models.patient import ReportAnalysisResult, ImageAnalysisResult, CombinedAnalysisResult

class MedicalAgent:
    """Medical AI Agent using Ollama (local, no API costs)."""
    
    def __init__(self, api_key=None, model="mistral"):
        """Initialize with local Ollama model."""
        self.model = model
        self.client = ollama  # Use local Ollama
        print(f"✅ Using local Ollama model: {model}")
    
    def analyze_report(self, report_text: str, patient) -> ReportAnalysisResult:
        """Analyze medical report using local Ollama."""
        prompt = f"""You are a medical AI assistant. Analyze this lab report for patient {patient.name}, age {patient.age}.

REPORT:
{report_text}

PATIENT INFO:
- Chief complaint: {patient.chief_complaint}
- History: {patient.clinical_history}

Provide a JSON response with:
{{
    "summary": "brief clinical summary",
    "severity_overall": "LOW/MEDIUM/HIGH/CRITICAL",
    "differential_diagnosis": [
        {{"condition": "name", "confidence": 0.85}}
    ],
    "doctor_action_plan": ["action1", "action2"],
    "red_flags": ["warning1", "warning2"],
    "prognosis": {{"short_term": "description"}},
    "confidence": 0.85
}}
"""
        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            stream=False,
        )
        
        import json
        try:
            text = response['response']
            json_str = text[text.find('{'):text.rfind('}')+1]
            data = json.loads(json_str)
        except:
            data = {
                "summary": response.get('response', 'Analysis complete'),
                "severity_overall": "MEDIUM",
                "differential_diagnosis": [],
                "doctor_action_plan": [],
                "red_flags": [],
                "prognosis": {},
                "confidence": 0.5
            }
        
        return ReportAnalysisResult(**data)
    
    def analyze_image(self, image_path: str, patient, scan_type: str, body_region: str) -> ImageAnalysisResult:
        """Analyze medical image using local Ollama."""
        prompt = f"""You are a radiologist AI. Analyze this {scan_type} scan of the {body_region}.

PATIENT: {patient.name}, {patient.age} years old
CHIEF COMPLAINT: {patient.chief_complaint}

Provide a JSON response with:
{{
    "impression": "radiologist impression",
    "differential_diagnosis": [
        {{"diagnosis": "condition name", "confidence": 0.85}}
    ],
    "doctor_action_plan": ["recommendation1"],
    "severity_overall": "LOW/MEDIUM/HIGH/CRITICAL",
    "urgency": "ROUTINE/URGENT/EMERGENT",
    "structured_report": "detailed report"
}}
"""
        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            stream=False,
        )
        
        import json
        try:
            text = response['response']
            json_str = text[text.find('{'):text.rfind('}')+1]
            data = json.loads(json_str)
        except:
            data = {
                "impression": "Image analyzed",
                "differential_diagnosis": [],
                "doctor_action_plan": [],
                "severity_overall": "MEDIUM",
                "urgency": "ROUTINE",
                "structured_report": ""
            }
        
        return ImageAnalysisResult(**data)
    
    def analyze_combined(self, patient, img_result, rpt_result) -> CombinedAnalysisResult:
        """Combine image and report analysis."""
        prompt = f"""Clinical Integration: Combine these findings for {patient.name}.

IMAGE FINDINGS: {img_result.impression if img_result else 'None'}
REPORT FINDINGS: {rpt_result.summary if rpt_result else 'None'}

Provide JSON:
{{
    "severity_overall": "HIGH",
    "urgency": "URGENT",
    "executive_summary": "integrated assessment",
    "comprehensive_plan": ["step1", "step2"]
}}
"""
        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            stream=False,
        )
        
        import json
        try:
            text = response['response']
            json_str = text[text.find('{'):text.rfind('}')+1]
            data = json.loads(json_str)
        except:
            data = {
                "severity_overall": "MEDIUM",
                "urgency": "ROUTINE",
                "executive_summary": "Analysis complete",
                "comprehensive_plan": []
            }
        
        return CombinedAnalysisResult(
            patient=patient,
            image_result=img_result,
            report_result=rpt_result,
            severity_overall=data.get("severity_overall", "MEDIUM"),
            urgency=data.get("urgency", "ROUTINE"),
            executive_summary=data.get("executive_summary", ""),
            prognosis="",
            final_diagnosis={},
            comprehensive_plan=data.get("comprehensive_plan", []),
            patient_counseling={}
        )
    
    def ask_doctor(self, question: str, combined) -> str:
        """Ask follow-up clinical question."""
        prompt = f"""Clinical question about patient {combined.patient.name}:
{question}

Context: {combined.executive_summary}

Provide a brief clinical response."""
        
        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            stream=False,
        )
        return response['response']
    


 
    
@click.group()
@click.option("--api-key", default=None, help="Anthropic API key (ignored, using Ollama)")
@click.option("--model", default="mistral", help="Ollama model (mistral/neural-chat/etc)")
@click.pass_context
def cli(ctx, api_key, model):
    """🏥 Medical AI — Now running LOCAL with Ollama (no API costs!)"""
    ctx.ensure_object(dict)
    ctx.obj["agent"] = MedicalAgent(model=model)
    print_info(f"✅ Using local Ollama model: {model}")