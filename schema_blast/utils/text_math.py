import re
from dataclasses import dataclass
from typing import Set, List, Tuple, Optional

@dataclass
class MatchResult:
    """Structured result for schema comparison used for CLI and HTML reports."""
    target_schema_id: str
    target_schema_name: str
    similarity_score: float
    # List of tuples: (query_attribute, target_attribute, fuzzy_confidence_score)
    matching_attributes: List[Tuple[str, str, float]]

    @property
    def quality_label(self) -> str:
        """Determines reliability for external partners based on coverage."""
        if self.similarity_score >= 0.90:
            return "HIGH"
        if self.similarity_score >= 0.70:
            return "MEDIUM"
        return "LOW"

class AttributeSimilarity:
    """Handles normalization and set-based similarity calculations."""
    
    @staticmethod
    def normalize(text: str) -> str:
        if not isinstance(text, str): 
            return ""
        # Standardize for comparison: lower, no underscores/hyphens
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
        Calculates Jaccard Similarity for Exact Matching.
        Used when --fuzzy is NOT enabled.
        """
        # Normalize sets to catch minor formatting differences as "Exact"
        src_norm = {self.normalize(a): a for a in source_attrs if a}
        tgt_norm = {self.normalize(a): a for a in target_attrs if a}
        
        # Find intersection of normalized keys
        common_keys = set(src_norm.keys()).intersection(set(tgt_norm.keys()))
        union_keys = set(src_norm.keys()).union(set(tgt_norm.keys()))
        
        score = len(common_keys) / len(union_keys) if union_keys else 0.0
        
        # Map back to original attribute names for the report
        # For exact matches, we pass 100.0 as the individual attribute score
        matching_details = [(src_norm[k], tgt_norm[k], 100.0) for k in sorted(list(common_keys))]
        
        return MatchResult(
            target_schema_id=target_id or "unknown",
            target_schema_name=target_name,
            similarity_score=score,
            matching_attributes=matching_details
        )