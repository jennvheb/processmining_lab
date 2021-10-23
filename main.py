from flask.app import Flask
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.filtering.log.attributes import attributes_filter
import pm4py
from pm4py.util.xes_constants import KEY_KEYS
from alpha_miner import Alpha
from heuristic_miner import Heuristic
import os
from flask import Flask, flash, request, redirect, url_for, render_template, Markup
from werkzeug.utils import secure_filename
import base64
from io import BytesIO

def mining(xes):
    log = xes_importer.apply(xes)
    tracefilter_log_pos = attributes_filter.apply_events(log, ["complete"], parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: "lifecycle:transition", attributes_filter.Parameters.POSITIVE: True})
    variants = pm4py.get_variants_as_tuples(tracefilter_log_pos)
    return variants

def alpha_algo(variants):
    Alpha(variants.keys())

def heuristic_algo(variants, freq_thrshld, ms_thrshold):
    Heuristic(variants.keys(), freq_thrshld, ms_thrshold)


UPLOAD_FOLDER = '/Users/jenny/processmining_lab/uploads'
ALLOWED_EXTENSIONS = set(['xes'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def main_page():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            sfilename = secure_filename(file.filename)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], sfilename)
            # Now save to this `output_path` and pass that same var to your mining function
            file.save(output_path)
            pro_file = mining(output_path)

            if 'Alpha Miner' in request.form:
                alpha_algo(pro_file)
                img_url = url_for('static', filename='alpha.gv.svg')
                return render_template('svg.html', img_url=img_url)

                #return render_template('upload.html', file=processed_file)
            
            elif 'Heuristic Miner' in request.form and 'Absolute' in request.form and 'Relative' in request.form:
                frequency = request.form['Absolute']
                dependency = request.form['Relative']
                heuristic_algo(pro_file, frequency, dependency)
                img_url = url_for('static', filename='cnet.gv.svg')
                return render_template('cnet.html', img_url=img_url)



if __name__==('__main__'):
    app.run(debug=True)