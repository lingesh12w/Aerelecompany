# Inventory Management System

A professional web application built with Flask for managing inventory across multiple locations.

## Features

- **Product Management**: Add, edit, view, and manage products
- **Location Management**: Manage warehouse/storage locations
- **Product Movement Tracking**: Track product movements between locations
- **Balance Reports**: View current inventory levels across all locations
- **Professional UI**: Modern, responsive design with Bootstrap

## Database Schema

### Tables
- **Product**: Stores product information
- **Location**: Stores warehouse/location information  
- **ProductMovement**: Tracks all product movements with timestamps

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000`

## Usage

1. **Setup**: Create products and locations first
2. **Movement**: Record product movements in/out of locations
3. **Reports**: View balance reports to see current inventory levels

## Sample Data

The application includes sample data with:
- 4 products (Laptop, Mouse, Keyboard, Monitor)
- 4 locations (Main Warehouse, Store A, Store B, Returns)
- 20+ sample movements demonstrating various scenarios
