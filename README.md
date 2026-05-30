# Smart-Inventory-Management-System


A Python-based Inventory Management System designed for small businesses to efficiently manage products, stock levels, sales transactions, and inventory reports. The application follows Object-Oriented Programming (OOP) principles and uses SQLite for persistent data storage.

## Features

### Product Management

* Add new products
* Update existing products
* Delete products
* Search products
* View complete inventory

### Inventory Tracking

* Real-time stock monitoring
* Product availability checking
* Automatic inventory updates
* Low-stock alerts

### Sales Management

* Record sales transactions
* Automatic stock deduction
* Sales history tracking
* Revenue calculation

### Reporting

* Inventory reports
* Sales reports
* Revenue summaries
* CSV export functionality

### Security & Reliability

* User authentication
* Input validation
* Exception handling
* Activity logging
* Database integrity checks

---

## Technology Stack

* Python 3.x
* SQLite Database
* Object-Oriented Programming (OOP)
* PyTest
* Git & GitHub
* Logging Module
* CSV Reporting

---

## OOP Concepts Implemented

### Encapsulation

Protects sensitive product and user information using private attributes.

### Inheritance

Admin and User classes inherit common functionality.

### Polymorphism

Different report types implement common report generation methods.

### Abstraction

Abstract classes define common behavior for report generation and management modules.

---

## Project Structure


SmartInventorySystem/
│
├── main.py
├── database.py
├── config.py
├── requirements.txt
├── README.md
│
├── models/
│   ├── product.py
│   ├── user.py
│   └── sale.py
│
├── services/
│   ├── inventory_service.py
│   ├── sales_service.py
│   └── report_service.py
│
├── utils/
│   ├── logger.py
│   ├── validators.py
│   └── helpers.py
│
├── tests/
│   ├── test_inventory.py
│   ├── test_sales.py
│   └── test_reports.py
│
├── data/
│   └── inventory.db
│
└── exports/
    └── reports/




## Installation

### Clone Repository

```bash
git clone https://github.com/maheshkonduru51/smart-inventory-management-system.git
```

### Navigate to Project Directory

```bash
cd smart-inventory-management-system
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

Run the application using:

```bash
python main.py
```

If using Streamlit:

```bash
streamlit run app.py
```

---

## Sample Workflow

1. Login as Admin
2. Add Products
3. Update Stock Quantities
4. Record Sales
5. Generate Inventory Reports
6. Export Reports to CSV
7. Monitor Low-Stock Alerts

---

## Database Schema

### Products Table

| Field        | Type    |
| ------------ | ------- |
| product_id   | INTEGER |
| product_name | TEXT    |
| category     | TEXT    |
| quantity     | INTEGER |
| price        | REAL    |
| created_date | DATE    |

### Sales Table

| Field         | Type    |
| ------------- | ------- |
| sale_id       | INTEGER |
| product_id    | INTEGER |
| quantity_sold | INTEGER |
| sale_amount   | REAL    |
| sale_date     | DATE    |

### Users Table

| Field    | Type    |
| -------- | ------- |
| user_id  | INTEGER |
| username | TEXT    |
| password | TEXT    |

---

## Testing

Run unit tests:

```bash
pytest
```

---

## Key Learning Outcomes

* Object-Oriented Programming
* Python Application Development
* SQLite Database Integration
* Software Design Principles
* Exception Handling
* Logging and Monitoring
* Unit Testing with PyTest
* Git Version Control
* SDLC and Agile Development Practices

---

## Future Enhancements

* Web-based Dashboard
* Role-Based Access Control
* Email Notifications
* Barcode Integration
* Cloud Database Support
* Inventory Forecasting
* REST API Integration
* Docker Deployment

---

## Author

**Mahesh Raju Konduru**

* GitHub: https://github.com/maheshkonduru51
* LinkedIn: https://www.linkedin.com/in/mahesh-raju-konduru-a0b5002a5/

---

## License

This project is licensed under the MIT License.
