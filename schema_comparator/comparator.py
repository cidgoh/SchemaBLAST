import os
import json
import yaml
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Internal imports
from .storage import SolrManager
from .models import SchemaMatch
from .utils.extractors import OCAExtractor, GenericJSONExtractor
from .utils.text_math import AttributeSimilarity

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class ComparatorEngine:
    """
    The core orchestrator that connects extractors, storage, and 
    similarity logic.
    """
    
    def __init__(self, solr_url: Optional[str] = None):
        # Configuration Priority: 1. Constructor Arg, 2. .env file, 3. Hardcoded Default
        self.solr_endpoint = solr_url or os.getenv("SOLR_URL", "http://localhost:8984/solr")
        self.solr_core = os.getenv("SOLR_CORE", "schemas-dj")
        
        self.db = SolrManager(self.solr_endpoint, core_name=self.solr_core)
        self.oca_extractor = OCAExtractor()
        self.json_extractor = GenericJSONExtractor()
        self.similarity_engine = AttributeSimilarity()

    def _load_file_data(self, file_path: Path) -> Dict:
        """Helper to read JSON or YAML data."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() == '.json':
                return json.load(f)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def process_and_upload(self, file_path: str, name: Optional[str] = None, user_description: str = "") -> Optional[str]:
        """
        Extracts attributes and description from a file and indexes them into Solr.
        """
        path = Path(file_path)
        try:
            data = self._load_file_data(path)
            
            # 1. Extract data using the updated Dictionary-return extractor
            # This now returns {"attributes": set(), "description": str}
            extracted_data = self.oca_extractor.extract(data)
            attributes = extracted_data.get("attributes", set())
            
            if not attributes:
                logger.warning(f"No attributes extracted from {file_path}")
                return None

            # 2. Determine Description (CLI arg takes priority over file content)
            final_description = user_description or extracted_data.get("description", "")

            # 3. Generate a unique ID
            schema_name = name or path.stem
            # We sort attributes to ensure the hash is consistent regardless of order
            attr_string = "".join(sorted(list(attributes)))
            content_hash = hashlib.md5(f"{schema_name}{attr_string}".encode()).hexdigest()[:12]
            schema_id = f"schema_{content_hash}"
            
            # 4. Index in Solr
            success = self.db.index(
                schema_id=schema_id,
                name=schema_name,
                attributes=attributes,
                description=final_description, # Passing the new field
                metadata={"source_file": str(path.absolute())}
            )
            
            return schema_id if success else None

        except Exception as e:
            logger.error(f"Failed to process and upload {file_path}: {e}")
            return None

    def find_similar_schemas(self, schema_id: str, threshold: float = 0.4, limit: int = 5) -> List[SchemaMatch]:
        """
        Retrieves a schema by ID and finds other schemas with overlapping attributes.
        """
        # 1. Fetch the source schema from Solr
        source_doc = self.db.get_schema(schema_id)
        if not source_doc:
            logger.error(f"Schema ID {schema_id} not found in database.")
            return []

        # Solr returns attributes as a list; convert to set for math
        source_attrs = set(source_doc.get('attributes', []))
        if not source_attrs:
            return []

        # 2. Query Solr for potential candidates (Pre-filtered by Solr index)
        candidates = self.db.query_similar(list(source_attrs))
        
        results = []
        for cand in candidates:
            target_id = cand['schema_id']
            
            if target_id == schema_id:
                continue
                
            target_attrs = set(cand.get('attributes', []))
            
            # 3. Calculate overlap using your Similarity Engine
            matches = []
            matched_count = 0
            
            for s_attr in source_attrs:
                for t_attr in target_attrs:
                    score = self.similarity_engine.calculate_similarity(s_attr, t_attr)
                    if score >= 0.8: # Threshold for considering two strings a match
                        matches.append((s_attr, t_attr, score))
                        matched_count += 1
                        break 
            
            # 4. Calculate Jaccard-style score
            # Score = Matches / Total distinct attributes across both
            union_size = len(source_attrs.union(target_attrs))
            similarity_score = matched_count / union_size if union_size > 0 else 0
            
            if similarity_score >= threshold:
                results.append(SchemaMatch(
                    target_schema_id=target_id,
                    target_schema_name=cand.get('schema_name', 'Unknown'),
                    similarity_score=round(similarity_score, 4),
                    matching_attributes=matches,
                    attribute_overlap=similarity_score
                ))

        # Sort by score descending
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:limit]