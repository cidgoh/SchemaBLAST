import re
from difflib import SequenceMatcher

class AttributeSimilarity:
    """Handles normalization and similarity calculations between strings."""
    
    @staticmethod
    def normalize(text: str) -> str:
        if not isinstance(text, str): return ""
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return re.sub(r'\s+', ' ', text).strip()

    def calculate_similarity(self, attr1: str, attr2: str) -> float:
        norm1 = self.normalize(attr1)
        norm2 = self.normalize(attr2)
        
        if not norm1 or not norm2:
            return 0.0
            
        # Sequence Matcher Ratio (0.0 - 1.0)
        return SequenceMatcher(None, norm1, norm2).ratio()