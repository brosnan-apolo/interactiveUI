from flask import Flask, request, jsonify
import yaml

app = Flask(__name__)

LIVE_YML_TEMPLATE = {
    "kind": {
        "value": "live",
        "description": "Specifies the type of configuration file. Always 'live' for live.yml."
    },
    "title": {
        "value": "custom_project",
        "description": "The title of your project."
    },
    "defaults": {
        "life_span": {
            "value": "5d",
            "description": "Default lifespan of the job (e.g., 5 days)."
        }
    },
    "volumes": {},
    "images": {},
    "jobs": {}
}

JOB_TEMPLATE = {
    "name": {
        "value": "example_job",
        "description": "The name of the job. This must be unique."
    },
    "preset": {
        "value": "cpu-small",
        "description": "The resource preset for the job (e.g., 'cpu-small', 'gpu-large')."
    },
    "http_port": {
        "value": "8080",
        "description": "The HTTP port exposed by the job. Default is 8080."
    },
    "browse": {
        "value": True,
        "description": "Whether the job's HTTP endpoint should be browseable."
    },
    "env": {
        "value": {},
        "description": "Environment variables for the job as key-value pairs."
    },
    "volumes": {
        "value": [],
        "description": "A list of volume names linked to this job."
    }
}

VOLUME_TEMPLATE = {
    "remote": {
        "value": "storage:/project_id/data",
        "description": "The remote path to the storage location (e.g., 'storage:/project_id/data')."
    },
    "mount": {
        "value": "/data",
        "description": "The path inside the container where the volume will be mounted (e.g., '/data')."
    },
    "local": {
        "value": "data_folder",
        "description": "The local folder to be used for the volume (e.g., 'data_folder')."
    }
}

IMAGE_TEMPLATE = {
    "ref": {
        "value": "image:project_id:v1",
        "description": "The reference to the container image (e.g., 'image:project_id:v1')."
    },
    "dockerfile": {
        "value": "./Dockerfile",
        "description": "The path to the Dockerfile used to build the image."
    },
    "context": {
        "value": "./",
        "description": "The build context directory for the Docker image."
    },
    "build_preset": {
        "value": "cpu-large",
        "description": "The resource preset to use when building the Docker image."
    }
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

    live_yml = {
        key: {"value": LIVE_YML_TEMPLATE[key]["value"], "description": LIVE_YML_TEMPLATE[key]["description"]} if key in LIVE_YML_TEMPLATE else {}
        for key in LIVE_YML_TEMPLATE
    }

    if "title" in data:
        live_yml["title"] = {
            "value": data["title"],
            "description": LIVE_YML_TEMPLATE["title"]["description"]
        }

    if "defaults" in data:
        for key, value in data["defaults"].items():
            if key in live_yml["defaults"]:
                live_yml["defaults"][key] = {
                    "value": value,
                    "description": LIVE_YML_TEMPLATE["defaults"][key]["description"]
                }

    if "volumes" in data:
        live_yml["volumes"] = {
            k: {
                sub_key: {
                    "value": v.get(sub_key, VOLUME_TEMPLATE[sub_key]["value"]),
                    "description": VOLUME_TEMPLATE[sub_key]["description"]
                } for sub_key in VOLUME_TEMPLATE
            } for k, v in data["volumes"].items()
        }

    if "images" in data:
        live_yml["images"] = {
            k: {
                sub_key: {
                    "value": v.get(sub_key, IMAGE_TEMPLATE[sub_key]["value"]),
                    "description": IMAGE_TEMPLATE[sub_key]["description"]
                } for sub_key in IMAGE_TEMPLATE
            } for k, v in data["images"].items()
        }

    if "jobs" in data:
        live_yml["jobs"] = {
            k: {
                sub_key: {
                    "value": v.get(sub_key, JOB_TEMPLATE[sub_key]["value"]),
                    "description": JOB_TEMPLATE[sub_key]["description"]
                } for sub_key in JOB_TEMPLATE
            } for k, v in data["jobs"].items()
        }

    output_file = data.get('output_file', 'live.yaml')

    with open(output_file, "w") as file:
        yaml.dump(live_yml, file, default_flow_style=False)

    return jsonify({"message": f"'live.yaml' has been generated successfully.", "output_file": output_file})

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the live.yml generation API! Use /get_defaults or /generate_live_yml."})

if __name__ == "__main__":
    app.run(debug=True)
