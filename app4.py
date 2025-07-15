# CN included by default in SAN

from flask import Flask, request, render_template_string, send_file
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509 import DNSName, SubjectAlternativeName
import tempfile
import os
#from io import BytesIO
#from datetime import datetime, timezone

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
<title>CSR Generator with SAN</title>
</head>
<body>
  <h2>Generate CSR and Un-Encrypted Private Key (Algorithm: ECC, Key-Length: 256)</h2>
  <h4>CN will be auto added in SAN.</h4>
  <form method="post">
    <span style="margin-right: 40px;">Common Name (CN) (Required) :</span> <input name="common_name" required><br><br>
    <span style="margin-right: 100px;">Country (C) (Required) :</span> <input name="country" maxlength="2"><br><br>
    <span style="margin-right: 187px;">State (ST) :</span> <input name="state"><br><br>
    <span style="margin-right: 175px;">Locality (L) :</span> <input name="locality"><br><br>
    <span style="margin-right: 145px;">Organization (O) :</span> <input name="organization"><br><br>
    <span style="margin-right: 90px;">Organizational Unit (OU) :</span> <input name="org_unit"><br><br>
    <span style="margin-right: 215px;">Email :</span> <input name="email"><br><br>
    <span style="margin-right: 87px;">SANs (comma-separated) :</span> <input name="san"><br><br>
    <button type="submit">Generate</button>
  </form>
  {% if csr_link %}
    <h3>Download Files</h3>
    <a href="{{ csr_link }}">Download CSR</a><br>
    <a href="{{ key_link }}">Download Un-Encrypted Private Key</a>
  {% endif %}
    
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def generate_csr():
    if request.method == 'POST':
        # Build subject
        name_attrs = [
            x509.NameAttribute(NameOID.COMMON_NAME, request.form['common_name']),
        ]
        if request.form['country']:
            name_attrs.append(x509.NameAttribute(NameOID.COUNTRY_NAME, request.form['country']))
        if request.form['state']:
            name_attrs.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, request.form['state']))
        if request.form['locality']:
            name_attrs.append(x509.NameAttribute(NameOID.LOCALITY_NAME, request.form['locality']))
        if request.form['organization']:
            name_attrs.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, request.form['organization']))
        if request.form['org_unit']:
            name_attrs.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, request.form['org_unit']))
        if request.form['email']:
            name_attrs.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, request.form['email']))

        subject = x509.Name(name_attrs)

        # Generate private key
        key = ec.generate_private_key(ec.SECP256R1())
        key_pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Create CSR builder
        csr_builder = x509.CertificateSigningRequestBuilder().subject_name(subject)

        # Parse SANs and include Common Name by default
        common_name = request.form['common_name'].strip()
        san_input = request.form.get('san', '').strip()

        # Split SAN input and ensure CN is included
        san_set = set(s.strip() for s in san_input.split(',') if s.strip())
        san_set.add(common_name)  # Ensure CN is in SAN

        san_list = [DNSName(name) for name in sorted(san_set)]
        if san_list:
            csr_builder = csr_builder.add_extension(
                SubjectAlternativeName(san_list),
                critical=False
            )

        # Sign the CSR
        csr = csr_builder.sign(key, hashes.SHA256())
        csr_pem = csr.public_bytes(serialization.Encoding.PEM)

        # Save to temp files
        key_file = tempfile.NamedTemporaryFile(delete=False, suffix=".key")
        csr_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csr")
        key_file.write(key_pem)
        csr_file.write(csr_pem)
        key_file.close()
        csr_file.close()

        # Zip and send
        import zipfile
        zip_path = tempfile.NamedTemporaryFile(delete=False, suffix='.zip').name
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(key_file.name, "private.key")
            zipf.write(csr_file.name, "request.csr")

        os.unlink(key_file.name)
        os.unlink(csr_file.name)

        return send_file(zip_path, as_attachment=True, download_name="csr_and_key.zip")

    return render_template_string(HTML_FORM)

