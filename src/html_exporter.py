import json
import os
from src.logger import get_logger

logger = get_logger("html_exporter")

def export_to_html(report, output_path = "outputs/cost_optimization_report.html"):
    try:
        project_name = report.get("project_name", "Project")
        analysis = report.get("analysis", {})
        recommendations = report.get("recommendations", [])
        summary = report.get("summary", {})
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cost Optimization Report - {project_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; background-color: #f4f7f6; }}
        header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        h1 {{ margin: 0; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
        .stat {{ text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #2a5298; }}
        .stat-label {{ color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; }}
        .rec-card {{ border-left: 5px solid #2a5298; margin-bottom: 15px; padding: 15px; background: white; border-radius: 0 8px 8px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .rec-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .rec-title {{ font-size: 1.2em; font-weight: bold; color: #2a5298; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }}
        .badge-effort {{ background-color: #e3f2fd; color: #1565c0; }}
        .badge-savings {{ background-color: #e8f5e9; color: #2e7d32; }}
        .steps {{ background-color: #f9f9f9; padding: 10px 20px; border-radius: 4px; border: 1px dashed #ccc; }}
        .footer {{ text-align: center; margin-top: 40px; color: #888; font-size: 0.9em; }}
    </style>
</head>
<body>

<header>
    <h1>Cloud Cost Optimization Report</h1>
    <p>{project_name}</p>
</header>

<div class="card">
    <h2>Executive Summary</h2>
    <div class="summary-grid">
        <div class="stat">
            <div class="stat-value">₹{analysis.get('total_monthly_cost', 0)}</div>
            <div class="stat-label">Total Monthly Cost</div>
        </div>
        <div class="stat">
            <div class="stat-value">₹{analysis.get('budget', 0)}</div>
            <div class="stat-label">Budget</div>
        </div>
        <div class="stat">
            <div class="stat-value">₹{summary.get('total_potential_savings', 0)}</div>
            <div class="stat-label">Potential Savings</div>
        </div>
        <div class="stat">
            <div class="stat-value" style="color: #27ae60;">{summary.get('savings_percentage', 0)}%</div>
            <div class="stat-label">Optimization Score</div>
        </div>
    </div>
</div>

<div class="card">
    <h2>Cost Breakdown</h2>
    <table>
        <thead>
            <tr>
                <th>Service</th>
                <th>Cost (INR)</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
"""
        for service, cost in analysis.get('service_costs', {}).items():
            html_content += f"""
            <tr>
                <td>{service}</td>
                <td>₹{cost}</td>
                <td>{'High' if service in analysis.get('high_cost_services', {}) else 'Normal'}</td>
            </tr>
            """

        html_content += """
        </tbody>
    </table>
</div>

<h2>💡 Recommendations</h2>
"""
        for rec in recommendations:
            html_content += f"""
<div class="rec-card">
    <div class="rec-header">
        <div class="rec-title">{rec.get('title')}</div>
        <div>
            <span class="badge badge-savings">Save ₹{rec.get('potential_savings')}</span>
            <span class="badge badge-effort">{rec.get('implementation_effort', 'medium').upper()} Effort</span>
        </div>
    </div>
    <p><strong>Service:</strong> {rec.get('service')} | <strong>Type:</strong> {rec.get('recommendation_type')}</p>
    <p>{rec.get('description')}</p>
    
    <div class="steps">
        <strong>Implementation Steps:</strong>
        <ol>
"""
            for step in rec.get('steps', []):
                html_content += f"<li>{step}</li>"
            
            html_content += """
        </ol>
    </div>
    
    <p style="margin-top: 10px;">
        <strong>Cloud Providers:</strong> 
        """ + ", ".join(rec.get('cloud_providers', [])) + """
    </p>
</div>
"""

        html_content += f"""
<div class="footer">
    Generated by Cloud Cost Optimizer (AI-Powered) | {report.get('generated_at', '2025')}
</div>

</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"HTML report exported to {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to export HTML: {e}")
        return False