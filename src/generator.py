"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    OBJECT PERMANENCE TASK GENERATOR                          ║
║                                                                               ║
║  Generates object permanence tasks for video model evaluation.               ║
║  Tests whether models understand that objects remain unchanged when occluded.║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from PIL import Image
import numpy as np

# Check if matplotlib is available
import importlib.util
MATPLOTLIB_AVAILABLE = importlib.util.find_spec("matplotlib") is not None

if MATPLOTLIB_AVAILABLE:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import Rectangle, Circle, RegularPolygon
else:
    plt = None
    patches = None
    Rectangle = None
    Circle = None
    RegularPolygon = None
    print("⚠️  Warning: matplotlib not installed. Install with: pip install matplotlib")

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


class ObjectGenerator:
    """Generate objects with colors, shapes, and positions."""
    
    COLORS = ["red", "green", "blue", "yellow", "orange", "purple"]
    SHAPES = ["square", "circle", "triangle", "trapezoid"]
    
    COLOR_MAP = {
        "red": "#FF0000",
        "green": "#00FF00",
        "blue": "#0000FF",
        "yellow": "#FFFF00",
        "orange": "#FFA500",
        "purple": "#800080"
    }
    
    def __init__(self, canvas_size: Tuple[int, int] = (256, 256), 
                 min_size: int = 20, max_size: int = 40,
                 min_spacing: int = 40):
        self.canvas_size = canvas_size
        self.min_size = min_size
        self.max_size = max_size
        self.min_spacing = min_spacing
        self.rng = random.Random()
    
    def generate_objects(self, num_objects: int, seed: Optional[int] = None,
                        ensure_occluder_path: bool = True) -> List[Dict[str, Any]]:
        """Generate objects with random colors, shapes, and positions."""
        if seed is not None:
            self.rng.seed(seed)
        
        objects = []
        canvas_w, canvas_h = self.canvas_size
        
        for i in range(num_objects):
            max_attempts = 200
            placed = False
            
            for attempt in range(max_attempts):
                size = 30  # Fixed size for consistency
                
                if ensure_occluder_path:
                    margin = size // 2 + self.min_spacing
                    occluder_width = 50
                    occluder_x_start = 1
                    occluder_right_edge = occluder_x_start + occluder_width
                    min_distance_from_occluder = 40
                    x_min = max(margin, occluder_right_edge + min_distance_from_occluder)
                    center_start = x_min
                    center_end = canvas_w - margin
                    center_width = center_end - center_start
                    x_min_center = center_start + int(center_width * 0.2)
                    x_max_center = center_start + int(center_width * 0.8)
                    x = self.rng.randint(x_min_center, x_max_center)
                    vertical_margin_ratio = 0.2
                    y_min = int(canvas_h * vertical_margin_ratio) + margin
                    y_max = int(canvas_h * (1 - vertical_margin_ratio)) - margin
                    y = self.rng.randint(y_min, y_max)
                else:
                    margin = size // 2 + self.min_spacing
                    x = self.rng.randint(margin, canvas_w - margin)
                    y = self.rng.randint(margin, canvas_h - margin)
                
                # Check collision
                collision = False
                for obj in objects:
                    dx = x - obj["x"]
                    dy = y - obj["y"]
                    distance = np.sqrt(dx*dx + dy*dy)
                    min_distance = (size + obj["size"]) // 2 + self.min_spacing
                    if distance < min_distance:
                        collision = True
                        break
                
                if not collision:
                    color = self.rng.choice(self.COLORS)
                    shape = self.rng.choice(self.SHAPES)
                    
                    if shape == "square":
                        area = size * size
                    elif shape == "circle":
                        area = int(np.pi * (size // 2) ** 2)
                    elif shape == "triangle":
                        area = int(size * size * 0.433)
                    else:  # trapezoid
                        area = int(size * size * 0.75)
                    
                    obj = {
                        "id": i,
                        "color": color,
                        "shape": shape,
                        "x": x,
                        "y": y,
                        "size": size,
                        "area": area
                    }
                    objects.append(obj)
                    placed = True
                    break
            
            if not placed:
                # Fallback: place in center if can't find position
                x = canvas_w // 2
                y = canvas_h // 2 + (i - num_objects // 2) * 50
                color = self.rng.choice(self.COLORS)
                shape = self.rng.choice(self.SHAPES)
                size = 30
                
                if shape == "square":
                    area = size * size
                elif shape == "circle":
                    area = int(np.pi * (size // 2) ** 2)
                elif shape == "triangle":
                    area = int(size * size * 0.433)
                else:
                    area = int(size * size * 0.75)
                
                obj = {
                    "id": i,
                    "color": color,
                    "shape": shape,
                    "x": x,
                    "y": y,
                    "size": size,
                    "area": area
                }
                objects.append(obj)
        
        return objects


class SceneRenderer:
    """Render scene images with objects and occluder."""
    
    def __init__(self, canvas_size: Tuple[int, int] = (256, 256), dpi: int = 100):
        self.canvas_size = canvas_size
        self.dpi = dpi
        self.occluder_width = 50
        self.COLOR_MAP = ObjectGenerator.COLOR_MAP
    
    def render_first_frame(self, objects: List[Dict[str, Any]], 
                          occluder_x: float,
                          output_path: Union[str, Path]) -> None:
        """Render first frame: objects fully visible, occluder on left."""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required for rendering")
        
        fig, ax = plt.subplots(1, 1, figsize=(self.canvas_size[0]/self.dpi, 
                                               self.canvas_size[1]/self.dpi), 
                              dpi=self.dpi)
        
        ax.set_xlim(0, self.canvas_size[0])
        ax.set_ylim(0, self.canvas_size[1])
        ax.set_aspect('equal')
        ax.axis('off')
        ax.invert_yaxis()
        
        # Draw objects
        for obj in objects:
            color = self.COLOR_MAP.get(obj["color"], "#000000")
            x = obj["x"]
            y = obj["y"]
            size = obj["size"]
            shape = obj["shape"]
            self._draw_object(ax, x, y, size, shape, color)
        
        # Draw occluder on left
        edge_margin = 1
        occluder_x_adjusted = occluder_x + edge_margin
        occluder_y = edge_margin
        occluder_height = self.canvas_size[1] - 2 * edge_margin
        
        occluder = Rectangle((occluder_x_adjusted, occluder_y), self.occluder_width, occluder_height,
                           facecolor="#606060", edgecolor="#303030", linewidth=2, 
                           alpha=1.0, joinstyle='miter', capstyle='butt')
        ax.add_patch(occluder)
        
        plt.tight_layout(pad=0)
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close(fig)
    
    def render_final_frame(self, objects: List[Dict[str, Any]], 
                           output_path: Union[str, Path]) -> None:
        """Render final frame: occluder moved out of frame, objects unchanged."""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required for rendering")
        
        fig, ax = plt.subplots(1, 1, figsize=(self.canvas_size[0]/self.dpi, 
                                               self.canvas_size[1]/self.dpi), 
                              dpi=self.dpi)
        
        ax.set_xlim(0, self.canvas_size[0])
        ax.set_ylim(0, self.canvas_size[1])
        ax.set_aspect('equal')
        ax.axis('off')
        ax.invert_yaxis()
        
        # Draw objects (same as first frame)
        for obj in objects:
            color = self.COLOR_MAP.get(obj["color"], "#000000")
            x = obj["x"]
            y = obj["y"]
            size = obj["size"]
            shape = obj["shape"]
            self._draw_object(ax, x, y, size, shape, color)
        
        # No occluder in final frame
        
        plt.tight_layout(pad=0)
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close(fig)
    
    def _draw_object(self, ax, x: float, y: float, size: int, shape: str, color: str):
        """Draw a single 2D object."""
        if shape == "square":
            rect = Rectangle((x - size//2, y - size//2), size, size,
                           facecolor=color, edgecolor="black", linewidth=2)
            ax.add_patch(rect)
        elif shape == "circle":
            circle = Circle((x, y), size//2, facecolor=color, 
                          edgecolor="black", linewidth=2)
            ax.add_patch(circle)
        elif shape == "triangle":
            triangle = RegularPolygon((x, y), 3, radius=size//2,
                                    orientation=np.pi/6,
                                    facecolor=color, edgecolor="black", linewidth=2)
            ax.add_patch(triangle)
        elif shape == "trapezoid":
            half_size = size // 2
            points = [
                (x - half_size, y - half_size),
                (x + half_size, y - half_size),
                (x + half_size//2, y + half_size),
                (x - half_size//2, y + half_size)
            ]
            polygon = patches.Polygon(points, facecolor=color, 
                                    edgecolor="black", linewidth=2)
            ax.add_patch(polygon)


class TaskGenerator(BaseGenerator):
    """
    Object Permanence Task Generator.
    
    Generates tasks that test video models' understanding of object permanence:
    - Objects remain unchanged when occluded
    - Objects maintain position, color, shape when occluder moves
    """
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required. Install with: pip install matplotlib")
        
        self.canvas_size = config.image_size
        self.object_generator = ObjectGenerator(canvas_size=config.image_size)
        self.renderer = SceneRenderer(canvas_size=config.image_size)
        
        # Initialize video generator if enabled
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one object permanence task pair."""
        
        # Determine number of objects based on difficulty
        difficulty = self.config.difficulty or "easy"
        if difficulty == "easy":
            num_objects = 1
        elif difficulty == "medium":
            num_objects = 2
        elif difficulty == "hard":
            num_objects = 3
        else:
            num_objects = 1
        
        # Generate seed for reproducibility
        seed = None
        if self.config.random_seed is not None:
            # Use task_id to create deterministic seed
            seed = hash(task_id) % (2**31)
        
        # Generate objects
        objects = self.object_generator.generate_objects(
            num_objects=num_objects,
            seed=seed,
            ensure_occluder_path=True
        )
        
        # Create temporary directory for images
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_images"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        first_image_path = temp_dir / f"{task_id}_first.png"
        final_image_path = temp_dir / f"{task_id}_final.png"
        
        # Occluder initial position (on left, not occluding objects)
        occluder_x_start = 0
        
        # Render first frame: objects visible, occluder on left
        self.renderer.render_first_frame(objects, occluder_x_start, first_image_path)
        
        # Render final frame: occluder out of frame, objects unchanged
        self.renderer.render_final_frame(objects, final_image_path)
        
        # Load images
        first_image = Image.open(first_image_path).convert('RGB')
        final_image = Image.open(final_image_path).convert('RGB')
        
        # Generate video (optional)
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(first_image, final_image, task_id, objects, occluder_x_start)
        
        # Generate prompt
        prompt = get_prompt(objects, difficulty)
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO GENERATION
    # ══════════════════════════════════════════════════════════════════════════
    
    def _generate_video(
        self,
        first_image: Image.Image,
        final_image: Image.Image,
        task_id: str,
        objects: List[Dict[str, Any]],
        occluder_x_start: float
    ) -> Optional[str]:
        """Generate ground truth video showing occluder moving from left to right."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        # Create animation frames
        frames = self._create_occluder_animation_frames(objects, occluder_x_start)
        
        result = self.video_generator.create_video_from_frames(
            frames,
            video_path
        )
        
        return str(result) if result else None
    
    def _create_occluder_animation_frames(
        self,
        objects: List[Dict[str, Any]],
        occluder_x_start: float,
        hold_frames: int = 5,
        transition_frames: int = 25
    ) -> List[Image.Image]:
        """Create animation frames where occluder moves from left to right."""
        frames = []
        canvas_w, canvas_h = self.canvas_size
        occluder_width = 50
        
        # Hold initial position
        first_frame = self._render_frame_with_occluder(objects, occluder_x_start)
        for _ in range(hold_frames):
            frames.append(first_frame)
        
        # Create transition frames
        occluder_x_end = canvas_w + occluder_width  # Move completely out of frame
        
        for i in range(transition_frames):
            progress = i / (transition_frames - 1) if transition_frames > 1 else 1.0
            current_x = occluder_x_start + (occluder_x_end - occluder_x_start) * progress
            
            frame = self._render_frame_with_occluder(objects, current_x)
            frames.append(frame)
        
        # Hold final position (no occluder)
        final_frame = self._render_frame_with_occluder(objects, canvas_w + occluder_width)
        for _ in range(hold_frames):
            frames.append(final_frame)
        
        return frames
    
    def _render_frame_with_occluder(
        self,
        objects: List[Dict[str, Any]],
        occluder_x: float
    ) -> Image.Image:
        """Render a single frame with occluder at specified x position."""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required for rendering")
        
        temp_path = Path(tempfile.gettempdir()) / f"temp_frame_{random.randint(0, 1000000)}.png"
        
        fig, ax = plt.subplots(1, 1, figsize=(self.canvas_size[0]/self.renderer.dpi, 
                                               self.canvas_size[1]/self.renderer.dpi), 
                              dpi=self.renderer.dpi)
        
        ax.set_xlim(0, self.canvas_size[0])
        ax.set_ylim(0, self.canvas_size[1])
        ax.set_aspect('equal')
        ax.axis('off')
        ax.invert_yaxis()
        
        # Draw objects
        for obj in objects:
            color = self.renderer.COLOR_MAP.get(obj["color"], "#000000")
            x = obj["x"]
            y = obj["y"]
            size = obj["size"]
            shape = obj["shape"]
            self.renderer._draw_object(ax, x, y, size, shape, color)
        
        # Draw occluder if it's still in frame
        if occluder_x < self.canvas_size[0] + self.renderer.occluder_width:
            edge_margin = 1
            occluder_x_adjusted = occluder_x + edge_margin
            occluder_y = edge_margin
            occluder_height = self.canvas_size[1] - 2 * edge_margin
            
            # Only draw if occluder is visible
            if occluder_x_adjusted + self.renderer.occluder_width > 0:
                visible_width = min(self.renderer.occluder_width, 
                                  self.canvas_size[0] - occluder_x_adjusted)
                if visible_width > 0:
                    occluder = Rectangle((occluder_x_adjusted, occluder_y), 
                                       visible_width, occluder_height,
                                       facecolor="#606060", edgecolor="#303030", 
                                       linewidth=2, alpha=1.0, 
                                       joinstyle='miter', capstyle='butt')
                    ax.add_patch(occluder)
        
        plt.tight_layout(pad=0)
        plt.savefig(temp_path, dpi=self.renderer.dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close(fig)
        
        # Load and return image
        image = Image.open(temp_path).convert('RGB')
        temp_path.unlink()  # Clean up temp file
        return image
