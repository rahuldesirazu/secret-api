from flask import Flask, jsonify, make_response, abort, request, url_for
from flask_httpauth import HTTPBasicAuth
import shelve
import sys
import atexit
import readwritelock as lock
import time

auth = HTTPBasicAuth()
app = Flask(__name__)

""" The persistent database mapping usernames to passwords. """
accounts = shelve.open("accounts-shelf", "c") 
""" The persistent database mapping usernames to a list of that users secrets. """
data = shelve.open("data-shelf", "c")
""" The r/w lock for the account info. """
accountLock = lock.ReadWriteLock()
""" The r/w lock for the secret info. """
dataLock = lock.ReadWriteLock()

@auth.get_password
def get_password(username):
	if username in accounts:
		return accounts[username]
	return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/secret/api/account/create', methods=['POST'])
def create_account():
	if not request.json or not 'username' in request.json or not 'password' in request.json:
		abort(400)
	username = request.json['username']
	password = request.json['password']
	accountLock.acquire_read()
	if username in accounts:
		response = {'message':'username already exists'}
		return jsonify(response), 409
	accountLock.release_read()
	accountLock.acquire_write()
	accounts[username] = password
	accountLock.release_write()
	dataLock.acquire_write()
	data[username] = []
	dataLock.release_write()
	account = {
		'username':username,
		'password':password,
		'uri':'/secret/api/' + username
	}
	return jsonify(account), 201

@app.route('/secret/api/<string:user>', methods=['GET'])
@auth.login_required
def get_secrets(user):
	if auth.username() == user:
		dataLock.acquire_read()
		userData = data[user]
		dataLock.release_read()
		return jsonify({"secrets": userData}), 200
	else:
		return unauthorized()

@app.route('/secret/api/<string:user>', methods=['PUT'])
@auth.login_required
def add_secrets(user):
	if not request.json or not 'secrets' in request.json:
		abort(400)
	username = auth.username()
	if username != user:
		return unauthorized()
	d = request.json['secrets']
	dataLock.acquire_write()
	data[username] = list(set(data[username] + d))
	userData = data[username]
	dataLock.release_write()
	return jsonify({'secrets': userData}), 201

@app.route('/secret/api/<string:user>', methods=['DELETE'])
@auth.login_required
def delete_secrets(user):
	if not request.json or not 'secrets' in request.json:
		abort(400)
	username = auth.username()
	if username != user:
		return unauthorized()
	d = request.json['secrets']
	dataLock.acquire_write()
	data[username] = [s for s in data[username] if s not in d]
	userData = data[username]
	dataLock.release_write()
	return jsonify({'secrets': userData}), 200

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def bad_request(error):
	return jsonify({'error': 'bad request'}), 400

@app.errorhandler(405)
def method_not_supported(error):
	return jsonify({'error': 'method not supported'}), 405

def cleanup():
	accounts.close()
	data.close()

if __name__ == '__main__':
	app.run(host='0.0.0.0', threaded=True)
	atexit.register(cleanup)
