/secret/api/account/create: URI to create a new account. Use a POST request with format {"username":username, "password":password} to create a new account. Upon successful creation, the server returns a json with the username, password, and created uri for the user

/secret/api/string:username: URI to access the stored secrets. To access the secrets, the username and password used to make the URI must be used in the request. GET request to get the secrets, secrets returned in json {"secrets":[list of secrets]}. PUT request to add new secrets, update with json {"secrets":[list of secrets]} to add to the current list. DELETE request to delete secrets, update with json {"secrets":[list of secrets]}.

I tested the api using my tests.py script, which tested the basic functionality of the service. I also tested multithreading in 2 ways:
1. For write operations, I tested that if one thread got the write lock and blocked, no other thread could do a write operation.
2. For read operations, I tested that if one thread got the read lock and blocked, other threads could do reads but no other threads could do writes.

My implementation of the api used two dictionaries. One dictionary mapped usernames to passwords and the other dictionary mapped usernames to the list of secrets associated with that username. My service supported creating a new account, and adding, deleting, and getting all the secrets for the given user. Authentication is ensured using username, password, as any request to access secrets needed be accompanied by authentication. I also handled multithreading by using read-write locks around the account information and the secret information. If I had more time, I would implement features to change account information (username or password), query secrets to determine whether a given secret is in the stored list, and tag secrets with a small note so the user remembers what the secret was for.

BUILD INSTRUCTIONS:
run . venv/bin/activate
run python app.py. Will automatically launch the app on port 5000
