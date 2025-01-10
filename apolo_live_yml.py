from flask import Flask, request, jsonify
import yaml
import subprocess

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

DOCKERFILE_TEMPLATE = """\
FROM neuromation/python:{python_version}
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
"""

def check_apolo_installed():
    try:
        subprocess.run(["apolo", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error checking Apolo CLI: {e}")
        return False

def get_apolo_presets():
    try:
        result = subprocess.run(["apolo", "resources", "presets"], check=True, stdout=subprocess.PIPE, text=True)
        presets = result.stdout.splitlines()
        return presets
    except subprocess.CalledProcessError as e:
        print(f"Error fetching resource presets: {e}")
        return []

@app.route('/generate_live_yml', methods=['POST'])
def generate_live_yml():
    if not check_apolo_installed():
        return jsonify({"error": "Apolo CLI is not installed. Please install it to proceed."}), 400

    presets = get_apolo_presets()
    if not presets:
        return jsonify({"error": "Failed to fetch presets from Apolo CLI."}), 500

    data = request.json
    preset = data.get('preset', 'cpu-small')
    if preset not in presets:
        return jsonify({"error": f"Invalid preset. Available presets are: {presets}"}), 400

    output_file = data.get('output_file', 'live.yml')

    live_yml = LIVE_YML_TEMPLATE.copy()
    live_yml["jobs"]["app_job"]["preset"] = preset

    with open(output_file, "w") as file:
        yaml.dump(live_yml, file, default_flow_style=False)

    return jsonify({"message": f"'live.yml' has been generated with preset '{preset}'", "output_file": output_file})

@app.route('/generate_dockerfile', methods=['POST'])
def generate_dockerfile():
    data = request.json
    python_version = data.get('python_version', '3.9')
    output_file = data.get('output_file', 'Dockerfile')

    dockerfile_content = DOCKERFILE_TEMPLATE.format(python_version=python_version)
    with open(output_file, "w") as file:
        file.write(dockerfile_content)

    return jsonify({"message": f"'Dockerfile' has been generated with Python version '{python_version}'", "output_file": output_file})

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the file generation API! Use /generate_live_yml or /generate_dockerfile."})

if __name__ == "__main__":
    app.run(debug=True)
