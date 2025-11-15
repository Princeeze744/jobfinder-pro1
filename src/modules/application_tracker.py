"""
Application Tracker Module
Tracks job applications and sends follow-ups
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from src.logger import logger
from src.config import DATA_DIR

class ApplicationTracker:
    """
    Tracks job applications and their status
    """
    
    def __init__(self, tracker_file: str = "src/data/applications.json"):
        """Initialize application tracker"""
        self.tracker_file = Path(tracker_file)
        self.applications = self._load_applications()
        logger.info("✅ ApplicationTracker initialized")
    
    def _load_applications(self) -> List[Dict]:
        """Load existing applications from file"""
        try:
            if self.tracker_file.exists():
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.warning(f"⚠️ Could not load applications: {str(e)}")
            return []
    
    def add_application(self, candidate_name: str, company_name: str, 
                       company_email: str, email_sent: bool = False) -> Dict:
        """
        Add a new application record
        
        Args:
            candidate_name: Name of candidate
            company_name: Company name
            company_email: Company email
            email_sent: Whether email was sent
            
        Returns:
            Application record
        """
        try:
            application = {
                "id": len(self.applications) + 1,
                "candidate_name": candidate_name,
                "company_name": company_name,
                "company_email": company_email,
                "status": "Applied",
                "date_applied": datetime.now().isoformat(),
                "email_sent": email_sent,
                "follow_up_sent": False,
                "follow_up_date": None,
                "notes": "",
                "response_received": False,
                "response_date": None,
                "interview_scheduled": False,
                "interview_date": None
            }
            
            self.applications.append(application)
            self._save_applications()
            
            logger.info(f"✅ Application added: {company_name}")
            return application
        
        except Exception as e:
            logger.error(f"❌ Error adding application: {str(e)}")
            raise
    
    def update_application_status(self, application_id: int, 
                                  status: str, notes: str = "") -> Dict:
        """
        Update application status
        
        Args:
            application_id: Application ID
            status: New status (Applied, Interviewing, Rejected, Offered)
            notes: Additional notes
            
        Returns:
            Updated application
        """
        try:
            app = self._find_application(application_id)
            if app:
                app['status'] = status
                if notes:
                    app['notes'] = notes
                self._save_applications()
                logger.info(f"✅ Status updated for application {application_id}: {status}")
                return app
            else:
                logger.warning(f"⚠️ Application {application_id} not found")
                return None
        
        except Exception as e:
            logger.error(f"❌ Error updating status: {str(e)}")
            raise
    
    def mark_email_sent(self, application_id: int) -> Dict:
        """Mark email as sent"""
        app = self._find_application(application_id)
        if app:
            app['email_sent'] = True
            self._save_applications()
            logger.info(f"✅ Email marked as sent for application {application_id}")
            return app
        return None
    
    def record_response(self, application_id: int, response_notes: str = "") -> Dict:
        """Record response from company"""
        app = self._find_application(application_id)
        if app:
            app['response_received'] = True
            app['response_date'] = datetime.now().isoformat()
            if response_notes:
                app['notes'] += f"\nResponse: {response_notes}"
            self._save_applications()
            logger.info(f"✅ Response recorded for application {application_id}")
            return app
        return None
    
    def schedule_interview(self, application_id: int, interview_date: str) -> Dict:
        """Schedule interview"""
        app = self._find_application(application_id)
        if app:
            app['interview_scheduled'] = True
            app['interview_date'] = interview_date
            app['status'] = "Interviewing"
            self._save_applications()
            logger.info(f"✅ Interview scheduled for application {application_id}: {interview_date}")
            return app
        return None
    
    def get_statistics(self) -> Dict:
        """Get application statistics"""
        total = len(self.applications)
        
        if total == 0:
            return {
                "total_applications": 0,
                "emails_sent": 0,
                "responses_received": 0,
                "interviews_scheduled": 0,
                "offers_received": 0
            }
        
        emails_sent = sum(1 for app in self.applications if app['email_sent'])
        responses = sum(1 for app in self.applications if app['response_received'])
        interviews = sum(1 for app in self.applications if app['interview_scheduled'])
        offers = sum(1 for app in self.applications if app['status'] == 'Offered')
        
        return {
            "total_applications": total,
            "emails_sent": emails_sent,
            "responses_received": responses,
            "interviews_scheduled": interviews,
            "offers_received": offers,
            "response_rate": round((responses / total * 100), 2) if total > 0 else 0,
            "interview_rate": round((interviews / total * 100), 2) if total > 0 else 0
        }
    
    def get_pending_followups(self) -> List[Dict]:
        """Get applications pending follow-up"""
        pending = [
            app for app in self.applications
            if app['email_sent'] and not app['follow_up_sent']
        ]
        logger.info(f"✅ Found {len(pending)} applications pending follow-up")
        return pending
    
    def get_all_applications(self) -> List[Dict]:
        """Get all applications"""
        return self.applications
    
    def export_as_csv(self) -> str:
        """Export applications as CSV"""
        import csv
        import io
        
        buffer = io.StringIO()
        
        if not self.applications:
            return ""
        
        fieldnames = self.applications[0].keys()
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(self.applications)
        
        logger.info(f"✅ Exported {len(self.applications)} applications as CSV")
        return buffer.getvalue()
    
    def _find_application(self, application_id: int) -> Optional[Dict]:
        """Find application by ID"""
        for app in self.applications:
            if app['id'] == application_id:
                return app
        return None
    
    def _save_applications(self):
        """Save applications to file"""
        try:
            self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.tracker_file, 'w', encoding='utf-8') as f:
                json.dump(self.applications, f, indent=2, ensure_ascii=False)
            logger.debug(f"✅ Applications saved to {self.tracker_file}")
        except Exception as e:
            logger.error(f"❌ Error saving applications: {str(e)}")


if __name__ == "__main__":
    tracker = ApplicationTracker()
    print(tracker.get_statistics())