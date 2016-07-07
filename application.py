import requests, json
from flask import Flask, request, redirect, make_response, session
import traceback
 
application = Flask(__name__)
application.secret_key = ENTER_KEY_HERE

from lib import parse_lib, db_lib, venmo # custom libraries

@application.route("/", methods=['GET'])
def landing():
	return "Chomp Landing Page"

###### Twilio Management ######

from twilio.rest import TwilioRestClient
import twilio.twiml

@application.route("/twilio", methods=['GET', 'POST'])
def twilio_cmd():
	try:
		command = request.values.get('Body', None)
		from_number = request.values.get('From', None)
		last_cookie = request.cookies.get('last','raw')
		if last_cookie == "raw":
			resp = parse_lib.initial_sms(command, from_number)
		elif last_cookie == "awaiting user confirmation":
			resp = parse_lib.await_user_conf(command, request.cookies.get('order_id'))
		elif last_cookie == "user awaiting vendor confirmation":
			resp = parse_lib.user_await_vendor_conf(command, request.cookies.get('order_id'), from_number)
		else:
			resp = twilio.twiml.Response()
			resp.message("Parsing failure.")
			resp = str(resp)
	except:
		resp = twilio.twiml.Response()
		resp.message("Unexpected error:" + str(traceback.format_exc()))
		resp = str(resp)
	return resp

###### Venmo Management ######

#TODO: add database query to get vendor phone number from payment id
#TODO: notify both parties that payment was completed, maybe record action in database
@application.route("/venmo/status", methods=['GET', 'POST'])
def venmo_status():
	logfile = open("venmolog.txt", "w")
	if request.method == 'GET':
		return str(request.values.get('venmo_challenge'))

	request_data = request.get_json()['data']
	order_id = request_data['note']
	status = request_data['status']
	amount = request_data['amount']
	target_user = request_data['target']['user']
	actor = request_data['actor']
	action = request_data['action']
	actor_id = actor['id']
	target_id = target_user['id']
	
	if status == 'settled' and action == 'charge':
		vendor_phone = db_lib.db_get_vendor_phone(int(order_id))
		r = venmo.charge_or_pay(vendor_phone, abs(amount), order_id)
	elif status == 'settled' and action == 'pay':
		logfile.write("order id: " + str(order_id) + "\n")
		db_lib.update_order_venmo_complete(order_id)
		vendor_phone = db_lib.db_get_vendor_phone(order_id)
		logfile.write("vendor phone: " + vendor_phone + "\n")
		order = db_lib.db_get_order(order_id)
		logfile.write("desc: " + order['description'] + "\n")
		logfile.write("price: " + str(order['price']) + "\n")
		logfile.close();
		parse_lib.send_sms(vendor_phone, "Confirmed: " + order['description'] + " for which the customer paid " + '${:,.2f}'.format(float(str(order['price']))) + ".")
		parse_lib.send_sms(order['user_phone'], "Incoming: " + order['description'] + " for which you paid " + '${:,.2f}'.format(float(str(order['price'])))  + ".")
	return make_response('', 200)

@application.route("/venmo/me", methods=['GET'])
def venmo_me():
	return venmo.get_me()

# @application.route("/venmo/payments", methods=['GET'])
# def venmo_payments():
# 	url = 'https://api.venmo.com/v1/payments'
# 	token = session.get('venmo_token')
# 	if not token:
# 		return 'no access token'
# 	payload = {'access_token' : token}
# 	res = requests.get(url, params=payload)
# 	data = res.json()
# 	# print get_payment_id(data)
# 	# print json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '))
# 	return str(data)

# @application.route("/venmo/singlepayment", methods=['GET'])
# def venmo_singlepayments():
# 	payment_id = request.values.get('id')
# 	url = 'https://api.venmo.com/v1/payments/'
# 	token = session.get('venmo_token')
# 	if not token:
# 		return 'no access token'
# 	payload = {'access_token' : token}
# 	res = requests.get(url + payment_id, params=payload)
# 	data = res.json()
# 	# print json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '))
# 	return str(data)

# @application.route("/venmo/auth", methods=['GET', 'POST'])
# def venmo_auth():
# 	code = request.values.get('code', None)
# 	url = url = 'https://api.venmo.com/v1/oauth/access_token'
# 	data = {
# 		'client_id' : CLIENT_ID,
# 		'client_secret' : CLIENT_SECRET,
# 		'code' : code
# 	}
# 	response = requests.post(url, data)
# 	res_dict = response.json()
# 	access_token = res_dict.get('access_token')
# 	user = res_dict.get('user')
# 	session['venmo_token'] = access_token
# 	session['venmo_username'] = user['username']
# 	return str(res_dict)

# @application.route("/venmo/request", methods=['GET'])
# def venmo_request():
# 	if session.get('venmo_token'):
# 		return 'already have token'
# 	scope_list = ['make_payments', 'access_profile', 'access_email', \
# 		'access_phone', 'access_balance', 'access_payment_history', \
# 		'access_friends']
# 	scope_string = ' '.join(scope_list)
# 	auth_params = {
# 		'client_id' : CLIENT_ID,
# 		'scope' : scope_string,
# 		'response_type' : 'code'
# 	}
# 	auth_url = 'https://api.venmo.com/v1/oauth/authorize'
# 	auth_res = requests.get(auth_url, params=auth_params)
# 	return redirect(auth_res.url)
 
if __name__ == "__main__":
    application.run(debug=True)