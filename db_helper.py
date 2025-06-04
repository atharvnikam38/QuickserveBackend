import mysql.connector
import os

# MySQL connection (uses environment variables and TiDB PEM)
cnx = mysql.connector.connect(
    host=os.environ.get("MYSQL_HOST", "localhost"),
    user=os.environ.get("MYSQL_USER", "root"),
    password=os.environ.get("MYSQL_PASSWORD", ""),
    database=os.environ.get("MYSQL_DB", "quickserve"),
    port=int(os.environ.get("MYSQL_PORT", 4000)),
    ssl_ca=os.path.join(os.path.dirname(__file__), "tidb-ca.pem")
)

# ✅ Inserts one item into `orders` table with price lookup
def insert_order_item(food_item_name, quantity, order_id):
    try:
        cursor = cnx.cursor()

        # Get item_id and price from food_items table
        item_query = "SELECT item_id, price FROM food_items WHERE name = %s"
        cursor.execute(item_query, (food_item_name,))
        item = cursor.fetchone()

        if not item:
            print(f"Food item '{food_item_name}' not found in food_items table.")
            return -1

        item_id, price = item
        total_price = price * quantity

        # Insert into orders table
        insert_query = """
            INSERT INTO orders (order_id, item_id, quantity, total_price)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (order_id, item_id, quantity, total_price))
        cnx.commit()
        cursor.close()

        print(f"Inserted {quantity}x {food_item_name} into order {order_id}")
        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")
        cnx.rollback()
        return -1

    except Exception as e:
        print(f"An error occurred: {e}")
        cnx.rollback()
        return -1

# ✅ Insert order status into order_tracking
def insert_order_tracking(order_id, status):
    try:
        cursor = cnx.cursor()
        insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
        cursor.execute(insert_query, (order_id, status))
        cnx.commit()
        cursor.close()
    except Exception as e:
        print(f"Error inserting order tracking: {e}")
        cnx.rollback()

# ✅ Get total order price by summing total_price in orders table
def get_total_order_price(order_id):
    try:
        cursor = cnx.cursor()
        query = "SELECT SUM(total_price) FROM orders WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()[0]
        cursor.close()
        return result or 0
    except Exception as e:
        print(f"Error fetching total order price: {e}")
        return 0

# ✅ Get next available order_id (safe fallback to 1)
def get_next_order_id():
    cursor = cnx.cursor()
    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)
    result = cursor.fetchone()[0]
    cursor.close()
    return 1 if result is None else result + 1

# ✅ Get order status from order_tracking
def get_order_status(order_id):
    cursor = cnx.cursor()
    query = "SELECT status FROM order_tracking WHERE order_id = %s"
    cursor.execute(query, (order_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None
