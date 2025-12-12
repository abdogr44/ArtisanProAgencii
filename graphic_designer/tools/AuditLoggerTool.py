from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import json
from datetime import datetime, timedelta
import glob

class AuditLoggerTool(BaseTool):
    """
    Logs all prompts, API requests, responses, and artifact URLs to a structured log file.
    Retains logs for 30 days for audit purposes.
    """
    action: str = Field(
        ..., description="Action being logged (e.g., 'prompt_sent', 'image_generated', 'api_error')"
    )
    target: str = Field(
        ..., description="Target system or service (e.g., 'kie.ai', 'local_processing')"
    )
    data: dict = Field(
        ..., description="Data to log (prompt, response, URLs, etc.)"
    )
    response_status: int = Field(
        default=200, description="HTTP response status code if applicable"
    )
    log_dir: str = Field(
        default="./graphic_designer/files/audit_logs", description="Directory for audit log files"
    )
    
    def run(self):
        """
        Appends audit log entry to daily log file.
        Auto-cleans logs older than 30 days.
        """
        # Step 1: Create log directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Step 2: Determine log file (one per day)
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"audit_{today}.json")
        
        # Step 3: Create log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': self.action,
            'target': self.target,
            'response_status': self.response_status,
            'data': self.data
        }
        
        # Step 4: Append to log file
        try:
            # Read existing logs if file exists
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Append new entry
            logs.append(log_entry)
            
            # Write back
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)
        
        except Exception as e:
            return json.dumps({
                'status': 'error',
                'message': f'Error writing to log file: {str(e)}'
            }, indent=2)
        
        # Step 5: Clean up old logs (>30 days)
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            log_pattern = os.path.join(self.log_dir, "audit_*.json")
            
            for old_log in glob.glob(log_pattern):
                filename = os.path.basename(old_log)
                # Extract date from filename: audit_YYYY-MM-DD.json
                date_str = filename.replace('audit_', '').replace('.json', '')
                try:
                    log_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if log_date < cutoff_date:
                        os.remove(old_log)
                except:
                    pass  # Skip files with unexpected naming
        
        except Exception as e:
            # Log cleanup failure shouldn't block the main operation
            pass
        
        # Step 6: Return success
        return json.dumps({
            'status': 'success',
            'log_file': log_file,
            'entry_logged': True,
            'timestamp': log_entry['timestamp']
        }, indent=2)

if __name__ == "__main__":
    # Test case: Log a sample API call
    tool = AuditLoggerTool(
        action="prompt_sent",
        target="kie.ai",
        data={
            'prompt': 'Generate a bold social media graphic...',
            'dimensions': '1080x1080',
            'style': 'bold'
        },
        response_status=200
    )
    result = tool.run()
    print(result)
