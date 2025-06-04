import mysql.connector
import os

# Connect to TiDB Cloud using environment variables
cnx = mysql.connector.connect(
    host=os.environ.get("MYSQL_HOST", "localhost"),
    user=os.environ.get("MYSQL_USER", "root"),
    password=os.environ.get("MYSQL_PASSWORD", ""),
    database=os.environ.get("MYSQL_DB", "quickserve"),
    port=int(os.environ.get("MYSQL_PORT", 4000)),
    ssl_ca=os.path.join(os.path.dirname(__file__), "tidb-ca.pem")  # PEM file for SSL
)

# Insert individual order items (no stored proc)
def insert_order_item(food_item, quantity, order_id):
    try:
        cursor = cnx.cursor()

        query = "INSERT INTO order_items (food_item, quantity, order_id) VALUES (%s, %s, %s)"
        cursor.execute(query, (food_item, quantity, order_id))

        cnx.commit()
        cursor.close()
        print("Order item inserted successfully!")
        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")
        cnx.rollback()
        return -1

    except Exception as e:
        print(f"An error occurred: {e}")
        cnx.rollback()
        return -1

# Insert order status into order_tracking table
def insert_order_tracking(order_id, status):
    try:
        cursor = cnx.cursor()
        query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
        cursor.execute(query, (order_id, status))
        cnx.commit()
        cursor.close()
    except Exception as e:
        print(f"Error inserting order tracking: {e}")
        cnx.rollback()

# Get total order price (replace with inline logic, since functions not supported)
def get_total_order_price(order_id):
    try:
        cursor = cnx.cursor()
        query = "SELECT SUM(price * quantity) FROM order_items WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()[0]
        cursor.close()
        return result or 0
    except Exception as e:
        print(f"Error fetching total order price: {e}")
        return 0

# Get next available order_id (TiDB-compatible)
def get_next_order_id():
    cursor = cnx.cursor()
    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)
    result = cursor.fetchone()[0]
    cursor.close()
    return 1 if result is None else result + 1

# Get order status from order_tracking table
def get_order_status(order_id):
    cursor = cnx.cursor()
    query = "SELECT status FROM order_tracking WHERE order_id = %s"
    cursor.execute(query, (order_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None
