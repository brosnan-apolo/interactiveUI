from flask import Flask, render_template, request, jsonify, send_file
import yaml
import os

app = Flask(__name__)

LIVE_YML_TEMPLATE = {
    "kind": "live",
    "title": "custom_project",
    "defaults": {"life_span": "5d"},
    "volumes": {},
    "images": {},
    "jobs": {}
}

JOB_TEMPLATE = {
    "name": "example_job",
    "preset": "cpu-small",
    "http_port": "8080",
    "browse": True,
    "env": {},
    "volumes": []
}

VOLUME_TEMPLATE = {
    "remote": {
        "value": "storage:/project_id/data",
        "description": "Remote path in Apolo platform."
    },
    "mount": {
        "value": "/data",
        "description": "Path inside the container where volume is mounted."
    },
    "local": {
        "value": "data_folder",
        "description": "Local directory used for synchronization."
    }
}

IMAGE_TEMPLATE = {
    "ref": {
        "value": "image:project_id:v1",
        "description": "Reference to the container image for the job."
    },
    "dockerfile": {
        "value": "./Dockerfile",
        "description": "Path to the Dockerfile for building the image."
    },
    "context": {
        "value": "./",
        "description": "Build context directory for the Docker image."
    },
    "build_preset": {
        "value": "cpu-large",
        "description": "Resource preset for building the Docker image."
    }
}


def validate_input(data):
    """
    Validates user input for live.yml generation.
    """
    errors = []

    if not data.get("title"):
        errors.append("The 'title' field is required and specifies the title of your workflow.")

    if "jobs" not in data or not isinstance(data["jobs"], dict):
        errors.append("At least one 'job' is required and must be a dictionary.")
    else:
        for job_name, job in data["jobs"].items():
            if "preset" not in job:
                errors.append(f"Job '{job_name}' is missing the 'preset' field.")
            if "http_port" in job:
                try:
                    port = int(job["http_port"])
                    if port < 1 or port > 65535:
                        errors.append(f"Job '{job_name}' has an invalid 'http_port': {port}. Must be between 1 and 65535.")
                except ValueError:
                    errors.append(f"Job '{job_name}' has an invalid 'http_port': must be an integer.")

    if "volumes" in data:
        if not isinstance(data["volumes"], dict):
            errors.append("'volumes' must be a dictionary.")

    if "images" in data:
        if not isinstance(data["images"], dict):
            errors.append("'images' must be a dictionary.")

    return errors


@app.route('/')
def index():
    """
    Serves the interactive web interface.
    """
    return render_template('index.html')


@app.route('/get_defaults', methods=['GET'])
def get_defaults():
    """
    Provides the default structure and templates for live.yml generation.
    """
    return jsonify({
        "title": "Title of your project",
        "defaults": {"life_span": "Specifies the lifespan of the workflow (e.g., '5d')."},
        "volumes": {"template": VOLUME_TEMPLATE},
        "images": {"template": IMAGE_TEMPLATE},
        "jobs": {"template": JOB_TEMPLATE}
    })


@app.route('/generate_live_yml', methods=['POST'])
def generate_live_yml():
    """
    Generates a live.yml file based on user input.
    """
    data = request.json
    errors = validate_input(data)

    if errors:
        return jsonify({"errors": errors}), 400

    live_yml = LIVE_YML_TEMPLATE.copy()
    live_yml["title"] = data.get("title", "custom_project")
    live_yml["defaults"].update(data.get("defaults", {}))
    live_yml["volumes"].update(data.get("volumes", {}))
    live_yml["images"].update(data.get("images", {}))
    live_yml["jobs"].update(data.get("jobs", {}))

    output_file = "live.yaml"
    with open(output_file, "w") as file:
        yaml.dump(live_yml, file, default_flow_style=False)

    return jsonify({"message": f"'{output_file}' has been generated successfully.", "output_file": output_file})


@app.route('/download_live_yml', methods=['GET'])
def download_live_yml():
    """
    Allows users to download the generated live.yml file.
    """
    file_path = "live.yaml"
    if not os.path.exists(file_path):
        return jsonify({"error": "live.yaml not found. Please generate it first."}), 404
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
