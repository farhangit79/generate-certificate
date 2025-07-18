#!/home/qurefa00/.venv/bin/gunicorn

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.exceptions import NotFound

# App1 - Upload a PFX file to extract Certificate and Private Key
from app1 import app as app1
# App2 - Upload Certificate and Private Key to create PFX file
from app2 import app as app2
# App3 - Generate CSR and Un-Encrypted Private Key (Algorithm: RSA, Key-Length Options: 2048 & 4096)
from app3 import app as app3
# App4 - Generate CSR and Un-Encrypted Private Key (Algorithm: ECC, Key-Length: 256)
from app4 import app as app4
# App5 - Fortigate - Create script for address objects.
from app5 import app as app5
# Ap6 - Fortigate - Create script for Service (TCP/UDP) objects (Single ports only)
from app6 import app as app6

application = DispatcherMiddleware(NotFound(), {
    '/app1': app1,
    '/app2': app2,
    '/app3': app3,
    '/app4': app4,
    '/app5': app5,
    '/app6': app6
})


