# Volume 1 — Appendix A1: Git

> **Resources for the appendix "Git: Version Control for Drone Projects"**
> **Level:** Beginner

---

## Contents

This appendix does not require additional scripts — Git is the tool itself.
Here you will find a quick reference of the commands used in the book.

```
VOLUME-1/Appendices/A1-Git/
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
git init my-drone-project

# 2. Check file status
git status

# 3. Stage changes
git add file.py              # specific file
git add .                    # all files

# 4. Save snapshot (commit)
git commit -m "description of the change"

# 5. View history
git log --oneline
```

### Working with branches
```bash
# Create and switch to new branch
git checkout -b pid-experiment

# List branches
git branch

# Return to main branch
git checkout main

# Merge branch
git merge pid-experiment
```

### Remote repository (GitHub)
```bash
# Clone course scripts repository
git clone https://github.com/DroneBooks/AutonomousDrones.git

# Download updates
git pull

# Push your own changes (if you have permissions)
git push origin main
```

### Undoing changes
```bash
# View differences before committing
git diff

# Discard changes in a file
git restore file.py

# Revert to a previous commit (without deleting history)
git revert HEAD
```

---

## Recommended Project Structure for Drones

```
my-drone-project/
├── README.md               # Project description
├── .gitignore              # Files to ignore
├── scripts/
│   ├── autonomous_flight.py
│   └── telemetry.py
├── tests/
│   └── test_waypoints.py
└── docs/
    └── configuration.md
```

### Recommended .gitignore for Python
```
__pycache__/
*.pyc
*.pyo
.venv/
venv/
*.log
*.csv
*.bag
```

---

## Book Reference

This appendix accompanies **Volume 1, Appendix A1: Git** of the book
*Autonomous Drones I: Hardware, Ardupilot and MAVLink*.

Topics covered in the appendix:
- Installing Git on Ubuntu, macOS and Windows
- Branch-based workflow for flight experiments
- Collaboration on robotics projects
- VS Code integration (GitLens)

---

**Last updated:** April 2026 | DroneBooks
