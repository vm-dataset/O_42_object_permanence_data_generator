"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    OBJECT PERMANENCE TASK PROMPTS                            ║
║                                                                               ║
║  Prompts for object permanence tasks.                                         ║
║  Unified template that adapts to any number of objects.                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from typing import List, Dict, Any
from collections import Counter


# ══════════════════════════════════════════════════════════════════════════════
#  PROMPT TEMPLATE
# ══════════════════════════════════════════════════════════════════════════════

PROMPT_TEMPLATE = (
    "The scene contains several stable 2D objects on a flat plane:\n\n"
    "(1) {objects_description}\n\n"
    "(2) A tall narrow vertical gray rectangle positioned on the left side of the scene.\n\n"
    "Move the tall narrow vertical gray rectangle horizontally to the right at a steady speed, "
    "keeping it in its vertical orientation throughout the entire movement.\n\n"
    "As it moves, the tall narrow vertical gray rectangle will pass in front of {objects_reference} "
    "on the 2D plane and occlude {objects_pronoun}, without any physical interaction.\n\n"
    "Continue moving the tall narrow vertical gray rectangle to the right until it has fully exited the scene.\n\n"
    "The camera view remains fixed for the entire sequence."
)


def get_prompt(objects: List[Dict[str, Any]], difficulty: str = "easy") -> str:
    """
    Generate prompt for object permanence task.
    
    Args:
        objects: List of object dictionaries with 'color' and 'shape' keys
        difficulty: Difficulty level (not used but kept for compatibility)
        
    Returns:
        Formatted prompt string
    """
    return _format_prompt(PROMPT_TEMPLATE, objects)


def _format_prompt(template: str, objects: List[Dict[str, Any]]) -> str:
    """Format prompt template with object descriptions."""
    num_objects = len(objects)
    
    def get_article(word: str) -> str:
        """Return 'a' or 'an' based on whether word starts with vowel sound."""
        vowels = ['a', 'e', 'i', 'o', 'u']
        return "an" if word[0].lower() in vowels else "a"
    
    def number_to_word(n: int) -> str:
        """Convert number to word (1-10)."""
        words = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
        if 1 <= n <= 10:
            return words[n - 1]
        else:
            return str(n)
    
    # Build object descriptions and group duplicates
    object_keys = [(obj['color'], obj['shape']) for obj in objects]
    object_counts = Counter(object_keys)
    
    # Build description list with counts for duplicates
    description_parts = []
    seen = set()
    for obj in objects:
        key = (obj['color'], obj['shape'])
        if key in seen:
            continue
        seen.add(key)
        count = object_counts[key]
        article = get_article(obj['color'])
        if count == 1:
            description_parts.append(f"{article} {obj['color']} {obj['shape']}")
        else:
            # Use plural form: "two green circles"
            description_parts.append(f"{number_to_word(count)} {obj['color']} {obj['shape']}s")
    
    # Format objects description based on count
    def capitalize_first(s: str) -> str:
        """Capitalize first letter of string."""
        if not s:
            return s
        return s[0].upper() + s[1:] if len(s) > 1 else s.upper()
    
    if num_objects == 1:
        objects_description = capitalize_first(description_parts[0])
        obj = objects[0]
        shape_name = obj['shape']
        objects_reference = f"the {shape_name}"
        objects_pronoun = "it"
    elif num_objects == 2:
        if len(description_parts) == 1:
            objects_description = capitalize_first(description_parts[0])
        else:
            objects_description = capitalize_first(description_parts[0]) + f" and {description_parts[1]}"
        objects_reference = "the other objects"
        objects_pronoun = "them"
    else:
        if len(description_parts) == 1:
            objects_description = capitalize_first(description_parts[0])
        else:
            if len(description_parts) == 2:
                objects_description = capitalize_first(description_parts[0]) + f" and {description_parts[1]}"
            else:
                objects_description = capitalize_first(description_parts[0]) + ", " + ", ".join(description_parts[1:-1]) + f", and {description_parts[-1]}"
        objects_reference = "the other objects"
        objects_pronoun = "them"
    
    return template.format(
        objects_description=objects_description,
        objects_reference=objects_reference,
        objects_pronoun=objects_pronoun
    )
