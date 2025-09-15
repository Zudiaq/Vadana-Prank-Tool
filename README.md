# Vadana SMS Prank Tool

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20|%20Windows%20(WSL)-orange)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An automated tool for sending password recovery requests to the Vadana educational system of Islamic Azad University, featuring automatic CAPTCHA solving.

**⚠️ Note: This tool is intended for educational, experimental, and prank purposes only. Any malicious use or harassment of others is the sole responsibility of the user.**

</div>

---

## ## 🚀 Features

-   **Multi-Campus Support:** Includes a default list of various university campuses.
-   **Manual URL Entry:** Can be used for any other Vadana system by providing a custom URL.
-   **Automatic CAPTCHA Solving:** Uses Tesseract OCR to automatically read and solve security codes.
-   **Clean CLI:** Displays status using a progress bar and live logs directly in the terminal.
-   **Headless Operation:** The script runs in the background without needing a visible browser window.
-   **Packagable:** Can be compiled into a standalone executable for Linux (NetHunter) and Windows (via WSL).

---

## ## ‼️ Disclaimer

The misuse of this tool for harassment, spamming, or any illegal activities is strictly prohibited. The developer assumes no responsibility for any improper use of this script. Please use it responsibly.

---

## ## 🛠️ Requirements

You will need the following tools to run this script.

#### 1. To Run from Source Code:
-   **Python 3.9+**
-   **Google Chrome** or **Chromium Browser**
-   **Tesseract OCR Engine**
-   **ChromeDriver**

#### 2. To Run the Packaged Executable (`.bin`):
-   Only **Google Chrome** or **Chromium Browser** is required.

---

## ## ⚙️ Installation and Usage

There are two methods to run this script:

### ### Method 1: Run from Source Code (Recommended for Developers)

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git)
    cd YOUR_REPOSITORY
    ```

2.  **Install system dependencies (on Debian/Ubuntu/NetHunter):**
    ```bash
    sudo apt update
    sudo apt install -y python3-pip tesseract-ocr chromium-driver chromium-browser
    ```

3.  **Install Python libraries:**
    Create a file named `requirements.txt` with the following content:
    ```txt
    selenium
    pillow
    pytesseract
    rich
    ```
    Then, install them using `pip`:
    ```bash
    pip3 install -r requirements.txt
    ```

4.  **Run the script:**
    ```bash
    python3 script_name.py
    ```

### ### Method 2: Use the Executable (For Regular Users)

1.  **Download the file:**
    Navigate to the **Releases** section of this GitHub repository and download the latest version of the executable file (`vadana_bomber`).

2.  **Transfer to the target system:**
    Move the downloaded file to your Linux system (e.g., NetHunter).

3.  **Make the file executable:**
    In your terminal, grant the file execution permissions:
    ```bash
    chmod +x vadana_bomber
    ```

4.  **Run the application:**
    ```bash
    ./vadana_bomber
    ```
After running, select the desired system from the menu, enter the student number and the number of attempts to begin the process.

---

## ## 🔧 How to Build

If you want to build the executable yourself, use `PyInstaller`.

1.  **Install PyInstaller:**
    ```bash
    pip3 install pyinstaller
    ```

2.  **Build the executable (on Linux):**
    Ensure all system dependencies (from Method 1, Step 2) are installed. Then, run the following command:
    ```bash
    pyinstaller --onefile --name vadana_bomber \
    --add-binary '/usr/bin/chromedriver:.' \
    --add-binary '/usr/bin/tesseract:.' \
    --add-data '/usr/share/tesseract-ocr/5/tessdata:tessdata' \
    script_name.py
    ```
    > **Note:** The path `/usr/share/tesseract-ocr/5/tessdata` might be different on your system. Use the command `sudo find / -name "tessdata" -type d` to find the correct path.

---

## ## 🤝 Contribution

Contributions are welcome! If you have suggestions for improving the script, please open an **Issue** or submit a **Pull Request**.
