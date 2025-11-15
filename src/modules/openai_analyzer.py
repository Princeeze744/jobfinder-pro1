"""
OpenAI Analyzer Module
Uses GPT-4o Mini for CV analysis (MUCH CHEAPER than Claude!)
"""

import json
import os
from typing import Dict, Optional
from pathlib import Path
import PyPDF2
from src.logger import logger

class OpenAIAnalyzer:
    """
    Analyzes CV using OpenAI's GPT-4o Mini (ultra-cheap!)
    """
    
    def __init__(self):
        """Initialize OpenAI analyzer"""
        try:
            import openai
            self.client = openai
            self.api_key = os.getenv("OPENAI_API_KEY")
            
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not found in .env")
            
            self.model = "gpt-4o-mini"  # Ultra-cheap model!
            self.max_tokens = 1500
            logger.info("✅ OpenAIAnalyzer initialized with GPT-4o Mini")
        
        except ImportError:
            logger.error("❌ OpenAI library not installed. Run: pip install openai")
            raise
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                logger.info(f"📄 Reading PDF: {pdf_path} ({len(pdf_reader.pages)} pages)")
                
                for page in pdf_reader.pages:
                    text += page.extract_text()
            
            logger.info(f"✅ Extracted {len(text)} characters from PDF")
            return text
        
        except Exception as e:
            logger.error(f"❌ Error reading PDF: {str(e)}")
            raise
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from .txt or .docx files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            logger.info(f"✅ Read text file: {file_path}")
            return text
        
        except Exception as e:
            logger.error(f"❌ Error reading text file: {str(e)}")
            raise
    
    def read_cv_file(self, cv_path: str) -> str:
        """Read CV from various file formats"""
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
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def analyze_cv_with_openai(self, cv_text: str) -> Dict:
        """
        Use GPT-4o Mini to analyze CV (CHEAP!)
        
        Args:
            cv_text: Raw CV text
            
        Returns:
            Structured CV analysis
        """
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            system_prompt = """You are an expert HR analyst. Analyze the CV and extract structured information in JSON format.

Return ONLY valid JSON, no markdown:
{
    "name": "Full name",
    "email": "Email or null",
    "phone": "Phone or null",
    "skills": ["skill1", "skill2", ...],
    "experience_years": number,
    "job_titles": ["title1", "title2", ...],
    "industries": ["industry1", "industry2", ...],
    "keywords": ["keyword1", "keyword2", ...],
    "summary": "Brief professional summary",
    "education": ["degree1", "degree2"],
    "certifications": ["cert1", "cert2"]
}"""
            
            logger.info("🔄 Sending CV to GPT-4o Mini for analysis...")
            
            response = client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this CV:\n\n{cv_text}"}
                ]
            )
            
            response_text = response.choices[0].message.content
            logger.info("✅ Received response from GPT-4o Mini")
            
            # Parse JSON
            clean_response = response_text.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            elif clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            cv_analysis = json.loads(clean_response)
            logger.info(f"✅ CV analysis complete for: {cv_analysis.get('name', 'Unknown')}")
            
            return cv_analysis
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse response: {str(e)}")
            return self._generate_fallback_cv(cv_text)
        
        except Exception as e:
            logger.error(f"❌ Error analyzing CV: {str(e)}")
            raise
    
    def _generate_fallback_cv(self, cv_text: str) -> Dict:
        """Generate fallback CV analysis"""
        logger.warning("⚠️ Using fallback CV analysis")
        
        return {
            "name": "Candidate",
            "email": None,
            "phone": None,
            "skills": ["Professional"],
            "experience_years": 0,
            "job_titles": ["Professional"],
            "industries": ["Technology"],
            "keywords": ["professional"],
            "summary": "Professional with experience",
            "education": ["Degree"],
            "certifications": []
        }
    
    def analyze_cv(self, cv_path: str, output_path: Optional[str] = None) -> Dict:
        """
        Complete CV analysis workflow using GPT-4o Mini
        
        Args:
            cv_path: Path to CV file
            output_path: Output file path (optional)
            
        Returns:
            CV analysis dictionary
        """
        logger.info(f"🚀 Starting CV analysis (GPT-4o Mini) for: {cv_path}")
        
        try:
            # Step 1: Read CV
            cv_text = self.read_cv_file(cv_path)
            
            # Step 2: Analyze with GPT-4o Mini
            analysis = self.analyze_cv_with_openai(cv_text)
            
            # Step 3: Save if path provided
            if output_path:
                from pathlib import Path
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✅ CV analysis saved to: {output_file}")
            
            logger.info("✅ CV analysis completed successfully!")
            return analysis
        
        except Exception as e:
            logger.error(f"❌ CV analysis failed: {str(e)}")
            raise


if __name__ == "__main__":
    analyzer = OpenAIAnalyzer()
    print("✅ OpenAI Analyzer ready")