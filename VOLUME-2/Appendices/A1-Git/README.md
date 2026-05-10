# Volume 2 — Appendix A1: Git

> **Resources for the appendix "Git: Version Control for Drone Projects"**
> **Level:** Beginner

---

## Contents

This appendix contains the Git quick reference applied to ROS2 and Python drone projects.

```
VOLUME-2/Appendices/A1-Git/
└── README.md    # This quick reference guide
```

---

## Essential Commands from the Book

### Initial setup (once only)
```bash
git config --global user.name "Your Name"
git config --global user.email "you@email.com"
```

### Basic workflow
```bash
# 1. Initialise repository
git init my-ros2-package

# 2. Check file status
git status

# 3. Stage changes
git add src/my_node.cpp
git add .                    # all files

# 4. Save snapshot (commit)
git commit -m "feat: add telemetry publisher node"

# 5. View history
git log --oneline
```

### Recommended structure for ROS2 packages
```bash
my_ros2_package/
├── README.md
├── .gitignore
├── package.xml
├── CMakeLists.txt          # (C++) or setup.py (Python)
├── src/
│   └── my_node.cpp
├── launch/
│   └── my_launch.py
└── config/
    └── parameters.yaml
```

### Recommended .gitignore for ROS2
```
build/
install/
log/
__pycache__/
*.pyc
*.egg-info/
.venv/
```

### Working with branches
```bash
# Create branch for navigation experiment
git checkout -b nav2-experiment

# List branches
git branch

# Merge when the experiment works
git checkout main
git merge nav2-experiment
```

### Remote repository (GitHub)
```bash
# Clone this course scripts repository
git clone https://github.com/DroneBooks/AutonomousDrones.git

# Download updates
git pull
```

---

## Book Reference

This appendix accompanies **Volume 2, Appendix A1: Git** of the book
*Autonomous Drones II: Robotics, Computer Vision and Embedded AI*.

Topics covered in the appendix:
- Installing Git on Ubuntu, macOS and Windows
- Branch management for ROS2 projects
- Collaboration in robotics teams
- VS Code integration (GitLens)

---

**Last updated:** April 2026 | DroneBooks
