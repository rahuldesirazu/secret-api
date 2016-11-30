import sys
import requests
import shutil
import os

def test_create_account(username, password):
	r = requests.post("http://localhost:5000/secret/api/account/create", json={"username":username, "password":password})
	print(r.status_code)
	if r.status_code == 201:
		print('passed test_create_account')
		return True
	else:
		print('failed test_create_account')
		return False

def test_create_account_with_same_username(username):
	r = requests.post("http://localhost:5000/secret/api/account/create", json={"username":username, "password":"bar"})
	if r.status_code == 409:
		print('passed test_create_account_with_same_username')	
		return True
	else:
		print('failed test_create_account_with_same_username')
		return False

def test_get_secrets(username, password, expected):
	r = requests.get("http://localhost:5000/secret/api/" + username, auth=(username, password))
	if r.status_code == 200 and 'secrets' in r.json() and r.json()['secrets'] == expected:
		print('passed test_get_secrets')
		return True
	else:
		print('failed test_get_secrets, expected', expected, 'but got', r.json()['secrets'])
		return False

def test_get_secrets_bad_uri(username, password):
	r = requests.get("http://localhost:5000/secret/api/random/", auth=(username, password))
	print(r.status_code)
	if r.status_code == 404:
		print('passed test_get_secrets_bad_uri')
		return True
	else:
		print('failed test_get_secrets_bad_uri')
		return False

def test_get_secrets_bad_password(username):
	r = requests.get("http://localhost:5000/secret/api/" + username, auth=(username, "bar"))
	if r.status_code == 401:
		print('passed test_get_secrets_bad_password')
		return True
	else:
		print('failed test_get_secrets_bad_password')
		return False

def test_method_not_supported():
	r = requests.get("http://localhost:5000/secret/api/account/create")
	if r.status_code == 405:
		print('passed test_method_not_supported')
		return True
	else:
		print('failed test_method_not_supported')
		return False

def add_secrets(username, password, secrets):
	r = requests.put("http://localhost:5000/secret/api/" + username, auth=(username, password), json={"secrets":secrets})

def delete_secrets(username, password, secrets):	
	r = requests.delete("http://localhost:5000/secret/api/" + username, auth=(username, password), json={"secrets":secrets})
	print(r.json())
	
shutil.rmtree('./data')
os.mkdir('./data')
test_create_account('rahul', 'foo')
test_create_account_with_same_username('rahul')
test_get_secrets('rahul', 'foo', [])
test_get_secrets_bad_uri('rahul', 'foo')
test_get_secrets_bad_password('rahul')
add_secrets('rahul', 'foo', [1, 2])
test_get_secrets('rahul', 'foo', [1, 2])
add_secrets('rahul', 'foo', [1, 3])
delete_secrets('rahul', 'foo', [2, 3, 4])
test_get_secrets('rahul', 'foo', [1])
test_method_not_supported()

