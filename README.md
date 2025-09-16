# Vadana SMS Prank Tool

<div align="center">
  <table>
    <tr>
      <td><img src="https://raw.githubusercontent.com/Zudiaq/Vadana-Prank-Tool/main/menu.jpg" alt="Menu Selection" width="350"></td>
      <td><img src="https://raw.githubusercontent.com/Zudiaq/Vadana-Prank-Tool/main/prog.jpg" alt="Progress View" width="350"></td>
    </tr>
  </table>
</div>

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20|%20Windows%20(WSL)-orange)

An automated tool for sending password recovery requests to the Vadana educational system of Islamic Azad University, featuring automatic CAPTCHA solving.

**⚠️ Note: This tool is intended for educational, experimental, and prank purposes only. Any malicious use or harassment of others is the sole responsibility of the user.**

</div>

---

## 🚀 Features

-   **Multi-Campus Support:** Includes a default list of various university campuses.
-   **Manual URL Entry:** Can be used for any other Vadana system by providing a custom URL.
-   **Automatic CAPTCHA Solving:** Uses Tesseract OCR to automatically read and solve security codes.
-   **Clean CLI:** Displays status using a progress bar and live logs directly in the terminal.
-   **Headless Operation:** The script runs in the background without needing a visible browser window.
-   **Packagable:** Can be compiled into a standalone executable for different architectures.

---

## ‼️ Disclaimer

The misuse of this tool for harassment, spamming, or any illegal activities is strictly prohibited. The developer assumes no responsibility for any improper use of this script. Please use it responsibly.

---

## 🛠️ Requirements

-   **Google Chrome** or **Chromium Browser** must be installed on the target system.

---

## ⚙️ Installation and Usage

There are two primary ways to use this tool: running a pre-compiled release or running from the source code.

### Method 1: Run from a Pre-compiled Release (Recommended for Users)

This is the easiest way to get started. No need to install Python or any dependencies.

#### **On NetHunter / ARM-based Linux (e.g., Android Phone):**

1.  Navigate to the [Releases](https://github.com/Zudiaq/Vadana-Prank-Tool/releases) page.
2.  Download the `vada_bomber_ARM` asset.
3.  Transfer the file to your NetHunter environment.
4.  Open a terminal, make the file executable, and run it:
    ```bash
    chmod +x vada_bomber_arm
    ./vada_bomber_arm
    ```

#### **On WSL / x86-based Linux (e.g., PC/Laptop):**

1.  Navigate to the [Releases](https://github.com/Zudiaq/Vadana-Prank-Tool/releases) page.
2.  Download the `vada_bomber_x86_64` asset.
3.  Open a terminal in the download location, make the file executable, and run it:
    ```bash
    chmod +x vada_bomber_x86_64
    ./vada_bomber_x86_64
    ```

---

### Method 2: Run from Source Code (For Developers)

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Zudiaq/Vadana-Prank-Tool.git](https://github.com/Zudiaq/Vadana-Prank-Tool.git)
    cd Vadana-Prank-Tool
    ```

2.  **Install system dependencies (on Debian/Ubuntu/NetHunter):**
    ```bash
    sudo apt update
    sudo apt install -y python3-pip tesseract-ocr chromium-driver chromium-browser
    ```

3.  **Install Python libraries:**
    ```bash
    pip3 install -r requirements.txt
    ```

4.  **Run the script:**
    ```bash
    python3 script_name.py
    ```

---

## 🔧 How to Build

If you want to build the executable yourself, use `PyInstaller`.

1.  **Install PyInstaller:**
    ```bash
    pip3 install pyinstaller
    ```

2.  **Build the executable (on Linux):**
    Ensure all system dependencies are installed. Then, run the following command:
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
