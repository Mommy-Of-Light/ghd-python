# File manager in docker

This is a sub-system linux based in a safe container working on a python script. — **isolated, safe, and minimal**

It's somthing that already exist but this is just a small project idea that i wanted to make, so if you want to try, use or inspire yourself with this, fell free to do.

![Demo](https://img.shields.io/badge/Status-Ready-green) 
![Docker](https://img.shields.io/badge/Docker-Required-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)

---

## 🚀 Features

### Commands at version 1.0

|Command|Description                                                                                                        |Use                |
|-------|-------------------------------------------------------------------------------------------------------------------|-------------------|
|ls     |List the files and directory in the current or specified directory, with -a show the hidden files and directory    |ls [-a/-l] [path]  |
|cd     |Move to the specified directory                                                                                    |cd [dir]           |
|pwd    |Print the current wworking directory                                                                               |pwd                |
|cat    |Print the content of the specified file                                                                            |cat [path]         |
|head   |Print the first 10 lines or the specified amount of the specified file                                             |head [path/file]   |

---

## 🛠️ Intallation

### Prerequisites

---

#### Operating System

Works on Linux, macOS, or Windows (Windows 10/11 with WSL2 preferred for Docker).

---

#### Installed Software if not installed

Docker → Install ([Docker-desktop](https://www.docker.com/products/docker-desktop))

WSL2 → Install ([WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)) 

Python 3.8+ → ([Python](https://www.python.org/downloads))

---

Verify installation:

```bash
docker --version
```

Docker Compose (often bundled with Docker Desktop)

Verify installation:

```bash
docker compose version
```

---

Python 3.8+ (optional but useful for local development outside Docker)

Verify installation:

```bash
python --version
pip --version
```

---

### ⚙️ Set Up

#### Launch Docker - Important

```bash
git clone [https://github.com/Mommy-Of-Light/gdh-python.git](https://github.com/Mommy-Of-Light/gdh-python.git)
cd file-manager
```

### Linux/Mac (additional steps)

```bash
chmod +x run.sh
```

---

## 💡 Usage

### Linux/Mac

Execute one of the 3

```bash
./run.sh
sh run.sh
bash run.sh
```

---

### Windows - Powershell

```powershell
.\run.ps1
```

### Windows - CMD

```powershell
.\run.bat
```

---

## ⚙️ Configuration

No configuration needed for this project

---

## 🧪 Tests

There is no test set up other than using the app for now

---

## 📁 Project structure

```text
file-manager/
├── src/
│    ├── classes/
│    │    ├── __init__.py
│    │    ├── cli.py
│    │    ├── commands.py
│    │    ├── utils.py
│    │    └── venv_manager.py
│    ├── __init__.py
│    └── main.py.py
├── .gitignore
├── dockercompose.yaml
├── Dockerfile
├── README.md
├── run.bat
├── run.ps1
└── run.sh
```

---

## 📦 Built with 

- Python
- Docker

---

## 🤝 Contributing

### 1. Fork the repository (Click the "Fork" button on the top right of the repo page)

### 2. Clone your fork
```bash
git clone git@github.com:your-username/ghd-python.git
cd ghd-python
```

### 3. Create your feature branch
```bash
git checkout -b feature/fooBar
```

### 4. Commit your changes
```bash
git commit -m "Add some fooBar"
```

### 5. Push to the branch
```bash
git push origin feature/fooBar
```

### 6. Open a Pull Request
Go to: [https://github.com/Mommy-Of-Light/ghd-python/pulls](https://github.com/Mommy-Of-Light/ghd-python/pulls) and click "New Pull Request"

---

## 📜 Licence 

This project is licensed under the MIT License

---

## 🙌 Acknowledgements

### Inspiration

A linux shell. 

### References

Went on my own.

### Contributors

No one.

## 📞 Contact

Mommy of light — no twitter at the time 

Email: empress.mommy.of.light@gmail.com

Project Link: [https://github.com/Mommy-Of-Light/ghd-python/pulls](https://github.com/Mommy-Of-Light/ghd-python/pulls)