import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class SolrManager:
    def __init__(self, base_url: str, core_name: str = "schemas-dj"):
        # The base endpoint for all Solr actions
        self.url = f"{base_url.rstrip('/')}/{core_name}"

    def index(self, schema_id: str, name: str, attributes: set, description: str = "", metadata: Optional[dict] = None) -> bool:
        """
        Indexes a schema document into Solr using the requests library.
        """
        doc = {
            "id": schema_id,
            "schema_id": schema_id,
            "schema_name": name,
            "description": description,
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

    def query_similar(self, attributes: List[str], limit: int = 10) -> List[dict]:
        """
        Finds candidate schemas in Solr that share at least one attribute.
        Re-written to use requests for consistency.
        """
        try:
            # Build a query: attributes:("attr1" OR "attr2")
            attr_query = " OR ".join([f'"{a}"' for a in attributes])
            query = f"attributes:({attr_query})"
            
            params = {
                'q': query,
                'rows': limit,
                'wt': 'json'
            }
            
            r = requests.get(f"{self.url}/select", params=params, timeout=10)
            r.raise_for_status()
            
            # Return the list of documents found
            return r.json().get('response', {}).get('docs', [])
        except Exception as e:
            logger.error(f"Failed to query similar schemas: {e}")
            return []

    def list_all(self, limit: int = 100) -> List[dict]:
        """
        Utility to list all indexed schemas.
        """
        try:
            params = {'q': '*:*', 'rows': limit, 'wt': 'json', 'sort': 'timestamp desc'}
            r = requests.get(f"{self.url}/select", params=params, timeout=5)
            r.raise_for_status()
            return r.json().get('response', {}).get('docs', [])
        except Exception as e:
            logger.error(f"Failed to list schemas: {e}")
            return []
    
    def delete_by_id(self, schema_id: str) -> bool:
        """Removes a single schema from the index using HTTP POST."""
        try:
            # Solr expects a 'delete' command in the body
            payload = {"delete": {"id": schema_id}}
            r = requests.post(f"{self.url}/update?commit=true", json=payload, timeout=10)
            r.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error deleting schema {schema_id}: {e}")
            return False

    def delete_all(self) -> bool:
        """Wipes the entire index using HTTP POST."""
        try:
            # Solr expects a 'delete' command with a 'query' for all documents
            payload = {"delete": {"query": "*:*"}}
            r = requests.post(f"{self.url}/update?commit=true", json=payload, timeout=10)
            r.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error wiping index: {e}")
            return False