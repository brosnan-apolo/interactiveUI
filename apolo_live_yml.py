from flask import Flask, request, jsonify
import yaml

app = Flask(__name__)

LIVE_YML_TEMPLATE = {
    "kind": "live",
    "title": "custom_project",
    "defaults": {"life_span": "5d"},
    "volumes": {
        "app_data": {
            "remote": "storage:$[[ flow.project_id ]]/app_data",
            "mount": "/app/data",
            "local": "data"
        }
    },
    "images": {
        "app_image": {
            "ref": "image:$[[ project.id ]]:v1",
            "dockerfile": "$[[ flow.workspace ]]/Dockerfile",
            "context": "$[[ flow.workspace ]]/",
            "build_preset": "cpu-large"
        }
    },
    "jobs": {
        "app_job": {
            "image": "${{ images.app_image.ref }}",
            "name": "app_job",
            "preset": "cpu-small",
            "http_port": "8080",
            "browse": True,
            "env": {},
            "volumes": ["${{ volumes.app_data.ref_rw }}"]
        }
    }
}

@app.route('/get_defaults', methods=['GET'])
def get_defaults():
    defaults = {
        "title": "The title of your project",
        "defaults": {"life_span": "Default lifespan of the job (e.g., 5d)"},
        "volumes": "Define the volume mappings for your project",
        "images": "Specify images and their build context",
        "jobs": "Configure jobs, including presets and environment variables"
    }
    return jsonify(defaults)

@app.route('/generate_live_yml', methods=['POST'])
def generate_live_yml():
    data = request.json

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

    output_file = data.get('output_file', 'live.yml')

    with open(output_file, "w") as file:
        yaml.dump(live_yml, file, default_flow_style=False)

    return jsonify({"message": f"'live.yml' has been generated successfully.", "output_file": output_file})

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the live.yml generation API! Use /get_defaults or /generate_live_yml."})

if __name__ == "__main__":
    app.run(debug=True)
