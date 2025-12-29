"""
AI-Powered Complaint Summarizer
Generates executive summaries for management review using Gemini API
"""

import google.generativeai as genai
from datetime import datetime
import json
import time
from functools import wraps


def rate_limit(calls_per_minute=12):
    """
    Rate limiting decorator to stay under Gemini API free tier limits (15/min)
    Conservative limit of 12/min for safety margin
    """
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator


class ComplaintSummarizer:
    """Generates executive-style AI summaries of complaint data"""

    def __init__(self, gemini_api_key, model="gemini-2.0-flash"):
        """
        Initialize with Gemini API

        Args:
            gemini_api_key (str): Google Gemini API key
            model (str): Gemini model to use (default: gemini-2.0-flash)
        """
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(model)

    @rate_limit(calls_per_minute=12)
    def generate_summary(self, complaints, department, date_range):
        """
        Generate executive summary from complaint list

        Args:
            complaints (list): List of complaint records from database
            department (str): Department name for context
            date_range (dict): Dict with 'start' and 'end' datetime objects

        Returns:
            dict: Summary data including generated text, metadata, and stats
        """
        if not complaints:
            return {
                'summary': f"No complaints found for {department} during the specified period.",
                'complaint_count': 0,
                'high_priority_count': 0,
                'key_issues': [],
                'generated_at': datetime.now().isoformat()
            }

        # Prepare complaint data for LLM
        complaint_data = []
        high_priority_count = 0

        for comp in complaints:
            # comp structure from SQL query:
            # 0: complaint_id, 1: complaint_type, 2: department, 3: priority,
            # 4: description, 5: status, 6: created_at, 7: extracted_entities,
            # 8: name, 9: phone

            if comp[3] == 'HIGH':
                high_priority_count += 1

            complaint_data.append({
                'id': comp[0],
                'type': comp[1],
                'priority': comp[3],
                'description': comp[4],
                'status': comp[5],
                'date': comp[6].strftime('%Y-%m-%d %H:%M') if hasattr(comp[6], 'strftime') else str(comp[6]),
                'customer': comp[8],
                'entities': json.loads(comp[7]) if comp[7] and isinstance(comp[7], str) else (comp[7] or {})
            })

        # Build prompt for executive summary
        start_date_str = date_range['start'].strftime('%d %B %Y')
        end_date_str = date_range['end'].strftime('%d %B %Y')

        prompt = f"""You are a Personal Assistant preparing a brief executive summary for telecom company management.

**Context:**
Department: {department}
Period: {start_date_str} to {end_date_str}
Total Complaints: {len(complaints)}
High Priority: {high_priority_count}

**Complaint Details:**
{json.dumps(complaint_data[:20], indent=2)}
{f"... and {len(complaint_data) - 20} more complaints" if len(complaint_data) > 20 else ""}

**Task:** Create a concise executive summary in the style of a Personal Assistant briefing a CEO.

**Format:**
1. **Overview** (2-3 sentences): High-level summary of complaint volume, severity, and trends
2. **Key Issues** (3-5 bullet points): Main problem categories with counts and impact
3. **Critical Cases** (if any HIGH priority): Specific urgent matters requiring immediate attention
4. **Recommendations** (2-3 bullet points): Actionable next steps for the department

**Tone:**
- Professional, concise, action-oriented
- Focus on business impact, not technical details
- Use numbers and specific examples
- Avoid jargon - make it accessible to non-technical executives

**Length:** Maximum 250 words total.

**Example Start:**
"During {start_date_str} to {end_date_str}, the {department} department received {len(complaints)} complaints, with {high_priority_count} marked as high priority..."
"""

        try:
            response = self.model.generate_content(prompt)
            summary_text = response.text

            # Extract key issues (attempt to parse from summary)
            key_issues = self._extract_key_issues(complaint_data)

            return {
                'summary': summary_text,
                'complaint_count': len(complaints),
                'high_priority_count': high_priority_count,
                'key_issues': key_issues,
                'generated_at': datetime.now().isoformat(),
                'department': department,
                'date_range': {
                    'start': start_date_str,
                    'end': end_date_str
                }
            }

        except Exception as e:
            print(f"[SUMMARY ERROR] {e}")
            return {
                'summary': f"Error generating summary: {str(e)}",
                'complaint_count': len(complaints),
                'high_priority_count': high_priority_count,
                'error': True,
                'error_message': str(e),
                'generated_at': datetime.now().isoformat()
            }

    def _extract_key_issues(self, complaint_data):
        """
        Extract top complaint types from complaint data

        Args:
            complaint_data (list): List of complaint dicts

        Returns:
            list: Top 5 issues with counts
        """
        issue_counts = {}

        for comp in complaint_data:
            comp_type = comp['type']
            issue_counts[comp_type] = issue_counts.get(comp_type, 0) + 1

        # Sort by count and return top 5
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return [
            {
                'issue': issue.replace('_', ' ').title(),
                'count': count,
                'percentage': round(count / len(complaint_data) * 100, 1)
            }
            for issue, count in sorted_issues
        ]

    def generate_department_comparison(self, all_departments_data):
        """
        Compare complaints across all departments

        Args:
            all_departments_data (dict): Mapping of department -> complaint list

        Returns:
            dict: Cross-department analysis summary
        """
        total_complaints = sum(len(comps) for comps in all_departments_data.values())

        if total_complaints == 0:
            return {
                'summary': "No complaints found across any department.",
                'total_complaints': 0,
                'generated_at': datetime.now().isoformat()
            }

        # Build comparative data
        dept_stats = {}
        for dept, complaints in all_departments_data.items():
            high_priority = sum(1 for c in complaints if c[3] == 'HIGH')
            dept_stats[dept] = {
                'total': len(complaints),
                'high_priority': high_priority,
                'percentage': round(len(complaints) / total_complaints * 100, 1)
            }

        prompt = f"""You are a Personal Assistant preparing a cross-department complaint analysis for senior management.

**Overview:**
Total Complaints: {total_complaints}

**Department Breakdown:**
{json.dumps(dept_stats, indent=2)}

**Task:** Create a 150-word executive summary comparing complaint volumes across departments.

**Focus on:**
1. Which departments have the highest complaint volumes
2. Priority distribution across departments
3. Any concerning trends or patterns
4. Recommended areas for management focus

**Tone:** Professional, data-driven, actionable.
"""

        try:
            response = self.model.generate_content(prompt)

            return {
                'summary': response.text,
                'total_complaints': total_complaints,
                'department_stats': dept_stats,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"[COMPARISON ERROR] {e}")
            return {
                'summary': f"Error generating comparison: {str(e)}",
                'total_complaints': total_complaints,
                'error': True,
                'generated_at': datetime.now().isoformat()
            }
