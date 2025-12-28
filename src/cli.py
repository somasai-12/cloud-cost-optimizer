import sys
import threading
import time
import itertools
from src.config import DESCRIPTION_FILE, PROFILE_FILE, BILLING_FILE, REPORT_FILE
from src.file_utils import load_json, save_json, save_text, load_text, file_exists
from src.profile_extractor import extract_project_profile
from src.billing_generator import generate_billing
from src.cost_analyzer import analyze_costs
from src.recommendation_generator import generate_recommendations
from src.report_builder import build_cost_optimization_report
from src.html_exporter import export_to_html
from src.logger import get_logger

logger = get_logger("cli")

class Spinner:
    def __init__(self, message="Processing..."):
        self.message = message
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._animate)

    def _animate(self):
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if self.stop_event.is_set():
                break
            sys.stdout.write(f'\r{c} {self.message}')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
        sys.stdout.flush()

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_event.set()
        self.thread.join()

def run_cli():
    print("\n" + "=" * 60)
    print(" CLOUD COST OPTIMIZER (LLM-Driven)")
    print("=" * 60)
    
    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            option_1_enter_description()
        elif choice == "2":
            option_2_run_analysis()
        elif choice == "3":
            option_3_view_recommendations()
        elif choice == "4":
            option_4_export_report()
        elif choice == "5":
            print("\n✓ Cloud Cost Optimizer closed!")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1-5.\n")

def display_menu():
    status_2 = "✓ Available" if file_exists(PROFILE_FILE) else "(Complete Step 1 first)"
    status_3 = "✓ Available" if file_exists(REPORT_FILE) else "(Complete Step 2 first)"
    status_4 = "✓ Available" if file_exists(REPORT_FILE) else "(Complete Step 2 first)"
    
    print("\n" + "=" * 60)
    print("MENU OPTIONS")
    print("=" * 60)
    print(f"1. Enter a new project description")
    print(f"2. Run Complete Cost Analysis          {status_2}")
    print(f"3. View Recommendations               {status_3}")
    print(f"4. Export Report (JSON & HTML)         {status_4}")
    print(f"5. Exit")
    print("=" * 60)

def option_1_enter_description():
    print("\n" + "-" * 60)
    print("ENTER PROJECT DESCRIPTION")
    print("-" * 60)
    while True:
        print("Describe your cloud project (press Enter twice when done):")
        print()
        
        lines = []
        while True:
            line = input()
            if line == "":
                if len(lines) > 0 and lines[-1] == "":
                    lines.pop()
                    break
                lines.append(line)
            else:
                lines.append(line)
        
        description = "\n".join(lines).strip()
        
        if len(description) < 10:
            print("Description too short. Please provide more details.\n")
            continue
        
        if not save_text(DESCRIPTION_FILE, description):
            print("Failed to save description\n")
            return
        
        print()
        
        profile = None
        with Spinner("Extracting project profile ..."):
            profile = extract_project_profile(description)
            
        if profile:
            if not save_json(PROFILE_FILE, profile):
                print("\nFailed to save profile\n")
                return
            
            print("\n✓ Project profile extracted and saved!")
            print(f"Project: {profile.get('name')}")
            print(f"Budget: ₹{profile.get('budget_inr_per_month')}/month")
            print(f"Tech Stack: {profile.get('tech_stack')}\n")
            break
        print("\nFailed to extract profile.")
        retry = input("   check for budget feasibility for given description\n   Try again with a NEW description? (y/n): ").strip().lower()
        if retry != 'y':
            return
        
        print("\n" + "-" * 60)
        print("RE-ENTER PROJECT DESCRIPTION")
        print("-" * 60)

def option_2_run_analysis():

    print("\n" + "-" * 60)
    print("RUN COMPLETE COST ANALYSIS")
    print("-" * 60)
    
    if not file_exists(PROFILE_FILE):
        print("Project profile not found!")
        print(" Please complete Step 1 first: Enter project description\n")
        return
    profile = load_json(PROFILE_FILE)
    if not profile:
        print("Failed to load project profile\n")
        return
    
    print(f"Project: {profile.get('name')}")
    billing = None
    while True:
        with Spinner("Generating synthetic billing data ..."):
            billing = generate_billing(profile)
            
        if billing:
            break
            
        print("\nFailed to generate billing.")
        retry = input("   Retry? (y/n): ").strip().lower()
        if retry != 'y':
            return
        print()
    if not save_json(BILLING_FILE, billing):
        print("Failed to save billing\n")
        return
    
    print(f"✓ Generated {len(billing)} billing records")
    with Spinner("Analyzing costs..."):
        analysis = analyze_costs(profile, billing)
        
    if not analysis:
        print("\nFailed to analyze costs\n")
        return
    
    print("✓ Cost analysis complete")
    recommendations = None
    while True:
        with Spinner("Generating optimization recommendations "):
            recommendations = generate_recommendations(profile, billing, analysis)
        
        if recommendations:
            break
            
        print("\nFailed to generate recommendations.")
        retry = input("   Retry? (y/n): ").strip().lower()
        if retry != 'y':
            return
        print()
    
    print(f"✓ Generated {len(recommendations)} recommendations")
    
    report = build_cost_optimization_report(profile, analysis, recommendations)
    if not report:
        print("Failed to build report\n")
        retry = input("   Retry? (y/n): ").strip().lower()
        if retry != 'y':
            return
    
    if not save_json(REPORT_FILE, report):
        print("Failed to save report\n")
        return
    
    print("✓ Report saved")
    
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total Monthly Cost: ₹{analysis['total_monthly_cost']}")
    print(f"Budget: ₹{analysis['budget']}")
    print(f"Variance: ₹{analysis['budget_variance']}")
    print(f"Over Budget: {'Yes' if analysis['is_over_budget'] else 'No ✓'}")
    print(f"\nRecommendations: {len(recommendations)}")
    print(f"Potential Savings: ₹{report['summary']['total_potential_savings']}")
    print(f"Savings %: {report['summary']['savings_percentage']}%")
    print("=" * 60)
    print("\n Analysis complete! View recommendations in Step 3.\n")

def option_3_view_recommendations():
   
    print("\n" + "-" * 60)
    print(" VIEW RECOMMENDATIONS")
    print("-" * 60)

    if not file_exists(REPORT_FILE):
        print("Analysis report not found!")
        print("    Please complete Step 2 first: Run cost analysis\n")
        return
    
    report = load_json(REPORT_FILE)
    if not report:
        print(" Failed to load report\n")
        return
    
    recommendations = report.get("recommendations", [])
    
    print(f"\n Project: {report.get('project_name')}")
    print(f" Total Potential Savings: ₹{report['summary']['total_potential_savings']}")
    print(f" Savings Percentage: {report['summary']['savings_percentage']}%\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{'=' * 60}")
        print(f"Recommendation #{i}: {rec.get('title')}")
        print(f"{'=' * 60}")
        print(f"Service: {rec.get('service')}")
        print(f"Current Cost: ₹{rec.get('current_cost')}")
        print(f"Potential Savings: ₹{rec.get('potential_savings')}")
        print(f"Type: {rec.get('recommendation_type')}")
        print(f"Effort: {rec.get('implementation_effort')}")
        print(f"Risk: {rec.get('risk_level')}")
        print(f"Cloud Providers: {', '.join(rec.get('cloud_providers', []))}")
        print(f"\nDescription:")
        print(f"{rec.get('description')}")
        print(f"\nImplementation Steps:")
        for j, step in enumerate(rec.get('steps', []), 1):
            print(f"  {j}. {step}")
    
    print(f"\n{'=' * 60}\n")

def option_4_export_report():
    
    print("\n" + "-" * 60)
    print(" EXPORT REPORT")
    print("-" * 60)
    if not file_exists(REPORT_FILE):
        print(" Analysis report not found!")
        print("  Please complete Step 2 first: Run cost analysis\n")
        return

    report = load_json(REPORT_FILE)
    if not report:
        print(" Failed to load report\n")
        return
    
    print(" JSON Report: outputs/cost_optimization_report.json")

    html_path = "outputs/cost_optimization_report.html"
    if export_to_html(report, html_path):
        print(f" HTML Report: {html_path}")
    else:
        print(" Failed to export HTML report")

    print(f"\nProject: {report.get('project_name')}")
    print(f"Total Cost: ₹{report['analysis']['total_monthly_cost']}")
    print(f"Recommendations: {len(report['recommendations'])}\n")