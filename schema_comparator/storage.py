import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class SolrManager:
    def __init__(self, base_url: str, core_name: str = "schemas-dj"):
        # Ensure we use the core name defined in your setup script
        self.url = f"{base_url.rstrip('/')}/{core_name}"

    def index(self, schema_id: str, name: str, attributes: set, description: str = "", metadata: Optional[dict] = None) -> bool:
        """
        Indexes a schema document into Solr.
        """
        doc = {
            "id": schema_id,
            "schema_id": schema_id,
            "schema_name": name,
            "description": description,  # <-- Added new field
            "attributes": list(attributes),
            "attribute_count": len(attributes),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": json.dumps(metadata or {})
        }
        try:
            # commit=true ensures data is searchable immediately
            r = requests.post(f"{self.url}/update?commit=true", json=[doc], timeout=10)
            r.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to index in Solr: {e}")
            return False

    def get_schema(self, schema_id: str) -> Optional[dict]:
        """
        Retrieves a single schema by its ID.
        """
        try:
            params = {'q': f'schema_id:"{schema_id}"', 'wt': 'json'}
            r = requests.get(f"{self.url}/select", params=params, timeout=5)
            r.raise_for_status()
            docs = r.json().get('response', {}).get('docs', [])
            return docs[0] if docs else None
        except Exception as e:
            logger.error(f"Error fetching schema {schema_id}: {e}")
            return None

    def query_similar(self, attributes: List[str]) -> List[dict]:
        """
        Finds schemas that share at least one attribute with the provided list.
        """
        if not attributes:
            return []
            
        # Build an OR query for overlapping attributes
        # Example: attributes:"email" OR attributes:"first_name"
        query_parts = [f'attributes:"{a}"' for a in attributes]
        query = " OR ".join(query_parts)
        
        try:
            # We use POST for the search to handle potentially large query strings
            data = {
                'q': query,
                'rows': 50,
                'wt': 'json',
                'fl': 'schema_id,schema_name,attributes,description,attribute_count' # Field list
            }
            r = requests.post(f"{self.url}/select", data=data, timeout=10)
            r.raise_for_status()
            return r.json().get('response', {}).get('docs', [])
        except Exception as e:
            logger.error(f"Search query failed: {e}")
            return []

    def list_all(self, limit: int = 100) -> List[dict]:
        """
        Utility to list all indexed schemas.
        """
        try:
            params = {'q': '*:*', 'rows': limit, 'wt': 'json', 'sort': 'timestamp desc'}
            r = requests.get(f"{self.url}/select", params=params, timeout=5)
            return r.json().get('response', {}).get('docs', [])
        except Exception as e:
            logger.error(f"Failed to list schemas: {e}")
            return []