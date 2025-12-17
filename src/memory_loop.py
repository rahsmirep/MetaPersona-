"""
MetaPersona - Memory Loop
Implements learning and feedback mechanism for continuous improvement.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel


class Interaction(BaseModel):
    """Single interaction record."""
    timestamp: str
    task: str
    response: str
    feedback_score: Optional[float] = None
    feedback_text: Optional[str] = None
    tags: List[str] = []


class MemoryLoop:
    """Manages interaction history and learning feedback."""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.memory_path = self.data_dir / "memory.jsonl"
        
    def record_interaction(self, task: str, response: str, tags: List[str] = None) -> Interaction:
        """Record a new interaction."""
        interaction = Interaction(
            timestamp=datetime.now().isoformat(),
            task=task,
            response=response,
            tags=tags or []
        )
        
        # Append to memory file
        with open(self.memory_path, 'a', encoding='utf-8') as f:
            f.write(interaction.model_dump_json() + '\n')
        
        return interaction
    
    def add_feedback(self, interaction_index: int, score: float, text: str = None):
        """Add feedback to a specific interaction."""
        interactions = self.load_all_interactions()
        
        if 0 <= interaction_index < len(interactions):
            interactions[interaction_index].feedback_score = score
            interactions[interaction_index].feedback_text = text
            
            # Rewrite memory file
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                for interaction in interactions:
                    f.write(interaction.model_dump_json() + '\n')
            
            print(f"✓ Feedback recorded: {score:.1f}/5.0")
            return True
        return False
    
    def load_all_interactions(self) -> List[Interaction]:
        """Load all recorded interactions."""
        if not self.memory_path.exists():
            return []
        
        interactions = []
        with open(self.memory_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    interactions.append(Interaction.model_validate_json(line))
        return interactions
    
    def get_recent_interactions(self, count: int = 10) -> List[Interaction]:
        """Get most recent interactions."""
        interactions = self.load_all_interactions()
        return interactions[-count:] if interactions else []
    
    def get_interactions_by_tag(self, tag: str) -> List[Interaction]:
        """Get interactions with specific tag."""
        interactions = self.load_all_interactions()
        return [i for i in interactions if tag in i.tags]
    
    def get_feedback_summary(self) -> Dict:
        """Get summary of feedback metrics."""
        interactions = self.load_all_interactions()
        
        total = len(interactions)
        with_feedback = [i for i in interactions if i.feedback_score is not None]
        
        if not with_feedback:
            return {
                "total_interactions": total,
                "feedback_count": 0,
                "average_score": 0.0,
                "feedback_rate": 0.0
            }
        
        avg_score = sum(i.feedback_score for i in with_feedback) / len(with_feedback)
        
        return {
            "total_interactions": total,
            "feedback_count": len(with_feedback),
            "average_score": avg_score,
            "feedback_rate": len(with_feedback) / total if total > 0 else 0.0
        }
    
    def analyze_learning_progress(self) -> Dict:
        """Analyze learning progress over time."""
        interactions = self.load_all_interactions()
        with_feedback = [i for i in interactions if i.feedback_score is not None]
        
        if len(with_feedback) < 2:
            return {"status": "insufficient_data", "message": "Need at least 2 feedback points"}
        
        # Split into first half and second half
        mid = len(with_feedback) // 2
        first_half = with_feedback[:mid]
        second_half = with_feedback[mid:]
        
        avg_first = sum(i.feedback_score for i in first_half) / len(first_half)
        avg_second = sum(i.feedback_score for i in second_half) / len(second_half)
        
        improvement = avg_second - avg_first
        
        return {
            "status": "analyzed",
            "early_period_score": avg_first,
            "recent_period_score": avg_second,
            "improvement": improvement,
            "trend": "improving" if improvement > 0.1 else "declining" if improvement < -0.1 else "stable"
        }
    
    def extract_learning_insights(self) -> List[str]:
        """Extract insights from feedback for profile improvement."""
        interactions = self.load_all_interactions()
        
        # High-scoring interactions
        high_score = [i for i in interactions if i.feedback_score and i.feedback_score >= 4.0]
        
        # Low-scoring interactions
        low_score = [i for i in interactions if i.feedback_score and i.feedback_score <= 2.0]
        
        insights = []
        
        if high_score:
            insights.append(f"✓ {len(high_score)} high-quality responses (4+/5)")
        
        if low_score:
            insights.append(f"⚠ {len(low_score)} low-quality responses (2-/5) - review needed")
        
        # Tag analysis
        all_tags = [tag for i in interactions for tag in i.tags]
        if all_tags:
            from collections import Counter
            common_tags = Counter(all_tags).most_common(3)
            insights.append(f"Most common tasks: {', '.join([t[0] for t in common_tags])}")
        
        return insights
    
    def export_training_data(self, output_path: str = None, min_score: float = 3.5):
        """Export high-quality interactions for fine-tuning."""
        output_path = output_path or str(self.data_dir / "training_export.jsonl")
        
        interactions = self.load_all_interactions()
        quality_interactions = [
            i for i in interactions 
            if i.feedback_score and i.feedback_score >= min_score
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for interaction in quality_interactions:
                training_example = {
                    "messages": [
                        {"role": "user", "content": interaction.task},
                        {"role": "assistant", "content": interaction.response}
                    ]
                }
                f.write(json.dumps(training_example) + '\n')
        
        print(f"✓ Exported {len(quality_interactions)} training examples to {output_path}")
        return len(quality_interactions)
