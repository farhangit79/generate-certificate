#!/home/qurefa00/.venv/bin/python3

from flask import Flask, request, send_file, render_template_string
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
import os, tempfile, subprocess, zipfile


# Create pfx by combing certificate and key using OpenSSL

HTML_FORM = '''
<!doctype html>
<html>
<title>PFX Tool</title>
<h2>Upload Certificate and Private Key to create PFX file</h2>
<form method="POST" enctype="multipart/form-data">
    Certificate (.crt or .pem): <input type="file" name="cert2"><br><br>
    Private Key (.key): <input type="file" name="key2"><br><br>
    PFX Password: <input type="password" name="password2"><br><br>
    <input type="submit" value="Generate PFX">
</form>
</html>
'''

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        cert_file = request.files['cert2']
        key_file = request.files['key2']
        password = request.form['password2']

        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=".crt") as cert_temp, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".key") as key_temp, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".pfx") as pfx_temp:

            # Save uploaded files to temporary cert/key
            cert_temp.write(cert_file.read())
            key_temp.write(key_file.read())
            cert_temp.flush()
            key_temp.flush()

            # Generate PFX using OpenSSL
            try:
                subprocess.check_call([
                    "openssl", "pkcs12", "-export",
                    "-out", pfx_temp.name,
                    "-inkey", key_temp.name,
                    "-in", cert_temp.name,
                    "-passout", f"pass:{password}"
                ])
            except subprocess.CalledProcessError:
                return "Failed to generate PFX file", 500

            # Send PFX file to user
            response = send_file(pfx_temp.name, as_attachment=True, download_name="certificate.pfx")
        
        # Clean up temp files
        os.remove(cert_temp.name)
        os.remove(key_temp.name)
        os.remove(pfx_temp.name)

        return response  

    return render_template_string(HTML_FORM)

'''
def run_app():
    app.run(debug=True)


if __name__ == '__main__':
    app.run(port=6060,debug=True)
'''