#!/usr/bin/env python
#
#
# Regenerate files in example_conf

from datetime import datetime
from cork import Cork

def populate_conf_directory():
    cork = Cork('.', initialize=True)

    cork._store.roles['admin'] = 100
    cork._store._savejson('roles', cork._store.roles)

    tstamp = str(datetime.utcnow())
    username = ""
    while not username:
        username = raw_input("Enter admin username: ")
    password = ""
    while not password:
        password = raw_input("Enter admin password: ") 
        
    cork._store.users[username] = {
        'role': 'admin',
        'hash': cork._hash(username, password),
        'creation_date': tstamp
    }
    cork._store._save_users()

if __name__ == '__main__':
    populate_conf_directory()

