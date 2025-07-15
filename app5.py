from flask import Flask, request, render_template_string, Response
import pandas as pd
from io import StringIO
import warnings
warnings.filterwarnings("ignore", message="Data Validation extension is not supported and will be removed")

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<title>FortiGate Address Object Generator</title>
<h3>Fortigate - Create script for address objects</h3>
<h4>Upload .xlsx format.</h4>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Generate>
</form>
"""

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        
        file = request.files.get('file')
        reader = pd.read_excel(file, sheet_name='objects', dtype=str)

        cli_output = StringIO()
        cli_output.write(f"config firewall address\n")

        for index,row in reader.iterrows():

            type = row['type']
            name = row['name']
            subnet = row['subnet']
            start_ip = row['start_ip']
            end_ip = row['end_ip']
            fqdn = row['fqdn']
            comment = row.get('comment', '')

            if type == "ipmask":
                cli_output.write(f" edit \"{name}\"\n")
                cli_output.write(f"     set type {type}\n")
                cli_output.write(f"     set subnet {subnet}\n")
            
                if comment:
                    cli_output.write(f"     set comment \"{comment}\"\n")
                    cli_output.write(f"next\n")
                
            elif type == "iprange":
                cli_output.write(f" edit \"{name}\"\n")
                cli_output.write(f"     set type {type}\n")
                cli_output.write(f"     set start-ip {start_ip}\n")
                cli_output.write(f"     set end-ip {end_ip}\n")
            
                if comment:
                    cli_output.write(f"     set comment \"{comment}\"\n")
                    cli_output.write(f"next\n")
               
            elif type == "fqdn":
                cli_output.write(f" edit \"{name}\"\n")
                cli_output.write(f"     set type {type}\n")
                cli_output.write(f"     set fqdn {fqdn}\n")
                            
                if comment:
                    cli_output.write(f"     set comment \"{comment}\"\n")
                    cli_output.write(f"next\n")
                
            else:
               print()
    
        cli_output.write(f"end\n\n")

        output_text = cli_output.getvalue()
                
        return Response(
            output_text,
            mimetype="text/plain",
            headers={"Content-Disposition": "attachment;filename=address_object_output.txt"}
        )
    
            
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)
