from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class SchemaMatch:
    target_schema_id: str
    target_schema_name: str
    similarity_score: float
    matching_attributes: List[Tuple[str, str, float]]
    attribute_overlap: float