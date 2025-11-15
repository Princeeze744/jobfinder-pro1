"""
Hybrid Company Finder - PRODUCTION GRADE
Main orchestrator for the talent acquisition automation engine
Coordinates CV analysis, company finding, and email generation
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from src.modules.cv_analyzer import CVAnalyzer
from src.modules.company_finder import CompanyFinder
from src.modules.email_generator import EmailGenerator
from src.logger import logger
from src.config import COMPANIES_OUTPUT, EMAILS_OUTPUT

class HybridCompanyFinder:
    """
    Production-grade orchestrator for the entire talent acquisition pipeline
    Manages the complete workflow: CV → Companies → Emails
    """
    
    def __init__(self):
        """Initialize all modules"""
        self.cv_analyzer = CVAnalyzer()
        self.company_finder = CompanyFinder()
        self.email_generator = EmailGenerator()
        self.cv_analysis = None
        self.companies = []
        self.emails = []
        logger.info("✅ HybridCompanyFinder initialized (Full Pipeline Mode)")
    
    def run_full_pipeline(self, cv_path: str, 
                         num_companies: int = 20,
                         num_emails: Optional[int] = None,
                         save_outputs: bool = True) -> Dict:
        """
        Run the complete talent acquisition pipeline
        CV Analysis → Company Finding → Email Generation
        
        Args:
            cv_path: Path to CV file (PDF, TXT, DOCX)
            num_companies: Number of companies to find
            num_emails: Number of emails to generate (None = all companies)
            save_outputs: Save intermediate results
            
        Returns:
            Complete pipeline results
        """
        logger.info("=" * 60)
        logger.info("🚀 STARTING FULL TALENT ACQUISITION PIPELINE")
        logger.info("=" * 60)
        
        try:
            # Step 1: Analyze CV
            logger.info("\n📄 STEP 1: CV ANALYSIS")
            logger.info("-" * 60)
            self.cv_analysis = self.cv_analyzer.analyze_cv(cv_path)
            logger.info(f"✅ CV analyzed: {self.cv_analysis.get('name')}")
            logger.info(f"   Skills: {len(self.cv_analysis.get('skills', []))}")
            logger.info(f"   Experience: {self.cv_analysis.get('experience_years')} years")
            
            # Step 2: Find Companies
            logger.info("\n🏢 STEP 2: COMPANY DISCOVERY")
            logger.info("-" * 60)
            self.companies = self.company_finder.find_companies(
                self.cv_analysis, 
                num_queries=min(num_companies // 3, 8)  # Optimize query count
            )
            logger.info(f"✅ Found {len(self.companies)} companies")
            
            if save_outputs:
                self.company_finder.save_companies()
            
            # Step 3: Generate Emails
            logger.info("\n✉️  STEP 3: EMAIL GENERATION")
            logger.info("-" * 60)
            companies_for_emails = self.companies[:num_emails] if num_emails else self.companies
            self.emails = self.email_generator.generate_emails_batch(
                self.cv_analysis,
                companies_for_emails
            )
            logger.info(f"✅ Generated {len(self.emails)} emails")
            
            if save_outputs:
                self.email_generator.save_emails()
                self.email_generator.export_emails_as_text()
            
            # Pipeline Summary
            logger.info("\n" + "=" * 60)
            logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"📊 FINAL RESULTS:")
            logger.info(f"   Candidate: {self.cv_analysis.get('name')}")
            logger.info(f"   Companies Found: {len(self.companies)}")
            logger.info(f"   Emails Generated: {len(self.emails)}")
            logger.info(f"   Premium Emails: {sum(1 for e in self.emails if e.get('quality_score') == 'premium')}")
            logger.info("=" * 60)
            
            return {
                'cv_analysis': self.cv_analysis,
                'companies': self.companies,
                'emails': self.emails,
                'stats': {
                    'total_companies': len(self.companies),
                    'total_emails': len(self.emails),
                    'premium_emails': sum(1 for e in self.emails if e.get('quality_score') == 'premium'),
                    'candidate_name': self.cv_analysis.get('name')
                }
            }
        
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {str(e)}")
            raise
    
    def find_companies_ai_mode(self, cv_analysis: Dict, num_queries: int = 5) -> List[Dict]:
        """
        AI-powered company finding mode (fast, comprehensive)
        
        Args:
            cv_analysis: CV analysis from CVAnalyzer
            num_queries: Number of search queries to perform
            
        Returns:
            List of AI-discovered companies
        """
        logger.info(f"🤖 AI Mode: Finding companies with {num_queries} queries...")
        
        self.cv_analysis = cv_analysis
        self.companies = self.company_finder.find_companies(cv_analysis, num_queries=num_queries)
        
        # Add discovery metadata
        for company in self.companies:
            company['discovery_mode'] = 'AI-Powered Research'
            company['pipeline_stage'] = 'discovered'
        
        logger.info(f"✅ AI Mode: Discovered {len(self.companies)} companies")
        return self.companies
    
    def generate_emails_for_companies(self, cv_analysis: Optional[Dict] = None,
                                     companies: Optional[List[Dict]] = None,
                                     max_emails: Optional[int] = None) -> List[Dict]:
        """
        Generate emails for discovered companies
        
        Args:
            cv_analysis: CV analysis (uses self.cv_analysis if None)
            companies: Companies list (uses self.companies if None)
            max_emails: Maximum emails to generate
            
        Returns:
            List of generated emails
        """
        if cv_analysis is None:
            cv_analysis = self.cv_analysis
        
        if companies is None:
            companies = self.companies
        
        if not cv_analysis:
            raise ValueError("No CV analysis available. Run CV analysis first.")
        
        if not companies:
            raise ValueError("No companies available. Run company finding first.")
        
        logger.info(f"✉️  Generating emails for {len(companies)} companies...")
        
        self.emails = self.email_generator.generate_emails_batch(
            cv_analysis,
            companies,
            max_emails=max_emails
        )
        
        # Update company records with email status
        for i, company in enumerate(companies[:len(self.emails)]):
            company['email_generated'] = True
            company['pipeline_stage'] = 'ready_to_send'
        
        return self.emails
    
    def load_existing_data(self, cv_analysis_path: Optional[str] = None,
                          companies_path: Optional[str] = None) -> Dict:
        """
        Load existing CV analysis and companies data
        Useful for resuming pipeline or generating more emails
        
        Args:
            cv_analysis_path: Path to CV analysis JSON
            companies_path: Path to companies JSON
            
        Returns:
            Loaded data dictionary
        """
        loaded = {}
        
        if cv_analysis_path:
            try:
                with open(cv_analysis_path, 'r', encoding='utf-8') as f:
                    self.cv_analysis = json.load(f)
                loaded['cv_analysis'] = self.cv_analysis
                logger.info(f"✅ Loaded CV analysis: {self.cv_analysis.get('name')}")
            except Exception as e:
                logger.error(f"❌ Failed to load CV analysis: {str(e)}")
        
        if companies_path:
            try:
                with open(companies_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle both formats
                    if isinstance(data, dict) and 'companies' in data:
                        self.companies = data['companies']
                    elif isinstance(data, list):
                        self.companies = data
                    else:
                        self.companies = []
                loaded['companies'] = self.companies
                logger.info(f"✅ Loaded {len(self.companies)} companies")
            except Exception as e:
                logger.error(f"❌ Failed to load companies: {str(e)}")
        
        return loaded
    
    def get_pipeline_status(self) -> Dict:
        """
        Get current pipeline status
        
        Returns:
            Status dictionary
        """
        return {
            'cv_analyzed': self.cv_analysis is not None,
            'candidate_name': self.cv_analysis.get('name') if self.cv_analysis else None,
            'companies_found': len(self.companies),
            'emails_generated': len(self.emails),
            'ready_to_send': sum(1 for c in self.companies if c.get('email_generated', False)),
            'premium_quality': sum(1 for e in self.emails if e.get('quality_score') == 'premium')
        }
    
    def save_all_outputs(self, companies_path: Optional[str] = None,
                        emails_path: Optional[str] = None):
        """
        Save all pipeline outputs
        
        Args:
            companies_path: Output path for companies
            emails_path: Output path for emails
        """
        if self.companies:
            self.company_finder.companies = self.companies
            self.company_finder.save_companies(output_path=companies_path)
        
        if self.emails:
            self.email_generator.emails = self.emails
            self.email_generator.save_emails(output_path=emails_path)
            self.email_generator.export_emails_as_text()
    
    def get_results_summary(self) -> Dict:
        """
        Get comprehensive results summary
        
        Returns:
            Results summary dictionary
        """
        if not self.cv_analysis:
            return {'error': 'No pipeline data available'}
        
        return {
            'candidate': {
                'name': self.cv_analysis.get('name'),
                'experience': self.cv_analysis.get('experience_years'),
                'top_skills': self.cv_analysis.get('skills', [])[:5],
                'target_industries': self.cv_analysis.get('industries', [])
            },
            'companies': {
                'total': len(self.companies),
                'with_verified_contacts': sum(1 for c in self.companies if c.get('verified')),
                'top_companies': [c.get('company_name') for c in self.companies[:5]]
            },
            'emails': {
                'total': len(self.emails),
                'premium_quality': sum(1 for e in self.emails if e.get('quality_score') == 'premium'),
                'ready_to_send': len(self.emails)
            },
            'next_steps': self._get_next_steps()
        }
    
    def _get_next_steps(self) -> List[str]:
        """Generate next steps recommendations"""
        steps = []
        
        if not self.cv_analysis:
            steps.append("1. Analyze your CV using run_full_pipeline()")
        elif not self.companies:
            steps.append("1. Find companies using find_companies_ai_mode()")
        elif not self.emails:
            steps.append("1. Generate emails using generate_emails_for_companies()")
        else:
            steps.append("1. Review generated emails in src/data/emails_text/")
            steps.append("2. Customize emails if needed")
            steps.append("3. Start sending emails to companies")
            steps.append("4. Track responses and follow up")
        
        return steps
    
    def get_companies(self) -> List[Dict]:
        """Get discovered companies"""
        return self.companies
    
    def get_emails(self) -> List[Dict]:
        """Get generated emails"""
        return self.emails


# Production CLI functions
def run_pipeline_from_cv(cv_path: str, num_companies: int = 20, num_emails: Optional[int] = None):
    """
    Production function: Run complete pipeline from CV file
    
    Args:
        cv_path: Path to CV file
        num_companies: Number of companies to find
        num_emails: Number of emails to generate (None = all)
    """
    print("=" * 60)
    print("🎯 TALENT ACQUISITION AUTOMATION ENGINE")
    print("=" * 60)
    
    finder = HybridCompanyFinder()
    results = finder.run_full_pipeline(
        cv_path=cv_path,
        num_companies=num_companies,
        num_emails=num_emails
    )
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 PIPELINE SUMMARY")
    print("=" * 60)
    summary = finder.get_results_summary()
    print(f"\n👤 CANDIDATE:")
    print(f"   Name: {summary['candidate']['name']}")
    print(f"   Experience: {summary['candidate']['experience']} years")
    print(f"   Skills: {', '.join(summary['candidate']['top_skills'][:3])}")
    
    print(f"\n🏢 COMPANIES:")
    print(f"   Total Found: {summary['companies']['total']}")
    print(f"   Verified Contacts: {summary['companies']['with_verified_contacts']}")
    
    print(f"\n✉️  EMAILS:")
    print(f"   Total Generated: {summary['emails']['total']}")
    print(f"   Premium Quality: {summary['emails']['premium_quality']}")
    
    print(f"\n📋 NEXT STEPS:")
    for step in summary['next_steps']:
        print(f"   {step}")
    
    print("\n" + "=" * 60)
    print("✅ Pipeline complete! Check output files:")
    print("   - src/data/cv_analysis.json")
    print("   - src/data/companies.json")
    print("   - src/data/emails.json")
    print("   - src/data/emails_text/ (ready to send!)")
    print("=" * 60)
    
    return results


def resume_pipeline_from_existing(cv_analysis_path: str, companies_path: str, 
                                  max_emails: Optional[int] = None):
    """
    Resume pipeline from existing CV analysis and companies
    Useful for generating more emails or re-generating
    
    Args:
        cv_analysis_path: Path to CV analysis JSON
        companies_path: Path to companies JSON
        max_emails: Maximum emails to generate
    """
    print("=" * 60)
    print("🔄 RESUMING PIPELINE FROM EXISTING DATA")
    print("=" * 60)
    
    finder = HybridCompanyFinder()
    finder.load_existing_data(cv_analysis_path, companies_path)
    
    # Generate emails
    emails = finder.generate_emails_for_companies(max_emails=max_emails)
    
    # Save outputs
    finder.save_all_outputs()
    
    print(f"\n✅ Generated {len(emails)} new emails!")
    print("=" * 60)
    
    return emails


def quick_test(cv_path: str):
    """
    Quick test with 5 companies and 5 emails
    
    Args:
        cv_path: Path to CV file
    """
    print("=" * 60)
    print("🧪 QUICK TEST MODE (5 companies, 5 emails)")
    print("=" * 60)
    
    return run_pipeline_from_cv(cv_path, num_companies=5, num_emails=5)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("=" * 60)
        print("🎯 TALENT ACQUISITION AUTOMATION ENGINE")
        print("=" * 60)
        print("\nUsage:")
        print("  Full Pipeline:")
        print("    python -m src.modules.hybrid_company_finder <cv_file> [num_companies] [num_emails]")
        print("\n  Resume from Existing:")
        print("    python -m src.modules.hybrid_company_finder --resume <cv_analysis.json> <companies.json> [max_emails]")
        print("\n  Quick Test:")
        print("    python -m src.modules.hybrid_company_finder --test <cv_file>")
        print("\nExamples:")
        print("  python -m src.modules.hybrid_company_finder src/data/my_cv.pdf")
        print("  python -m src.modules.hybrid_company_finder src/data/my_cv.pdf 30 20")
        print("  python -m src.modules.hybrid_company_finder --resume src/data/cv_analysis.json src/data/companies.json")
        print("  python -m src.modules.hybrid_company_finder --test src/data/my_cv.pdf")
        print("=" * 60)
    
    elif sys.argv[1] == "--resume" and len(sys.argv) >= 4:
        max_emails = int(sys.argv[4]) if len(sys.argv) > 4 else None
        resume_pipeline_from_existing(sys.argv[2], sys.argv[3], max_emails)
    
    elif sys.argv[1] == "--test" and len(sys.argv) >= 3:
        quick_test(sys.argv[2])
    
    else:
        cv_path = sys.argv[1]
        num_companies = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        num_emails = int(sys.argv[3]) if len(sys.argv) > 3 else None
        run_pipeline_from_cv(cv_path, num_companies, num_emails)