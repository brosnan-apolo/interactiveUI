from flask import Flask, request, jsonify
import yaml

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
        "description": "Specifies the remote path to the storage location in the Apolo platform (e.g., 'storage:/project_id/data')."
    },
    "mount": {
        "value": "/data",
        "description": "Defines the path inside the container where the volume will be mounted (e.g., '/data')."
    },
    "local": {
        "value": "data_folder",
        "description": "Specifies the local directory used as the volume's source for synchronization (e.g., 'data_folder')."
    }
}

IMAGE_TEMPLATE = {
    "ref": {
        "value": "image:project_id:v1",
        "description": "Specifies the reference to the container image used for the job (e.g., 'image:project_id:v1')."
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

def validate_input(data):
    errors = []

    if not data.get("title"):
        errors.append("The 'title' field is required and specifies the title of your workflow.")

    if "defaults" in data:
        if not isinstance(data["defaults"], dict):
            errors.append("'defaults' must be a dictionary containing workflow-wide settings.")

    if "jobs" not in data or not isinstance(data["jobs"], dict):
        errors.append("At least one 'job' is required and must be a dictionary.")
    else:
        for job_name, job in data["jobs"].items():
            if "preset" not in job:
                errors.append(f"Job '{job_name}' is missing the 'preset' field, which specifies the compute resource preset.")
            if "http_port" in job:
                try:
                    port = int(job["http_port"])
                    if port < 1 or port > 65535:
                        errors.append(f"Job '{job_name}' has an invalid 'http_port': {port}. Must be between 1 and 65535.")
                except ValueError:
                    errors.append(f"Job '{job_name}' has an invalid 'http_port': must be an integer.")

    if "volumes" in data:
        if not isinstance(data["volumes"], dict):
            errors.append("'volumes' must be a dictionary defining volume configurations.")
        else:
            for volume_name, volume in data["volumes"].items():
                for field in ["remote", "mount", "local"]:
                    if field not in volume:
                        errors.append(f"Volume '{volume_name}' is missing the '{field}' field, which defines its {VOLUME_TEMPLATE[field]['description'].lower()}.")

    if "images" in data:
        if not isinstance(data["images"], dict):
            errors.append("'images' must be a dictionary specifying image build configurations.")

    return errors

@app.route('/get_defaults', methods=['GET'])
def get_defaults():
    defaults = {
        "title": "The title of your project",
        "defaults": {"life_span": "Specifies the default lifespan of the workflow (e.g., '5d')."},
        "volumes": {
            "description": "Define volume mappings for your project.",
            "template": VOLUME_TEMPLATE
        },
        "images": {
            "description": "Specify images and their build context.",
            "template": IMAGE_TEMPLATE
        },
        "jobs": {
            "description": "Configure jobs with resource presets and environment variables.",
            "template": JOB_TEMPLATE
        },
        "expandable_tabs": {
            "data_dependency": "Do you have any data this job should rely on?",
            "build_first": "Should your job be built first?"
        }
    }
    return jsonify(defaults)

@app.route('/generate_live_yml', methods=['POST'])
def generate_live_yml():
    data = request.json

    errors = validate_input(data)
    if errors:
        return jsonify({"errors": errors}), 400

    live_yml = LIVE_YML_TEMPLATE.copy()
    if "title" in data:
        live_yml["title"] = data["title"]
    if "defaults" in data:
        live_yml["defaults"].update(data["defaults"])
    if "volumes" in data:
        live_yml["volumes"].update(data["volumes"])
    if "images" in data:
        live_yml["images"].update(data["images"])
    if "jobs" in data:
        live_yml["jobs"].update(data["jobs"])

    output_file = data.get('output_file', 'live.yaml')

    with open(output_file, "w") as file:
        yaml.dump(live_yml, file, default_flow_style=False)

    return jsonify({"message": f"'live.yaml' has been generated successfully.", "output_file": output_file})

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the live.yml generation API! Use /get_defaults or /generate_live_yml."})

if __name__ == "__main__":
    app.run(debug=True)
