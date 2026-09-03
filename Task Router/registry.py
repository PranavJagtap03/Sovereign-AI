"""
Loads the model registry from config/models.yaml and exposes lookup helpers.
This is the layer that makes "add a new model" a config edit, not a code change.
"""

from pathlib import Path
from typing import List, Dict
import yaml

CONFIG_PATH = Path(__file__).parent / "models.yaml"


class ModelEntry:
    def __init__(self, name: str, task_types: List[str], vram_gb: float,
                 endpoint: str, priority: int = 1):
        self.name = name
        self.task_types = task_types
        self.vram_gb = vram_gb
        self.endpoint = endpoint
        self.priority = priority

    def __repr__(self):
        return f"<ModelEntry {self.name} task_types={self.task_types} priority={self.priority}>"


class ModelRegistry:
    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self.models: List[ModelEntry] = []
        self.load()

    def load(self):
        """Read the YAML file fresh. Call this to hot-reload without restarting the service."""
        with open(self.config_path, "r") as f:
            raw = yaml.safe_load(f)

        entries = []
        for m in raw.get("models", []):
            required = {"name", "task_types", "endpoint"}
            missing = required - m.keys()
            if missing:
                raise ValueError(f"Model entry {m.get('name', '?')} missing fields: {missing}")
            entries.append(ModelEntry(
                name=m["name"],
                task_types=m["task_types"],
                vram_gb=m.get("vram_gb", 0),
                endpoint=m["endpoint"],
                priority=m.get("priority", 1),
            ))
        self.models = entries

    def candidates_for(self, task_type: str) -> List[ModelEntry]:
        """Return models capable of this task type, sorted by priority (lower = tried first)."""
        matches = [m for m in self.models if task_type in m.task_types]
        return sorted(matches, key=lambda m: m.priority)

    def all_task_types(self) -> List[str]:
        types = set()
        for m in self.models:
            types.update(m.task_types)
        return sorted(types)


if __name__ == "__main__":
    # quick manual check: python registry.py
    reg = ModelRegistry()
    for t in reg.all_task_types():
        print(t, "->", [m.name for m in reg.candidates_for(t)])
