"""Parser for Work.ua search results pages."""
from typing import List, Optional
from bs4 import BeautifulSoup
import re
import logging

from .models import ResumeCard, EmploymentType

logger = logging.getLogger(__name__)


class SearchPageParser:
    """Parser for search results page containing resume cards."""
    
    def parse_search_page(self, html: str) -> List[ResumeCard]:
        """
        Parse search results page and extract resume cards.
        
        Args:
            html: HTML content of search page
            
        Returns:
            List of ResumeCard objects
        """
        soup = BeautifulSoup(html, 'lxml')
        resume_cards = []
        
        # Find all resume card containers
        # Based on example: div.card.card-hover.resume-link
        cards = soup.find_all('div', class_=['card', 'resume-link'])
        
        for card in cards:
            try:
                resume_card = self._parse_resume_card(card)
                if resume_card:
                    resume_cards.append(resume_card)
            except Exception as e:
                logger.warning(f"Failed to parse resume card: {e}")
                continue
        
        logger.info(f"Parsed {len(resume_cards)} resume cards from search page")
        return resume_cards
    
    def _parse_resume_card(self, card_element) -> Optional[ResumeCard]:
        """
        Parse individual resume card element.
        
        Args:
            card_element: BeautifulSoup element for resume card
            
        Returns:
            ResumeCard object or None if parsing fails
        """
        # Extract URL and position from h2 > a
        h2 = card_element.find('h2')
        if not h2:
            return None
        
        link = h2.find('a', href=re.compile(r'/resumes/\d+/'))
        if not link:
            return None
        
        url = link['href']
        position = link.text.strip()
        
        # Extract resume ID from URL
        resume_id_match = re.search(r'/resumes/(\d+)/', url)
        if not resume_id_match:
            return None
        resume_id = int(resume_id_match.group(1))
        
        # Extract person name from <b> tag after h2
        person_name = None
        name_tag = card_element.find('b')
        if name_tag:
            person_name = name_tag.text.strip()
        
        # Extract age from text (format: "25 років" or "25 лет")
        age = None
        age_match = re.search(r'(\d+)\s+(?:років|лет|года)', card_element.text)
        if age_match:
            age = int(age_match.group(1))
        
        # Extract city
        city = None
        # City typically appears after comma or in specific span
        text_parts = card_element.get_text(separator='|', strip=True).split('|')
        for part in text_parts:
            if 'Київ' in part or 'Киев' in part or 'Львів' in part or 'Харків' in part:
                city = part.strip(' ,·')
                break
        
        # Extract education level and employment types from text-muted div
        education_level = None
        employment_types = []
        muted_div = card_element.find('div', class_='text-muted')
        if muted_div:
            muted_text = muted_div.text
            
            # Education keywords
            if 'Вища освіта' in muted_text or 'Высшее образование' in muted_text:
                education_level = 'Вища освіта'
            elif 'Неоконченное высшее' in muted_text or 'Незакінчена вища' in muted_text:
                education_level = 'Незакінчена вища'
            elif 'Середня спеціальна' in muted_text or 'Средне специальное' in muted_text:
                education_level = 'Середня спеціальна'
            
            # Employment types
            if 'Повна зайнятість' in muted_text or 'Полная занятость' in muted_text:
                employment_types.append(EmploymentType.FULL_TIME.value)
            if 'Неповна зайнятість' in muted_text or 'Неполная занятость' in muted_text:
                employment_types.append(EmploymentType.PART_TIME.value)
            if 'Віддалена робота' in muted_text or 'Удаленная работа' in muted_text or 'удаленная работа' in muted_text:
                employment_types.append(EmploymentType.REMOTE.value)
        
        return ResumeCard(
            resume_id=resume_id,
            url=url,
            position=position,
            person_name=person_name,
            age=age,
            city=city,
            education_level=education_level,
            employment_types=employment_types
        )
    
    def has_next_page(self, html: str) -> bool:
        """
        Check if there's a next page link in pagination.
        
        Args:
            html: HTML content of search page
            
        Returns:
            True if next page exists, False otherwise
        """
        soup = BeautifulSoup(html, 'lxml')
        # Look for pagination next button
        next_link = soup.find('a', class_=['page-next', 'pagination-next'])
        return next_link is not None
