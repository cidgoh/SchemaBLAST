from typing import Dict, Set

class BaseExtractor:
    """Base class for all future schema extractors (OCA, SQL, GraphQL, etc.)"""
    def extract(self, data: Dict) -> Set[str]:
        raise NotImplementedError

class OCAExtractor(BaseExtractor):
    def extract(self, data: Dict) -> Set[str]:
        attributes = set()
        if 'attributes' in data:
            for attr in data['attributes']:
                if isinstance(attr, dict)): attributes.add(attr.get('name'))
                else: attributes.add(attr)
        if 'properties' in data:
            attributes.update(data['properties'].keys())
        return {str(a).lower().strip() for a in attributes if a}

class GenericJSONExtractor(BaseExtractor):
    """A simple extractor for standard JSON objects"""
    def extract(self, data: Dict) -> Set[str]:
        return {str(k).lower().strip() for k in data.keys()}