from typing import List, Dict, Any
from core.schemas import PhotoRecord, ScoredPhoto

class BaselineMatcher:
    @staticmethod
    def rank_neighborhood(photos: List[Dict[str, Any]], clues: List[str]) -> List[ScoredPhoto]:
        scored = []
        clue_lower = [c.lower() for c in clues if len(c) > 3]
        
        for idx, p_dict in enumerate(photos):
            photo = PhotoRecord(**p_dict)
            score = 0.0
            has_highlight = False
            
            search_text = " ".join(filter(None, [
                photo.caption, 
                " ".join(photo.visual_tags), 
                photo.ocr_text,
                photo.location_name,
                photo.event_tag
            ])).lower()
            
            if clue_lower:
                for c in clue_lower:
                    if c in search_text:
                        score += 0.5
                        has_highlight = True
                        
            scored.append(ScoredPhoto(
                photo=photo,
                in_neighborhood_rank=idx,
                semantic_score=min(1.0, score),
                has_clue_highlight=has_highlight,
                highlight_badge_text="✨ Clue Match" if has_highlight else None
            ))
            
        scored.sort(key=lambda x: (-x.semantic_score, x.in_neighborhood_rank))
        
        # Re-assign rank after sort
        for i, s in enumerate(scored):
            s.in_neighborhood_rank = i
            
        return scored
