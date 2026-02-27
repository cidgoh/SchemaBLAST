import requests
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SolrManager:
    def __init__(self, url: str):
        self.url = f"{url}/schemas"

    def index(self, schema_id, name, attributes, metadata=None):
        doc = {
            "id": schema_id,
            "schema_name": name,
            "attributes": list(attributes),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": json.dumps(metadata or {})
        }
        try:
            r = requests.post(f"{self.url}/update?commit=true", json=[doc], timeout=10)
            r.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Solr Index Error: {e}")
            return False

    def query_similar(self, attributes: list):
        # Simplified query logic
        params = {'q': ' OR '.join([f'attributes:"{a}"' for a in attributes[:5]]), 'wt': 'json'}
        r = requests.get(f"{self.url}/select", params=params)
        return r.json().get('response', {}).get('docs', [])