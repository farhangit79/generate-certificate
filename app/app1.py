#!/home/qurefa00/.venv/bin/python3

from flask import Flask, request, send_file, render_template_string
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
import os, tempfile, subprocess, zipfile


# Extract certificate and key from pfx file

HTML_FORM = '''
<!doctype html>
<html>
<head>
<title>PFX Tool</title>
</head>
<body>
  <h2>Upload a PFX file to extract Certificate and Private Key</h2>
  <form method="POST" enctype="multipart/form-data">
    <label for="pfxfile">Choose PFX file:</label>
    <input type="file" name="pfxfile" required><br><br>
    <label for="password">PFX Password:</label>
    <input type="password" name="password"><br><br>
    <button type="submit">Upload & Download</button>
  </form>
</body>
</html>
'''

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_pfx():
    if request.method == 'POST':
        file = request.files['pfxfile']
        password = request.form.get('password', '').encode()

        if file:
            pfx_data = file.read()
            private_key, cert, _ = load_key_and_certificates(pfx_data, password)

            # Create temporary files and zip
            temp_dir = tempfile.mkdtemp()
            key_path = os.path.join(temp_dir, 'private.key')
            cert_path = os.path.join(temp_dir, 'certificate.crt')
            zip_path = os.path.join(temp_dir, 'pfx_output.zip')

            with open(key_path, 'wb') as key_file:
                key_file.write(private_key.private_bytes(
                    encoding=Encoding.PEM,
                    format=PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=NoEncryption()
                ))

            with open(cert_path, 'wb') as cert_file:
                cert_file.write(cert.public_bytes(Encoding.PEM))

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(cert_path, arcname='certificate.crt')
                zipf.write(key_path, arcname='private.key')

            return send_file(zip_path, as_attachment=True, download_name='pfx_extracted.zip')

    return render_template_string(HTML_FORM)

'''
def run_app():
    app.run(debug=True)


if __name__ == '__main__':
    app.run(port=6060,debug=True)
'''