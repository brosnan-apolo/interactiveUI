import typer
import yaml
from typing import List

app = typer.Typer()

# Options for users
python_versions = ["3.7", "3.8", "3.9", "3.10"]
base_images = ["neuromation/base:latest", "neuromation/base:python-3.9", "neuromation/base:python-3.10"]
default_dependencies = ["numpy", "pandas", "scipy"]

# User selections
selected_python_version = ""
selected_base_image = ""
selected_dependencies = []
selected_command = "python app.py"
resources = {"cpu": 1, "memory": 512}


@app.command()
def start():
    typer.echo("\nWelcome to the Live.yml & Dockerfile Generator!")
    
    global selected_python_version
    typer.echo("\nStep 1: Select Python Version")
    selected_python_version = typer.prompt(
        f"Choose a Python version ({', '.join(python_versions)})", default="3.9"
    )
    if selected_python_version not in python_versions:
        typer.echo(f"Invalid choice. Defaulting to 3.9.")
        selected_python_version = "3.9"

    global selected_base_image
    typer.echo("\nStep 2: Select a Base Image")
    selected_base_image = typer.prompt(
        f"Choose a base image ({', '.join(base_images)})", default="neuromation/base:python-3.9"
    )
    if selected_base_image not in base_images:
        typer.echo(f"Invalid choice. Defaulting to neuromation/base:python-3.9.")
        selected_base_image = "neuromation/base:python-3.9"

    global selected_dependencies
    typer.echo("\nStep 3: Add Dependencies")
    typer.echo(f"Available dependencies: {', '.join(default_dependencies)}")
    selected_dependencies = typer.prompt("Enter dependencies separated by commas", default="numpy,pandas").split(",")
    selected_dependencies = [dep.strip() for dep in selected_dependencies]

    global resources
    typer.echo("\nStep 4: Configure Resources")
    resources["cpu"] = typer.prompt("Enter CPU cores", default=1)
    resources["memory"] = typer.prompt("Enter memory (Mi)", default=512)

    global selected_command
    typer.echo("\nStep 5: Define Command")
    selected_command = typer.prompt("Enter the command to run your application", default="python app.py")

    generate_files()


def generate_files():
    live_yml = {
        "resources": {"cpu": int(resources["cpu"]), "memory": f"{resources['memory']}Mi"},
        "env": {"PYTHON_VERSION": selected_python_version},
        "command": selected_command,
    }

    with open("live.yml", "w") as f:
        yaml.dump(live_yml, f)
    
    dependencies_str = " ".join(selected_dependencies)
    dockerfile_content = f"""
FROM {selected_base_image}
RUN pip install {dependencies_str}
CMD ["{selected_command}"]
    """
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content.strip())

    typer.echo("\nFiles generated successfully!")
    typer.echo("- live.yml")
    typer.echo("- Dockerfile")


if __name__ == "__main__":
    app()
