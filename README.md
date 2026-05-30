# Smart Inventory Management System

## Project Overview

Smart Inventory Management System is a production-style Python application for
small businesses to manage products, stock, sales, low-stock alerts, and CSV
reports. It uses SQLite for persistence and a modular object-oriented design
that is easy to test, extend, and discuss in interviews.

## Features

- Admin login with password validation and session management
- Product management: add, update, delete, search, and list products
- Inventory tracking with quantity updates and availability checks
- Sales transactions that automatically reduce stock
- Sales history and total revenue calculation
- Inventory, sales, and revenue reports
- CSV export for reports
- Low-stock alerts when quantity is below 10
- Exception handling for invalid input, missing products, negative quantities,
  insufficient stock, and database errors
- File-based logging for operations, errors, and transactions

## Installation Steps

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## How to Run

Start the CLI app from the project folder:

```bash
python main.py
```

Default admin credentials:

- Username: `admin`
- Password: `Admin@123`

The application creates the SQLite database automatically at
`data/inventory.db`.

## How to Run in Browser with Streamlit

Create and activate the local virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies inside the virtual environment:

```bash
pip install -r requirements.txt
```

Start the browser dashboard with either command:

```bash
streamlit run streamlit_app.py
```

```powershell
.\run_streamlit.ps1
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

Use the same default admin credentials:

- Username: `admin`
- Password: `Admin@123`

## How to Test

Run the PyTest suite:

```bash
pytest
```

## Screenshots Section

Add screenshots here after running the CLI, such as:

- Admin login screen
- Product list output
- Low-stock warning
- CSV export confirmation

## Technologies Used

- Python 3.12+
- SQLite
- Object-Oriented Programming
- PyTest
- Python logging module
- CSV module

## OOP Concepts Used

- Classes and objects: `Product`, `Sale`, `User`, `Admin`,
  `InventoryManager`, `SalesManager`, and `ReportGenerator`
- Encapsulation: service classes hide database logic behind clear methods
- Inheritance: `Admin` extends `User`
- Polymorphism: `ReportGenerator` implements the `BaseReport.generate` method
- Abstraction: `User` defines an abstract `role` contract

## Project Structure

```text
SmartInventorySystem/
├── main.py
├── database.py
├── config.py
├── requirements.txt
├── README.md
├── models/
├── services/
├── utils/
├── tests/
├── data/
├── exports/
└── reports/
```

## Future Enhancements

- Role-based permissions beyond the admin role
- Web dashboard with charts
- Barcode scanning support
- Import products from CSV
- PDF report exports
- Cloud database support
- Strong password hashing with Argon2 or bcrypt
