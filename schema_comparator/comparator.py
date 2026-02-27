from pathlib import Path
import json
import yaml
import hashlib
from .storage import SolrManager
from .utils.extractors import OCAExtractor, GenericJSONExtractor

class ComparatorEngine:
    def __init__(self, solr_url="http://localhost:8984/solr"):
        self.db = SolrManager(solr_url)
        # You can switch extractors based on file content or flags later
        self.oca_extractor = OCAExtractor()

    def process_and_upload(self, file_path, name=None):
        path = Path(file_path)
        with open(path, 'r') as f:
            data = json.load(f) if path.suffix == '.json' else yaml.safe_load(f)
        
        attrs = self.oca_extractor.extract(data)
        schema_id = hashlib.sha256(f"{path.stem}{attrs}".encode()).hexdigest()[:12]
        
        if self.db.index(schema_id, name or path.stem, attrs):
            return schema_id
        return None