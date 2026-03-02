import re
from dataclasses import dataclass
from typing import Set, List, Tuple, Optional

@dataclass
class SimilarityResult:
    """Structured result for schema comparison."""
    target_schema_id: str
    target_schema_name: str
    similarity_score: float
    matching_attributes: List[Tuple[str, str]]

class AttributeSimilarity:
    """Handles normalization and set-based similarity calculations."""
    
    @staticmethod
    def normalize(text: str) -> str:
        """Basic text normalization for cleaner matching."""
        if not isinstance(text, str): 
            return ""
        # Remove special characters and lowercase
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return re.sub(r'\s+', ' ', text).strip()

    def calculate_similarity(
        self, 
        source_attrs: Set[str], 
        target_attrs: Set[str],
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        target_name: str = "Unknown"
    ) -> SimilarityResult:
        """
        Calculates Jaccard Similarity between two sets of attributes.
        Formula: (Size of Intersection) / (Size of Union)
        """
        # Ensure we are working with normalized sets for better matching
        src_norm = {self.normalize(a) for a in source_attrs if a}
        tgt_norm = {self.normalize(a) for a in target_attrs if a}
        
        # Calculate Intersection (Common attributes)
        intersection = src_norm.intersection(tgt_norm)
        # Calculate Union (Total unique attributes across both)
        union = src_norm.union(tgt_norm)
        
        # Jaccard Score
        score = len(intersection) / len(union) if union else 0.0
        
        # Prepare the list of matching attribute names for the CLI display
        # We return them as a list of tuples to keep the CLI logic happy
        matching_details = [(attr, attr) for attr in sorted(list(intersection))]
        
        return SimilarityResult(
            target_schema_id=target_id or "unknown",
            target_schema_name=target_name,
            similarity_score=score,
            matching_attributes=matching_details
        )