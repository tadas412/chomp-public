import MySQLdb
from datetime import datetime, timedelta

db_params = {
	'user' : USER,
	'passwd' : PASS,
	'host' : HOST,
	'db' : DB
}

def pull_db(query, vals):
	cnx = MySQLdb.connect(**db_params)
	cursor = cnx.cursor()
	cursor.execute(query, vals)
	try:
		result = cursor.fetchall()
	except:
		return None
	cursor.close()
	cnx.close()
	return result if len(result) > 0 else None

def push_db(query, vals):
	cnx = MySQLdb.connect(**db_params)
	cursor = cnx.cursor()
	cursor.execute(query, vals)
	cursor.execute("SELECT LAST_INSERT_ID()")
	id_inc = cursor.fetchone()[0]
	cnx.commit()
	cursor.close()
	cnx.close()
	return id_inc


# Returns list of elements in the form [(vendor phone, order ID), ...]
def db_get_vendor_phones():
	query = ("SELECT v.phone, o.id FROM vendors as v, orders as o WHERE o.vendor_id = v.id and o.vendor_conf = 0")
	result = pull_db(query, None)
	if result is None or len(result) == 0:
		return []
	return [("+14848001773", x[1]) for x in result] # TODO hardcode
	#return [(x[0], x[1]) for x in result]

# Returns list of elements in the form [vendor name, ...]
def db_get_vendors():
	query = ("SELECT name FROM vendors")
	result = pull_db(query, None)
	if result is None or len(result) == 0:
		return []
	return [x[0] for x in result]

# Returns the vendor phone number that corresponds to the given order id
def db_get_vendor_phone(order_id):
	return "+14848001773" # TODO hardcode
	query = ("SELECT v.phone FROM vendors as v, orders as o WHERE o.vendor_id = v.id and o.id = %s")
	vals = (order_id,)
	result = pull_db(query, vals)
	if result is None or len(result) == 0:
		return None
	return result[0][0]

# Returns user_phone, description, price the corresponds to given order id
def db_get_order(order_id):
	query = ("SELECT phone, description, price FROM orders WHERE id = %s")
	vals = (order_id,)
	result = pull_db(query, vals)[0]
	if result is None or len(result) == 0:
		return None
	final = dict()
	final['user_phone'] = result[0]
	final['description'] = result[1]
	final['price'] = result[2]
	return final

def pull_location(parsed_command):
	vendor = parsed_command['handle']
	query = ("SELECT location FROM vendors WHERE name = %s")
	vals = (vendor,)
	result = pull_db(query, vals)
	return "Unknown Location" if result is None else result[0][0]

def pull_menu(parsed_command):
	vendor = parsed_command['handle']
	query = ("SELECT f.name, f.price FROM food as f, vendors as v WHERE f.vendor_id = v.id and v.name = %s")
	vals = (vendor,)
	result = pull_db(query, vals)
	return "Unknown Menu" if result is None else " | ".join([x[0] + " for " + '${:,.2f}'.format(float(x[1])) for x in result])

def push_order(parsed_command, phone):
	vendor = parsed_command['handle']
	order_text = parsed_command['freetext'].lower()
	query = ("SELECT f.name, f.price, v.id FROM food as f, vendors as v WHERE f.vendor_id = v.id and v.name = %s")
	vals = (vendor,)
	result = pull_db(query, vals)
	foods_available = dict()
	if result is None or len(result) == 0:
		return None
	vendor_id = result[0][2]
	for x in result:
		foods_available[x[0].lower()] = x[1]
	if order_text not in foods_available:
		return None
	food_name = order_text.lower() # TODO needs to be more robust
	query = ("INSERT INTO orders (time, description, phone, user_conf, vendor_conf, price, vendor_id, venmo_charged, venmo_completed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);")
	vals = (datetime.now, food_name, phone, 0, 0, foods_available[food_name], vendor_id, 0, 0)
	id_inc = push_db(query, vals)
	return ("Order " + food_name + " for " + str(foods_available[food_name]) + " & charge to venmo at " + phone + "? y/n", id_inc)

def update_order_venmo_charge(order_id):
	query = ("UPDATE orders SET venmo_charged = 1 WHERE id = %s")
	vals = (order_id,)
	push_db(query, vals)

def update_order_venmo_complete(order_id):
	query = ("UPDATE orders SET venmo_completed = 1 WHERE id = %s")
	vals = (order_id,)
	push_db(query, vals)


