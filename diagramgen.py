"""
Generate detailed UML diagrams for GameApp with straight, blocky arrows.

This script creates UML class and package diagrams with customized styling
and enhanced readability.
"""
import os
import subprocess
import re
import sys
from typing import List, Dict


# Configuration
CONFIG = {
    "project_name": "GameApp",
    "source_dir": "app/",
    "output_dir": "docs/uml",
    "ignore_dirs": ["tests", "venv"],
    "dpi": 300,
    "font": "Arial",
    "font_size": 10,
    "filter_init_imports": True,
}


def create_output_directory(output_dir: str) -> None:
    """Create the output directory if it doesn't exist."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory: {output_dir}")
    except PermissionError:
        sys.exit(f"Error: No permission to create directory {output_dir}")


def generate_dot_files(config: Dict) -> None:
    """Generate DOT files using pyreverse with detailed settings."""
    ignore_param = f"--ignore={','.join(config['ignore_dirs'])}" if config['ignore_dirs'] else ""

    cmd = [
        "pyreverse",
        "-ASmy",           # Show all classes
        "-k",              # Keep consistency between modules
        "--colorized",     # Use colors
        ignore_param,
        "-o", "dot",       # Generate dot files
        "-p", config["project_name"],
        "--output-directory", config["output_dir"],
        config["source_dir"]
    ]

    # Filter out empty elements
    cmd = [item for item in cmd if item]

    try:
        print("Generating DOT files...")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        sys.exit("Error: Failed to generate DOT files with pyreverse")
    except FileNotFoundError:
        sys.exit("Error: pyreverse command not found. Is pylint installed?")


def modify_dot_files(config: Dict) -> None:
    """Enhance DOT files with custom styling and filter __init__.py imports."""
    dot_files = [
        f"{config['output_dir']}/classes_{config['project_name']}.dot",
        f"{config['output_dir']}/packages_{config['project_name']}.dot"
    ]

    print("Modifying DOT files with custom styling...")
    for dot_file in dot_files:
        if not os.path.exists(dot_file):
            print(f"Warning: File {dot_file} not found")
            continue

        try:
            with open(dot_file, 'r') as f:
                content = f.read()

            # Add graph styling for better readability and hide text outside nodes
            styling = (
                f'\\1\n'
                f'  splines=ortho;\n'
                f'  edge [dir="forward", labelfloat=false, label=""];\n'  # Hide edge labels
                f'  node [shape=record, fontname={config["font"]}, fontsize={config["font_size"]}];\n'
                f'  graph [label=""];\n'  # Remove graph label
            )
            modified = re.sub(r'(digraph ".*?" {)', styling, content)

            # Enhance method display with parameter information
            modified = re.sub(r'\\l', r'\\l\n', modified)

            # Remove edge labels specifically
            modified = re.sub(r'\[arrowhead="[^"]*", arrowtail="[^"]*", label="[^"]*"\]',
                              r'[arrowhead="open", arrowtail="none"]', modified)

            # Filter out direct imports from app.__init__.py in packages diagram
            if "packages" in dot_file and config.get("filter_init_imports", True):
                # Remove edges from modules to the base app package (likely from __init__.py)
                modified = re.sub(r'"([^"]+)" -> "app" \[arrowhead="open", arrowtail="none"\];(\r?\n)', '', modified)

            # Clean up any double newlines resulting from removals
            modified = re.sub(r'\n\s*\n', '\n\n', modified)

            with open(dot_file, 'w') as f:
                f.write(modified)

        except Exception as e:
            print(f"Warning: Could not modify {dot_file}: {str(e)}")


def convert_to_png(config: Dict) -> None:
    """Convert DOT files to PNG with high resolution."""
    dot_files = [
        f"{config['output_dir']}/classes_{config['project_name']}.dot",
        f"{config['output_dir']}/packages_{config['project_name']}.dot"
    ]

    print("Converting DOT files to PNG images...")
    for dot_file in dot_files:
        if not os.path.exists(dot_file):
            continue

        try:
            output_png = dot_file.replace(".dot", ".png")
            subprocess.run([
                "dot",
                "-Tpng",
                f"-Gdpi={config['dpi']}",
                dot_file,
                "-o", output_png
            ], check=True)
            print(f"Generated: {output_png}")
        except subprocess.CalledProcessError:
            print(f"Warning: Failed to convert {dot_file} to PNG")
        except FileNotFoundError:
            sys.exit("Error: 'dot' command not found. Is GraphViz installed?")


def main() -> None:
    """Main function to orchestrate UML diagram generation."""
    create_output_directory(CONFIG["output_dir"])
    generate_dot_files(CONFIG)
    modify_dot_files(CONFIG)
    convert_to_png(CONFIG)
    print("\nUML diagram generation complete!")


if __name__ == "__main__":
    main()