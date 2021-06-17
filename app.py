from flask import Flask, request, render_template, redirect, url_for, make_response
import io, time, zipfile,os
import flask
import pandas as pd
import NorthLink
app = Flask(__name__)

my_path = os.getcwd()+'\static'
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if request.files:
            dfotherActivities = pd.read_excel(request.files.get('otherActivities'))
            dfparticipantActivities = pd.read_excel(request.files.get('participantActivities'))
            dfcleanedReport = pd.read_excel(request.files.get('cleanedReport'))
            dfparticipantProject = pd.read_excel(request.files.get('participantProject'))
            if not dfcleanedReport.empty and not dfotherActivities.empty and not dfparticipantActivities.empty and not dfparticipantProject.empty:
                info = NorthLink.data_processing(dfcleanedReport,dfotherActivities,dfparticipantActivities,dfparticipantProject)
                zipped_file = zipFiles(info['files'],info['names'])
                response = make_response(zipped_file)
                response.headers["Content-Type"] = "application/octet-stream"
                response.headers["Content-Disposition"] = "attachment; filename=OutputFiles.zip"
                return response
        else:
            return redirect(url_for('dashboard'))
    return render_template('upload.html')

def zipFiles(files, names):
    outfile = io.BytesIO() 
    with zipfile.ZipFile(outfile, 'w') as zf:
        for name, data in zip(names,files):
           zf.writestr(name, data.to_csv(index=False))
    return outfile.getvalue()

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@app.route('/',)
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)