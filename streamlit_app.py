"""Streamlit browser UI for Smart Inventory Management System."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from config import DATABASE_PATH, LOW_STOCK_THRESHOLD
from database import Database
from main import AuthService, Session
from services.inventory_service import InventoryManager
from services.report_service import ReportGenerator
from services.sales_service import SalesManager
from utils.validators import ValidationError


Database(DATABASE_PATH).initialize()


def get_services() -> tuple[InventoryManager, SalesManager, ReportGenerator]:
    """Create service objects for the current Streamlit run."""
    return (
        InventoryManager(DATABASE_PATH),
        SalesManager(DATABASE_PATH),
        ReportGenerator(DATABASE_PATH),
    )


def product_rows(inventory: InventoryManager) -> list[dict[str, object]]:
    """Return product rows formatted for Streamlit tables."""
    return [
        {
            "ID": product.product_id,
            "Name": product.product_name,
            "Category": product.category,
            "Quantity": product.quantity,
            "Price": product.price,
            "Created": product.created_date,
            "Low Stock": product.quantity < LOW_STOCK_THRESHOLD,
        }
        for product in inventory.list_products()
    ]


def login_page() -> None:
    """Render the login screen."""
    st.title("Smart Inventory Management System")
    st.caption("Admin dashboard")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        session = Session()
        if AuthService(DATABASE_PATH).authenticate(username, password, session):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.rerun()
        st.error("Invalid username or password.")


def render_sidebar() -> str:
    """Render navigation and return the selected page name."""
    st.sidebar.title("Inventory")
    st.sidebar.caption(f"Logged in as {st.session_state.get('username', 'admin')}")
    page = st.sidebar.radio(
        "Navigate",
        [
            "Dashboard",
            "Products",
            "Sales",
            "Reports",
        ],
    )
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    return page


def render_dashboard(inventory: InventoryManager, sales: SalesManager) -> None:
    """Render summary metrics and low-stock alerts."""
    summary = inventory.inventory_summary()
    revenue = sales.calculate_revenue()

    st.title("Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Products", summary["total_products"])
    col2.metric("Units in Stock", summary["total_units"])
    col3.metric("Inventory Value", f"${summary['inventory_value']:.2f}")
    col4.metric("Revenue", f"${revenue:.2f}")

    low_stock = inventory.low_stock_products()
    if low_stock:
        st.warning(
            "Low stock: "
            + ", ".join(product.product_name for product in low_stock)
        )

    st.subheader("Products")
    rows = product_rows(inventory)
    if rows:
        st.dataframe(rows, hide_index=True, use_container_width=True)
    else:
        st.info("No products yet.")


def render_products(inventory: InventoryManager) -> None:
    """Render product CRUD workflows."""
    st.title("Products")

    tab_add, tab_update, tab_delete, tab_search = st.tabs(
        ["Add", "Update", "Delete", "Search"]
    )

    with tab_add:
        with st.form("add_product"):
            name = st.text_input("Product name")
            category = st.text_input("Category")
            quantity = st.number_input("Quantity", min_value=0, step=1)
            price = st.number_input("Price", min_value=0.0, step=0.5)
            submitted = st.form_submit_button("Add Product")
        if submitted:
            try:
                product = inventory.add_product(name, category, int(quantity), price)
                st.success(f"Added product #{product.product_id}.")
            except ValidationError as exc:
                st.error(str(exc))

    products = inventory.list_products()
    product_options = {
        f"{product.product_id} - {product.product_name}": product
        for product in products
    }

    with tab_update:
        if not product_options:
            st.info("Add a product first.")
        else:
            selected_label = st.selectbox("Product", list(product_options))
            selected = product_options[selected_label]
            with st.form("update_product"):
                name = st.text_input("Product name", selected.product_name)
                category = st.text_input("Category", selected.category)
                quantity = st.number_input(
                    "Quantity",
                    min_value=0,
                    value=selected.quantity,
                    step=1,
                )
                price = st.number_input(
                    "Price",
                    min_value=0.0,
                    value=float(selected.price),
                    step=0.5,
                )
                submitted = st.form_submit_button("Update Product")
            if submitted:
                try:
                    inventory.update_product(
                        selected.product_id,
                        product_name=name,
                        category=category,
                        quantity=int(quantity),
                        price=price,
                    )
                    st.success("Product updated.")
                except (ValidationError, RuntimeError) as exc:
                    st.error(str(exc))

    with tab_delete:
        if not product_options:
            st.info("No products to delete.")
        else:
            selected_label = st.selectbox("Delete product", list(product_options))
            selected = product_options[selected_label]
            if st.button("Delete Product", type="primary"):
                try:
                    inventory.delete_product(selected.product_id)
                    st.success("Product deleted.")
                    st.rerun()
                except (ValidationError, RuntimeError) as exc:
                    st.error(str(exc))

    with tab_search:
        keyword = st.text_input("Search by name or category")
        if keyword:
            rows = [
                {
                    "ID": product.product_id,
                    "Name": product.product_name,
                    "Category": product.category,
                    "Quantity": product.quantity,
                    "Price": product.price,
                }
                for product in inventory.search_products(keyword)
            ]
            st.dataframe(rows, hide_index=True, use_container_width=True)


def render_sales(inventory: InventoryManager, sales: SalesManager) -> None:
    """Render sales recording and history."""
    st.title("Sales")
    products = inventory.list_products()
    product_options = {
        f"{product.product_id} - {product.product_name} (${product.price:.2f})": product
        for product in products
    }

    if not product_options:
        st.info("Add products before recording sales.")
        return

    with st.form("record_sale"):
        selected_label = st.selectbox("Product", list(product_options))
        quantity = st.number_input("Quantity sold", min_value=1, step=1)
        submitted = st.form_submit_button("Record Sale")

    if submitted:
        try:
            selected = product_options[selected_label]
            sale = sales.record_sale(selected.product_id, int(quantity))
            st.success(f"Sale recorded for ${sale.sale_amount:.2f}.")
        except ValidationError as exc:
            st.error(str(exc))

    st.subheader("Sales History")
    history = sales.sales_history()
    if history:
        st.dataframe(history, hide_index=True, use_container_width=True)
    else:
        st.info("No sales recorded yet.")


def render_reports(reports: ReportGenerator) -> None:
    """Render report previews and CSV export buttons."""
    st.title("Reports")

    report_type = st.selectbox("Report type", ["Inventory", "Sales", "Revenue"])
    report_map = {
        "Inventory": ("inventory", reports.inventory_report),
        "Sales": ("sales", reports.sales_report),
        "Revenue": ("revenue", reports.revenue_report),
    }
    report_name, report_builder = report_map[report_type]
    rows = report_builder()

    if rows:
        st.dataframe(rows, hide_index=True, use_container_width=True)
    else:
        st.info("No rows for this report yet.")

    if st.button("Export CSV"):
        destination = reports.export_to_csv(report_name, rows)
        st.success(f"Exported to {Path(destination).name}")


def main() -> None:
    """Run the Streamlit UI."""
    st.set_page_config(
        page_title="Smart Inventory Management System",
        page_icon="SIMS",
        layout="wide",
    )

    if not st.session_state.get("authenticated"):
        login_page()
        return

    inventory, sales, reports = get_services()
    page = render_sidebar()

    if page == "Dashboard":
        render_dashboard(inventory, sales)
    elif page == "Products":
        render_products(inventory)
    elif page == "Sales":
        render_sales(inventory, sales)
    else:
        render_reports(reports)


if __name__ == "__main__":
    main()
