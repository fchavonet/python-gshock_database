<img  height="50px" align="right" src="https://raw.githubusercontent.com/fchavonet/fchavonet/main/resources/images/logo-python.png" alt="Python logo">

# G-Shock Database

## 🔖 Table of contents

<details>
        <summary>
            CLICK TO ENLARGE 😇
        </summary>
        📄 <a href="#description">Description</a>
        <br>
        🎓 <a href="#objectives">Objectives</a>
        <br>
        🔨 <a href="#tech-stack">Tech stack</a>
        <br>
        📂 <a href="#files-description">Files description</a>
        <br>
        💻 <a href="#installation_and_how_to_use">Installation and how to use</a>
        <br>
        🔧 <a href="#whats-next">What's next ?</a>
        <br>
        ♥️ <a href="#thanks">Thanks</a>
        <br>
        👷 <a href="#authors">Authors</a>
</details>

## 📄 <span id="description">Description</span>

This project is an application designed to explore the world of Casio G-Shock watches. As a fan of the brand, I wanted to create a tool that gathers data about these watches and makes it easily accessible. The development started with a web scraper that retrieves detailed information from the [ShockBase](https://shockbase.org) website, one of the most comprehensive resources for G-Shock enthusiasts. The collected data is then presented through a graphical user interface that allows users to browse, search, filter information, and view photos of the products.

This project was inspired by my passion for G-Shock watches and serves as a tool for learning and exploration. All credit for the database content belongs to [ShockBase](https://shockbase.org), and the app is not intended for public distribution to avoid competing with their excellent work.

## 🎓 <span id="objectives">Objectives</span>

The aim of this project was to improve my skills in web scraping and GUI development with Python. By creating a functional tool centered around a subject I care about, I sought to gain hands-on experience with data processing, user interface design, and the integration of these components into a cohesive project.

## 🔨 <span id="tech-stack">Tech stack</span>

<p align="left">
    <img src="https://img.shields.io/badge/PYTHON-3776ab?logo=python&logoColor=white&style=for-the-badge" alt="Python badge">
    <img src="https://img.shields.io/badge/GIT-f05032?logo=git&logoColor=white&style=for-the-badge" alt="Git badge">
    <img src="https://img.shields.io/badge/GITHUB-181717?logo=github&logoColor=white&style=for-the-badge" alt="GitHub badge">
</p>

## 📂 <span id="files-description">File description</span>

| **FILE**               | **DESCRIPTION**                                       |
| :--------------------: | ----------------------------------------------------- |
| `assets`               | Contains the resources required for the repository.   |
| `shockbase_scraper.py` | Script to scrape data from the ShockBase website.     |
| `gshock_database.py`   | Main script to launch the application.                |
| `shockbase.csv`        | Local database generated from the scraping process.   |
| `requirements.txt`     | Lists the dependencies required to run the project.   |
| `.gitignore`           | Specifies files and directories to be ignored by Git. |
| `README.md`            | The readme file you are currently reading 😉.         |

## 💻 <span id="installation_and_how_to_use">Installation and how to use</span>

**Installation:**

1. Clone this repository:
    - Open your preferred Terminal.
    - Navigate to the directory where you want to clone the repository.
    - Run the following command:

```
git clone https://github.com/fchavonet/python-gshock_database.git
```

2. Open the repository you've just cloned.

3. Ensure Python is installed.

4. Create a virtual environment:

```
python3 -m venv venv
```

5. Activate the virtual environment:

- On Linux/macOS:

```
source venv/bin/activate
```

- On Windows:

```
venv\Scripts\activate
```

6. Install the required packages:

```
pip install -r requirements.txt
```

**How to use:**

1. Run the `shockbase_scraper.py` script to scrape the data:

```
./shockbase_scraper.py
```

2. Launch the application:

```
./gshock_database.py
```

<p align="center">
    <img src="./assets/images/screenshot-gshock_database.webp">
</p>

## 🔧 <span id="whats-next">What's next ?</span>

- Add a search engine.
- Implement a sorting menu to organize results by release date or other criteria.
- Add an update button in the GUI to trigger the scraping process in the background, keeping the database up-to-date.

## ♥️ <span id="thanks">Thanks</span>

- A big thank you to the [ShockBase](https://shockbase.org) website for their incredible work cataloging G-Shock watches.
- Thank you to my friends for their feedback and support during the development of this little project.

## 👷 <span id="authors">Authors</span>

**Fabien CHAVONET**
- Github: [@fchavonet](https://github.com/fchavonet)
