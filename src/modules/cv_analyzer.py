"""
CV Analyzer Module - PRODUCTION GRADE
Analyzes CV using OpenAI GPT-4o Mini for cost-effective, high-quality analysis
Designed for real job seekers - no compromises on quality
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2
from openai import OpenAI
from src.logger import logger
from src.config import MAX_TOKENS, TEMPERATURE, CV_ANALYSIS_OUTPUT

class CVAnalyzer:
    """
    Production-grade CV analyzer using OpenAI GPT-4o Mini
    Extracts comprehensive candidate information for real job applications
    """
    
    def __init__(self):
        """Initialize the CV Analyzer with OpenAI client"""
        self.client = OpenAI()  # Reads OPENAI_API_KEY from .env automatically
        self.model = "gpt-4o-mini"  # Cost-effective but high quality
        self.max_tokens = MAX_TOKENS
        self.temperature = TEMPERATURE
        logger.info("✅ CVAnalyzer initialized with OpenAI GPT-4o Mini (Production Mode)")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text from PDF
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                logger.info(f"📄 Reading PDF: {pdf_path} ({len(pdf_reader.pages)} pages)")
                
                for page in pdf_reader.pages:
                    text += page.extract_text()
            
            logger.info(f"✅ Successfully extracted {len(text)} characters from PDF")
            return text
        
        except Exception as e:
            logger.error(f"❌ Error reading PDF: {str(e)}")
            raise
    
    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from .txt or .docx files
        
        Args:
            file_path: Path to text file
            
        Returns:
            File content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            logger.info(f"✅ Successfully read text file: {file_path}")
            return text
        
        except Exception as e:
            logger.error(f"❌ Error reading text file: {str(e)}")
            raise
    
    def read_cv_file(self, cv_path: str) -> str:
        """
        Read CV from various file formats (PDF, TXT, DOCX)
        
        Args:
            cv_path: Path to CV file
            
        Returns:
            CV text content
        """
        file_path = Path(cv_path)
        
        if not file_path.exists():
            logger.error(f"❌ File not found: {cv_path}")
            raise FileNotFoundError(f"CV file not found: {cv_path}")
        
        file_extension = file_path.suffix.lower()
        
        logger.info(f"📂 Reading CV file: {file_path.name}")
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(cv_path)
        elif file_extension in ['.txt', '.docx']:
            return self.extract_text_from_file(cv_path)
        else:
            logger.error(f"❌ Unsupported file format: {file_extension}")
            raise ValueError(f"Unsupported file format: {file_extension}. Use PDF, TXT, or DOCX")
    
    def analyze_cv_with_openai(self, cv_text: str) -> Dict:
        """
        Use OpenAI GPT-4o Mini to analyze CV and extract structured information
        Production-grade analysis with comprehensive extraction
        
        Args:
            cv_text: Raw CV text
            
        Returns:
            Structured CV analysis as dictionary
        """
        
        system_prompt = """You are an elite HR analyst and senior recruitment specialist with 15+ years of experience. 
Your task is to perform a comprehensive, professional CV analysis for a REAL job seeker.

CRITICAL REQUIREMENTS:
1. Extract EVERY skill mentioned (technical, soft, domain-specific)
2. Identify ALL relevant industries and job titles
3. Calculate experience accurately from dates
4. Generate comprehensive keywords for job matching
5. Create a compelling professional summary
6. Be thorough - this directly impacts someone's career

Return ONLY valid JSON in this EXACT format:
{
    "name": "Full name of candidate",
    "email": "Email address or null",
    "phone": "Phone number or null",
    "skills": ["skill1", "skill2", "skill3", ...],
    "experience_years": number,
    "job_titles": ["current/recent title", "previous title", ...],
    "industries": ["industry1", "industry2", ...],
    "keywords": ["keyword1", "keyword2", ...],
    "summary": "Compelling 3-4 sentence professional summary highlighting strengths and value proposition",
    "education": ["Degree/Institution 1", "Degree/Institution 2", ...],
    "certifications": ["certification1", "certification2", ...]
}

EXTRACTION GUIDELINES:
- Skills: Include programming languages, frameworks, tools, methodologies, soft skills
- Experience: Count total years from earliest to latest job (use 2025 as current year)
- Job Titles: List all positions held, most recent first
- Industries: Technology, Finance, Healthcare, Consulting, etc.
- Keywords: Technical terms, job-related keywords for ATS matching
- Summary: Highlight unique value, key achievements, career trajectory
- Education: Degree + University/Institution
- Certifications: Professional certifications, licenses, courses

If information is not found, use null for strings or empty arrays for lists.
NEVER make up information - only extract what's clearly stated in the CV."""
        
        user_prompt = f"""Perform a comprehensive analysis of this CV. This is for a REAL job seeker, so be thorough and professional.

CV CONTENT:
{cv_text}

Remember: Extract ALL skills, experience, and qualifications. Create a strong professional summary that will help this person land interviews."""
        
        try:
            logger.info("🔄 Sending CV to OpenAI GPT-4o Mini for analysis...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}  # Ensures valid JSON response
            )
            
            response_text = response.choices[0].message.content
            logger.info("✅ Received response from OpenAI")
            
            # Parse JSON response
            cv_analysis = json.loads(response_text)
            
            # Quality validation
            skills_count = len(cv_analysis.get('skills', []))
            keywords_count = len(cv_analysis.get('keywords', []))
            
            logger.info(f"✅ CV Analysis Complete:")
            logger.info(f"   Candidate: {cv_analysis.get('name', 'Unknown')}")
            logger.info(f"   Skills Extracted: {skills_count}")
            logger.info(f"   Keywords Generated: {keywords_count}")
            logger.info(f"   Experience: {cv_analysis.get('experience_years', 0)} years")
            
            # Quality check
            if skills_count < 3:
                logger.warning("⚠️ Low skill count - CV may need manual review")
            
            return cv_analysis
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse OpenAI response as JSON: {str(e)}")
            logger.debug(f"Response was: {response_text}")
            raise ValueError("Failed to parse CV analysis - please check CV format")
        
        except Exception as e:
            logger.error(f"❌ Error calling OpenAI API: {str(e)}")
            raise
    
    def validate_analysis(self, analysis: Dict) -> bool:
        """
        Validate that all required fields are present and meet quality standards
        
        Args:
            analysis: CV analysis dictionary
            
        Returns:
            True if valid, raises exception if critical issues found
        """
        required_fields = ['name', 'skills', 'experience_years', 'job_titles', 'industries', 'keywords']
        
        # Check required fields
        for field in required_fields:
            if field not in analysis:
                raise ValueError(f"Critical field missing in CV analysis: {field}")
        
        # Validate name
        if not analysis['name'] or analysis['name'] == "Unknown":
            logger.warning("⚠️ Name not clearly identified in CV")
        
        # Validate skills (critical for job matching)
        if len(analysis.get('skills', [])) < 3:
            logger.warning("⚠️ Low skill count detected - may affect job matching")
        
        # Validate experience
        if analysis.get('experience_years', 0) < 0:
            logger.warning("⚠️ Invalid experience years detected")
            analysis['experience_years'] = 0
        
        logger.info(f"✅ CV analysis validation passed for: {analysis['name']}")
        return True
    
    def save_analysis(self, analysis: Dict, output_path: Optional[str] = None) -> str:
        """
        Save CV analysis to JSON file
        
        Args:
            analysis: CV analysis dictionary
            output_path: Output file path (default: config)
            
        Returns:
            Path to saved file
        """
        if output_path is None:
            output_path = CV_ANALYSIS_OUTPUT
        
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ CV analysis saved to: {output_file}")
            return str(output_file)
        
        except Exception as e:
            logger.error(f"❌ Error saving analysis: {str(e)}")
            raise
    
    def analyze_cv(self, cv_path: str, output_path: Optional[str] = None) -> Dict:
        """
        Complete CV analysis workflow - PRODUCTION GRADE
        
        Args:
            cv_path: Path to CV file
            output_path: Output file path (optional)
            
        Returns:
            Complete CV analysis
        """
        logger.info(f"🚀 Starting PRODUCTION CV analysis for: {cv_path}")
        
        try:
            # Step 1: Read CV file
            cv_text = self.read_cv_file(cv_path)
            
            if len(cv_text) < 100:
                logger.warning("⚠️ CV appears very short - may not have enough information")
            
            # Step 2: Analyze with OpenAI
            analysis = self.analyze_cv_with_openai(cv_text)
            
            # Step 3: Validate analysis
            self.validate_analysis(analysis)
            
            # Step 4: Save results
            self.save_analysis(analysis, output_path)
            
            logger.info("✅ CV analysis completed successfully!")
            logger.info(f"   Ready for job matching and email generation")
            
            return analysis
        
        except Exception as e:
            logger.error(f"❌ CV analysis failed: {str(e)}")
            raise


# Production testing function
def test_cv_analysis(cv_file_path: str):
    """Production test function"""
    print("=" * 60)
    print("🎯 PRODUCTION CV ANALYSIS TEST")
    print("=" * 60)
    
    analyzer = CVAnalyzer()
    result = analyzer.analyze_cv(cv_file_path)
    
    print("\n📊 ANALYSIS RESULTS:")
    print(f"   Name: {result.get('name')}")
    print(f"   Experience: {result.get('experience_years')} years")
    print(f"   Skills: {len(result.get('skills', []))} identified")
    print(f"   Industries: {', '.join(result.get('industries', [])[:3])}")
    print("\n✅ Analysis complete and saved!")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    # Production testing entry point
    import sys
    if len(sys.argv) > 1:
        test_cv_analysis(sys.argv[1])
    else:
        print("Usage: python -m src.modules.cv_analyzer <path_to_cv_file>")
        print("Example: python -m src.modules.cv_analyzer src/data/john_doe_cv.pdf")