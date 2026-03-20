#!/usr/bin/env python3
# ============================================================
# main.py — Medical AI Analysis System CLI
# ============================================================
# Usage:
#   python main.py                              # Interactive
#   python main.py analyze-image scan.jpg       # Image only
#   python main.py analyze-report report.txt    # Report only
#   python main.py analyze-both scan.jpg report.txt  # Combined
#   python main.py demo                         # Run demo
# ============================================================

import os
import sys
import json
import click
from pathlib import Path
from dotenv import load_dotenv
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from agents.medical_agent import MedicalAgent
from models.patient import PatientInfo, Gender
from services.report_generator import ReportGenerator
from display import (
    console, print_header, print_disclaimer,
    print_analysis_result, print_image_result,
    print_report_result, print_action_plan,
    print_combined_summary, create_progress,
    print_success, print_error, print_info, print_warn,
)
from config.settings import SCAN_TYPES, BODY_REGIONS, MEDICAL_DISCLAIMER

load_dotenv()

# ─── Demo data ───────────────────────────────────────────────
DEMO_REPORT = """
PATIENT: John Doe, 55 years, Male
DATE: 2025-03-15

LABORATORY REPORT

COMPLETE BLOOD COUNT:
- Hemoglobin: 9.2 g/dL (Normal: 13.5-17.5) — LOW
- WBC: 12,500 /μL (Normal: 4,500-11,000) — HIGH
- Platelets: 145,000 /μL (Normal: 150,000-400,000) — LOW NORMAL
- Hematocrit: 28% (Normal: 41-53%) — LOW

BASIC METABOLIC PANEL:
- Sodium: 138 mEq/L (Normal: 136-145) — Normal
- Potassium: 5.8 mEq/L (Normal: 3.5-5.0) — HIGH ⚠️
- Creatinine: 3.2 mg/dL (Normal: 0.7-1.2) — HIGH ⚠️
- BUN: 52 mg/dL (Normal: 7-20) — HIGH
- Glucose: 245 mg/dL (Normal: 70-99) — HIGH ⚠️
- eGFR: 18 mL/min/1.73m² — CRITICALLY LOW

LIVER FUNCTION:
- ALT: 85 U/L (Normal: 7-56) — HIGH
- AST: 92 U/L (Normal: 10-40) — HIGH
- Bilirubin Total: 1.8 mg/dL (Normal: 0.1-1.2) — HIGH

LIPID PANEL:
- Total Cholesterol: 285 mg/dL (Normal: <200) — HIGH
- LDL: 178 mg/dL (Normal: <100) — HIGH
- HbA1c: 9.2% (Normal: <5.7%) — HIGH (Diabetic range)

CLINICAL NOTES:
Patient presents with fatigue, shortness of breath, decreased urine output,
peripheral edema, and poorly controlled diabetes.
History of hypertension and type 2 diabetes for 10 years.
Current medications: Metformin, Amlodipine, Furosemide.
"""


def get_patient_info_interactive() -> PatientInfo:
    """Collect patient information interactively."""
    console.print("\n[bold cyan]📋 Patient Information[/]")
    console.print("[dim]Press Enter to skip optional fields[/]")
    console.print()

    name = Prompt.ask("Patient name", default="Anonymous")
    age  = Prompt.ask("Age",          default="0")
    gender_choice = Prompt.ask(
        "Gender", choices=["Male","Female","Other","Unknown"], default="Unknown"
    )
    chief = Prompt.ask("Chief complaint / reason for scan", default="")
    history = Prompt.ask("Clinical history (brief)", default="")
    notes = Prompt.ask("Physician notes", default="")
    referring = Prompt.ask("Referring doctor", default="")

    return PatientInfo(
        name=name,
        age=int(age) if age.isdigit() else 0,
        gender=Gender(gender_choice),
        chief_complaint=chief,
        clinical_history=history,
        physician_notes=notes,
        referring_doctor=referring,
    )


def run_image_analysis(
    agent: MedicalAgent,
    image_path: str,
    patient: PatientInfo,
    save_pdf: bool = True,
) -> dict:
    """Run image analysis pipeline."""
    console.print(f"\n[bold]Image:[/] {image_path}")

    scan_types_display = ", ".join(list(SCAN_TYPES.keys())[:8])
    scan_type = Prompt.ask(
        f"Scan type [{scan_types_display}]", default="general"
    )
    body_region = Prompt.ask(
        f"Body region [{', '.join(BODY_REGIONS[:8])}]", default="unknown"
    )

    with create_progress() as progress:
        task = progress.add_task("🧠 Analyzing medical image with AI...", total=None)
        img_result = agent.analyze_image(
            image_path=image_path,
            patient=patient,
            scan_type=scan_type,
            body_region=body_region,
        )
        progress.update(task, completed=True, description="✅ Image analysis complete!")

    # Display
    sev = img_result.severity_overall.value if hasattr(img_result.severity_overall, 'value') else str(img_result.severity_overall)
    urg = img_result.urgency.value if hasattr(img_result.urgency, 'value') else str(img_result.urgency)

    from models.patient import CombinedAnalysisResult
    combined = CombinedAnalysisResult(
        patient=patient,
        image_result=img_result,
        severity_overall=sev,
        urgency=urg,
        executive_summary=img_result.impression,
        prognosis="",
        final_diagnosis={"primary": img_result.differential_diagnosis[0].diagnosis if img_result.differential_diagnosis else "Pending"},
        comprehensive_plan=img_result.doctor_action_plan,
        patient_counseling={"diagnosis_explanation": img_result.structured_report[:200] if img_result.structured_report else ""},
    )

    print_analysis_result(combined, "IMAGE ANALYSIS RESULT")
    print_image_result(img_result)

    if img_result.doctor_action_plan:
        print_action_plan(img_result.doctor_action_plan, "Doctor Action Plan")

    # PDF report
    if save_pdf:
        try:
            rg   = ReportGenerator()
            path = rg.generate(combined)
            print_success(f"PDF Report saved: [bold]{path}[/]")
        except Exception as e:
            print_warn(f"PDF generation failed: {e}")

    return {"type": "image", "result": img_result}


def run_report_analysis(
    agent: MedicalAgent,
    report_text: str,
    patient: PatientInfo,
    save_pdf: bool = True,
) -> dict:
    """Run report analysis pipeline."""
    with create_progress() as progress:
        task = progress.add_task("🧠 Analyzing medical report with AI...", total=None)
        rpt_result = agent.analyze_report(report_text=report_text, patient=patient)
        progress.update(task, completed=True, description="✅ Report analysis complete!")

    from models.patient import CombinedAnalysisResult
    combined = CombinedAnalysisResult(
        patient=patient,
        report_result=rpt_result,
        severity_overall=rpt_result.severity_overall,
        urgency="URGENT" if rpt_result.severity_overall in ["CRITICAL","HIGH"] else "ROUTINE",
        executive_summary=rpt_result.summary,
        prognosis=rpt_result.prognosis.get("short_term","") if rpt_result.prognosis else "",
        final_diagnosis={
            "primary": rpt_result.differential_diagnosis[0].get("condition","") if rpt_result.differential_diagnosis else "Pending",
            "confidence": rpt_result.confidence,
        },
        comprehensive_plan=rpt_result.doctor_action_plan,
        patient_counseling={"warning_signs": rpt_result.red_flags},
    )

    print_analysis_result(combined, "REPORT ANALYSIS RESULT")
    print_report_result(rpt_result)
    print_combined_summary(combined)

    if rpt_result.doctor_action_plan:
        print_action_plan(rpt_result.doctor_action_plan, "Doctor Action Plan")

    if rpt_result.red_flags:
        console.print("\n[bold red]🚨 RED FLAGS — Go to ER if:[/]")
        for rf in rpt_result.red_flags:
            console.print(f"  [red]• {rf}[/]")

    if save_pdf:
        try:
            rg   = ReportGenerator()
            path = rg.generate(combined)
            print_success(f"PDF Report saved: [bold]{path}[/]")
        except Exception as e:
            print_warn(f"PDF generation failed: {e}")

    return {"type": "report", "result": rpt_result}


def run_combined_analysis(
    agent: MedicalAgent,
    image_path: str,
    report_text: str,
    patient: PatientInfo,
    scan_type: str = "general",
    body_region: str = "unknown",
    save_pdf: bool = True,
) -> dict:
    """Run full combined analysis pipeline."""
    img_result = rpt_result = None

    with create_progress() as progress:
        # Analyze image
        if image_path:
            task = progress.add_task("🩻 Analyzing medical image...", total=None)
            img_result = agent.analyze_image(image_path, patient, scan_type, body_region)
            progress.update(task, completed=True, description="✅ Image done!")

        # Analyze report
        if report_text:
            task2 = progress.add_task("📄 Analyzing medical report...", total=None)
            rpt_result = agent.analyze_report(report_text, patient)
            progress.update(task2, completed=True, description="✅ Report done!")

        # Combined
        task3 = progress.add_task("🧠 Generating combined analysis...", total=None)
        combined = agent.analyze_combined(patient, img_result, rpt_result)
        progress.update(task3, completed=True, description="✅ Combined analysis done!")

    # Display
    print_analysis_result(combined, "COMBINED CLINICAL ANALYSIS")
    print_combined_summary(combined)

    if img_result:
        print_image_result(img_result)
    if rpt_result:
        print_report_result(rpt_result)

    if combined.comprehensive_plan:
        print_action_plan(combined.comprehensive_plan, "Comprehensive Physician Action Plan")

    if combined.patient_counseling.get("warning_signs"):
        console.print("\n[bold red]🚨 EMERGENCY WARNING SIGNS:[/]")
        for ws in combined.patient_counseling["warning_signs"]:
            console.print(f"  [red]• {ws}[/]")

    # Q&A with doctor
    while True:
        console.print()
        if not Confirm.ask("[bold]Ask a follow-up clinical question?[/]", default=False):
            break
        question = Prompt.ask("[bold cyan]Your question[/]")
        with create_progress() as p:
            t = p.add_task("🤔 Consulting AI physician...", total=None)
            answer = agent.ask_doctor(question, combined)
            p.update(t, completed=True)
        console.print(Panel(answer, title="[bold cyan]🩺 AI Clinical Consultant[/]",
                           border_style="cyan", padding=(1,2)))

    # Save PDF
    if save_pdf:
        try:
            rg   = ReportGenerator()
            path = rg.generate(combined)
            print_success(f"PDF Report saved: [bold]{path}[/]")
            combined.report_path = path
        except Exception as e:
            print_warn(f"PDF generation failed: {e}")

    return {"type": "combined", "result": combined}


# ─── CLI ─────────────────────────────────────────────────────

@click.group()
@click.option("--api-key", default=None, help="Anthropic API key")
@click.pass_context
def cli(ctx, api_key):
    """
    \b
    🏥 Medical Image Analysis AI — Clinical Decision Support System
    Powered by Claude AI | X-Ray | MRI | CT | Lab Reports | Pathology

    \b
    Examples:
      python main.py demo
      python main.py analyze-image chest_xray.jpg
      python main.py analyze-report lab_results.txt
      python main.py analyze-both mri.jpg report.txt
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        print_header()
        key = Prompt.ask("[bold cyan]Enter Anthropic API key[/]")
    ctx.ensure_object(dict)
    ctx.obj["agent"] = MedicalAgent(api_key=key)


@cli.command()
@click.pass_context
def menu(ctx):
    """Interactive menu."""
    print_header()
    print_disclaimer()
    agent = ctx.obj["agent"]

    console.print(Panel(
        "  [cyan]1.[/] Analyze medical image (X-ray, MRI, CT, Ultrasound)\n"
        "  [cyan]2.[/] Analyze medical report (lab results, radiology report)\n"
        "  [cyan]3.[/] Full analysis (image + report together)\n"
        "  [cyan]4.[/] Run demo (sample lab report analysis)\n"
        "  [cyan]0.[/] Exit",
        title="[bold #1a237e]🏥 Medical AI System[/]",
        border_style="#1a237e", padding=(1,3),
    ))
    choice = Prompt.ask("[bold]Choose[/]", choices=["0","1","2","3","4"], default="4")

    if choice == "0":
        return
    elif choice == "1":
        patient    = get_patient_info_interactive()
        image_path = Prompt.ask("[bold cyan]Image file path[/]")
        run_image_analysis(agent, image_path, patient)
    elif choice == "2":
        patient = get_patient_info_interactive()
        report_path = Prompt.ask("[bold cyan]Report file path (.txt/.pdf)[/]")
        report_text = Path(report_path).read_text()
        run_report_analysis(agent, report_text, patient)
    elif choice == "3":
        patient    = get_patient_info_interactive()
        image_path = Prompt.ask("[bold cyan]Image file path[/]")
        report_path= Prompt.ask("[bold cyan]Report file path[/]")
        report_text= Path(report_path).read_text()
        run_combined_analysis(agent, image_path, report_text, patient)
    elif choice == "4":
        run_demo(agent)


@cli.command("analyze-image")
@click.argument("image_path")
@click.option("--scan-type",   default="general",  help="xray/mri/ct/ultrasound")
@click.option("--body-region", default="unknown",  help="chest/brain/abdomen etc")
@click.option("--age",         default=0,          help="Patient age")
@click.option("--gender",      default="Unknown",  help="Male/Female/Other")
@click.option("--complaint",   default="",         help="Chief complaint")
@click.option("--history",     default="",         help="Clinical history")
@click.option("--no-pdf",      is_flag=True,       help="Skip PDF generation")
@click.pass_context
def analyze_image_cmd(ctx, image_path, scan_type, body_region,
                       age, gender, complaint, history, no_pdf):
    """Analyze a medical image file."""
    print_header()
    print_disclaimer()
    patient = PatientInfo(age=age, gender=Gender(gender),
                          chief_complaint=complaint, clinical_history=history)
    run_image_analysis(ctx.obj["agent"], image_path, patient, save_pdf=not no_pdf)


@cli.command("analyze-report")
@click.argument("report_path")
@click.option("--age",      default=0,       help="Patient age")
@click.option("--gender",   default="Unknown")
@click.option("--complaint",default="")
@click.option("--no-pdf",   is_flag=True)
@click.pass_context
def analyze_report_cmd(ctx, report_path, age, gender, complaint, no_pdf):
    """Analyze a medical report file."""
    print_header()
    print_disclaimer()
    report_text = Path(report_path).read_text(encoding="utf-8")
    patient = PatientInfo(age=age, gender=Gender(gender), chief_complaint=complaint)
    run_report_analysis(ctx.obj["agent"], report_text, patient, save_pdf=not no_pdf)


@cli.command("analyze-both")
@click.argument("image_path")
@click.argument("report_path")
@click.option("--scan-type",   default="general")
@click.option("--body-region", default="unknown")
@click.option("--age",         default=0)
@click.option("--gender",      default="Unknown")
@click.option("--complaint",   default="")
@click.option("--no-pdf",      is_flag=True)
@click.pass_context
def analyze_both_cmd(ctx, image_path, report_path, scan_type,
                      body_region, age, gender, complaint, no_pdf):
    """Analyze both image and report together for comprehensive diagnosis."""
    print_header()
    print_disclaimer()
    report_text = Path(report_path).read_text(encoding="utf-8")
    patient = PatientInfo(age=age, gender=Gender(gender), chief_complaint=complaint)
    run_combined_analysis(ctx.obj["agent"], image_path, report_text,
                          patient, scan_type, body_region, save_pdf=not no_pdf)


@cli.command()
@click.pass_context
def demo(ctx):
    """Run demo with sample lab report."""
    print_header()
    print_disclaimer()
    run_demo(ctx.obj["agent"])


def run_demo(agent: MedicalAgent):
    """Run demo analysis with sample patient data."""
    print_info("Running demo: 55-year-old male with diabetes + kidney disease...")
    patient = PatientInfo(
        name="Demo Patient",
        age=55,
        gender=Gender.MALE,
        chief_complaint="Fatigue, shortness of breath, decreased urine output",
        clinical_history="10-year history of T2DM and hypertension. Recent worsening.",
        referring_doctor="Dr. Smith",
    )
    run_report_analysis(agent, DEMO_REPORT, patient, save_pdf=True)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        load_dotenv()
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        agent = MedicalAgent(api_key=key)
        print_header()
        print_disclaimer()
        run_demo(agent)
    else:
        cli(obj={})
