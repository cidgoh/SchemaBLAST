import os
import json
import yaml
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dotenv import load_dotenv

from .storage import SolrManager
from .utils.extractors import ExtractorFactory
from .utils.text_math import AttributeSimilarity

load_dotenv()
logger = logging.getLogger(__name__)

class ComparatorEngine:
    def __init__(self, solr_url: Optional[str] = None):
        self.solr_endpoint = solr_url or os.getenv("SOLR_URL", "http://localhost:8983/solr")
        self.db = SolrManager(self.solr_endpoint)
        self.similarity_engine = AttributeSimilarity()

    def _load_file_data(self, path: Path) -> Dict:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif path.suffix.lower() == '.json':
                    return json.load(f)
                return {}
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
            return {}

    def process_and_upload(self, file_path: str, schema_format: str = "auto", 
                           name_override: Optional[str] = None, 
                           user_description: str = "") -> List[str]:
        path = Path(file_path)
        data = self._load_file_data(path)
        if not data: return []

        extractor = ExtractorFactory.get_extractor(schema_format, data)
        extracted_schemas = extractor.extract(data)
        
        uploaded_ids = []
        for schema_info in extracted_schemas:
            display_name = name_override if (name_override and len(extracted_schemas) == 1) else schema_info.get("name", "Unknown")
            desc = user_description if (user_description and len(extracted_schemas) == 1) else schema_info.get("description", "")
            
            attr_list = sorted(list(schema_info["attributes"]))
            content_hash = hashlib.md5(f"{display_name}{''.join(attr_list)}".encode()).hexdigest()[:12]
            schema_id = f"schema_{content_hash}"
            
            if self.db.index(schema_id=schema_id, name=display_name, attributes=schema_info["attributes"], description=desc):
                uploaded_ids.append(schema_id)
        return uploaded_ids

    def batch_upload(self, directory_path: str, schema_format: str = "auto") -> Dict[str, int]:
        folder = Path(directory_path)
        stats = {"files_processed": 0, "schemas_indexed": 0}
        if not folder.is_dir(): return stats

        for file in folder.glob("*"):
            if file.suffix.lower() in ['.json', '.yaml', '.yml']:
                ids = self.process_and_upload(str(file), schema_format=schema_format)
                stats["files_processed"] += 1
                stats["schemas_indexed"] += len(ids)
        return stats

    def find_similar_schemas(self, schema_id: str, threshold: float = 0.4, limit: int = 5) -> Tuple[List, Set[str]]:
        source_data = self.db.get_schema(schema_id)
        if not source_data:
            logger.error(f"Source schema '{schema_id}' not found.")
            return [], set()

        source_attributes = set(source_data.get('attributes', []))
        return self._compare_against_db(source_attributes, schema_id, threshold, limit), source_attributes

    def probe_file(self, file_path: str, schema_format: str = "auto", threshold: float = 0.4, limit: int = 5) -> Tuple[List, Set[str]]:
        path = Path(file_path)
        data = self._load_file_data(path)
        if not data: return [], set()

        extractor = ExtractorFactory.get_extractor(schema_format, data)
        extracted = extractor.extract(data)
        if not extracted: return [], set()

        query_attrs = set(extracted[0]['attributes'])
        return self._compare_against_db(query_attrs, "local_file", threshold, limit), query_attrs

    def _compare_against_db(self, source_attributes: Set[str], source_id: str, threshold: float, limit: int) -> List:
        if not source_attributes: return []
        candidates = self.db.query_similar(list(source_attributes), limit=limit * 5)
        matches = []
        for cand in candidates:
            cand_id = cand['schema_id'][0] if isinstance(cand['schema_id'], list) else cand['schema_id']
            if cand_id == source_id: continue
                
            cand_name = cand['schema_name'][0] if isinstance(cand.get('schema_name'), list) else cand.get('schema_name', 'Unknown')
            candidate_attrs = set(cand.get('attributes', []))
            
            result = self.similarity_engine.calculate_similarity(
                source_attrs=source_attributes, target_attrs=candidate_attrs,
                source_id=source_id, target_id=cand_id, target_name=cand_name
            )
            if result.similarity_score >= threshold:
                matches.append(result)
                
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        return matches[:limit]
    
    def remove_schema(self, schema_id: str) -> bool:
        return self.db.delete_by_id(schema_id)

    def clear_all_data(self) -> bool:
        return self.db.delete_all()