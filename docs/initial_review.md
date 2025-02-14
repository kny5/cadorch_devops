# Initial Assessment  

## Resources  
- [CADOrchestrator GitLab Repository](https://gitlab.com/gitbuilding/cadorchestrator)  
- [Nimble Assembly Documentation](https://wakoma.github.io/nimble/assembly-docs/)  
- [Nimble Generate Documentation](https://github.com/Wakoma/nimble/blob/master/generate.md)  

## Key Issues  

### 1. Failure to Generate Docker Images for Development Environments  

I encountered difficulties in producing Docker images to set up the development environments for each repository due to the following issues:  

#### a) Scattered Operational and Replication Details 

Key operational details are inconsistently distributed across the repositories. For example, the **CADOrchestrator** repository is not directly operable. Instead, the **cadorchestrator-example** repository must be used for testing. A Docker image building requires a `.yml` configuration file, the file specification is unclear.

By auditing the network API navigator request we can get an idea of the following, a JSON file with, name, nameplate, and configuration.

WIP

**Recommendation:** Include an example configuration file within the **CADOrchestrator** source repository would facilitate sandboxed testing. 

#### b) Inconsistencies Between Example repository and Nimble-CADOrchestration repository.

The **CADOrchestrator example** repository explicitly includes a `.yml` configuration file, whereas **Nimble-CADOrchestration repository** relies on a hardcoded configuration Python script that generates this file.  

**Recommendation:** A note has been added by the developers to highlight the need for future modifications to align these approaches. Documentation with the specification of the Python objects must be added.

#### c) Hardcoded Server Ports  

The server defaults to port **8000**, with no configuration option to modify it. The `--production` flag determines the server’s binding:  
- `0.0.0.0` (for external access)  
- `127.0.0.1` (for local access)

**Recommendation:** For best development practices, this option should be configurable to support encapsulated environments such as containers or virtual machines. This is particularly important when using **Xorg** or a framebuffer for graphical operations, as it would enhance debugging capabilities.  

#### d) Silent Bugs and Errors  

Issues related to **OpenCASCADE, VRT,** or other OpenSCAD backend components are difficult to diagnose when the server is running.  

**Recommendation:** Implement better `stdout` error handling to facilitate debugging, detect broken dependencies, and improve maintainability in containerized environments.  

#### e) Dependency Management Challenges  

A **CADOrchestrator** instance is embedded within the **Nimble cadorchestrator** repository, creating redundancy and complicating maintenance. This duplication makes the system more error-prone, as **CADOrchestrator** package has its own repository. 

**Recommendation:** Streamline dependency management to avoid unnecessary redundancy.

### 2. Dockerfiles  

#### cadorch-Example Repository stdout:

[![asciicast](https://asciinema.org/a/mbBiRYmNYu29LVuD9oKhF3Jr1.svg)](https://asciinema.org/a/mbBiRYmNYu29LVuD9oKhF3Jr1)


#### cadorch-Nimble Repository stdout:  

[![asciicast](https://asciinema.org/a/UI23nhtITpgbRM2fUPYmzTylx.svg)](https://asciinema.org/a/UI23nhtITpgbRM2fUPYmzTylx)

### 3. Running CADORCHESTRATOR inside Docker containers with XVFB  

**Command:** For running server at 0.0.0.0:8000, Accessible for Docker container operation.

`xvfb-run -a --server-args="-screen 0 1024x768x24" cadorchestrator serve --production`

**Command:** for headless (without web server UI) CADorchestrator generation.

`xvfb-run -a --server-args="-screen 0 1024x768x24" cadorchestrator --headless generate '{"device-ids": ["NUC10i5FNH", "Raspberry_Pi_4B", "Raspberry_Pi_4B"]}'`

## Dockerfile for Nimble Repository:

WIP
