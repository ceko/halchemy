import functools
from bottle import request
import subprocess
import settings


class NotAuthorizedException(Exception):
    pass

def require(role=None, method='GET', auth=None):
    def decorator(method):
        @functools.wraps(method)
        def f(*args, **kwargs):
            login_successful = auth.login(str(request.query.user), str(request.query.password))
            if login_successful and auth.current_user.role == role:
                return method(*args, **kwargs)
            else:
                raise NotAuthorizedException("Not authorized.")
        return f
    return decorator

def query_haproxy(command):
    return run_process("echo \"{0}\" | socat unix-connect:{1} stdio".format(command, settings.HA_PROXY_SOCKET))

def run_process(command):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    (output, error) = proc.communicate()
    
    return output

class HAStatParser(object):
    
    @property
    def input(self):
        return self._input
    
    def __init__(self, input):
        self._input = input
        self._objectified_headers = None
        self._objectified_rows = None
        
    def parse_to_object(self):
        if not self._objectified_headers:
            """
            The header row starts with a pound space. Each row is separated by a new line, 
            and each value in each row is separated by a comma.  
            """
            headers = []
            rows = {}
            for line in (x.strip() for x in self._input.split('\n') if x.strip()):
                #header row found
                if line.startswith("# "):
                    headers = line[2:-1].split(',')
                else:
                    row = {}
                    for index, value in enumerate(line.split(',')[:-1]):
                        row[headers[index]] = value
                    rows["{0}/{1}".format(row['pxname'], row['svname'])] = row
                    
            self._objectified_rows = rows
            self._objectified_headers = headers
            
        return (self._objectified_headers, self._objectified_rows)
        
        
            