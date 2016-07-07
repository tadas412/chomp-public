import db_lib, venmo
from datetime import datetime, timedelta

### Twilio Params ###

from twilio.rest import TwilioRestClient
import twilio.twiml
from flask import make_response

account_sid = SID 
auth_token = TOKEN 
client = TwilioRestClient(account_sid, auth_token)
TWILIO_PHONE = PHONE

#####################

def send_sms(to_number, msg):
	client.messages.create(to=to_number, from_=TWILIO_PHONE, body=msg)

def clean_sms(command):
	if command.startswith('"'):
		command = command[1:]
	if command.endswith('"'):
		command = command[:-1]
	return command

def parse_initial_command(command):
	command = clean_sms(command)
	parsed_command = dict()
	tokens = command.split(" ")
	if len(tokens) < 2: #minimum grammar is two tokens unless it's "chomp"
		if len(tokens) == 1:
			if tokens[0].strip().lower() == "chomp":
				return "chomp"
		return None
	if tokens[0][0] != "@": #first token should be handle
		return None
	parsed_command['handle'] = tokens[0][1:]
	action = tokens[1].lower()
	if action == "location" or action == "menu":
		if len(tokens) > 2: #in this case, should only be two tokens
			return None
		parsed_command['action'] = action
	elif action == "order":
		if len(tokens) == 2: #in this case, should be more than two tokens
			return None
		parsed_command['action'] = "order"
		parsed_command['freetext'] = " ".join(tokens[2:])
	else: #action must be one of the above things
		return None
	return parsed_command

def is_vendor(from_number):
	vendor_phones = db_lib.db_get_vendor_phones()
	for (phone, oid) in vendor_phones:
		if phone == from_number:
			return oid
	return -1

def vendor_conf(command, order_id):
	command = clean_sms(command.lower())
	resp = twilio.twiml.Response()
	msg = None

	if command == "y":
		query = "UPDATE orders SET vendor_conf = 1 WHERE id = %s"
		vals = (order_id,)
		db_lib.push_db(query, vals)
		msg = "Order confirmed, venmo charge pushed!"
		query = "SELECT phone, price FROM orders WHERE id = %s"
		vals = (order_id,)
		result = db_lib.pull_db(query, vals)
		venmo_data = venmo.charge_or_pay(result[0][0], -1 * float(result[0][1]), str(order_id))
		db_lib.update_order_venmo_charge(order_id);
		# do something with venmo_data? TODO
		body = "Order confirmed by vendor! Please accept the venmo charge to continue."
		client.messages.create(to=result[0][0], from_=TWILIO_PHONE, body=body) # sends message to user
	elif command == "n":

		query = "SELECT phone FROM orders WHERE id = %s"
		vals = (order_id,)
		result = db_lib.pull_db(query, vals)
		body = "Order rejected by vendor..."
		client.messages.create(to=result[0][0], from_=TWILIO_PHONE, body=body) # sends message to user

		query = "DELETE FROM orders WHERE id = %s"
		vals = (order_id,)
		db_lib.push_db(query, vals)
		msg = "Order rejected"
	else:
		msg = "Unrecognized command. Send y or n."

	resp.message(msg)
	resp = make_response(str(resp))
	return resp

def get_instructions():
	result = "Format: @[food truck handle] [action] [other arguments]. Action can be location, menu, or order. \
	You only need other arguments if you're doing the action order. In that case, \
	set other arguments to be the exact name of the food item you're buying."
	handles = "Possible handles (@handle): " + " ".join(db_lib.db_get_vendors())
	return result + "\n\n" + handles


def initial_sms(command, from_number):
	order_id_vendor = is_vendor(from_number)
	if order_id_vendor != -1:
		return vendor_conf(command, order_id_vendor)
	parsed_command = parse_initial_command(command.strip())
	resp = twilio.twiml.Response()
	if parsed_command is None:
		resp.message("Invalid command.")
		return str(resp)
	
	msg = None
	if parsed_command == "chomp":
		msg = get_instructions()
		resp.message(msg)

		resp = make_response(str(resp))
	elif parsed_command['action'] == "location":
		msg = db_lib.pull_location(parsed_command)
		resp.message(msg)
		resp = make_response(str(resp))
	elif parsed_command['action'] == "menu":
		print "menu!"
		msg = db_lib.pull_menu(parsed_command)
		resp.message(msg)
		resp = make_response(str(resp))
	elif parsed_command['action'] == "order":
		(msg, order_id) = db_lib.push_order(parsed_command, from_number)
		expires = datetime.utcnow() + timedelta(hours=4)
		resp.message(msg)
		resp = make_response(str(resp))
		resp.set_cookie('order_id', str(order_id))
		resp.set_cookie('last',value="awaiting user confirmation",expires=expires.strftime('%a, %d %b %Y %H:%M:%S GMT'))
	else:
		msg = "Failed to parse command."
	return resp

def await_user_conf(command, order_id):
	command = clean_sms(command.lower())
	resp = twilio.twiml.Response()
	msg = None

	last_cookie = "awaiting user confirmation"
	if command == "y":
		query = "UPDATE orders SET user_conf = 1 WHERE id = %s"
		vals = (order_id,)
		db_lib.push_db(query, vals)

		# vendor handling...
		query = "SELECT o.description, o.price, v.phone FROM orders as o, vendors as v WHERE o.id = %s"
		vals = (order_id,)
		order = db_lib.pull_db(query, vals)[0]
		if order is None or len(order) == 0:
			query = "DELETE FROM orders WHERE id = %s"
			vals = (order_id,)
			db_lib.push_db(query, vals)
			msg = "Failed to contact vendor. Transaction cancelled"
			last_cookie = 'raw'
		else:
			body = "Received order of " + order[0] + " for " + '${:,.2f}'.format(float(order[1])) + ". Accept? y/n"
			client.messages.create(to="+14848001773", from_=TWILIO_PHONE, body=body) # sends message to vendor
			msg = "Order forwarded to vendor for confirmation!"
			last_cookie = 'user awaiting vendor confirmation'

	elif command == "n":
		query = "DELETE FROM orders WHERE id = %s"
		vals = (order_id,)
		db_lib.push_db(query, vals)
		msg = "Order cancelled"
		last_cookie = "raw"
	else:
		msg = "Unrecognized command. Send y or n."

	resp.message(msg)
	resp = make_response(str(resp))
	resp.set_cookie('last', last_cookie)
	return resp

def user_await_vendor_conf(command, order_id, from_number):
	command = clean_sms(command.lower())
	resp = twilio.twiml.Response()
	msg = None

	query = "SELECT vendor_conf FROM orders WHERE id = %s"
	vals = (order_id,)
	result = db_lib.pull_db(query, vals)
	if result is None or len(result) == 0: # if we couldn't find the entry, restart
		return initial_sms(command, from_number)

	last_cookie = 'user awaiting vendor confirmation'
	if int(result[0][0]) == 0:
		if command == "c":
			query = "SELECT o.description, o.price, v.phone FROM orders as o, vendors as v WHERE o.id = %s"
			vals = (order_id,)
			order = db_lib.pull_db(query, vals)[0]
			body = "User cancelled order of " + order[0] + " for " + '${:,.2f}'.format(float(order[1])) + "."
			client.messages.create(to="+14848001773", from_=TWILIO_PHONE, body=body) # sends message to vendor

			query = "DELETE FROM orders WHERE id = %s"
			vals = (order_id,)
			db_lib.push_db(query, vals)
			msg = "Order cancelled"
			last_cookie = 'raw'
		else:
			msg = "Invalid command. Waiting for vendor. Send 'c' to cancel order."
	else:
		return initial_sms(command, from_number)

	resp.message(msg)
	resp = make_response(str(resp))
	resp.set_cookie('last', last_cookie)
	return resp