'''
Script to create fortigate service objects.
object type: tcp and udp single ports only.
'''

from flask import Flask, request, render_template_string, Response
import pandas as pd
from io import StringIO
import warnings
warnings.filterwarnings("ignore", message="Data Validation extension is not supported and will be removed")

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<title>FortiGate Service (TCP/UDP) Object Generator</title>
<h3>Fortigate - Create script for Service (TCP/UDP) objects (Single ports only)</h3>
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
        cli_output.write(f"config firewall service custom\n")

        for index,row in reader.iterrows():

            type = str(row['type'])
            port = str(row['port']).strip()
            comment = row.get('comment', '')

            if type == "tcp":
                cli_output.write(f" edit \"{type}_{port}\"\n")
                cli_output.write(f"     set tcp-portrange {port}\n")
                            
                if comment:
                    cli_output.write(f"     set comment \"{comment}\"\n")
                    cli_output.write(f"next\n")
            
            elif type == "udp":
                cli_output.write(f" edit \"{type}_{port}\"\n")
                cli_output.write(f"     set udp-portrange {port}\n")
                            
                if comment:
                    cli_output.write(f"     set comment \"{comment}\"\n")
                    cli_output.write(f"next\n")
                
            else:
               pass
    
        cli_output.write(f"end\n\n")

        output_text = cli_output.getvalue()
        #print(f'{output_text}')
                
        return Response(
           output_text,
           mimetype="text/plain",
            headers={"Content-Disposition": "attachment;filename=service_object_output.txt"}
        )
    
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)
