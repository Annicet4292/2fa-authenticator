import pyotp
import json
import os
import getpass
import sys

TARGET_DIR = os.path.expanduser("~/storage/shared/Annicet Mobile/Développement/Programmation/Python")
DB_FILE = os.path.join(TARGET_DIR, "accounts.json")
CONFIG_FILE = os.path.join(TARGET_DIR, "config.json")

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
 ╔══════════════════════════════════════════════════╗
 ║               MARKETPLACESS STOTTE               ║
 ╚══════════════════════════════════════════════════╝{W}
{Y}===================================================={W}
{B}         Professional 2FA Authenticator             {W}
{G}Sponsor officiel : Marketplacess Stotte{W}
{C}Développeur      : Annicet Mobile{W}
{Y}===================================================={W}"""

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_banner(self):
        self.clear_screen()
        print(self.banner)

    def get_pin(self):
        if not os.path.exists(CONFIG_FILE):
            self.print_banner()
            print(f"\n{Y}[SETUP] Create Master PIN{W}")
            pin = getpass.getpass("Enter new PIN: ").strip()
            confirm_pin = getpass.getpass("Confirm new PIN: ").strip()
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
        user_pin = getpass.getpass("Enter PIN: ").strip()
        if user_pin != correct_pin:
            print(f"{R}[✘] Invalid PIN!{W}")
            return False
        return True

    def change_pin(self, current_pin):
        if not self.verify_pin(current_pin):
            return current_pin
        self.print_banner()
        print(f"\n{Y}--- CHANGE PIN ---{W}")
        new_pin = getpass.getpass("Enter new PIN: ").strip()
        confirm_pin = getpass.getpass("Confirm new PIN: ").strip()
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
                return json.load(f)
            except Exception:
                return {}

    def save_accounts(self, accounts):
        with open(DB_FILE, "w") as f:
            json.dump(accounts, f, indent=4)

    def display_codes(self, pin):
        if not self.verify_pin(pin):
            return
        accounts = self.load_accounts()
        self.print_banner()
        if not accounts:
            print(f"\n{Y}[!] No accounts configured.{W}")
            return

        print(f"\n{C}┌" + "─"*22 + "┬" + "─"*16 + "┐" + f"{W}")
        print(f"{C}│ {B}{'CODE NAME':<20}{W}{C} │ {B}{'2FA CODE':<14}{W}{C} │{W}")
        print(f"{C}├" + "─"*22 + "┼" + "─"*16 + "┤" + f"{W}")
        for name, key in accounts.items():
            try:
                totp = pyotp.TOTP(key)
                code = totp.now()
                print(f"{C}│{W} {G}{name:<20}{W} {C}│{W} {Y}{B}{code:<14}{W} {C}│{W}")
            except Exception:
                print(f"{C}│{W} {R}{name:<20}{W} {C}│{W} {R}{'Invalid':<14}{W} {C}│{W}")
        print(f"{C}└" + "─"*22 + "┴" + "─"*16 + "┘" + f"{W}")

    def add_account(self, pin):
        if not self.verify_pin(pin):
            return
        self.print_banner()
        print(f"\n{Y}--- ENTER CODE DETAILS ---{W}")
        name = input(f"{C}Code name:{W} ").strip()
        if not name:
            print(f"{R}[✘] Cannot be empty!{W}")
            return

        key = input(f"{C}Your key:{W} ").strip().replace(" ", "").upper()
        if not key:
            print(f"{R}[✘] Cannot be empty!{W}")
            return

        try:
            pyotp.TOTP(key).now()
        except Exception:
            print(f"{R}[✘] Invalid key format!{W}")
            return

        accounts = self.load_accounts()
        accounts[name] = key
        self.save_accounts(accounts)
        print(f"\n{G}[✔] Added successfully!{W}")

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
        for idx, name in enumerate(acc_list, start=1):
            print(f" {C}[{idx}]{W} {name}")
        print(f" {C}[0]{W} Cancel")

        choice = input(f"\n{Y}Select account:{W} ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(acc_list):
                target = acc_list[idx]
                confirm = input(f"{R}Delete '{target}'? (y/N):{W} ").strip().lower()
                if confirm == 'y':
                    del accounts[target]
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
            print(f"  {C}[3]{W} {R}Delete Account{W}")
            print(f"  {C}[4]{W} {C}Change PIN{W}")
            print(f"  {C}[0]{W} Exit")
            
            choice = input(f"\n{B}Select Option (0-4):{W} ").strip()
            
            if choice == "1":
                self.display_codes(pin)
                input(f"\n{C}Press Enter to continue...{W}")
            elif choice == "2":
                self.add_account(pin)
                input(f"\n{C}Press Enter to continue...{W}")
            elif choice == "3":
                self.delete_account(pin)
                input(f"\n{C}Press Enter to continue...{W}")
            elif choice == "4":
                pin = self.change_pin(pin)
                input(f"\n{C}Press Enter to continue...{W}")
            elif choice == "0":
                self.clear_screen()
                print(f"\n{G}Thank you for using Marketplacess Stotte Authenticator!{W}\n")
                break
            else:
                input(f"\n{R}[✘] Invalid option! Press Enter...{W}")

if __name__ == "__main__":
    app = AuthenticatorManager()
    app.run()
  
