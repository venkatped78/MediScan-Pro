# ============================================================
# display.py — Rich Terminal UI for Medical AI
# ============================================================

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.rule import Rule
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

console = Console()

SEV_STYLES = {
    "CRITICAL": ("bold red",     "🚨"),
    "HIGH":     ("red",          "🔴"),
    "MODERATE": ("yellow",       "🟡"),
    "LOW":      ("green",        "🟢"),
    "NORMAL":   ("bright_green", "✅"),
}

URG_STYLES = {
    "EMERGENCY": "bold red",
    "URGENT":    "red",
    "ROUTINE":   "yellow",
    "ELECTIVE":  "green",
}


def print_header():
    console.print()
    console.print(Align.center(
        "[bold white on #1a237e]  🏥 MEDICAL IMAGE ANALYSIS AI  [/]"
        "[bold white on #0d47a1]  Powered by Claude · Clinical Decision Support  [/]"
    ))
    console.print(Align.center(
        "[dim]X-Ray · MRI · CT · Ultrasound · Lab Reports · Pathology[/dim]"
    ))
    console.print()


def print_disclaimer():
    console.print(Panel(
        "[bold red]⚠️  MEDICAL DISCLAIMER[/bold red]\n\n"
        "This AI analysis is for [bold]EDUCATIONAL and RESEARCH[/bold] purposes ONLY.\n"
        "It is [bold red]NOT[/bold red] a substitute for professional medical diagnosis.\n"
        "Always consult a qualified healthcare professional for medical decisions.\n"
        "[bold]In emergencies: Call 112 / 911 immediately.[/bold]",
        border_style="red", padding=(1, 2),
    ))
    console.print()


def print_analysis_result(result, label="Analysis Result"):
    from models.patient import CombinedAnalysisResult

    sev   = result.severity_overall if isinstance(result.severity_overall, str) else result.severity_overall.value
    urg   = getattr(result, 'urgency', 'ROUTINE')
    urg   = urg if isinstance(urg, str) else urg.value

    sev_style, sev_icon = SEV_STYLES.get(sev, ("white", "•"))
    urg_style            = URG_STYLES.get(urg, "white")

    console.print()
    console.print(Rule(f"[bold #1a237e]{label}[/]"))
    console.print()

    # Status panels
    panels = [
        Panel(f"[bold {sev_style}]{sev_icon} {sev}[/]\n[dim]Severity[/]",
              border_style=sev_style.split()[-1], padding=(0,2)),
        Panel(f"[bold {urg_style}]{urg}[/]\n[dim]Urgency[/]",
              border_style=urg_style.split()[-1], padding=(0,2)),
    ]

    if hasattr(result, 'confidence_overall'):
        panels.append(Panel(
            f"[bold cyan]{result.confidence_overall}%[/]\n[dim]Confidence[/]",
            border_style="cyan", padding=(0,2)
        ))
    if hasattr(result, 'image_quality_score'):
        panels.append(Panel(
            f"[bold]{result.image_quality_score}%[/]\n[dim]Image Quality[/]",
            border_style="white", padding=(0,2)
        ))
    console.print(Columns(panels, equal=True, expand=True))
    console.print()


def print_image_result(img_result):
    console.print(Rule("[bold #1a237e]🩻 IMAGING ANALYSIS[/]"))
    console.print()

    # Impression
    if img_result.impression:
        console.print(Panel(
            f"[italic]{img_result.impression}[/]",
            title="[bold cyan]📋 Radiological Impression[/]",
            border_style="cyan", padding=(1,2),
        ))

    # Critical findings
    if img_result.critical_findings:
        console.print(Panel(
            "\n".join(f"[bold red]🚨 {cf}[/]" for cf in img_result.critical_findings),
            title="[bold red]⚠️ CRITICAL FINDINGS[/]",
            border_style="red", padding=(1,2),
        ))

    # Findings table
    if img_result.findings:
        table = Table(title="Detailed Findings", box=box.ROUNDED,
                      border_style="#1a237e", header_style="bold #1a237e",
                      show_lines=True)
        table.add_column("#",       width=4,  justify="center")
        table.add_column("Region",  width=14)
        table.add_column("Finding", width=40)
        table.add_column("Severity",width=12, justify="center")
        table.add_column("Conf.",   width=8,  justify="center")

        for f in img_result.findings:
            sev = f.severity.value if hasattr(f.severity, 'value') else str(f.severity)
            sev_style, sev_icon = SEV_STYLES.get(sev, ("white", "•"))
            table.add_row(
                str(f.id), f.region,
                f.finding[:80] + ("..." if len(f.finding) > 80 else ""),
                f"[{sev_style}]{sev_icon} {sev}[/]",
                f"[bold]{f.confidence}%[/]",
            )
        console.print(table)
        console.print()

    # Differential diagnosis
    if img_result.differential_diagnosis:
        console.print("[bold #1a237e]🔬 Differential Diagnosis:[/]")
        for d in img_result.differential_diagnosis[:5]:
            prob_color = {"High": "red", "Moderate": "yellow", "Low": "green"}.get(d.probability, "white")
            console.print(
                f"  [bold]{d.rank}.[/] {d.diagnosis} "
                f"[dim](ICD: {d.icd_code})[/] — "
                f"[{prob_color}]{d.probability} probability[/] "
                f"[dim]{d.confidence}% confidence[/]"
            )
        console.print()


def print_report_result(rpt_result):
    console.print(Rule("[bold #1a237e]📄 REPORT ANALYSIS[/]"))
    console.print()

    if rpt_result.diagnosis_summary:
        console.print(Panel(
            rpt_result.diagnosis_summary,
            title="[bold cyan]Clinical Summary[/]",
            border_style="cyan", padding=(1,2),
        ))

    if rpt_result.critical_values:
        console.print("[bold red]🚨 CRITICAL VALUES:[/]")
        for cv in rpt_result.critical_values:
            console.print(f"  [bold red]⚠ {cv}[/]")
        console.print()

    if rpt_result.key_findings:
        table = Table(title="Key Findings", box=box.ROUNDED,
                      border_style="#1a237e", header_style="bold #1a237e")
        table.add_column("Parameter",   width=18)
        table.add_column("Value",       width=12)
        table.add_column("Normal",      width=14)
        table.add_column("Status",      width=10)
        table.add_column("Significance",width=32)

        for kf in rpt_result.key_findings[:12]:
            status = kf.get("status","")
            sc = "red" if status == "Critical" else "yellow" if status == "Abnormal" else "green"
            table.add_row(
                kf.get("parameter",""), kf.get("value",""),
                kf.get("normal_range",""),
                f"[{sc}]{status}[/]",
                kf.get("clinical_significance","")[:60],
            )
        console.print(table)
        console.print()


def print_action_plan(plan: dict, title: str = "Physician Action Plan"):
    console.print(Rule(f"[bold #1a237e]📋 {title}[/]"))
    console.print()

    sections = [
        ("Immediate Actions (24h)", "immediate_24h",          "bold red"),
        ("Week 1 Actions",          "week1",                  "yellow"),
        ("Long-term Management",    "ongoing",                "green"),
        ("Specialist Referrals",    "specialist_team",        "cyan"),
        ("Investigations Needed",   "investigations_needed",  "blue"),
        ("Monitoring",              "monitoring_parameters",  "dim"),
    ]

    for label, key, color in sections:
        vals = plan.get(key, [])
        if not vals:
            continue
        console.print(f"[{color}]▶ {label}:[/]")
        for v in (vals if isinstance(vals, list) else [vals]):
            console.print(f"   • {v}")
        console.print()


def print_combined_summary(result):
    console.print()
    console.print(Panel(
        result.executive_summary or "No summary available.",
        title="[bold #1a237e]📊 EXECUTIVE CLINICAL SUMMARY[/]",
        border_style="#1a237e", padding=(1,2),
    ))
    if result.prognosis:
        console.print(Panel(
            result.prognosis,
            title="[bold cyan]📈 Prognosis[/]",
            border_style="cyan", padding=(1,2),
        ))


def create_progress():
    return Progress(
        SpinnerColumn(style="#1a237e"),
        TextColumn("[bold #1a237e]{task.description}[/]"),
        BarColumn(bar_width=30, style="#1a237e", complete_style="bright_green"),
        console=console, transient=False,
    )


def print_success(msg): console.print(f"[bold green]✅[/] {msg}")
def print_error(msg):   console.print(f"[bold red]❌[/] {msg}")
def print_info(msg):    console.print(f"[bold cyan]ℹ[/]  {msg}")
def print_warn(msg):    console.print(f"[bold yellow]⚠[/]  {msg}")
