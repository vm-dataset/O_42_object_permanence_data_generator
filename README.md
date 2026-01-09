# Object Permanence Task Data Generator 🎯

A data generator for creating object permanence reasoning tasks for video model evaluation. This generator creates tasks that test whether video models understand that objects continue to exist and remain unchanged when occluded.

This task generator follows the [template-data-generator](https://github.com/vm-dataset/template-data-generator.git) format and is compatible with [VMEvalKit](https://github.com/Video-Reason/VMEvalKit.git).

Repository: [O_42_object_permanence_data_generator](https://github.com/vm-dataset/O_42_object_permanence_data_generator)

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/vm-dataset/O_42_object_permanence_data_generator.git
cd O_42_object_permanence_data_generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. Generate tasks
python3 examples/generate.py --num-samples 50
```

---

## 📁 Structure

```
object-permanence-task-data-generator/
├── core/                    # ✅ KEEP: Standard utilities
│   ├── base_generator.py   # Abstract base class
│   ├── schemas.py          # Pydantic models
│   ├── image_utils.py      # Image helpers
│   ├── video_utils.py      # Video generation
│   └── output_writer.py    # File output
├── src/                     # ⚠️ CUSTOMIZE: Your task logic
│   ├── generator.py        # Your task generator
│   ├── prompts.py          # Your prompt templates
│   └── config.py           # Your configuration
├── examples/
│   └── generate.py         # Entry point
└── data/questions/         # Generated output
```

---

## 📦 Output Format

Every generator produces:

```
data/questions/{domain}_task/{task_id}/
├── first_frame.png          # Initial state (REQUIRED)
├── final_frame.png          # Goal state (or goal.txt)
├── prompt.txt               # Instructions (REQUIRED)
└── ground_truth.mp4         # Solution video (OPTIONAL)
```

---

## 🎯 Task Description

The Object Permanence Task evaluates video generation models' ability to demonstrate **object permanence reasoning** - understanding that objects continue to exist and remain unchanged when occluded.

### Task Design

- **First Frame**: Objects fully visible, occluder (gray rectangle) on left side (not occluding)
- **Final Frame**: Occluder moved out of frame, objects remain exactly the same
- **Objects**: 1-3 colored 2D shapes (squares, circles, triangles, trapezoids)
- **Colors**: Red, green, blue, yellow, orange, purple
- **Difficulty Levels**:
  - **Easy**: 1 object
  - **Medium**: 2 objects
  - **Hard**: 3 objects

### Output Format

Each generated task includes:
- `first_frame.png`: Objects visible, occluder on left
- `final_frame.png`: Objects unchanged, occluder out of frame
- `prompt.txt`: Instructions for the video model
- `ground_truth.mp4`: Optional video showing occluder movement (if enabled)

**Single entry point:** `python3 examples/generate.py --num-samples 50`