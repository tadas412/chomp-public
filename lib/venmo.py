import requests, json

CLIENT_ID = ID
CLIENT_SECRET = SECRET
FROM_PHONE = PHONE
ACCESS_TOKEN = TOKEN
PAY_URL = 'https://api.venmo.com/v1/payments'
ME_URL = 'https://api.venmo.com/v1/me'
CHOMP_ID = ID

def charge_or_pay(phone, amount, note):
	phone = phone.strip()
	if phone.startswith("+"):
		phone = phone[1:]
		
	payload = {
		'access_token' : ACCESS_TOKEN,
		'phone' : phone,
		'note' : note,
		'amount' : amount,
		'audience' : 'private'
	}
	res = requests.post(PAY_URL, payload)
	data = res.json()
	# print json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '))
	return str(data)

def get_me():
	payload = {
		'access_token' : ACCESS_TOKEN
	}
	res = requests.get(ME_URL, params=payload)
	data = res.json()
	print json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '))
	return str(data)