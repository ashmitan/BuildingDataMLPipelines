import os
#import magic
from flask import Flask, flash, render_template, request, redirect
from werkzeug.utils import secure_filename
from downloads.s3_demo import upload_file_tos3

#UPLOAD_FOLDER1 = 'C:/Users/Ashmita/Desktop/Data pipeline/Assignment3'
UPLOAD_FOLDER = 'Raw_Images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
BUCKET ='info7374-image-detection'
ACCESS_SECRET_KEY = 'AKIAYLW4Z2L4WDOWIBOP'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "secret key"

@app.route("/")
def home():
    return render_template("UploadImage.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['POST'])
def upload_file():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			upload_file_tos3(f"Raw_Images/{file.filename}", BUCKET)
			flash('File successfully uploaded')
			return redirect('/')
		else:
			flash('Allowed file types are png, jpg, jpeg')
			return redirect(request.url)

if __name__ == "__main__":
    app.run(debug=True)