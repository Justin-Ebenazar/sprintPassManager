# 🔐 Jortress Vault

**Jortress Vault is a secure, local-only desktop password manager built with Python and Flask, utilizing Webview for a clean, cross-platform graphical user interface (GUI).**

The primary goal of this application is to provide users with a private and reliable way to store their credentials, keeping all sensitive data confined to their local machine.

## ✨ Features

* **Local Storage:** All user data and passwords are encrypted and stored locally.
* **Secure Authentication:** Passwords are never stored in plaintext (hashing is used).
* **Intuitive GUI:** Built using a modern Flask front-end rendered via Python Webview.
* **Standalone Executable:** Available as a single, bundled application for easy deployment on Windows.

## 🚀 Installation (For Users)

This project has been bundled into a Windows installer for quick deployment.

1.  **Download the Installer:** Navigate to the dedicated `windowsFile` branch of this repository.
2.  **Locate the Executable:** Download the latest installer file (e.g., `JortressVault_Setup.exe`).
3.  **Run and Install:** Execute the installer and follow the on-screen prompts.

## 💻 Development Setup (For Contributors)

If you wish to run the application from the source code, please follow these steps.

### Prerequisites

You need **Python 3.8+** installed on your system.

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/Justin-Ebenazar/sprintPassManager.git](https://github.com/Justin-Ebenazar/sprintPassManager.git)
    cd sprintPassManager
    ```

2.  **Run the Application:**
    ```bash
    python app.py
    ```
    The Webview application window should launch automatically.

## ⚙️ Technology Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend/Logic** | Python | Core application logic and data handling. |
| **Web Framework** | Flask | Serves the HTML/CSS/JS frontend interface. |
| **GUI/Desktop Wrapper** | Python Webview | Embeds the Flask application into a native desktop window. |
| **Database** | SQLite | Local, file-based data persistence. |

## 📂 Project Structure

This repository is divided into two primary branches:

* **`main` Branch:** Contains the complete, runnable Python **source code** and configuration files.
* **`windowsFile` Branch:** Contains the latest pre-built **Windows executable** and installer files.

## 🤝 Contribution and Feedback

I welcome any feedback, bug reports, or feature suggestions!

Please feel free to open an **Issue** or submit a **Pull Request** if you have improvements.

---

### Author

**Justin Ebenazar**
