from typing import Dict, List, Set, Optional

class BaseExtractor:
    def extract(self, data: Dict) -> List[Dict]:
        raise NotImplementedError

class OCAExtractor(BaseExtractor):
    """Handles standard OCA Layouts."""
    def extract(self, data: Dict) -> List[Dict]:
        attributes = set()
        # OCA logic: look for 'attributes' or 'properties'
        if 'attributes' in data:
            if isinstance(data['attributes'], list):
                for attr in data['attributes']:
                    name = attr.get('name') if isinstance(attr, dict) else attr
                    if name: attributes.add(name)
        elif 'properties' in data:
            attributes.update(data['properties'].keys())
            
        return [{
            "name": data.get('name', 'Unnamed OCA'),
            "attributes": {str(a).lower().strip() for a in attributes},
            "description": data.get('description', "")
        }]

class LinkMLExtractor(BaseExtractor):
    """Handles LinkML files with multiple classes/slots."""
    def extract(self, data: Dict) -> List[Dict]:
        results = []
        classes = data.get('classes', {})
        for class_name, content in classes.items():
            slots = content.get('slots', [])
            if slots:
                results.append({
                    "name": class_name,
                    "attributes": {str(s).lower().strip() for s in slots},
                    "description": content.get('description', f"LinkML Class: {class_name}")
                })
        return results

class ExtractorFactory:
    """Orchestrates which extractor to use."""
    @staticmethod
    def get_extractor(schema_format: str = "auto", data: Dict = None):
        if schema_format == "oca":
            return OCAExtractor()
        if schema_format == "linkml":
            return LinkMLExtractor()
        
        # Auto-detection logic
        if data and 'classes' in data:
            return LinkMLExtractor()
        return OCAExtractor()