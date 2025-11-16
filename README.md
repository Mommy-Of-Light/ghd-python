# File manager in docker

This is a sub-system linux based in a safe container working on a python script. — **isolated, safe, and minimal**

It's somthing that already exist but this is just a small project idea that i wanted to make, so if you want to try, use or inspire yourself with this, fell free to do.

![Demo](https://img.shields.io/badge/Status-Ready-green) 
![Docker](https://img.shields.io/badge/Docker-Required-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)

---

## 🚀 Features

## Commands

<details>
    <summary>File & Directory Operations</summary>

| Command | Description                                                                       | Usage                                            |
| ------- | --------------------------------------------------------------------------------- | ------------------------------------------------ |
| ls      | List files and directories. `-a` shows hidden files, `-l` shows detailed listing. | ls [-a/-l] [path]                                |
| cd      | Change to the specified directory.                                                | cd [dir]                                         |
| pwd     | Print the current working directory.                                              | pwd                                              |
| cat     | Print the content of a file.                                                      | cat [file]                                       |
| head    | Show the first 10 lines (or specified number) of a file.                          | head [-n N] [file]                               |
| tail    | Show the last 10 lines (or specified number) of a file.                           | tail [-n N] [file]                               |
| rm      | Remove a file.                                                                    | rm [file]                                        |
| rmdir   | Remove an empty directory.                                                        | rmdir [directory]                                |
| mkdir   | Create a new directory.                                                           | mkdir [directory]                                |
| touch   | Create an empty file or update a timestamp.                                       | touch [file]                                     |
| cp      | Copy a file or directory.                                                         | cp [source] [dest]                               |
| mv      | Move or rename a file or directory.                                               | mv [source] [dest]                               |
| rename  | Rename files using patterns.                                                      | rename [options] [pattern] [replacement] [files] |
| tree    | Display files and directories as a tree.                                          | tree [path]                                      |
</details>

<details>
    <summary>Search & Information Commands</summary>

| Command | Description                                   | Usage            |
| ------- | --------------------------------------------- | ---------------- |
| search  | Search for files (system dependent).          | search [pattern] |
| info    | Show detailed documentation (GNU info pages). | info [command]   |
| man     | Show a command’s manual pages.                | man [command]    |
| help    | Show the help for all commands                | help / ?         |
</details>

<details>
    <summary>Viewing, Editing, and System Interaction</summary>

| Command | Description                | Usage          |
| ------- | -------------------------- | -------------- |
| preview | Preview file content.      | preview [file] |
| edit    | Open a file in an editor.  | edit [file]    |
| echo    | Print text to terminal.    | echo [text]    |
| clear   | Clear the terminal screen. | clear          |
| cls     | Windows version of clear.  | cls            |
| history | Show command history.      | history        |
</details>

<details>
    <summary>Cross-Platform Command Equivalents</summary>

| Unix/Linux | Windows | Description              |
| ---------- | ------- | ------------------------ |
| ls         | dir     | List directory contents. |
| rm         | del     | Delete files.            |
| cp         | copy    | Copy files.              |
| mv         | move    | Move files.              |
| rename     | ren     | Rename files.            |
</details>

<details>
    <summary>Session & Environment Commands</summary>

| Command | Description                    | Usage            |
| ------- | ------------------------------ | ---------------- |
| export  | Set environment variables.     | export VAR=value |
| exit    | Exit the shell session.        | exit             |
| quit    | Alias of exit in some systems. | quit             |
</details>
 
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

#### Clone the project
```bash
git clone https://github.com/Mommy-Of-Light/gdh-python.git
cd ghd-python
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

Working alone on this project

## 📞 Contact

Mommy of light — no twitter at the time 

Email: empress.mommy.of.light@gmail.com

Project Link: [https://github.com/Mommy-Of-Light/ghd-python/pulls](https://github.com/Mommy-Of-Light/ghd-python/pulls)