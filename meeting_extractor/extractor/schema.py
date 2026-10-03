"""Step 4: structured output schema."""
from dataclasses import dataclass, field, asdict
from typing import Optional, List


@dataclass
class ActionItem:
    task: str
    owner: Optional[str] = None          # person responsible, None if unknown
    deadline: Optional[str] = None       # ISO date "YYYY-MM-DD", None if unknown
    confidence: float = 0.5              # 0..1
    status: str = "open"                 # "open" | "needs_review"
    source_sentence: str = ""
    flags: List[str] = field(default_factory=list)  # validation warnings

    def to_dict(self):
        return asdict(self)
