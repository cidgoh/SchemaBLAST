import re
from dataclasses import dataclass
from typing import Set, List, Tuple, Optional

@dataclass
class MatchResult:  # Renamed from SimilarityResult to match comparator.py
    """Structured result for schema comparison."""
    target_schema_id: str
    target_schema_name: str
    similarity_score: float
    # List of tuples: (query_attribute, target_attribute)
    matching_attributes: List[Tuple[str, str]]

class AttributeSimilarity:
    """Handles normalization and set-based similarity calculations."""
    
    @staticmethod
    def normalize(text: str) -> str:
        """Basic text normalization for cleaner matching."""
        if not isinstance(text, str): 
            return ""
        # Remove special characters, underscores, and lowercase
        # This helps with basic matching before even hitting fuzzy logic
        text = text.lower().replace('_', ' ').replace('-', ' ')
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()

    def calculate_similarity(
        self, 
        source_attrs: Set[str], 
        target_attrs: Set[str],
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        target_name: str = "Unknown"
    ) -> MatchResult:
        """
        Calculates Jaccard Similarity between two sets of attributes.
        Note: This is the 'Exact' logic. The 'Fuzzy' logic is handled 
        directly in comparator.py using rapidfuzz.
        """
        src_norm = {self.normalize(a) for a in source_attrs if a}
        tgt_norm = {self.normalize(a) for a in target_attrs if a}
        
        intersection = src_norm.intersection(tgt_norm)
        union = src_norm.union(tgt_norm)
        
        score = len(intersection) / len(union) if union else 0.0
        
        # We store matches as (attr, attr) because they are identical in this method
        matching_details = [(attr, attr) for attr in sorted(list(intersection))]
        
        return MatchResult(
            target_schema_id=target_id or "unknown",
            target_schema_name=target_name,
            similarity_score=score,
            matching_attributes=matching_details
        )