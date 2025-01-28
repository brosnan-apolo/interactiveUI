from flask import Flask, request, jsonify, render_template, send_file
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

VOLUME_TEMPLATE = {
    "remote": {
        "value": "storage:/project_id/data",
        "description": "Specifies the remote path to the storage location in the Apolo platform."
    },
    "mount": {
        "value": "/data",
        "description": "Defines the path inside the container where the volume will be mounted."
    },
    "local": {
        "value": "data_folder",
        "description": "Specifies the local directory used as the volume's source for synchronization."
    }
}

IMAGE_TEMPLATE = {
    "ref": {
        "value": "image:project_id:v1",
        "description": "Specifies the reference to the container image used for the job."
    },
    "dockerfile": {
        "value": "./Dockerfile",
        "description": "Path to the Dockerfile used to build the image."
    },
    "context": {
        "value": "./",
        "description": "Defines the build context directory for the Docker image."
    },
    "build_preset": {
        "value": "cpu-large",
        "description": "Specifies the resource preset for building the Docker image."
    }
}

JOB_TEMPLATE = {
    "name": "example_job",
    "preset": "cpu-small",
    "http_port": "8080",
    "browse": True,
    "env": {},
    "volumes": []
}

@app.route('/')
def index():
    """
    Serves the main HTML page.
    """
    return render_template('index.html')


@app.route('/get_defaults', methods=['GET'])
def get_defaults():
    """
    Provides default templates for live.yml.
    """
    defaults = {
        "title": "The title of your project",
        "defaults": {"life_span": "Specifies the lifespan of the workflow (e.g., '5d')."},
        "volumes": {"template": VOLUME_TEMPLATE},
        "images": {"template": IMAGE_TEMPLATE},
        "jobs": {"template": JOB_TEMPLATE}
    }

    html_response = "<div>"
    for key, value in defaults.items():
        html_response += f"""
        <details>
          <summary><strong>{key.capitalize()}</strong></summary>
          <pre>{yaml.dump(value, default_flow_style=False)}</pre>
        </details>
        """
    html_response += "</div>"

    return html_response


@app.route('/generate_live_yml', methods=['POST'])
def generate_live_yml():
    """
    Generates a live.yml file based on user input.
    """
    data = request.json
    errors = []

    if not data.get("title"):
        errors.append("The 'title' field is required.")
    
    if "jobs" not in data or not isinstance(data["jobs"], dict):
        errors.append("At least one 'job' is required and must be a dictionary.")
    
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

    return jsonify({"message": "live.yaml has been generated successfully.", "output_file": output_file})


@app.route('/download_live_yml', methods=['GET'])
def download_live_yml():
    """
    Downloads the generated live.yml file.
    """
    file_path = "live.yaml"
    if not os.path.exists(file_path):
        return jsonify({"error": "live.yaml not found. Please generate it first."}), 404
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
    
