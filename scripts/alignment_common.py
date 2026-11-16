"""Shared helpers for the contextual-alignment review based on cf1e80d."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "cf1e80d"

def load_baseline():
    reference = (ROOT / "english-wbw-translation.json").read_bytes()
    assert reference == subprocess.check_output(["git", "show", f"{BASELINE}:english-wbw-translation.json"], cwd=ROOT)
    turkish = subprocess.check_output(["git", "show", f"{BASELINE}:turkish-wbw-translation.json"], cwd=ROOT)
    return json.loads(reference), json.loads(turkish)

def lower(text):
    return text.replace("İ", "i").replace("I", "ı").lower()

def make_parts(text, spans):
    mask = [False] * len(text)
    for start, end in spans:
        mask[start:end] = [True] * (end - start)
    parts = []
    for char, primary in zip(text, mask):
        role = "relation" if primary else "content"
        if parts and parts[-1]["role"] == role:
            parts[-1]["text"] += char
        else:
            parts.append({"text": char, "role": role})
    return parts

def render(parts, focus):
    runs = []
    for part in parts:
        primary = part["role"] == focus
        if runs and runs[-1]["primary"] == primary:
            runs[-1]["text"] += part["text"]
        else:
            runs.append({"text": part["text"], "primary": primary})
    result = []
    for part in runs:
        text = part["text"]
        if part["primary"] or not text.strip():
            result.append(text)
        else:
            match = re.fullmatch(r"(\s*)(.*?)(\s*)", text, flags=re.S)
            result.append(match[1] + "(" + match[2] + ")" + match[3])
    return "".join(result)

def flat_surface(original):
    """Reserve parentheses for alignment while retaining existing note text."""
    surface = original.replace("(", "[").replace(")", "]")
    indexes = []
    depth = 0
    for i, char in enumerate(surface):
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
        elif depth == 0:
            indexes.append(i)
    return surface, "".join(surface[i] for i in indexes), indexes

def map_span(start, end, indexes, surface):
    left, right = indexes[start], indexes[end - 1] + 1
    if left and right < len(surface) and surface[left - 1] == "[" and surface[right] == "]":
        left -= 1
        right += 1
    return left, right
