import re
import logging
from typing import Dict, List
from app.config import settings

logger = logging.getLogger(__name__)

TECH_KEYWORDS = {"python", "fastapi", "react", "pytorch", "transformers", "spacy", "mongodb", "docker", "docker compose", "github actions", "render", "railway", "javascript", "bert", "roberta", "bart", "keybert", "chart.js", "bootstrap", "rest api", "jwt", "database", "ai", "nlp", "machine learning", "gpu", "cpu", "server"}
PRODUCT_KEYWORDS = {"software", "app", "system", "platform", "dashboard", "api", "service", "model", "portal", "application", "tool", "device", "engine"}

class NERService:
    def __init__(self):
        self.nlp = None
        self._is_loaded = False

    def _lazy_load(self):
        if not self._is_loaded:
            try:
                import spacy
                try:
                    self.nlp = spacy.load("en_core_web_trf")
                except Exception:
                    self.nlp = spacy.load("en_core_web_sm")
                self._is_loaded = True
                logger.info("Loaded spaCy NER pipeline.")
            except Exception as e:
                logger.warning(f"Could not load spaCy NER ({e}). Utilizing rule-based entity extractor.")
                self.nlp = None
                self._is_loaded = True

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        self._lazy_load()

        persons = set()
        organizations = set()
        locations = set()
        dates = set()
        technologies = set()
        products = set()

        if self.nlp is not None:
            try:
                doc = self.nlp(text[:50000])
                for ent in doc.ents:
                    val = ent.text.strip()
                    if len(val) < 2:
                        continue
                    if ent.label_ == "PERSON":
                        persons.add(val)
                    elif ent.label_ in ["ORG", "NORP"]:
                        organizations.add(val)
                    elif ent.label_ in ["GPE", "LOC", "FAC"]:
                        locations.add(val)
                    elif ent.label_ in ["DATE", "TIME"]:
                        dates.add(val)
                    elif ent.label_ in ["PRODUCT", "WORK_OF_ART"]:
                        products.add(val)
            except Exception as e:
                logger.error(f"spaCy NER processing error: {e}")

        # Regex and keyword enricher for tech, dates, orgs, persons
        text_lower = text.lower()
        
        # Technology keywords match
        for tech in TECH_KEYWORDS:
            if re.search(r'\b' + re.escape(tech) + r'\b', text_lower):
                technologies.add(tech.upper() if len(tech) <= 4 else tech.title())
                
        # Product keywords match
        for prod in PRODUCT_KEYWORDS:
            if re.search(r'\b' + re.escape(prod) + r'\b', text_lower):
                products.add(prod.title())

        # Regex Date matcher fallback
        date_matches = re.findall(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b', text, re.IGNORECASE)
        for d in date_matches:
            dates.add(d)

        # Capitalized multi-word regex for Persons/Orgs fallback if spacy returned few
        if not persons:
            cap_names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text)
            for name in cap_names[:5]:
                if name.lower() not in {"united states", "new york", "san francisco", "deep mind"}:
                    persons.add(name)

        if not organizations:
            org_matches = re.findall(r'\b[A-Z][a-zA-Z0-9]+ (?:Inc|Corp|LLC|Ltd|University|Hospital|Department|Team|Group|Agency)\b', text)
            for org in org_matches:
                organizations.add(org)

        return {
            "persons": sorted(list(persons))[:10],
            "organizations": sorted(list(organizations))[:10],
            "locations": sorted(list(locations))[:10],
            "dates": sorted(list(dates))[:10],
            "technologies": sorted(list(technologies))[:10],
            "products": sorted(list(products))[:10]
        }

ner_service = NERService()
