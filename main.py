from pm4py.algo.filtering.log.attributes import attributes_filter
import pm4py
from pm4py.util.xes_constants import KEY_KEYS
from pm4py.statistics.traces.generic.log import case_statistics
from alpha_miner import Alpha
from heuristic_miner import Heuristic
import os
from flask import Flask, request, url_for, render_template
from werkzeug.utils import secure_filename
import uuid


def preprocessing(xes):
    # read the xes file
    log = pm4py.read_xes(xes)

    # get all the values for lifecycle: transition
    activities = attributes_filter.get_attribute_values(log, "lifecycle:transition")
    # if there are two values (start and complete) then only keep the events that contain "complete"
    # if there are less than two values then that implies there is one or zero so there is no need to filter
    if (len(activities.keys()) == 2):
        log = attributes_filter.apply_events(log, ["complete"], parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: "lifecycle:transition", attributes_filter.Parameters.POSITIVE: True})
    # get only the activity attributes, for the alpha miner, this is enough
    pm4py.get_variants_as_tuples(log)
    # get the counts of the traces for the heuristic miner
    variants_count = case_statistics.get_variant_statistics(log)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
    # transform the current file into a list which contains all activity traces 
    event_list = []
    # variant is the activity trace and count is the number of times it occurs in the event log
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
        # if the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            return render_template('error.html')
        # secure the filename upload the file into the upload folder
        # create an upload folder if doesn't exist
        # then save the file
        if file and allowed_file(file.filename):
            sfilename = secure_filename(file.filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.mkdir(app.config['UPLOAD_FOLDER'])
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], sfilename)
            file.save(output_path)
            # read the xes-file and transform it in preprocessing
            pro_file = preprocessing(output_path)
            titel = "Output for: " + sfilename

            if 'Alpha Miner' in request.form:
                Alpha(pro_file, myuuid)
                # save the generated petri net from Alpha and return it along with the name of the original xes-file
                img_url = url_for('static', filename=str(myuuid) + '.gv.svg')
                return render_template('upload.html', img_url=img_url, titel = titel)
            
            elif 'Submit' in request.form and 'Absolute' in request.form and 'Relative' in request.form:
                frequency = request.form['Absolute']
                dependency = request.form['Relative']
                Heuristic(pro_file, frequency, dependency, myuuid)
                img_url = url_for('static', filename=str(myuuid) + '.gv.svg')
                descrx="[x] -> x describes the absolute number of edges between any pair of activities. Chosen threshold in this Causal Net: " + frequency
                descry="(y) -> y describes the relative number of edges between any pair of activities. Chosen threshold in this Causal Net: " + dependency
                return render_template('upload.html', img_url=img_url,  descrx = descrx, descry = descry, titel = titel)
        else: return render_template('error.html')
    return render_template('upload.html')



if __name__==('__main__'):
    app.run(debug=True)
    