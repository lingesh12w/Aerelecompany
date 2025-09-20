from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Product, Location, ProductMovement
from datetime import datetime
import uuid
from sqlalchemy import func
from typing import Optional

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def generate_id():
    """Generate a unique ID"""
    return str(uuid.uuid4())[:8].upper()

def get_stock(product_id: str, location_id: str, exclude_movement_id: Optional[str] = None) -> int:
    """Compute current stock for a product at a location.
    Optionally exclude a movement (useful when editing).
    """
    q = ProductMovement.query.filter_by(product_id=product_id)
    if exclude_movement_id:
        q = q.filter(ProductMovement.movement_id != exclude_movement_id)

    stock_in = q.filter(ProductMovement.to_location == location_id)\
                .with_entities(func.coalesce(func.sum(ProductMovement.qty), 0)).scalar() or 0
    stock_out = q.filter(ProductMovement.from_location == location_id)\
                .with_entities(func.coalesce(func.sum(ProductMovement.qty), 0)).scalar() or 0
    return int(stock_in) - int(stock_out)

@app.route('/')
def index():
    """Dashboard with overview statistics"""
    total_products = Product.query.count()
    total_locations = Location.query.count()
    total_movements = ProductMovement.query.count()
    
    # Recent movements
    recent_movements = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).limit(5).all()
    
    return render_template('index.html', 
                         total_products=total_products,
                         total_locations=total_locations,
                         total_movements=total_movements,
                         recent_movements=recent_movements)

# Product Routes
@app.route('/products')
def products():
    """List all products with search and pagination"""
    q = request.args.get('q', '').strip()
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)

    query = Product.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Product.product_id.ilike(like)) | (Product.name.ilike(like)) | (Product.description.ilike(like))
        )

    pagination = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('products/list.html', products=pagination.items, pagination=pagination, q=q)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    """Add a new product"""
    if request.method == 'POST':
        product_id = request.form['product_id']
        name = request.form['name']
        description = request.form.get('description', '')
        unit_price = float(request.form.get('unit_price', 0))
        
        # Check if product ID already exists
        if Product.query.get(product_id):
            flash('Product ID already exists!', 'error')
            return render_template('products/form.html')
        
        product = Product(
            product_id=product_id,
            name=name,
            description=description,
            unit_price=unit_price
        )
        
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))
    
    return render_template('products/form.html')

@app.route('/products/edit/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    """Edit an existing product"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form.get('description', '')
        product.unit_price = float(request.form.get('unit_price', 0))
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))
    
    return render_template('products/form.html', product=product)

@app.route('/products/delete/<product_id>', methods=['POST'])
def delete_product(product_id):
    """Delete a product if it has no movements"""
    product = Product.query.get_or_404(product_id)
    has_movements = ProductMovement.query.filter_by(product_id=product_id).first() is not None
    if has_movements:
        flash('Cannot delete product with existing movements.', 'error')
        return redirect(url_for('products'))
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products'))

@app.route('/products/view/<product_id>')
def view_product(product_id):
    """View product details"""
    product = Product.query.get_or_404(product_id)
    movements = ProductMovement.query.filter_by(product_id=product_id).order_by(ProductMovement.timestamp.desc()).all()
    return render_template('products/view.html', product=product, movements=movements)

# Location Routes
@app.route('/locations')
def locations():
    """List all locations with search and pagination"""
    q = request.args.get('q', '').strip()
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)

    query = Location.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Location.location_id.ilike(like)) | (Location.name.ilike(like)) | (Location.address.ilike(like))
        )

    pagination = query.order_by(Location.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('locations/list.html', locations=pagination.items, pagination=pagination, q=q)

@app.route('/locations/add', methods=['GET', 'POST'])
def add_location():
    """Add a new location"""
    if request.method == 'POST':
        location_id = request.form['location_id']
        name = request.form['name']
        address = request.form.get('address', '')
        manager = request.form.get('manager', '')
        
        # Check if location ID already exists
        if Location.query.get(location_id):
            flash('Location ID already exists!', 'error')
            return render_template('locations/form.html')
        
        location = Location(
            location_id=location_id,
            name=name,
            address=address,
            manager=manager
        )
        
        db.session.add(location)
        db.session.commit()
        flash('Location added successfully!', 'success')
        return redirect(url_for('locations'))
    
    return render_template('locations/form.html')

@app.route('/locations/edit/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    """Edit an existing location"""
    location = Location.query.get_or_404(location_id)
    
    if request.method == 'POST':
        location.name = request.form['name']
        location.address = request.form.get('address', '')
        location.manager = request.form.get('manager', '')
        
        db.session.commit()
        flash('Location updated successfully!', 'success')
        return redirect(url_for('locations'))
    
    return render_template('locations/form.html', location=location)

@app.route('/locations/delete/<location_id>', methods=['POST'])
def delete_location(location_id):
    """Delete a location if it has no related movements (as from/to)"""
    location = Location.query.get_or_404(location_id)
    has_movements = ProductMovement.query.filter(
        (ProductMovement.from_location == location_id) | (ProductMovement.to_location == location_id)
    ).first() is not None
    if has_movements:
        flash('Cannot delete location with existing movements.', 'error')
        return redirect(url_for('locations'))
    db.session.delete(location)
    db.session.commit()
    flash('Location deleted successfully!', 'success')
    return redirect(url_for('locations'))

@app.route('/locations/view/<location_id>')
def view_location(location_id):
    """View location details"""
    location = Location.query.get_or_404(location_id)
    movements_from = ProductMovement.query.filter_by(from_location=location_id).order_by(ProductMovement.timestamp.desc()).all()
    movements_to = ProductMovement.query.filter_by(to_location=location_id).order_by(ProductMovement.timestamp.desc()).all()
    return render_template('locations/view.html', location=location, movements_from=movements_from, movements_to=movements_to)

# Movement Routes
@app.route('/movements')
def movements():
    """List all movements with search and pagination"""
    q = request.args.get('q', '').strip()
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)

    query = ProductMovement.query
    if q:
        like = f"%{q}%"
        # Join products for filtering by product name
        query = query.join(Product, Product.product_id == ProductMovement.product_id)
        query = query.filter(
            (ProductMovement.movement_id.ilike(like)) |
            (ProductMovement.product_id.ilike(like)) |
            (Product.name.ilike(like))
        )

    pagination = query.order_by(ProductMovement.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('movements/list.html', movements=pagination.items, pagination=pagination, q=q)

@app.route('/movements/add', methods=['GET', 'POST'])
def add_movement():
    """Add a new movement"""
    if request.method == 'POST':
        movement_id = generate_id()
        product_id = request.form['product_id']
        from_location = request.form.get('from_location') or None
        to_location = request.form.get('to_location') or None
        qty = int(request.form['qty'])
        notes = request.form.get('notes', '')
        
        # Validation
        if not from_location and not to_location:
            flash('Either from_location or to_location must be specified!', 'error')
            products = Product.query.all()
            locations = Location.query.all()
            return render_template('movements/form.html', products=products, locations=locations)
        
        # Stock validation: from_location must have enough stock
        if from_location:
            available = get_stock(product_id, from_location)
            if qty > available:
                flash(f'Insufficient stock at source location. Available: {available}, Requested: {qty}', 'error')
                products = Product.query.all()
                locations = Location.query.all()
                return render_template('movements/form.html', products=products, locations=locations)

        movement = ProductMovement(
            movement_id=movement_id,
            product_id=product_id,
            from_location=from_location,
            to_location=to_location,
            qty=qty,
            notes=notes
        )
        
        db.session.add(movement)
        db.session.commit()
        flash('Movement added successfully!', 'success')
        return redirect(url_for('movements'))
    
    products = Product.query.all()
    locations = Location.query.all()
    return render_template('movements/form.html', products=products, locations=locations)

@app.route('/movements/edit/<movement_id>', methods=['GET', 'POST'])
def edit_movement(movement_id):
    """Edit an existing movement"""
    movement = ProductMovement.query.get_or_404(movement_id)
    
    if request.method == 'POST':
        movement.product_id = request.form['product_id']
        movement.from_location = request.form.get('from_location') or None
        movement.to_location = request.form.get('to_location') or None
        movement.qty = int(request.form['qty'])
        movement.notes = request.form.get('notes', '')
        
        # Validation
        if not movement.from_location and not movement.to_location:
            flash('Either from_location or to_location must be specified!', 'error')
            products = Product.query.all()
            locations = Location.query.all()
            return render_template('movements/form.html', movement=movement, products=products, locations=locations)

        # Stock validation for edits: consider excluding current movement when computing available
        if movement.from_location:
            available = get_stock(movement.product_id, movement.from_location, exclude_movement_id=movement.movement_id)
            if movement.qty > available:
                flash(f'Insufficient stock at source location. Available: {available}, Requested: {movement.qty}', 'error')
                products = Product.query.all()
                locations = Location.query.all()
                return render_template('movements/form.html', movement=movement, products=products, locations=locations)
        
        db.session.commit()
        flash('Movement updated successfully!', 'success')
        return redirect(url_for('movements'))
    
    products = Product.query.all()
    locations = Location.query.all()
    return render_template('movements/form.html', movement=movement, products=products, locations=locations)

@app.route('/movements/view/<movement_id>')
def view_movement(movement_id):
    """View movement details"""
    movement = ProductMovement.query.get_or_404(movement_id)
    return render_template('movements/view.html', movement=movement)

@app.route('/movements/delete/<movement_id>', methods=['POST'])
def delete_movement(movement_id):
    """Delete a movement"""
    movement = ProductMovement.query.get_or_404(movement_id)
    db.session.delete(movement)
    db.session.commit()
    flash('Movement deleted successfully!', 'success')
    return redirect(url_for('movements'))

# Reports
@app.route('/reports/balance')
def balance_report():
    """Generate balance report showing current inventory levels"""
    # Calculate balance for each product-location combination
    balances = {}
    
    # Get all movements
    movements = ProductMovement.query.all()
    
    for movement in movements:
        product_id = movement.product_id
        qty = movement.qty
        
        # Initialize product in balances if not exists
        if product_id not in balances:
            balances[product_id] = {}
        
        # Handle stock in (to_location)
        if movement.to_location:
            if movement.to_location not in balances[product_id]:
                balances[product_id][movement.to_location] = 0
            balances[product_id][movement.to_location] += qty
        
        # Handle stock out (from_location)
        if movement.from_location:
            if movement.from_location not in balances[product_id]:
                balances[product_id][movement.from_location] = 0
            balances[product_id][movement.from_location] -= qty
    
    # Convert to list format for template
    balance_data = []
    products = {p.product_id: p for p in Product.query.all()}
    locations = {l.location_id: l for l in Location.query.all()}
    
    for product_id, location_balances in balances.items():
        for location_id, qty in location_balances.items():
            if qty != 0:  # Only show non-zero balances
                balance_data.append({
                    'product': products.get(product_id),
                    'location': locations.get(location_id),
                    'qty': qty
                })
    
    # Sort by product name, then location name
    balance_data.sort(key=lambda x: (x['product'].name if x['product'] else '', 
                                   x['location'].name if x['location'] else ''))
    
    return render_template('reports/balance.html', balance_data=balance_data)

def create_sample_data():
    """Create sample data for testing"""
    # Create products
    products = [
        Product(product_id='LAPTOP001', name='Dell Laptop', description='Dell Inspiron 15 3000', unit_price=45000),
        Product(product_id='MOUSE001', name='Wireless Mouse', description='Logitech M705 Wireless Mouse', unit_price=2500),
        Product(product_id='KEYBOARD001', name='Mechanical Keyboard', description='Corsair K95 RGB Mechanical Keyboard', unit_price=8500),
        Product(product_id='MONITOR001', name='LED Monitor', description='Samsung 24" LED Monitor', unit_price=12000)
    ]
    
    # Create locations
    locations = [
        Location(location_id='WH001', name='Main Warehouse', address='123 Industrial Area, City', manager='John Smith'),
        Location(location_id='STORE_A', name='Store A', address='456 Mall Road, City', manager='Jane Doe'),
        Location(location_id='STORE_B', name='Store B', address='789 Market Street, City', manager='Bob Johnson'),
        Location(location_id='RETURNS', name='Returns Section', address='Main Warehouse - Returns Area', manager='Alice Brown')
    ]
    
    # Add to database
    for product in products:
        if not Product.query.get(product.product_id):
            db.session.add(product)
    
    for location in locations:
        if not Location.query.get(location.location_id):
            db.session.add(location)
    
    db.session.commit()
    
    # Create sample movements (only if no movements exist)
    if ProductMovement.query.count() == 0:
        movements = [
            # Initial stock in
            ProductMovement(movement_id=generate_id(), product_id='LAPTOP001', to_location='WH001', qty=50, notes='Initial stock'),
            ProductMovement(movement_id=generate_id(), product_id='MOUSE001', to_location='WH001', qty=100, notes='Initial stock'),
            ProductMovement(movement_id=generate_id(), product_id='KEYBOARD001', to_location='WH001', qty=75, notes='Initial stock'),
            ProductMovement(movement_id=generate_id(), product_id='MONITOR001', to_location='WH001', qty=30, notes='Initial stock'),
            
            # Transfers to stores
            ProductMovement(movement_id=generate_id(), product_id='LAPTOP001', from_location='WH001', to_location='STORE_A', qty=10, notes='Store A restock'),
            ProductMovement(movement_id=generate_id(), product_id='MOUSE001', from_location='WH001', to_location='STORE_A', qty=20, notes='Store A restock'),
            ProductMovement(movement_id=generate_id(), product_id='LAPTOP001', from_location='WH001', to_location='STORE_B', qty=8, notes='Store B restock'),
            ProductMovement(movement_id=generate_id(), product_id='KEYBOARD001', from_location='WH001', to_location='STORE_B', qty=15, notes='Store B restock'),
            
            # Sales (stock out)
            ProductMovement(movement_id=generate_id(), product_id='LAPTOP001', from_location='STORE_A', qty=3, notes='Customer sale'),
            ProductMovement(movement_id=generate_id(), product_id='MOUSE001', from_location='STORE_A', qty=5, notes='Customer sale'),
            ProductMovement(movement_id=generate_id(), product_id='LAPTOP001', from_location='STORE_B', qty=2, notes='Customer sale'),
            ProductMovement(movement_id=generate_id(), product_id='KEYBOARD001', from_location='STORE_B', qty=4, notes='Customer sale'),
            
            # Returns
            ProductMovement(movement_id=generate_id(), product_id='LAPTOP001', to_location='RETURNS', qty=1, notes='Customer return - defective'),
            ProductMovement(movement_id=generate_id(), product_id='MOUSE001', to_location='RETURNS', qty=2, notes='Customer return'),
            
            # More transfers
            ProductMovement(movement_id=generate_id(), product_id='MONITOR001', from_location='WH001', to_location='STORE_A', qty=8, notes='Store A monitor display'),
            ProductMovement(movement_id=generate_id(), product_id='MONITOR001', from_location='WH001', to_location='STORE_B', qty=6, notes='Store B monitor display'),
            ProductMovement(movement_id=generate_id(), product_id='KEYBOARD001', from_location='WH001', to_location='STORE_A', qty=12, notes='Store A keyboard stock'),
            
            # Additional sales
            ProductMovement(movement_id=generate_id(), product_id='MONITOR001', from_location='STORE_A', qty=3, notes='Customer sale'),
            ProductMovement(movement_id=generate_id(), product_id='MONITOR001', from_location='STORE_B', qty=2, notes='Customer sale'),
            ProductMovement(movement_id=generate_id(), product_id='KEYBOARD001', from_location='STORE_A', qty=6, notes='Customer sale'),
            
            # Inter-store transfers
            ProductMovement(movement_id=generate_id(), product_id='LAPTOP001', from_location='STORE_A', to_location='STORE_B', qty=2, notes='Inter-store transfer'),
            ProductMovement(movement_id=generate_id(), product_id='MOUSE001', from_location='STORE_A', to_location='STORE_B', qty=5, notes='Inter-store transfer')
        ]
        
        for movement in movements:
            db.session.add(movement)
        
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    
    app.run(debug=True)
