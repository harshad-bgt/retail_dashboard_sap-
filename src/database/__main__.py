"""
Executable entry point for: python -m src.database
"""
from src.database.star_schema_loader import load_star_schema

if __name__ == "__main__":
    load_star_schema()
