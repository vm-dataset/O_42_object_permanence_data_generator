"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    OBJECT PERMANENCE TASK CONFIGURATION                      ║
║                                                                               ║
║  Configuration for object permanence task data generation.                    ║
║  Inherits common settings from core.GenerationConfig                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from pydantic import Field
from core import GenerationConfig


class TaskConfig(GenerationConfig):
    """
    Object permanence task configuration.
    
    Configuration for generating object permanence reasoning tasks.
    
    Inherited from GenerationConfig:
        - num_samples: int          # Number of samples to generate
        - domain: str               # Task domain name (default: "object_permanence")
        - difficulty: Optional[str] # Difficulty level (easy/medium/hard)
        - random_seed: Optional[int] # For reproducibility
        - output_dir: Path          # Where to save outputs
        - image_size: tuple[int, int] # Image dimensions (default: (256, 256))
    """
    
    # ══════════════════════════════════════════════════════════════════════════
    #  OVERRIDE DEFAULTS
    # ══════════════════════════════════════════════════════════════════════════
    
    domain: str = Field(default="object_permanence")
    image_size: tuple[int, int] = Field(default=(256, 256))
    
    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    generate_videos: bool = Field(
        default=True,
        description="Whether to generate ground truth videos"
    )
    
    video_fps: int = Field(
        default=10,
        description="Video frame rate"
    )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  OBJECT PERMANENCE TASK SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    # Difficulty levels:
    # - "easy": 1 object
    # - "medium": 2 objects
    # - "hard": 3 objects
    # Set via difficulty parameter in GenerationConfig
