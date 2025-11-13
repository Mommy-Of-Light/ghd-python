# 🧱 Console File Manager (Dockerized)

A portable, interactive console-based file manager that runs fully inside a Docker container — **isolated, safe, and minimal**. 

Perfect for secure file operations, learning environments, or when you need a consistent file management experience across different systems.

![Demo](https://img.shields.io/badge/Status-Ready-green) ![Docker](https://img.shields.io/badge/Docker-Required-blue) ![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)

---

## ✨ Features

| Category | Features |
|----------|----------|
| **📁 File Operations** | `ls`, `cd`, `cp`, `mv`, `rm`, `mkdir`, `touch`, `cat`, `pwd` |
| **🎯 Enhanced UX** | Tab completion for paths & commands, Command history |
| **👀 File Viewing** | File preview with paging (`preview <file>`), Directory tree view (`tree`) |
| **✏️ File Editing** | Edit files using your preferred editor (`edit <file>`) |
| **🔍 Search** | Find files by pattern (`search *.py`) |
| **🛡️ Security** | Sandbox isolation via Docker, Confirmation prompts for destructive operations |
| **🐳 Portability** | Runs anywhere Docker runs, Consistent environment across platforms |

---

## 📂 Project Structure

```
console-file-manager/
├── Dockerfile
├── docker-compose.yml
├── main.py
├── README.md
└── sandbox/
├── example.txt
├── notes/
│ └── todo.txt
└── test/
└── demo.py
```

---

## 🚀 Getting Started

### 🐳 Build the Docker image

#### Run from inside the `console-file-manager` folder:

```bash
docker build -t console-file-manager:latest .
```

#### ▶️ Run using launch script
##### On Linux / macOS

Make the script executable

```bash
chmod +x run.sh
```

Then use one of the 3 way to launch in the main folder

```bash
./run.sh
sh run.sh
bash run.sh
```

##### On Windows PowerShell

```powershell
docker run --rm -it -v ${PWD}\sandbox:/workspace/sandbox console-file-manager:latest
```

#### ▶️ Run using Docker Compose - (recomanded)
```bash
docker-compose run --rm fm
```

#### To stop:
```bash
docker-compose down
```

#### 🧭 Inside the File Manager
Once running, you’ll see a prompt like:

```rust
Console File Manager - type 'help' for commands.
fm>
Example commands:
Command	Description
ls -l	List files in the current directory
cd notes	Change directory
pwd	Show current path
cat example.txt	Print a file’s contents
preview example.txt	View file with paging
edit example.txt	Edit file using $EDITOR (nano/notepad)
mkdir new_folder	Create a new directory
rm example.txt	Delete a file (asks for confirmation)
tree	Show a directory tree
search *.py	Find files by pattern
exit	Quit
```

### ⚙️ Configuration
The container’s working directory is /workspace.

Files outside /workspace are not visible to the container — this keeps it sandboxed.

The default editor is nano (Linux/macOS) or notepad (Windows).

To change editor inside the container:

```bash
export EDITOR=vim
```
or set it permanently in your Dockerfile.

🔒 Optional Enhancements
Ephemeral Sandbox
You can change the docker run command to mount a temporary folder:

```bash
docker run --rm -it -v $(mktemp -d):/workspace console-file-manager:latest
``` 
This gives you a clean environment every time — everything is deleted on exit.

Run as your host user (Linux only)
Preserve file ownership:

```bash
docker run --rm -it -u $(id -u):$(id -g) -v "$(pwd)/sandbox":/workspace console-file-manager:latest
```

🧹 Clean Up
Stop the container:
```python
Ctrl + D or exit
```

Remove the image:

```bash
docker rmi console-file-manager:latest
```

Remove all stopped containers:

```bash
docker container prune
```

🪄 Summary

Action	Command

Build the image	docker build -t console-file-manager:latest .

Run in sandbox	docker run --rm -it -v "$(pwd)/sandbox":/workspace console-file-manager:latest

Run with compose	docker-compose up --build

Exit	exit or Ctrl + D

Enjoy your sandboxed, portable file manager inside Docker 🐳
