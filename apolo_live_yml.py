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
    "remote": "storage:/project_id/data",
    "mount": "/data",
    "local": "data_folder"
}

IMAGE_TEMPLATE = {
    "ref": "image:project_id:v1",
    "dockerfile": "./Dockerfile",
    "context": "./",
    "build_preset": "cpu-large"
}

@app.route('/get_defaults', methods=['GET'])
def get_defaults():
    defaults = {
        "title": "The title of your project",
        "defaults": {"life_span": "Default lifespan of the job (e.g., 5d)"},
        "volumes": {
            "description": "Define volume mappings for your project",
            "template": VOLUME_TEMPLATE
        },
        "images": {
            "description": "Specify images and their build context",
            "template": IMAGE_TEMPLATE
        },
        "jobs": {
            "description": "Configure jobs with resource presets and environment variables",
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

    live_yml = LIVE_YML_TEMPLATE.copy()
    if "title" in data:
        live_yml["title"] = data["title"]
    if "defaults" in data:
        live_yml["defaults"].update(data["defaults"])
    if "volumes" in data:
        live_yml["volumes"].update({k: VOLUME_TEMPLATE | v for k, v in data["volumes"].items()})
    if "images" in data:
        live_yml["images"].update({k: IMAGE_TEMPLATE | v for k, v in data["images"].items()})
    if "jobs" in data:
        for job_name, job_config in data["jobs"].items():
            job = JOB_TEMPLATE.copy()
            job.update(job_config)

            if "volumes" in job_config:
                job["volumes"] = [data["volumes"].get(vol_name, VOLUME_TEMPLATE) for vol_name in job_config["volumes"]]

            live_yml["jobs"][job_name] = job

    output_file = data.get('output_file', 'live.yaml')

    with open(output_file, "w") as file:
        yaml.dump(live_yml, file, default_flow_style=False)

    return jsonify({"message": f"'live.yaml' has been generated successfully.", "output_file": output_file})

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the live.yml generation API! Use /get_defaults or /generate_live_yml."})

if __name__ == "__main__":
    app.run(debug=True)
