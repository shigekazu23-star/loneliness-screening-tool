import os
import sys

# Make the backend package importable when pytest runs from the repo root.
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src", "backend"),
)
