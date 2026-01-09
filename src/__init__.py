"""
Object Permanence Task implementation.

This module provides:
    - config.py   : Object permanence task configuration (TaskConfig)
    - generator.py: Object permanence task generation logic (TaskGenerator)
    - prompts.py  : Object permanence task prompts/instructions (get_prompt)
"""

from .config import TaskConfig
from .generator import TaskGenerator
from .prompts import get_prompt

__all__ = ["TaskConfig", "TaskGenerator", "get_prompt"]
