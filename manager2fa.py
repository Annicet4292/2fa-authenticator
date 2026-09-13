import pyotp
import json
import os
import getpass
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "accounts.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

VERSION = "3.0.0"

# ANSI Color Codes
G = '\033[92m'  # Green
C = '\033[96m'  # Cyan
Y = '\033[93m'  # Yellow
R = '\033[91m'  # Red
B = '\033[1m'   # Bold
W = '\033[0m'   # Reset / White

class AuthenticatorManager:
    def __init__(self):
        self.banner = f"""{C}{B}
╔══════════════════════════════════════════════════════════════╗
║                     MARKETPLACESS STOTTE                     ║
╚══════════════════════════════════════════════════════════════╝{W}
{Y}================================================================{W}
{B}                 Professional 2FA Authenticator                 {W}
{G}Sponsored by: Marketplacess Stotte{W}
{C}Développeur : Annicet Mobile{W}
{Y}Version     : {VERSION} | Cyber Terminal Edition{W}
{Y}================================================================{W}"""

    def setup_screen(self):
        print("\033[2J\033[1;1H", end="")
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_banner(self):
        self.setup_screen()
        print(self.banner)

    def prompt_secret(self, prompt_text):
        try:
            return getpass.getpass(prompt_text).strip()
        except Exception:
            return input(prompt_text).strip()

    def get_pin(self):
        if not os.path.exists(CONFIG_FILE):
            self.print_banner()
            print(f"\n{Y}[SETUP] Create Master PIN{W}")
            pin = self.prompt_secret("Enter new PIN: ")
            confirm_pin = self.prompt_secret("Confirm new PIN: ")
            if pin and pin == confirm_pin:
                with open(CONFIG_FILE, "w") as f:
                    json.dump({"pin": pin}, f)
                print(f"\n{G}[✔] Master PIN saved!{W}")
                input(f"\n{C}Press Enter to continue...{W}")
                return pin
            else:
                print(f"\n{R}[✘] PINs do not match!{W}")
                sys.exit()
        else:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f).get("pin")

    def verify_pin(self, correct_pin):
        user_pin = self.prompt_secret("Enter PIN: ")
        if user_pin != correct_pin:
            print(f"\n{R}[✘] Invalid PIN!{W}")
            return False
        return True

    def change_pin(self, current_pin):
        if not self.verify_pin(current_pin):
            return current_pin
        self.print_banner()
        print(f"\n{Y}--- CHANGE PIN ---{W}")
        new_pin = self.prompt_secret("Enter new PIN: ")
        confirm_pin = self.prompt_secret("Confirm new PIN: ")
        if new_pin and new_pin == confirm_pin:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"pin": new_pin}, f)
            print(f"\n{G}[✔] PIN changed successfully!{W}")
            return new_pin
        else:
            print(f"\n{R}[✘] PINs do not match!{W}")
            return current_pin

    def load_accounts(self):
        if not os.path.exists(DB_FILE):
            return {}
        with open(DB_FILE, "r") as f:
            try:
                data = json.load(f)
                updated = {}
                for k, v in data.items():
                    if isinstance(v, str):
                        parts = k.split(":", 1)
                        if len(parts) == 2:
                            service = parts[0].strip()
                            acc_name = parts[1].strip()
                        else:
                            service = "Service"
                            acc_name = k
                        updated[k] = {"service": service, "name": acc_name, "key": v}
                    else:
                        updated[k] = v
                return updated
            except Exception:
                return {}

    def save_accounts(self, accounts):
        with open(DB_FILE, "w") as f:
            json.dump(accounts, f, indent=4)

    def display_codes(self, pin):
        if not self.verify_pin(pin):
            return
        
        print(f"\n{G}[✔] PIN Correct! Displaying live codes (Press CTRL+C to stop)...{W}")
        time.sleep(1)

        try:
            while True:
                accounts = self.load_accounts()
                self.print_banner()
                if not accounts:
                    print(f"\n{Y}[!] No accounts configured.{W}")
                    break

                time_remaining = 30 - (int(time.time()) % 30)

                print(f"\n{C}┌" + "─"*15 + "┬" + "─"*30 + "┬" + "─"*14 + "┐" + f"{W}")
                print(f"{C}│ {B}{'SERVICE':<13}{W}{C} │ {B}{'CODE NAME':<28}{W}{C} │ {B}{'2FA CODE':<12}{W}{C} │{W}")
                print(f"{C}├" + "─"*15 + "┼" + "─"*30 + "┼" + "─"*14 + "┤" + f"{W}")
                
                acc_items = list(accounts.items())
                for i, (id_key, item) in enumerate(acc_items):
                    service = item.get("service", "General")[:13]
                    acc_name = item.get("name", id_key)[:28]
                    key = item.get("key", "")

                    try:
                        totp = pyotp.TOTP(key)
                        code = totp.now()
                        print(f"{C}│{W} {G}{service:<13}{W} {C}│{W} {W}{acc_name:<28}{W} {C}│{W} {Y}{B}{code:<12}{W} {C}│{W}")
                    except Exception:
                        print(f"{C}│{W} {G}{service:<13}{W} {C}│{W} {W}{acc_name:<28}{W} {C}│{W} {R}{'Invalid Key':<12}{W} {C}│{W}")
                    
                    if i < len(acc_items) - 1:
                        print(f"{C}├" + "─"*15 + "┼" + "─"*30 + "┼" + "─"*14 + "┤" + f"{W}")
                
                print(f"{C}└" + "─"*15 + "┴" + "─"*30 + "┴" + "─"*14 + "┘" + f"{W}")
                
                print(f"\n{B}Refresh in: {R}{time_remaining:02d}s{W} {Y}[CTRL+C to Exit]{W}")
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def add_account(self, pin):
        if not self.verify_pin(pin):
            return
        self.print_banner()
        print(f"\n{Y}--- ADD NEW CODE ---{W}")
        service = input(f"{C}1. Service   : {W}").strip()
        if not service:
            service = "General"

        name = input(f"{C}2. Code name : {W}").strip()
        if not name:
            print(f"{R}[✘] Code name cannot be empty!{W}")
            return

        key = input(f"{C}3. Code key  : {W}").replace(" ", "").upper().strip()
        if not key:
            print(f"{R}[✘] Code key cannot be empty!{W}")
            return

        try:
            pyotp.TOTP(key).now()
        except Exception:
            print(f"{R}[✘] Invalid key format!{W}")
            return

        accounts = self.load_accounts()
        unique_id = f"{service}:{name}"
        accounts[unique_id] = {
            "service": service,
            "name": name,
            "key": key
        }
        self.save_accounts(accounts)
        print(f"\n{G}[✔] Added successfully!{W}")

    def edit_account(self, pin):
        if not self.verify_pin(pin):
            return
        accounts = self.load_accounts()
        self.print_banner()
        if not accounts:
            print(f"\n{Y}[!] No accounts available to edit.{W}")
            return

        print(f"\n{Y}--- EDIT ACCOUNT ---{W}")
        acc_list = list(accounts.keys())
        for idx, id_key in enumerate(acc_list, start=1):
            item = accounts[id_key]
            print(f" {C}[{idx}]{W} {item.get('service')} - {item.get('name')}")
        print(f" {C}[0]{W} Cancel")

        choice = input(f"\n{Y}Select account to edit:{W} ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(acc_list):
                old_id = acc_list[idx]
                old_item = accounts[old_id]
                
                print(f"\n{C}Editing '{old_item.get('service')} - {old_item.get('name')}' (Leave blank to keep current){W}")
                new_service = input(f"1. Service [{old_item.get('service')}]: ").strip() or old_item.get('service')
                new_name = input(f"2. Code name [{old_item.get('name')}]: ").strip() or old_item.get('name')
                new_key = input(f"3. Code key: ").replace(" ", "").upper().strip() or old_item.get('key')

                try:
                    pyotp.TOTP(new_key).now()
                except Exception:
                    print(f"{R}[✘] Invalid key format! Aborted.{W}")
                    return

                del accounts[old_id]
                new_id = f"{new_service}:{new_name}"
                accounts[new_id] = {
                    "service": new_service,
                    "name": new_name,
                    "key": new_key
                }
                self.save_accounts(accounts)
                print(f"\n{G}[✔] Account updated successfully!{W}")
            elif idx == -1:
                print(f"\n{Y}[!] Cancelled.{W}")
            else:
                print(f"\n{R}[✘] Invalid selection!{W}")

    def delete_account(self, pin):
        if not self.verify_pin(pin):
            return
        accounts = self.load_accounts()
        self.print_banner()
        if not accounts:
            print(f"\n{Y}[!] No accounts available.{W}")
            return

        print(f"\n{R}--- DELETE ACCOUNT ---{W}")
        acc_list = list(accounts.keys())
        for idx, id_key in enumerate(acc_list, start=1):
            item = accounts[id_key]
            print(f" {C}[{idx}]{W} {item.get('service')} - {item.get('name')}")
        print(f" {C}[0]{W} Cancel")

        choice = input(f"\n{Y}Select account:{W} ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(acc_list):
                target_id = acc_list[idx]
                target_item = accounts[target_id]
                confirm = input(f"{R}Delete '{target_item.get('service')} - {target_item.get('name')}'? (y/N):{W} ").strip().lower()
                if confirm == 'y':
                    del accounts[target_id]
                    self.save_accounts(accounts)
                    print(f"\n{G}[✔] Deleted!{W}")
                else:
                    print(f"\n{Y}[!] Aborted.{W}")
            elif idx == -1:
                print(f"\n{Y}[!] Cancelled.{W}")
            else:
                print(f"\n{R}[✘] Invalid selection!{W}")

    def run(self):
        pin = self.get_pin()
        while True:
            self.print_banner()
            print(f"\n{B}MAIN MENU:{W}")
            print(f"  {C}[1]{W} {G}View Codes{W}")
            print(f"  {C}[2]{W} {Y}Add Account{W}")
            print(f"  {C}[3]{W} {C}Edit Account{W}")
            print(f"  {C}[4]{W} {R}Delete Account{W}")
            print(f"  {C}[5]{W} {B}Change PIN{W}")
            print(f"  {C}[0]{W} Exit")
            
            choice = input(f"\n{B}Select Option (0-5):{W} ").strip()
            
            if choice == "1":
                self.display_codes(pin)
            elif choice == "2":
                self.add_account(pin)
                input(f"\n{C}Press Enter to continue...{W}")
            elif choice == "3":
                self.edit_account(pin)
                input(f"\n{C}Press Enter to continue...{W}")
            elif choice == "4":
                self.delete_account(pin)
                input(f"\n{C}Press Enter to continue...{W}")
            elif choice == "5":
                pin = self.change_pin(pin)
                input(f"\n{C}Press Enter to continue...{W}")
            elif choice == "0":
                self.setup_screen()
                print(f"\n{G}Thank you for using Marketplacess Stotte Authenticator v{VERSION}!{W}\n")
                break
            else:
                input(f"\n{R}[✘] Invalid option! Press Enter...{W}")

if __name__ == "__main__":
    app = AuthenticatorManager()
    app.run()

