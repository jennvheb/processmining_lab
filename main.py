from werkzeug.wrappers import response
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.filtering.log.attributes import attributes_filter
import pm4py
from pm4py.util.xes_constants import KEY_KEYS
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.statistics.traces.generic.log import case_statistics
from alpha_miner import Alpha
from heuristic_miner import Heuristic
import os
from flask import Flask, request, url_for, render_template, after_this_request
from werkzeug.utils import secure_filename
import uuid


def preprocessing(xes):
    log = pm4py.read_xes(xes)
    activities = attributes_filter.get_attribute_values(log, "lifecycle:transition")
    if (len(activities.keys()) == 2):
        log = attributes_filter.apply_events(log, ["complete"], parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: "lifecycle:transition", attributes_filter.Parameters.POSITIVE: True})
    pm4py.get_variants_as_tuples(log)
    
    variants_count = case_statistics.get_variant_statistics(log)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
 

    ## to event list
    event_list = []
   
   
    for i in range(0, len(variants_count)):
        for e in range((variants_count[i]['count'])):
            stupl = variants_count[i]['variant']
            event_list.append(stupl)

    return event_list


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['xes'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        myuuid = uuid.uuid4()
        # check if the post request has the file part
        if 'file' not in request.files:
            return render_template('error.html')
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return render_template('error.html')

        if file and allowed_file(file.filename):
            sfilename = secure_filename(file.filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.mkdir(app.config['UPLOAD_FOLDER'])
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], sfilename)
            # Now save to this `output_path` and pass that same var to your mining function
            file.save(output_path)

            pro_file = preprocessing(output_path)
            #pro_file = pro_file2.keys()


            if 'Alpha Miner' in request.form:
                Alpha(pro_file, myuuid)
                img_url = url_for('static', filename=str(myuuid) + '.gv.svg')

                @after_this_request
                def remove_file(response):
                    os.remove(img_url)
                    return response
              
                titel = "Petri Net for Alpha Miner: " + sfilename    
                return render_template('upload.html', img_url=img_url, titel = titel)
             
                

            
            elif 'Submit' in request.form and 'Absolute' in request.form and 'Relative' in request.form:
                frequency = request.form['Absolute']
                dependency = request.form['Relative']
                Heuristic(pro_file, frequency, dependency, myuuid)
                img_url = url_for('static', filename=str(myuuid) + '.gv.svg')
                # put string as input as well
                titel = "Causal Net for Heuristic Miner " + sfilename
                descrx="[x] -> x describes the absolute number of edges between any pair of activities."
                descry="(y) -> y describes the relative number of edges between any pair of activities."
                return render_template('upload.html', img_url=img_url, titel=titel, descrx = descrx, descry = descry)
    return render_template('upload.html')

           


    



if __name__==('__main__'):
    app.run(debug=True)
    