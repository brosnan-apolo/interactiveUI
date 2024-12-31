from typing import TypeVar

import typer
import yaml

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
T = TypeVar("T")


def prompt_with_exit(message: str, default: T = None) -> T:
    user_input = typer.prompt(message, default=default)
    if isinstance(user_input, str) and user_input.strip().lower() == "exit":
        raise typer.Exit()
    return user_input


@app.command()
def start():
    typer.echo("\nWelcome to the Live.yml & Dockerfile Generator!")

    global selected_python_version
    typer.echo("\nStep 1: Select Python Version")
    selected_python_version = prompt_with_exit(
        f"Choose a Python version ({', '.join(python_versions)})",
        default="3.9"
    )
    if selected_python_version not in python_versions:
        typer.echo(f"Invalid choice. Defaulting to 3.9.")
        selected_python_version = "3.9"

    global selected_base_image
    typer.echo("\nStep 2: Select a Base Image")
    selected_base_image = prompt_with_exit(
        f"Choose a base image ({', '.join(base_images)})",
        default="neuromation/base:python-3.9"
    )
    if selected_base_image not in base_images:
        typer.echo(f"Invalid choice. Defaulting to neuromation/base:python-3.9.")
        selected_base_image = "neuromation/base:python-3.9"

    global selected_dependencies
    typer.echo("\nStep 3: Add Dependencies")
    typer.echo(f"Available dependencies: {', '.join(default_dependencies)}")
    deps_input = prompt_with_exit(
        "Enter dependencies separated by commas",
        default="numpy,pandas"
    )
    selected_dependencies = [dep.strip() for dep in deps_input.split(",")]

    global resources
    typer.echo("\nStep 4: Configure Resources")
    cpu_input = prompt_with_exit("Enter CPU cores", default=1)
    resources["cpu"] = cpu_input
    mem_input = prompt_with_exit("Enter memory (Mi)", default=512)
    resources["memory"] = mem_input

    global selected_command
    typer.echo("\nStep 5: Define Command")
    selected_command = prompt_with_exit("Enter the command to run your application", default="python app.py")

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


def main():
    try:
        app()
    except KeyboardInterrupt:
        typer.echo("\nExiting due to Keyboard Interrupt...")
        raise typer.Exit()


if __name__ == "__main__":
    main()
