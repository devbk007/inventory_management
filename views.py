from flask import Flask, request, jsonify, render_template
from models import db, Product, Location, ProductQuantity, ProductMovement
from app import app
import requests

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

# Product CRUD
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([product.serialize() for product in products]), 200

@app.route('/products', methods=['POST'])
def create_product():
    data = request.json
    product = Product(name=data['name'], product_id= data['product_id'])
    db.session.add(product)
    db.session.commit()
    return jsonify(product.serialize()), 201

@app.route('/products', methods=['PUT'])
def update_product():
    data = request.json
    product_id = data.get('id')
    if product_id is not None:
        existing_product = Product.query.get(product_id)
        if existing_product:
            existing_product.name = data.get('name', existing_product.name) # If name data is provided in request body, it will be used, else existing name value will be used.
            db.session.commit()
            return jsonify(existing_product.serialize()), 200
        else:
            return jsonify({"message":f"Product with product_id {product_id} does not exist"}), 400

# Location CRUD
@app.route('/location', methods=['GET'])
def get_locations():
    locations = Location.query.all()
    return jsonify([location.serialize() for location in locations])

@app.route('/location', methods=['POST'])
def create_location():
    data = request.json
    location = Location(name=data['name'], location_id= data['location_id'])
    db.session.add(location)
    db.session.commit()
    return jsonify(location.serialize()), 201

@app.route('/location', methods=['PUT'])
def update_location():
    data = request.json
    location_id = data.get('id')
    if location_id is not None:
        existing_location = Location.query.get(location_id)
        if existing_location:
            existing_location.name = data.get('name', existing_location.name)
            db.session.commit()
            return jsonify(existing_location.serialize()), 200
        else:
            return jsonify({"message":f"Location with location_id {existing_location} does not exist"}), 400


# ProductQuantity CRUD
# @app.route('/product_quantities', methods=['GET'])
# def get_product_quantities():
#     product_quantities = ProductQuantity.query.all()
#     return jsonify([pq.serialize() for pq in product_quantities]), 200

# @app.route('/product_quantities', methods=['POST'])
# def create_product_quantity():
#     data = request.json
#     # Check if product exists
#     product = Product.query.filter_by(product_id=data['product_id']).first()
#     if not product:
#         return jsonify({"message":f"Product does not exist"}), 400

#     location = Location.query.filter_by(location_id=data['location_id']).first()
#     if not location:
#         return jsonify({"message":f"Location does not exist"}), 400
    
#     # Check if product already present in the location

#     product_quantity = ProductQuantity.query.filter_by(product_id = data['product_id'], location_id = data['location_id']).first()
#     if not product_quantity:
#         product_quantity = ProductQuantity(
#             product_quantity_id = data['product_quantity_id'],
#             product_id=data['product_id'],
#             location_id=data['location_id'],
#             quantity=data['quantity']
#         )
#         db.session.add(product_quantity)
#     else:
#         product_quantity.quantity += data['quantity']
#     db.session.commit()
#     return jsonify(product_quantity.serialize()), 201

@app.route('/product_movements', methods=['GET'])
def get_product_movements():
    product_movements = ProductMovement.query.all()
    return jsonify([movement.serialize() for movement in product_movements]), 200

@app.route('/product_movements', methods=['POST'])
def create_product_movement():
    data = request.json

    if data["from_location_id"] != "" and data["to_location_id"] != "":
        to_location = Location.query.filter_by(
            location_id=data['to_location_id']
        ).first()

        from_location = Location.query.filter_by(
            location_id=data['from_location_id']
        ).first()

        if not to_location:
            return jsonify({"message":f"To location with id {data['to_location_id']} does not exist"}), 400
        
        if not from_location:
            return jsonify({"message":f"From location with id {data['from_location_id']} does not exist"}), 400
        
        # Get the product quantity entry for the from_location
        from_location_product_quantity = ProductQuantity.query.filter_by(
            product_id=data['product_id'],
            location_id=data['from_location_id']
        ).first()

        if not from_location_product_quantity:
            return jsonify({"message":f"Product does not exist in from location id {data['from_location_id']}"}), 400

        if from_location_product_quantity.quantity >= int(data['qty']):
            product = ProductQuantity.query.filter_by(product_id=data['product_id'], location_id=data['to_location_id']).first()

            if not product: # if product type is new to the location
                product_quantity = ProductQuantity(
                    product_id=data['product_id'],
                    location_id=data['to_location_id'],
                    quantity=0
                )
                db.session.add(product_quantity)
                db.session.commit()

            to_location_product_quantity = ProductQuantity.query.filter_by(
                product_id=data['product_id'],
                location_id=data['to_location_id']
            ).first()
            
            from_location_product_quantity.quantity -= int(data['qty'])
            to_location_product_quantity.quantity += int(data['qty'])
            db.session.commit()

            # Create the product movement entry
            movement = ProductMovement(
                product_id = data['product_id'],
                from_location_id = data['from_location_id'],
                to_location_id = data['to_location_id'],
                qty=data['qty']
            )

            db.session.add(movement)
            db.session.commit()

            return jsonify(movement.serialize()), 201
        else:
            return jsonify({"message":f"Not enough quantity in location id {data['from_location_id']}"}), 400
    
    # Remove from one location
    elif data["from_location_id"] != "":
        from_location = Location.query.filter_by(
            location_id=data['from_location_id']
        ).first()
        
        if not from_location:
            return jsonify({"message":f"From location with id {data['to_location_id']} does not exist"}), 400
        
        # Get the product quantity entry for the from_location
        from_location_product_quantity = ProductQuantity.query.filter_by(
            product_id=data['product_id'],
            location_id=data['from_location_id']
        ).first()

        if not from_location_product_quantity:
            return jsonify({"message":f"Product does not exist in from location id {data['from_location_id']}"}), 400

        if from_location_product_quantity.quantity >= int(data['qty']):

            from_location_product_quantity.quantity -= int(data['qty'])
            db.session.commit()

            # Create the product movement entry
            movement = ProductMovement(
                product_id = data['product_id'],
                from_location_id = data['from_location_id'],
                to_location_id = "",
                qty=data['qty']
            )

            db.session.add(movement)
            db.session.commit()

            return jsonify(movement.serialize()), 201
        else:
            return jsonify({"message":f"Not enough quantity in location id {data['from_location_id']}"}), 400
    
    # Add to a location
    elif data["to_location_id"] != "":
        to_location = Location.query.filter_by(
            location_id=data['to_location_id']
        ).first()


        if not to_location:
            return jsonify({"message":f"To location with id {data['to_location_id']} does not exist"}), 400
        
        product = ProductQuantity.query.filter_by(product_id=data['product_id'], location_id=data['to_location_id']).first()

        if not product: # if product type is new to the location
            product_quantity = ProductQuantity(
                product_id=data['product_id'],
                location_id=data['to_location_id'],
                quantity=0
            )
            db.session.add(product_quantity)
            db.session.commit()

        to_location_product_quantity = ProductQuantity.query.filter_by(
            product_id=data['product_id'],
            location_id=data['to_location_id']
        ).first()
        
        to_location_product_quantity.quantity += int(data['qty'])
        db.session.commit()

        # Create the product movement entry
        movement = ProductMovement(
            product_id = data['product_id'],
            from_location_id = "",
            to_location_id = data['to_location_id'],
            qty=data['qty']
        )

        db.session.add(movement)
        db.session.commit()

        return jsonify(movement.serialize()), 201
        
@app.route('/product_movements', methods=['PUT'])
def update_product_movements():
    data = request.json()
    product_movement_id = data.get('product_movement_id')
    if product_movement_id is not None:
        product_movement = ProductMovement.query.get(product_movement_id)
        if product_movement:
            product_movement.from_location_id = data.get('from_location_id', product_movement.from_location_id)
            product_movement.to_location_id = data.get('to_location_id', product_movement.to_location_id)
            product_movement.product_id = data.get('product_id', product_movement.product_id)
            product_movement.qty = data.get('qty', product_movement.qty)
            db.session.commit()
            return jsonify(product_movement.serialize()), 200
        else:
            return jsonify({"message":f"Movement with id {product_movement_id} does not exist"}), 400


# Report: Balance quantity in each location
@app.route('/location_balance', methods=['GET'])
def get_location_balance():
    locations = Location.query.all()
    balance_report = []

    for location in locations:
        # Query all ProductQuantity records for the current location
        product_quantities = ProductQuantity.query.filter_by(location_id=location.location_id).all()
        product_quantity_dict = {}
        for pq in product_quantities:
            if pq.product_id not in product_quantity_dict:
                product_quantity_dict[pq.product_id] = 0
            product_quantity_dict[pq.product_id] += pq.quantity

        # Create location data
        location_data = {
            'location_id': location.location_id,
            'location_name': location.name,
            'balance_quantity': product_quantity_dict
        }
        

        # Append to the balance report
        balance_report.append(location_data)
    
    final_balance_report = []

    for location_data in balance_report:
        location_id = location_data['location_id']
        location_name = location_data['location_name']
        product_quantity_dict = location_data['balance_quantity']

        for product_id, quantity in product_quantity_dict.items():
            # Retrieve the product object using the product_id
            product = Product.query.get(product_id)

            # Use the serialize method to get the product name
            product_data = product.serialize()
            product_name = product_data['name']

            # Append to the final_balance_report
            final_balance_report.append({
                'product_name': product_name,
                'location_name': location_name,
                'quantity': quantity
            })

    return jsonify(final_balance_report)

if __name__ == '__main__':
    app.run(debug=True)
