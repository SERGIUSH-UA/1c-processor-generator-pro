#!/usr/bin/env python3
"""Feature lookup tool for 1C Processor Generator.

Reads feature_registry.json and provides human-readable output for LLM consumption.

Usage:
    python feature_lookup.py                    # List all categories
    python feature_lookup.py elements           # List items in category
    python feature_lookup.py events             # List events
    python feature_lookup.py types              # List data types
    python feature_lookup.py --search table     # Search by keyword
    python feature_lookup.py --name InputField  # Get details for feature
"""

import json
import sys
from pathlib import Path


def load_registry():
    """Load feature registry from references directory."""
    script_dir = Path(__file__).parent
    registry_path = script_dir / ".." / "references" / "feature-registry.json"
    if not registry_path.exists():
        print(f"Error: Registry not found at {registry_path.resolve()}")
        sys.exit(1)
    with open(registry_path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_categories(registry):
    """List all available categories."""
    print(f"1C Processor Generator - Feature Registry v{registry.get('version', '?')}")
    print("=" * 60)
    for cat_name, cat_data in registry.get("categories", {}).items():
        desc = cat_data.get("description", "")
        count = cat_data.get("count", len(cat_data.get("items", [])))
        print(f"\n  {cat_name} ({count} items)")
        print(f"    {desc}")
    print(f"\nUsage: python {Path(__file__).name} <category>")
    print(f"       python {Path(__file__).name} --search <keyword>")
    print(f"       python {Path(__file__).name} --name <feature>")


def list_category(registry, category):
    """List all items in a category."""
    categories = registry.get("categories", {})
    if category not in categories:
        print(f"Error: Unknown category '{category}'")
        print(f"Available: {', '.join(categories.keys())}")
        sys.exit(1)

    cat_data = categories[category]
    print(f"\n{category.upper()} - {cat_data.get('description', '')}")
    print("=" * 60)

    for item in cat_data.get("items", []):
        name = item.get("name", "?")
        desc = item.get("description", "")
        since = item.get("since", "")
        since_str = f" (v{since})" if since else ""
        print(f"\n  {name}{since_str}")
        if desc:
            print(f"    {desc}")
        if item.get("docs"):
            print(f"    Docs: {item['docs']}")


def search_features(registry, keyword):
    """Search all features by keyword."""
    keyword_lower = keyword.lower()
    results = []

    for cat_name, cat_data in registry.get("categories", {}).items():
        for item in cat_data.get("items", []):
            name = item.get("name", "")
            desc = item.get("description", "")
            if keyword_lower in name.lower() or keyword_lower in desc.lower():
                results.append((cat_name, item))

    if not results:
        print(f"No features found matching '{keyword}'")
        return

    print(f"Search results for '{keyword}' ({len(results)} matches):")
    print("=" * 60)

    for cat_name, item in results:
        name = item.get("name", "?")
        desc = item.get("description", "")
        since = item.get("since", "")
        since_str = f" (v{since})" if since else ""
        print(f"\n  [{cat_name}] {name}{since_str}")
        if desc:
            print(f"    {desc}")


def get_feature(registry, name):
    """Get details for a specific feature by name."""
    for cat_name, cat_data in registry.get("categories", {}).items():
        for item in cat_data.get("items", []):
            if item.get("name", "").lower() == name.lower():
                print(f"\n{item.get('name', '?')}")
                print("=" * 40)
                print(f"  Category: {cat_name}")
                if item.get("description"):
                    print(f"  Description: {item['description']}")
                if item.get("since"):
                    print(f"  Since: v{item['since']}")
                if item.get("docs"):
                    print(f"  Docs: {item['docs']}")
                if item.get("properties"):
                    print(f"  Properties: {', '.join(item['properties'])}")
                if item.get("events"):
                    print(f"  Events: {', '.join(item['events'])}")
                if item.get("signature"):
                    print(f"  Signature: {item['signature']}")
                if item.get("values"):
                    print(f"  Values: {', '.join(str(v) for v in item['values'])}")
                return

    print(f"Feature '{name}' not found.")
    print("Try: python feature_lookup.py --search " + name)


def main():
    registry = load_registry()

    if len(sys.argv) < 2:
        list_categories(registry)
        return

    arg = sys.argv[1]

    if arg == "--search" and len(sys.argv) >= 3:
        search_features(registry, sys.argv[2])
    elif arg == "--name" and len(sys.argv) >= 3:
        get_feature(registry, sys.argv[2])
    elif arg.startswith("--"):
        print(f"Unknown option: {arg}")
        print("Usage: python feature_lookup.py [category|--search keyword|--name feature]")
    else:
        list_category(registry, arg)


if __name__ == "__main__":
    main()
