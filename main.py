"""Command-line entry point for Smart Inventory Management System."""

from __future__ import annotations

from getpass import getpass
from pathlib import Path

from config import DATABASE_PATH, LOW_STOCK_THRESHOLD
from database import Database
from services.inventory_service import InventoryManager
from services.report_service import ReportGenerator
from services.sales_service import SalesManager
from utils.helpers import constant_time_equals, hash_password
from utils.logger import get_logger
from utils.validators import ValidationError


class Session:
    """Simple in-memory session for the command-line app."""

    def __init__(self) -> None:
        self.username: str | None = None

    @property
    def is_authenticated(self) -> bool:
        """Return whether an admin user is logged in."""
        return self.username is not None

    def login(self, username: str) -> None:
        """Mark a user as logged in."""
        self.username = username

    def logout(self) -> None:
        """Clear the active session."""
        self.username = None


class AuthService:
    """Handles admin authentication against the users table."""

    def __init__(self, db_path: Path | str = DATABASE_PATH) -> None:
        self.database = Database(db_path)
        self.database.initialize()
        self.logger = get_logger(self.__class__.__name__)

    def authenticate(self, username: str, password: str, session: Session) -> bool:
        """Validate credentials and start a session when they match."""
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT username, password FROM users WHERE username = ?;",
                (username.strip(),),
            ).fetchone()

        if row and constant_time_equals(row["password"], hash_password(password)):
            session.login(row["username"])
            self.logger.info("Admin logged in: %s", username)
            return True

        self.logger.warning("Failed login attempt for username=%s", username)
        return False


class SmartInventoryApp:
    """Interactive CLI application facade."""

    def __init__(self, db_path: Path | str = DATABASE_PATH) -> None:
        self.session = Session()
        self.auth = AuthService(db_path)
        self.inventory = InventoryManager(db_path)
        self.sales = SalesManager(db_path)
        self.reports = ReportGenerator(db_path)
        self.logger = get_logger(self.__class__.__name__)

    def run(self) -> None:
        """Run the interactive command-line application."""
        print("Smart Inventory Management System")
        self._login_prompt()
        while self.session.is_authenticated:
            self._show_low_stock_alerts()
            self._print_menu()
            choice = input("Select an option: ").strip()
            try:
                should_continue = self._handle_choice(choice)
            except (ValidationError, ValueError) as exc:
                print(f"Error: {exc}")
                self.logger.error("User input error: %s", exc)
                should_continue = True
            if not should_continue:
                break

    def _login_prompt(self) -> None:
        """Ask for admin credentials until authentication succeeds."""
        while not self.session.is_authenticated:
            username = input("Username: ").strip()
            password = getpass("Password: ")
            if self.auth.authenticate(username, password, self.session):
                print(f"Welcome, {username}.")
            else:
                print("Invalid username or password.")

    def _print_menu(self) -> None:
        """Display available admin actions."""
        print(
            "\n1. Add Product\n"
            "2. Update Product\n"
            "3. Delete Product\n"
            "4. Search Product\n"
            "5. View Product List\n"
            "6. Record Sale\n"
            "7. Inventory Summary\n"
            "8. Export Reports\n"
            "9. Logout\n"
        )

    def _handle_choice(self, choice: str) -> bool:
        """Dispatch a menu choice. Returns False when the app should exit."""
        actions = {
            "1": self._add_product,
            "2": self._update_product,
            "3": self._delete_product,
            "4": self._search_products,
            "5": self._list_products,
            "6": self._record_sale,
            "7": self._inventory_summary,
            "8": self._export_reports,
            "9": self._logout,
        }
        action = actions.get(choice)
        if action is None:
            print("Invalid choice.")
            return True
        action()
        return choice != "9"

    def _add_product(self) -> None:
        product = self.inventory.add_product(
            product_name=input("Product name: "),
            category=input("Category: "),
            quantity=int(input("Quantity: ")),
            price=float(input("Price: ")),
        )
        print(f"Added product #{product.product_id}: {product.product_name}")

    def _update_product(self) -> None:
        product_id = int(input("Product ID: "))
        name = input("New name (blank to keep): ").strip() or None
        category = input("New category (blank to keep): ").strip() or None
        quantity_text = input("New quantity (blank to keep): ").strip()
        price_text = input("New price (blank to keep): ").strip()
        product = self.inventory.update_product(
            product_id=product_id,
            product_name=name,
            category=category,
            quantity=int(quantity_text) if quantity_text else None,
            price=float(price_text) if price_text else None,
        )
        print(f"Updated product #{product.product_id}: {product.product_name}")

    def _delete_product(self) -> None:
        product_id = int(input("Product ID: "))
        self.inventory.delete_product(product_id)
        print("Product deleted.")

    def _search_products(self) -> None:
        for product in self.inventory.search_products(input("Search keyword: ")):
            self._print_product(product)

    def _list_products(self) -> None:
        for product in self.inventory.list_products():
            self._print_product(product)

    def _record_sale(self) -> None:
        sale = self.sales.record_sale(
            product_id=int(input("Product ID: ")),
            quantity_sold=int(input("Quantity sold: ")),
        )
        print(f"Sale recorded. Amount: ${sale.sale_amount:.2f}")

    def _inventory_summary(self) -> None:
        summary = self.inventory.inventory_summary()
        print(
            f"Products: {summary['total_products']} | "
            f"Units: {summary['total_units']} | "
            f"Value: ${summary['inventory_value']:.2f}"
        )

    def _export_reports(self) -> None:
        inventory_file = self.reports.export_to_csv(
            "inventory", self.reports.inventory_report()
        )
        sales_file = self.reports.export_to_csv("sales", self.reports.sales_report())
        revenue_file = self.reports.export_to_csv(
            "revenue", self.reports.revenue_report()
        )
        print("Reports exported:")
        print(inventory_file)
        print(sales_file)
        print(revenue_file)

    def _logout(self) -> None:
        self.session.logout()
        print("Logged out.")

    def _show_low_stock_alerts(self) -> None:
        low_stock = self.inventory.low_stock_products()
        if low_stock:
            names = ", ".join(product.product_name for product in low_stock)
            print(
                f"Warning: low stock below {LOW_STOCK_THRESHOLD} units for {names}."
            )

    @staticmethod
    def _print_product(product: object) -> None:
        """Print a compact product row."""
        print(
            f"#{product.product_id} | {product.product_name} | "
            f"{product.category} | Qty: {product.quantity} | "
            f"${product.price:.2f}"
        )


if __name__ == "__main__":
    SmartInventoryApp().run()
