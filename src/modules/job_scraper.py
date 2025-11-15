"""
Multi-Platform Job Scraper Module - IMPROVED VERSION
Scrapes real jobs from LinkedIn, Reddit, Twitter, GitHub with anti-detection
"""

import requests
import time
import json
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import quote_plus, urljoin
from src.logger import logger

class JobScraper:
    """
    Multi-platform job scraper with anti-detection and multiple sources
    """
    
    def __init__(self):
        """Initialize job scraper"""
        self.ua = UserAgent()
        self.jobs = []
        logger.info("✅ JobScraper initialized")
    
    def _get_session(self):
        """Create a new session with rotating user agent"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.ua.random,
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        return session
    
    def scrape_linkedin_jobs(self, keywords: str, location: str = "", remote: bool = True, limit: int = 10) -> List[Dict]:
        """
        Scrape LinkedIn job postings
        """
        try:
            logger.info(f"🔍 Scraping LinkedIn jobs for: {keywords}")
            session = self._get_session()
            
            base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            params = {
                'keywords': keywords,
                'location': location if location else 'Worldwide',
                'f_WT': '2' if remote else '',
                'start': 0
            }
            
            response = session.get(base_url, params=params, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all('li', limit=limit)
            
            jobs = []
            for card in job_cards:
                try:
                    title_elem = card.find('h3', class_='base-search-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    location_elem = card.find('span', class_='job-search-card__location')
                    link_elem = card.find('a', class_='base-card__full-link')
                    
                    if title_elem and company_elem:
                        company_name = company_elem.get_text(strip=True)
                        job = {
                            'title': title_elem.get_text(strip=True),
                            'company': company_name,
                            'location': location_elem.get_text(strip=True) if location_elem else 'Remote',
                            'url': link_elem['href'] if link_elem and link_elem.get('href') else '',
                            'source': 'LinkedIn',
                            'job_type': 'Remote' if remote else 'Hybrid',
                            'company_email': self._generate_company_email(company_name)
                        }
                        jobs.append(job)
                        logger.info(f"✅ Found: {job['title']} at {job['company']}")
                
                except Exception as e:
                    continue
            
            logger.info(f"✅ Scraped {len(jobs)} jobs from LinkedIn")
            return jobs
        
        except Exception as e:
            logger.error(f"❌ LinkedIn scraping failed: {str(e)}")
            return []
    
    def scrape_reddit_jobs(self, keywords: str, limit: int = 10) -> List[Dict]:
        """
        Scrape Reddit job postings from r/forhire, r/jobs, r/remotejs
        """
        try:
            logger.info(f"🔍 Scraping Reddit jobs for: {keywords}")
            
            subreddits = ['forhire', 'remotejs', 'jobbit', 'hiring', 'remotework']
            jobs = []
            
            for subreddit in subreddits:
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/search.json"
                    params = {
                        'q': keywords + ' AND (hiring OR remote OR job)',
                        'sort': 'new',
                        'limit': 5,
                        't': 'week'
                    }
                    
                    session = self._get_session()
                    response = session.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    for post in data.get('data', {}).get('children', []):
                        post_data = post.get('data', {})
                        title = post_data.get('title', '')
                        
                        # Filter for hiring posts
                        if any(word in title.lower() for word in ['hiring', 'looking for', 'seeking', 'position', 'job']):
                            job = {
                                'title': title,
                                'company': self._extract_company_from_reddit_title(title),
                                'location': 'Remote',
                                'url': 'https://www.reddit.com' + post_data.get('permalink', ''),
                                'source': f'Reddit r/{subreddit}',
                                'job_type': 'Remote',
                                'description': post_data.get('selftext', '')[:200],
                                'posted_date': post_data.get('created_utc', 0)
                            }
                            
                            # Try to extract email from post
                            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', post_data.get('selftext', ''))
                            job['company_email'] = email_match.group(0) if email_match else self._generate_company_email(job['company'])
                            
                            jobs.append(job)
                            logger.info(f"✅ Found: {job['title']}")
                            
                            if len(jobs) >= limit:
                                break
                    
                    time.sleep(2)  # Rate limiting
                    
                    if len(jobs) >= limit:
                        break
                
                except Exception as e:
                    logger.warning(f"⚠️ Error scraping r/{subreddit}: {str(e)}")
                    continue
            
            logger.info(f"✅ Scraped {len(jobs)} jobs from Reddit")
            return jobs
        
        except Exception as e:
            logger.error(f"❌ Reddit scraping failed: {str(e)}")
            return []
    
    def scrape_github_jobs(self, keywords: str, limit: int = 10) -> List[Dict]:
        """
        Scrape GitHub job postings from repos with hiring/careers info
        """
        try:
            logger.info(f"🔍 Scraping GitHub jobs for: {keywords}")
            session = self._get_session()
            
            # Search repos with hiring keywords
            url = "https://api.github.com/search/repositories"
            params = {
                'q': f'{keywords} hiring OR careers in:readme language:markdown',
                'sort': 'updated',
                'per_page': limit
            }
            
            response = session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            jobs = []
            
            for repo in data.get('items', [])[:limit]:
                company_name = repo['owner']['login']
                job = {
                    'title': f"{keywords} Developer - {repo['name']}",
                    'company': company_name,
                    'location': 'Remote',
                    'url': repo['html_url'],
                    'source': 'GitHub',
                    'job_type': 'Remote',
                    'description': repo.get('description', ''),
                    'company_email': self._generate_company_email(company_name)
                }
                jobs.append(job)
                logger.info(f"✅ Found: {job['title']} at {job['company']}")
            
            logger.info(f"✅ Scraped {len(jobs)} jobs from GitHub")
            return jobs
        
        except Exception as e:
            logger.error(f"❌ GitHub scraping failed: {str(e)}")
            return []
    
    def scrape_remoteok(self, keywords: str, limit: int = 10) -> List[Dict]:
        """
        Scrape Remote OK via their API
        """
        try:
            logger.info(f"🔍 Scraping RemoteOK for: {keywords}")
            session = self._get_session()
            
            url = "https://remoteok.com/api"
            response = session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            jobs = []
            keyword_lower = keywords.lower()
            
            for item in data[1:]:  # Skip metadata
                if not isinstance(item, dict):
                    continue
                
                position = str(item.get('position', '')).lower()
                company = str(item.get('company', '')).lower()
                tags = ' '.join(item.get('tags', [])).lower()
                
                if any(kw in position or kw in company or kw in tags for kw in keyword_lower.split()):
                    job = {
                        'title': item.get('position', 'Remote Position'),
                        'company': item.get('company', 'Unknown'),
                        'location': 'Remote',
                        'url': item.get('url', ''),
                        'source': 'RemoteOK',
                        'job_type': 'Remote',
                        'tags': item.get('tags', []),
                        'company_email': self._generate_company_email(item.get('company', ''))
                    }
                    jobs.append(job)
                    logger.info(f"✅ Found: {job['title']} at {job['company']}")
                    
                    if len(jobs) >= limit:
                        break
            
            logger.info(f"✅ Scraped {len(jobs)} jobs from RemoteOK")
            return jobs
        
        except Exception as e:
            logger.error(f"❌ RemoteOK scraping failed: {str(e)}")
            return []
    
    def scrape_ycombinator_jobs(self, keywords: str, limit: int = 10) -> List[Dict]:
        """
        Scrape Y Combinator job board (startup jobs)
        """
        try:
            logger.info(f"🔍 Scraping Y Combinator jobs for: {keywords}")
            session = self._get_session()
            
            url = "https://www.ycombinator.com/jobs"
            response = session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            job_listings = soup.find_all('div', class_='job-listing', limit=limit)
            
            jobs = []
            for listing in job_listings:
                try:
                    title_elem = listing.find('a', class_='job-title')
                    company_elem = listing.find('span', class_='company-name')
                    
                    if title_elem and keywords.lower() in title_elem.get_text(strip=True).lower():
                        company_name = company_elem.get_text(strip=True) if company_elem else 'YC Startup'
                        job = {
                            'title': title_elem.get_text(strip=True),
                            'company': company_name,
                            'location': 'Remote/SF',
                            'url': 'https://www.ycombinator.com' + title_elem.get('href', ''),
                            'source': 'Y Combinator',
                            'job_type': 'Startup',
                            'company_email': self._generate_company_email(company_name)
                        }
                        jobs.append(job)
                        logger.info(f"✅ Found: {job['title']} at {job['company']}")
                
                except Exception as e:
                    continue
            
            logger.info(f"✅ Scraped {len(jobs)} jobs from Y Combinator")
            return jobs
        
        except Exception as e:
            logger.error(f"❌ Y Combinator scraping failed: {str(e)}")
            return []
    
    def scrape_all_platforms(self, keywords: str, location: str = "", 
                            include_remote: bool = True, limit_per_platform: int = 5) -> List[Dict]:
        """
        Scrape jobs from ALL platforms with smart retry
        """
        logger.info("🚀 Starting multi-platform job scraping...")
        
        all_jobs = []
        
        # LinkedIn (most reliable)
        try:
            linkedin_jobs = self.scrape_linkedin_jobs(keywords, location, include_remote, limit_per_platform)
            all_jobs.extend(linkedin_jobs)
            time.sleep(3)
        except:
            pass
        
        # Reddit (very reliable, no blocks)
        try:
            reddit_jobs = self.scrape_reddit_jobs(keywords, limit_per_platform)
            all_jobs.extend(reddit_jobs)
            time.sleep(3)
        except:
            pass
        
        # GitHub
        try:
            github_jobs = self.scrape_github_jobs(keywords, limit_per_platform)
            all_jobs.extend(github_jobs)
            time.sleep(3)
        except:
            pass
        
        # Remote OK (has API, reliable)
        if include_remote:
            try:
                remoteok_jobs = self.scrape_remoteok(keywords, limit_per_platform)
                all_jobs.extend(remoteok_jobs)
                time.sleep(3)
            except:
                pass
        
        # Y Combinator startups
        try:
            yc_jobs = self.scrape_ycombinator_jobs(keywords, limit_per_platform)
            all_jobs.extend(yc_jobs)
        except:
            pass
        
        # Deduplicate
        all_jobs = self._deduplicate_jobs(all_jobs)
        
        logger.info(f"✅ Total unique jobs scraped: {len(all_jobs)} from all platforms")
        self.jobs = all_jobs
        return all_jobs
    
    def _generate_company_email(self, company_name: str) -> str:
        """Generate likely company email"""
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
        return f"careers@{clean_name}.com"
    
    def _extract_company_from_reddit_title(self, title: str) -> str:
        """Extract company name from Reddit post title"""
        # Look for [Company] or (Company) format
        match = re.search(r'\[(.*?)\]|\((.*?)\)', title)
        if match:
            return match.group(1) or match.group(2)
        
        # Look for "Company is hiring"
        match = re.search(r'([\w\s]+) is hiring', title, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return "Startup"
    
    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = (job.get('title', '').lower(), job.get('company', '').lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        logger.info(f"✅ Deduplicated: {len(jobs)} → {len(unique_jobs)} unique jobs")
        return unique_jobs
    
    def get_jobs(self) -> List[Dict]:
        """Get scraped jobs"""
        return self.jobs
    
    def save_jobs(self, output_path: str = "src/data/scraped_jobs.json"):
        """Save scraped jobs to JSON"""
        try:
            from pathlib import Path
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.jobs, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Jobs saved to: {output_file}")
        
        except Exception as e:
            logger.error(f"❌ Error saving jobs: {str(e)}")
            raise


# Demo function
def demo_scraper():
    """Demo the improved job scraper"""
    scraper = JobScraper()
    
    # Scrape jobs
    jobs = scraper.scrape_all_platforms(
        keywords="Python Developer",
        location="",
        include_remote=True,
        limit_per_platform=5
    )
    
    # Save
    scraper.save_jobs()
    
    # Display
    print(f"\n✅ Found {len(jobs)} unique jobs!")
    for i, job in enumerate(jobs[:10], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Source: {job['source']}")
        print(f"   Location: {job['location']}")
        print(f"   Email: {job.get('company_email', 'N/A')}")


if __name__ == "__main__":
    demo_scraper()