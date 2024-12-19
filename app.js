import React, { useState } from "react";
import { Box, Button, Typography, TextField, MenuItem, Grid } from "@mui/material";
import YAML from "yaml";

const pythonVersions = ["3.7", "3.8", "3.9", "3.10"];
const baseImages = ["neuromation/base:latest", "neuromation/base:python-3.9", "neuromation/base:python-3.10"];
const defaultDependencies = ["numpy", "pandas", "scipy"];

const App = () => {
  const [pythonVersion, setPythonVersion] = useState("");
  const [baseImage, setBaseImage] = useState("");
  const [dependencies, setDependencies] = useState([]);
  const [resources, setResources] = useState({ cpu: 1, memory: 512 });
  const [command, setCommand] = useState("");

  const generateLiveYaml = () => {
    const liveYaml = {
      resources: {
        cpu: resources.cpu,
        memory: `${resources.memory}Mi`,
      },
      env: { PYTHON_VERSION: pythonVersion },
      command: command || "python app.py",
    };
    return YAML.stringify(liveYaml);
  };

  const generateDockerfile = () => {
    const deps = dependencies.join(" ");
    return `
      FROM ${baseImage}
      RUN pip install ${deps}
      CMD ["${command || "python app.py"}"]
    `;
  };

  const handleDownload = (filename, content) => {
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
  };

  return (
    <Box p={4}>
      <Typography variant="h4" gutterBottom>
        Live.yml & Dockerfile Generator
      </Typography>
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Typography variant="h6">Python Version</Typography>
          <TextField
            select
            fullWidth
            label="Select Python Version"
            value={pythonVersion}
            onChange={(e) => setPythonVersion(e.target.value)}
          >
            {pythonVersions.map((version) => (
              <MenuItem key={version} value={version}>
                {version}
              </MenuItem>
            ))}
          </TextField>

          <Typography variant="h6" mt={4}>
            Dependencies
          </Typography>
          {defaultDependencies.map((dep) => (
            <Button
              key={dep}
              variant={dependencies.includes(dep) ? "contained" : "outlined"}
              onClick={() =>
                setDependencies((prev) =>
                  prev.includes(dep) ? prev.filter((d) => d !== dep) : [...prev, dep]
                )
              }
              sx={{ m: 0.5 }}
            >
              {dep}
            </Button>
          ))}

          <Typography variant="h6" mt={4}>
            Base Image
          </Typography>
          <TextField
            select
            fullWidth
            label="Select Base Image"
            value={baseImage}
            onChange={(e) => setBaseImage(e.target.value)}
          >
            {baseImages.map((image) => (
              <MenuItem key={image} value={image}>
                {image}
              </MenuItem>
            ))}
          </TextField>
        </Grid>

        <Grid item xs={12} md={6}>
          <Typography variant="h6">Resources</Typography>
          <TextField
            type="number"
            label="CPU Cores"
            value={resources.cpu}
            onChange={(e) => setResources({ ...resources, cpu: e.target.value })}
            fullWidth
            margin="normal"
          />
          <TextField
            type="number"
            label="Memory (Mi)"
            value={resources.memory}
            onChange={(e) => setResources({ ...resources, memory: e.target.value })}
            fullWidth
            margin="normal"
          />

          <Typography variant="h6" mt={4}>
            Command
          </Typography>
          <TextField
            label="Command"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            fullWidth
            margin="normal"
          />
        </Grid>
      </Grid>

      <Box mt={4}>
        <Typography variant="h6">Generated Files</Typography>
        <Box mt={2}>
          <Typography variant="subtitle1">Live.yml:</Typography>
          <pre>{generateLiveYaml()}</pre>
        </Box>
        <Box mt={2}>
          <Typography variant="subtitle1">Dockerfile:</Typography>
          <pre>{generateDockerfile()}</pre>
        </Box>
      </Box>

      <Box mt={4}>
        <Button
          variant="contained"
          onClick={() => handleDownload("live.yml", generateLiveYaml())}
          sx={{ mr: 2 }}
        >
          Download live.yml
        </Button>
        <Button
          variant="contained"
          onClick={() => handleDownload("Dockerfile", generateDockerfile())}
        >
          Download Dockerfile
        </Button>
      </Box>
    </Box>
  );
};

export default App;
