from typing import Dict, Set, Tuple

class BaseExtractor:
    """Base class for all future schema extractors."""
    def extract(self, data: Dict) -> Dict:
        """Returns a dict with 'attributes' (Set) and 'description' (Str)."""
        raise NotImplementedError("Subclasses must implement extract()")

class OCAExtractor(BaseExtractor):
    """Extractor specifically for OCA (Overlay Capture Architecture) schemas."""
    def extract(self, data: Dict) -> Dict:
        attributes = set()
        
        # 1. Extract Attributes from 'attributes' list
        if 'attributes' in data and isinstance(data['attributes'], list):
            for attr in data['attributes']:
                if isinstance(attr, dict):
                    name = attr.get('name')
                    if name: attributes.add(name)
                elif isinstance(attr, str):
                    attributes.add(attr)
        
        # 2. Extract Attributes from 'properties' dictionary
        if 'properties' in data and isinstance(data['properties'], dict):
            attributes.update(data['properties'].keys())
            
        # 3. Clean attributes
        cleaned_attributes = {str(a).lower().strip() for a in attributes if a}

        # 4. Extract Description
        # Looks for 'description' at the root level of the JSON
        description = data.get('description', "")
        if not isinstance(description, str):
            description = str(description)

        return {
            "attributes": cleaned_attributes,
            "description": description.strip()
        }

class GenericJSONExtractor(BaseExtractor):
    """Fallback extractor for standard JSON objects."""
    def extract(self, data: Dict) -> Dict:
        return {
            "attributes": {str(k).lower().strip() for k in data.keys()},
            "description": data.get('description', "Generic JSON Schema")
        }