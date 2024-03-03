from flask import Flask, request, jsonify
import uuid
import math
from datetime import datetime, time

app = Flask(__name__)

# In-memory storage for receipt data and points
receipts_data = {}


@app.route('/receipts/process', methods=['POST'])
def process_receipts():
    try:
        # Assuming the receipt data is sent in the request body as JSON
        receipt_json = request.get_json()

        # Generating a unique ID for the receipt
        receipt_id = str(uuid.uuid4())

        # Storing the receipt data in memory
        receipts_data[receipt_id] = receipt_json

        # Calculating and storing points based on the receipt
        points = calculate_points(receipt_json)
        receipts_data[receipt_id]['points'] = points

        # Returning the generated ID in the response
        response_data = {'id': receipt_id}
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def calculate_points(receipt):
    points = 0

    # Rule 1: One point for every alphanumeric character in the retailer name
    points += sum(c.isalnum() for c in receipt.get('retailer', ''))

    # Rule 2: 50 points if the total is a round dollar amount with no cents
    total = receipt.get('total', 0)
    if total == int(total):
        points += 50

    # Rule 3: 25 points if the total is a multiple of 0.25
    if total % 0.25 == 0:
        points += 25

    # Rule 4: 5 points for every two items on the receipt
    items = receipt.get('items', [])
    points += len(items) // 2 * 5

    # Rule 5: If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2
    # and round up to the nearest integer. The result is the number of points earned.
    for item in items:
        description_length = len(item.get('shortDescription', '').strip())
        if description_length % 3 == 0:
            price = item.get('price', 0)
            points += math.ceil(price * 0.2)

    # Rule 6: 6 points if the day in the purchase date is odd
    purchase_date = receipt.get('purchaseDate', '')
    day = datetime.strptime(purchase_date, '%Y-%m-%d').day
    if day % 2 != 0:
        points += 6

    # Rule 7: 10 points if the time of purchase is after 2:00pm and before 4:00pm
    purchase_time = receipt.get('purchaseTime', '')
    purchase_time_obj = datetime.strptime(purchase_time, '%H:%M').time()
    if time(14, 0) < purchase_time_obj < time(16, 0):
        points += 10

    return points


@app.route('/receipts/<receipt_id>/points', methods=['GET'])
def get_receipt_points(receipt_id):
    try:
        receipt_data = receipts_data.get(receipt_id)

        if receipt_data:
            response_data = {'points': receipt_data.get('points', 0)}
            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Receipt not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run()
