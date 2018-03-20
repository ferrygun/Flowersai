import os
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import numpy as np
import argparse
import imutils
import cv2
import time
import uuid

from os.path import basename

IMGSIZE = 28
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def my_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4()) # Convert UUID format to a Python string.
    random = random.upper() # Make all characters uppercase.
    random = random.replace("-","") # Remove the UUID '-'.
    return random[0:string_length] # Return the random string.

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        import time
        start_time = time.time()
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            #thisis = app.catordog.run(file_path)
            print(file_path)
            image=cv2.imread(file_path)
            orig = image.copy()
            image = cv2.resize(image, (IMGSIZE, IMGSIZE))
            image = image.astype("float") / 255.0
            image = img_to_array(image)
            image = np.expand_dims(image, axis=0)
            MODEL_PATH = "flowers.model"
            model = load_model(MODEL_PATH)

            val = (daisy, dandelion, roses, sunflowers, tulips) = model.predict(image)[0]

			# classify the input image
            print("daisy: ", model.predict(image)[0][0] * 100)
            print("dandelion: ", model.predict(image)[0][1] * 100)
            print("roses: ", model.predict(image)[0][2] * 100)
            print("sunflowers: ", model.predict(image)[0][3] * 100)
            print("tulips: ", model.predict(image)[0][4] * 100)

            label_name = ["daisy", "dandelion", "roses", "sunflowers", "tulips"]
            indx = np.argmax(val)
            print(label_name[indx])
            label = label_name[indx]
            proba = max(val)

            
            os.rename(file_path, os.path.join(app.config['UPLOAD_FOLDER'], label + '__' + my_random_string(6) + filename))


            print("--- %s seconds ---" % str (time.time() - start_time))
            return redirect("/")
            return redirect(url_for('uploaded_file',
                                    filename="facedetect-"+filename))

    from os import listdir
    from os.path import isfile, join
    htmlpic=""
    for f in listdir(UPLOAD_FOLDER):
        if isfile(join(UPLOAD_FOLDER,f)) and f != '.gitignore':
            print(f)
            htmlpic += """<span>""" + f.split('__')[0] + """--></span>""" + """
                <img width=200px height=150px src='uploads/"""+f+"""'>&nbsp;  &nbsp;
                """
    return '''
    <!doctype html>
    <head>
    <title>My Flowers</title>
    </head>
	<h1>Is Daisy, Dandelion, Rose, Sunflower or Tulip ?</h1>
    <h2>Upload flower image file</h2>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''+htmlpic

from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

from werkzeug import SharedDataMiddleware
app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})

if __name__ == "__main__":
    app.debug=True
    app.run(host='0.0.0.0', port=3000)