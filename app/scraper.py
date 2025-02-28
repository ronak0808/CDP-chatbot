import requests
from bs4 import BeautifulSoup
import logging
import json
from pathlib import Path
import time
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class DocumentScraper:
    def __init__(self):
        self.docs_path = Path(__file__).parent.parent / 'data' / 'docs'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.cdp_configs = {
            'segment': {
                'base_url': 'https://segment.com/docs/',
                'selectors': {
                    'content': 'article',
                    'title': 'h1',
                    'sections': '.content-body'
                }
            },
            'mparticle': {
                'base_url': 'https://docs.mparticle.com/',
                'selectors': {
                    'content': 'article',
                    'title': 'h1',
                    'sections': '.content'
                }
            },
            'lytics': {
                'base_url': 'https://docs.lytics.com/',
                'selectors': {
                    'content': 'article',
                    'title': 'h1',
                    'sections': '.content'
                }
            },
            'zeotap': {
                'base_url': 'https://docs.zeotap.com/',
                'selectors': {
                    'content': 'article',
                    'title': 'h1',
                    'sections': '.content'
                }
            }
        }

    def _make_request(self, url, retry_count=3):
        """
        Make an HTTP request with retry logic.
        """
        for attempt in range(retry_count):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if attempt == retry_count - 1:
                    logger.error(f"Failed to fetch {url}: {str(e)}")
                    raise
                time.sleep(1 * (attempt + 1))  # Exponential backoff

    def _clean_text(self, text):
        """
        Clean and normalize text content.
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize newlines
        text = ' '.join(text.split())
        
        # Remove any special characters that might cause issues
        text = text.replace('\u200b', '')  # Zero-width space
        text = text.replace('\xa0', ' ')   # Non-breaking space
        
        return text.strip()

    def _extract_content(self, soup, selectors):
        """
        Extract content from a BeautifulSoup object using provided selectors.
        """
        sections = []
        
        # Find main content area
        content_area = soup.select_one(selectors['content'])
        if not content_area:
            return sections

        # Extract title
        title = content_area.select_one(selectors['title'])
        title_text = self._clean_text(title.get_text()) if title else "Untitled Section"

        # Extract content sections
        content_sections = content_area.select(selectors['sections'])
        
        if not content_sections:
            # If no sections found, treat entire content as one section
            main_content = self._clean_text(content_area.get_text())
            if main_content:
                sections.append({
                    "title": title_text,
                    "content": main_content
                })
        else:
            # Process each section
            for section in content_sections:
                section_title = section.find('h2')
                section_title = self._clean_text(section_title.get_text()) if section_title else title_text
                section_content = self._clean_text(section.get_text())
                
                if section_content:
                    sections.append({
                        "title": section_title,
                        "content": section_content
                    })

        return sections

    def _get_doc_links(self, base_url):
        """
        Get documentation page links from the base URL.
        """
        try:
            response = self._make_request(base_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = set()
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(base_url, href)
                
                # Only include links from the same domain and documentation section
                if (urlparse(full_url).netloc == urlparse(base_url).netloc and
                    'docs' in full_url and
                    '#' not in full_url):
                    links.add(full_url)
            
            return list(links)
        except Exception as e:
            logger.error(f"Error getting doc links from {base_url}: {str(e)}")
            return []

    def scrape_documentation(self, cdp):
        """
        Scrape documentation for a specific CDP.
        """
        if cdp not in self.cdp_configs:
            raise ValueError(f"Unsupported CDP: {cdp}")

        config = self.cdp_configs[cdp]
        base_url = config['base_url']
        selectors = config['selectors']
        
        try:
            # Get documentation pages
            doc_links = self._get_doc_links(base_url)
            if not doc_links:
                logger.warning(f"No documentation links found for {cdp}")
                return []

            all_sections = []
            
            # Process each documentation page
            for link in doc_links:
                try:
                    response = self._make_request(link)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    sections = self._extract_content(soup, selectors)
                    all_sections.extend(sections)
                    
                    # Be nice to the servers
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing {link}: {str(e)}")
                    continue

            return all_sections

        except Exception as e:
            logger.error(f"Error scraping documentation for {cdp}: {str(e)}")
            raise

    def save_documentation(self, cdp, sections):
        """
        Save scraped documentation to a JSON file.
        """
        try:
            self.docs_path.mkdir(parents=True, exist_ok=True)
            
            output_file = self.docs_path / f"{cdp}_docs.json"
            data = {
                "platform": cdp,
                "sections": sections
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Successfully saved documentation for {cdp}")
            
        except Exception as e:
            logger.error(f"Error saving documentation for {cdp}: {str(e)}")
            raise

    def update_all_documentation(self):
        """
        Update documentation for all supported CDPs.
        """
        for cdp in self.cdp_configs:
            try:
                logger.info(f"Updating documentation for {cdp}...")
                sections = self.scrape_documentation(cdp)
                if sections:
                    self.save_documentation(cdp, sections)
                    logger.info(f"Successfully updated {cdp} documentation")
                else:
                    logger.warning(f"No content found for {cdp}")
            except Exception as e:
                logger.error(f"Failed to update {cdp} documentation: {str(e)}")
                continue

# Create scraper instance
scraper = DocumentScraper()

def update_documentation():
    """
    Global function to update all documentation.
    """
    scraper.update_all_documentation()
