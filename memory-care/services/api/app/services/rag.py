from typing import List, Dict, Any

def answer_name(full_name: str) -> Dict[str, Any]:
    return {'answer': f'Your name is {full_name}.', 'sources': []}

def compose_relationship_answer(candidates: List[dict]) -> Dict[str, Any]:
    if not candidates:
        return {'answer': 'I’m not sure yet. Let’s check with your caregiver.', 'sources': []}
    context = ' '.join([c['text'] for c in candidates[:3]])[:300]
    return {'answer': f'We know each other through: {context}.', 'sources': candidates[:3]}
