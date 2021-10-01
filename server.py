from pyftpdlib import servers
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from common import FTPC2
import threading
import logging
import sys
from restapi import serve_api
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

def serve_ftp(c2: FTPC2):
    authorizer = DummyAuthorizer()
    for cred in c2.creds:
        authorizer.add_user(cred['user'], cred['pass'], c2.root_dir, perm=cred['perm'])

    address = ('0.0.0.0', 21)
    handler = FTPHandler
    handler.authorizer = authorizer

    try:
        server = servers.FTPServer(address, FTPHandler)
    except OSError:
        logging.error("Try running server using sudo privilege")
        logging.error("If you're using virtualenv, remember to run the virtualenv as privileged user as well")
        sys.exit(1)
    server.serve_forever()

if __name__ == '__main__':
    # Permission
    # https://pyftpdlib.readthedocs.io/en/latest/api.html#pyftpdlib.authorizers.DummyAuthorizer.add_user
    default_creds = [
        {"user": "victim", "pass": "IVAb6r+hALzhCSm4eCh2Y8oP8feNszzCHQ==", "perm": "elradfmwMT"}
    ]
    root_dir = '/tmp/c2_ftp'

    c2 = FTPC2(root_dir=root_dir, creds=default_creds)
    t1 = threading.Thread(target=serve_api, args=(c2,))
    t2 = threading.Thread(target=serve_ftp, args=(c2,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()
