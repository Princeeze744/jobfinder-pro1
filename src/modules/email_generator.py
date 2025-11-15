"""
Email Generator Module - PRODUCTION GRADE
Generates personalized cold emails using Claude Sonnet 4 for premium quality
Designed for REAL job seekers - creates emails that land interviews
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from anthropic import Anthropic
from src.logger import logger
from src.config import CLAUDE_MODEL, MAX_TOKENS, TEMPERATURE, EMAILS_OUTPUT

class EmailGenerator:
    """
    Production-grade email generator using Claude Sonnet 4
    Creates personalized, compelling cold emails that get responses
    """
    
    def __init__(self):
        """Initialize the Email Generator with Claude"""
        self.client = Anthropic()  # Reads ANTHROPIC_API_KEY from .env
        self.model = CLAUDE_MODEL  # claude-sonnet-4-20250514
        self.max_tokens = MAX_TOKENS
        self.temperature = TEMPERATURE
        self.emails = []
        logger.info("✅ EmailGenerator initialized with Claude Sonnet 4 (Premium Mode)")
    
    def generate_email_for_company(self, candidate: Dict, company: Dict) -> Dict:
        """
        Generate a highly personalized cold email using Claude
        Production-grade quality for real job applications
        
        Args:
            candidate: Candidate CV analysis data
            company: Company information
            
        Returns:
            Email dictionary with subject, body, and metadata
        """
        
        system_prompt = """You are a senior career advisor and professional cold email expert with 15+ years of experience helping candidates land interviews at top companies.

Your task is to write a HIGHLY PERSONALIZED cold email that will help a real job seeker get an interview.

CRITICAL REQUIREMENTS FOR PRODUCTION EMAILS:
1. Be authentic and genuine - avoid generic corporate speak
2. Show you've researched the company (reference their industry, mission, or recent news)
3. Highlight 2-3 specific skills that match the company's needs
4. Include a clear value proposition - what the candidate brings
5. Keep it concise (150-200 words max) - hiring managers are busy
6. Use a conversational but professional tone
7. End with a clear, low-pressure call-to-action
8. Make it feel human, not AI-generated

EMAIL BEST PRACTICES:
- Start with a hook that shows genuine interest in the company
- Connect candidate's experience to company's likely needs
- Use specific examples or achievements when possible
- Avoid: "I hope this email finds you well", "I am writing to express interest"
- Use: Natural, confident language that shows enthusiasm
- Subject line: Clear, specific, intriguing (not generic)

TONE GUIDELINES:
- Confident but humble
- Enthusiastic but not desperate
- Professional but personable
- Direct but not pushy

Return ONLY valid JSON in this EXACT format:
{
    "subject": "Compelling subject line (under 60 chars)",
    "body": "Full email body (150-200 words)",
    "key_skills_mentioned": ["skill1", "skill2", "skill3"],
    "personalization_elements": ["element1", "element2"],
    "tone": "professional/conversational/enthusiastic"
}

NEVER use templates or generic phrases. Each email must feel custom-written for that specific company."""
        
        # Build rich candidate context
        candidate_name = candidate.get('name', 'Candidate')
        experience = candidate.get('experience_years', 0)
        top_skills = candidate.get('skills', [])[:7]  # Top 7 skills
        job_titles = candidate.get('job_titles', [])
        industries = candidate.get('industries', [])
        summary = candidate.get('summary', '')
        keywords = candidate.get('keywords', [])[:10]
        
        candidate_summary = f"""
CANDIDATE PROFILE:
Name: {candidate_name}
Experience: {experience} years
Current/Recent Role: {job_titles[0] if job_titles else 'Professional'}
Previous Roles: {', '.join(job_titles[1:3]) if len(job_titles) > 1 else 'N/A'}

Core Technical Skills: {', '.join(top_skills[:5])}
Additional Skills: {', '.join(top_skills[5:7]) if len(top_skills) > 5 else 'N/A'}

Industry Background: {', '.join(industries)}
Key Strengths: {', '.join(keywords[:5])}

Professional Summary: {summary}

Candidate Email: {candidate.get('email', 'candidate@email.com')}
"""
        
        # Build rich company context
        company_name = company.get('company_name', 'Company')
        company_industry = company.get('industry', 'Technology')
        company_website = company.get('website', '')
        hiring_status = company.get('hiring_status', 'Actively hiring')
        why_match = company.get('why_match', 'Skills alignment')
        
        company_summary = f"""
TARGET COMPANY:
Company: {company_name}
Industry: {company_industry}
Website: {company_website}
Current Status: {hiring_status}
Why Good Match: {why_match}

Contact Email: {company.get('email', 'careers@company.com')}
"""
        
        user_prompt = f"""Write a highly personalized cold email for this REAL job application.

{candidate_summary}

{company_summary}

SPECIFIC INSTRUCTIONS:
1. Research angle: Reference something specific about {company_name}'s work in {company_industry}
2. Skills match: Highlight 2-3 of these skills that {company_name} likely needs: {', '.join(top_skills[:5])}
3. Value proposition: Explain how {candidate_name}'s {experience} years of experience can help the company
4. Call-to-action: Suggest a brief conversation/call (low pressure)
5. Tone: Professional but warm - like reaching out to a potential colleague

This is for a REAL job seeker who needs REAL interviews. Make this email compelling enough to get a response.

Return as JSON object with subject, body, key_skills_mentioned, personalization_elements, and tone."""
        
        try:
            logger.info(f"✉️  Generating premium email for: {company_name}")
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,  # Allow for detailed, quality emails
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            # Parse JSON response (handle potential markdown wrappers)
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            email_data = json.loads(response_text)
            
            # Add comprehensive metadata for tracking and analytics
            email_data['candidate_name'] = candidate_name
            email_data['candidate_email'] = candidate.get('email', 'candidate@email.com')
            email_data['candidate_phone'] = candidate.get('phone', None)
            email_data['company_name'] = company_name
            email_data['company_email'] = company.get('email', 'careers@company.com')
            email_data['company_website'] = company_website
            email_data['company_industry'] = company_industry
            email_data['match_reason'] = why_match
            email_data['generated_by'] = 'Claude Sonnet 4'
            email_data['quality_score'] = 'premium'
            
            # Quality validation
            word_count = len(email_data.get('body', '').split())
            if word_count < 80:
                logger.warning(f"⚠️  Email seems short ({word_count} words) - may need review")
            elif word_count > 300:
                logger.warning(f"⚠️  Email seems long ({word_count} words) - may need trimming")
            else:
                logger.info(f"✅ Quality email generated ({word_count} words)")
            
            logger.info(f"✅ Premium email generated for: {company_name}")
            return email_data
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Claude response as JSON: {str(e)}")
            logger.debug(f"Response was: {response_text[:200]}")
            return self._generate_fallback_email(candidate, company)
        
        except Exception as e:
            logger.error(f"❌ Error generating email with Claude: {str(e)}")
            return self._generate_fallback_email(candidate, company)
    
    def _generate_fallback_email(self, candidate: Dict, company: Dict) -> Dict:
        """
        Generate a high-quality fallback email if Claude fails
        Still maintains professionalism for production use
        
        Args:
            candidate: Candidate data
            company: Company data
            
        Returns:
            Professional email dictionary
        """
        name = candidate.get('name', 'Candidate')
        company_name = company.get('company_name', 'Company')
        skills = candidate.get('skills', [])[:3]
        experience = candidate.get('experience_years', 0)
        job_title = candidate.get('job_titles', ['Professional'])[0]
        industry = company.get('industry', 'your industry')
        
        skills_text = ', '.join(skills) if skills else 'software development'
        
        logger.warning(f"⚠️  Using fallback email for {company_name} (Claude API issue)")
        
        body = f"""Hi {company_name} team,

I came across {company_name} while researching innovative companies in {industry}, and I'm impressed by your work.

I'm {name}, a {job_title} with {experience} years of experience in {skills_text}. I've been following companies that are pushing boundaries in {industry}, and {company_name} stood out.

I'd love to explore how my background could contribute to your team. Would you be open to a brief conversation?

Best regards,
{name}
{candidate.get('email', 'email@example.com')}"""
        
        return {
            "subject": f"{job_title} interested in {company_name}",
            "body": body,
            "key_skills_mentioned": skills[:3],
            "personalization_elements": [f"Company name: {company_name}", f"Industry: {industry}"],
            "tone": "professional",
            "candidate_name": name,
            "candidate_email": candidate.get('email', 'candidate@email.com'),
            "candidate_phone": candidate.get('phone', None),
            "company_name": company_name,
            "company_email": company.get('email', 'careers@company.com'),
            "company_website": company.get('website', ''),
            "company_industry": industry,
            "match_reason": company.get('why_match', 'Skills alignment'),
            "generated_by": 'Fallback Template',
            "quality_score": 'standard'
        }
    
    def generate_emails_batch(self, candidate: Dict, companies: List[Dict], 
                             max_emails: Optional[int] = None) -> List[Dict]:
        """
        Generate premium emails for multiple companies
        Production batch processing with quality control
        
        Args:
            candidate: Candidate CV analysis
            companies: List of company data
            max_emails: Maximum number of emails to generate (None = all)
            
        Returns:
            List of generated emails
        """
        
        # Determine batch size
        companies_to_process = companies[:max_emails] if max_emails else companies
        total = len(companies_to_process)
        
        logger.info("=" * 60)
        logger.info(f"📧 Starting PREMIUM email generation batch")
        logger.info(f"   Candidate: {candidate.get('name', 'Unknown')}")
        logger.info(f"   Companies: {total}")
        logger.info(f"   Model: {self.model}")
        logger.info("=" * 60)
        
        emails = []
        successful = 0
        fallback = 0
        
        for i, company in enumerate(companies_to_process, 1):
            company_name = company.get('company_name', 'Company')
            
            try:
                logger.info(f"[{i}/{total}] Processing: {company_name}")
                
                email = self.generate_email_for_company(candidate, company)
                emails.append(email)
                
                if email.get('quality_score') == 'premium':
                    successful += 1
                else:
                    fallback += 1
                
                # Brief pause to avoid rate limits (if generating many emails)
                if i % 5 == 0:
                    import time
                    time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ Critical error for {company_name}: {str(e)}")
                # Generate fallback email as last resort
                email = self._generate_fallback_email(candidate, company)
                emails.append(email)
                fallback += 1
        
        self.emails = emails
        
        logger.info("=" * 60)
        logger.info(f"✅ Email generation COMPLETED!")
        logger.info(f"   Total Generated: {len(emails)}")
        logger.info(f"   Premium Quality: {successful}")
        logger.info(f"   Fallback Used: {fallback}")
        logger.info(f"   Success Rate: {(successful/total)*100:.1f}%")
        logger.info("=" * 60)
        
        return emails
    
    def validate_emails(self, emails: Optional[List[Dict]] = None) -> Dict:
        """
        Validate generated emails for production quality
        
        Args:
            emails: List of emails to validate (uses self.emails if None)
            
        Returns:
            Validation report
        """
        if emails is None:
            emails = self.emails
        
        report = {
            'total_emails': len(emails),
            'premium_quality': 0,
            'standard_quality': 0,
            'missing_subject': 0,
            'missing_body': 0,
            'short_emails': 0,
            'long_emails': 0,
            'valid_emails': 0
        }
        
        for email in emails:
            if email.get('quality_score') == 'premium':
                report['premium_quality'] += 1
            else:
                report['standard_quality'] += 1
            
            if not email.get('subject'):
                report['missing_subject'] += 1
            
            body = email.get('body', '')
            if not body:
                report['missing_body'] += 1
            else:
                word_count = len(body.split())
                if word_count < 80:
                    report['short_emails'] += 1
                elif word_count > 300:
                    report['long_emails'] += 1
                else:
                    report['valid_emails'] += 1
        
        logger.info(f"📊 Email Validation Report:")
        logger.info(f"   Premium Quality: {report['premium_quality']}/{report['total_emails']}")
        logger.info(f"   Valid Length: {report['valid_emails']}/{report['total_emails']}")
        
        return report
    
    def save_emails(self, emails: Optional[List[Dict]] = None, 
                   output_path: Optional[str] = None) -> str:
        """
        Save generated emails to JSON file with metadata
        
        Args:
            emails: List of emails (uses self.emails if None)
            output_path: Output file path
            
        Returns:
            Path to saved file
        """
        if emails is None:
            emails = self.emails
        
        if output_path is None:
            output_path = EMAILS_OUTPUT
        
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Add generation metadata
            output_data = {
                'metadata': {
                    'total_emails': len(emails),
                    'generated_by': self.model,
                    'candidate': emails[0].get('candidate_name') if emails else 'Unknown',
                    'generation_date': None  # Add timestamp if needed
                },
                'emails': emails
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ {len(emails)} emails saved to: {output_file}")
            return str(output_file)
        
        except Exception as e:
            logger.error(f"❌ Error saving emails: {str(e)}")
            raise
    
    def export_emails_as_text(self, output_dir: str = "src/data/emails_text") -> List[str]:
        """
        Export emails as individual text files ready to copy-paste
        
        Args:
            output_dir: Directory to save email text files
            
        Returns:
            List of file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        file_paths = []
        
        logger.info(f"📄 Exporting {len(self.emails)} emails as text files...")
        
        for i, email in enumerate(self.emails, 1):
            company_name = email.get('company_name', 'company')
            safe_name = company_name.replace(' ', '_').replace('/', '_')
            filename = f"{i:02d}_{safe_name}.txt"
            filepath = output_path / filename
            
            # Format for easy copy-paste
            content = f"""====================================
EMAIL #{i} - {company_name}
====================================

TO: {email.get('company_email', 'unknown@company.com')}
FROM: {email.get('candidate_email', 'candidate@email.com')}
SUBJECT: {email.get('subject', 'Application')}

====================================

{email.get('body', '')}

====================================
METADATA:
Company: {company_name}
Industry: {email.get('company_industry', 'N/A')}
Website: {email.get('company_website', 'N/A')}
Quality: {email.get('quality_score', 'N/A')}
Skills Mentioned: {', '.join(email.get('key_skills_mentioned', []))}
====================================
"""
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                file_paths.append(str(filepath))
            except Exception as e:
                logger.error(f"❌ Error exporting email {i}: {str(e)}")
        
        logger.info(f"✅ Exported {len(file_paths)} emails to: {output_dir}")
        return file_paths
    
    def get_email_preview(self, email_index: int = 0) -> Dict:
        """
        Get preview of a generated email
        
        Args:
            email_index: Index of email to preview
            
        Returns:
            Email dictionary
        """
        if email_index < len(self.emails):
            return self.emails[email_index]
        else:
            logger.warning(f"⚠️  Email index {email_index} out of range")
            return {}
    
    def print_email_preview(self, email_index: int = 0):
        """
        Print a formatted preview of an email
        
        Args:
            email_index: Index of email to preview
        """
        if email_index >= len(self.emails):
            logger.error(f"❌ Email index {email_index} out of range")
            return
        
        email = self.emails[email_index]
        
        print("\n" + "=" * 60)
        print(f"EMAIL PREVIEW #{email_index + 1}")
        print("=" * 60)
        print(f"TO: {email.get('company_email')}")
        print(f"SUBJECT: {email.get('subject')}")
        print(f"COMPANY: {email.get('company_name')}")
        print(f"QUALITY: {email.get('quality_score', 'N/A').upper()}")
        print("=" * 60)
        print(email.get('body', ''))
        print("=" * 60)
        print(f"Skills: {', '.join(email.get('key_skills_mentioned', []))}")
        print("=" * 60 + "\n")
    
    def get_emails(self) -> List[Dict]:
        """
        Get all generated emails
        
        Returns:
            List of emails
        """
        return self.emails


# Production testing function
def test_email_generator(cv_analysis_path: str, companies_path: str, max_emails: int = 5):
    """
    Production test function - generates real emails
    
    Args:
        cv_analysis_path: Path to CV analysis JSON
        companies_path: Path to companies JSON
        max_emails: Number of emails to generate for testing
    """
    print("=" * 60)
    print("🎯 PRODUCTION EMAIL GENERATOR TEST")
    print("=" * 60)
    
    # Load data
    with open(cv_analysis_path, 'r') as f:
        cv_analysis = json.load(f)
    
    with open(companies_path, 'r') as f:
        companies_data = json.load(f)
    
    # Handle both formats (with/without metadata wrapper)
    if isinstance(companies_data, dict) and 'companies' in companies_data:
        companies = companies_data['companies']
    else:
        companies = companies_data
    
    print(f"\nCandidate: {cv_analysis.get('name')}")
    print(f"Companies available: {len(companies)}")
    print(f"Generating: {max_emails} emails")
    
    # Generate emails
    generator = EmailGenerator()
    emails = generator.generate_emails_batch(cv_analysis, companies, max_emails=max_emails)
    
    # Validate
    validation = generator.validate_emails()
    
    # Save results
    generator.save_emails()
    generator.export_emails_as_text()
    
    # Preview first email
    if emails:
        print("\n" + "=" * 60)
        print("📧 SAMPLE EMAIL PREVIEW:")
        print("=" * 60)
        generator.print_email_preview(0)
    
    print("\n✅ Email generation test complete!")
    print(f"   Check: src/data/emails.json")
    print(f"   Check: src/data/emails_text/")
    print("=" * 60)
    
    return emails


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        max_emails = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        test_email_generator(sys.argv[1], sys.argv[2], max_emails)
    else:
        print("Usage: python -m src.modules.email_generator <cv_analysis.json> <companies.json> [max_emails]")
        print("Example: python -m src.modules.email_generator src/data/cv_analysis.json src/data/companies.json 10")