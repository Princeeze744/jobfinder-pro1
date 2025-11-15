"""
Main Engine - PRODUCTION GRADE
Orchestrates the entire talent acquisition automation pipeline
"""

from typing import Dict, List, Optional
from src.modules.cv_analyzer import CVAnalyzer
from src.modules.company_finder import CompanyFinder
from src.modules.email_generator import EmailGenerator
from src.logger import logger


class TalentAcquisitionEngine:
    """
    Main engine that orchestrates the complete talent acquisition pipeline
    """
    
    def __init__(self, ai_model: str = "gpt-4o-mini"):
        """
        Initialize the talent acquisition engine
        
        Args:
            ai_model: AI model to use (for backward compatibility, not used in current modules)
        """
        # Initialize modules (they read their own configs)
        self.cv_analyzer = CVAnalyzer()  # No ai_model parameter needed
        self.company_finder = CompanyFinder()
        self.email_generator = EmailGenerator()
        
        self.cv_analysis = None
        self.companies = []
        self.emails = []
        
        logger.info(f"✅ TalentAcquisitionEngine initialized")
    
    def run_full_pipeline(self, cv_path: str, 
                         num_companies: int = 20,
                         num_emails: Optional[int] = None,
                         mode: str = "ai",
                         location: str = "",
                         include_remote: bool = True) -> Dict:
        """
        Run the complete talent acquisition pipeline
        
        Args:
            cv_path: Path to CV file
            num_companies: Number of companies to find
            num_emails: Number of emails to generate (None = all)
            mode: Job discovery mode ("ai", "scraper", or "hybrid")
            location: Preferred location filter
            include_remote: Include remote jobs
            
        Returns:
            Complete results dictionary
        """
        logger.info("🚀 Starting full talent acquisition pipeline")
        
        try:
            # Step 1: Analyze CV
            logger.info("📄 Step 1: Analyzing CV...")
            self.cv_analysis = self.cv_analyzer.analyze_cv(cv_path)
            
            # Step 2: Find Companies
            logger.info("🏢 Step 2: Finding companies...")
            self.companies = self.company_finder.find_companies(
                self.cv_analysis, 
                num_queries=min(num_companies // 3, 8),
                mode=mode,
                location=location,
                include_remote=include_remote
            )
            
            # Step 3: Generate Emails
            logger.info("✉️ Step 3: Generating emails...")
            companies_for_emails = self.companies[:num_emails] if num_emails else self.companies
            self.emails = self.email_generator.generate_emails_batch(
                self.cv_analysis,
                companies_for_emails
            )
            
            logger.info("✅ Pipeline completed successfully!")
            
            return {
                'cv_analysis': self.cv_analysis,
                'companies': self.companies,
                'emails': self.emails,
                'stats': {
                    'total_companies': len(self.companies),
                    'total_emails': len(self.emails),
                    'candidate_name': self.cv_analysis.get('name')
                }
            }
        
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {str(e)}")
            raise
    
    def analyze_cv(self, cv_path: str) -> Dict:
        """Analyze CV only"""
        self.cv_analysis = self.cv_analyzer.analyze_cv(cv_path)
        return self.cv_analysis
    
    def find_companies(self, cv_analysis: Optional[Dict] = None, 
                      num_queries: int = 5,
                      mode: str = "ai",
                      location: str = "",
                      include_remote: bool = True) -> List[Dict]:
        """Find companies only"""
        if cv_analysis is None:
            cv_analysis = self.cv_analysis
        
        if not cv_analysis:
            raise ValueError("No CV analysis available")
        
        self.companies = self.company_finder.find_companies(
            cv_analysis, 
            num_queries,
            mode=mode,
            location=location,
            include_remote=include_remote
        )
        return self.companies
    
    def generate_emails(self, cv_analysis: Optional[Dict] = None,
                       companies: Optional[List[Dict]] = None,
                       max_emails: Optional[int] = None) -> List[Dict]:
        """Generate emails only"""
        if cv_analysis is None:
            cv_analysis = self.cv_analysis
        
        if companies is None:
            companies = self.companies
        
        if not cv_analysis or not companies:
            raise ValueError("Need CV analysis and companies")
        
        self.emails = self.email_generator.generate_emails_batch(
            cv_analysis, companies
        )
        return self.emails
    
    def get_results(self) -> Dict:
        """Get all results"""
        return {
            'cv_analysis': self.cv_analysis,
            'companies': self.companies,
            'emails': self.emails
        }
    
    def save_all_outputs(self):
        """Save all outputs to files"""
        if self.cv_analysis:
            self.cv_analyzer.save_analysis(self.cv_analysis)
        
        if self.companies:
            self.company_finder.save_companies(self.companies)
        
        if self.emails:
            self.email_generator.save_emails(self.emails)
            self.email_generator.export_emails_as_text()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <cv_file> [num_companies] [num_emails]")
        print("Example: python -m src.main src/data/my_cv.pdf 20 10")
    else:
        cv_path = sys.argv[1]
        num_companies = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        num_emails = int(sys.argv[3]) if len(sys.argv) > 3 else None
        
        engine = TalentAcquisitionEngine()
        results = engine.run_full_pipeline(cv_path, num_companies, num_emails)
        engine.save_all_outputs()
        
        print(f"\n✅ Pipeline complete!")
        print(f"   Companies: {len(results['companies'])}")
        print(f"   Emails: {len(results['emails'])}")