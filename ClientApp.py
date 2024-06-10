import cv2
from flask import Flask, redirect, url_for, render_template, request, Response, flash, jsonify
from werkzeug.utils import secure_filename  # it will replace or make changes in the original file names to secure it
from werkzeug.exceptions import RequestEntityTooLarge
from utils.detections import Detector
from werkzeug.utils import secure_filename, send_from_directory
import time
import os
import numpy as np

# create a object of flask
app = Flask(__name__)

app.config["UPLOAD_DIRECTORY"] = "uploads/"  # global file directory name to store files
app.config["MAX_CONTENT_LENGTH"] = 950 * 1024 *1024 # 950MB
app.config["ALLOWED_EXTENSIONS"] = ['.jpg', '.jpeg', '.png', '.mp4']
app.config["SECRET_KEY"] = "secretkey"

model_path = "Weights/ppe.pt"

uploadFile = []

camera = None
streaming_mode = None

target_width = 640
target_height = 480


# create app
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ComputerVision")
def ComputerVision():
    return render_template("ComputerVision.html")

# for object detection
@app.route("/objectDetection")
def objectDetection():
    return render_template("ObjectDetection.html")

# for PersonalProtectiveEquipment
@app.route("/PersonalProtectiveEquipment")
def PersonalProtectiveEquipment():
    return render_template("PersonalProtectiveEquipment.html", target_width=target_width, target_height=target_height)

@app.route("/handDetector")
def handDetector():
    return render_template("handDetector.html", target_width=target_width, target_height=target_height)

####################################################### For Web Camera #######################################################

@app.route('/toggle_webcam', methods=['POST'])
def toggle_webcam():
    global camera, streaming_mode
    global target_height, target_width
    iswebcam = request.json.get('iswebcam', False)
    if iswebcam:
        streaming_mode = 'webcam'
        if camera is None or not camera.isOpened():
            camera = Detector(videoPath=0, target_video_width=target_width)
            target_width = camera.target_width
            target_height = camera.target_height

            print(f"width: {target_width}, height:{target_height}")
        return jsonify({'status': 'webcam_on', 'target_width': target_width, 'target_height': target_height})
    else:
        streaming_mode = None
        if camera is not None and camera.isOpened():
            camera.release()
            camera = None
        return jsonify({'status': 'webcam_off'})



@app.route('/stop_streaming', methods=['POST'])
def stop_streaming():
    global camera, streaming_mode
    streaming_mode = None
    if camera is not None and camera.isOpened():
        camera.release()
        camera = None
    return jsonify({'status': 'streaming_off'})

def gen_frames():  # generate frame by frame from camera or file
    global camera
    
    while True:
        if camera is None or not camera.cam.isOpened():
            break
        
        frame = camera.outputFrames()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.1)

@app.before_request
def before_request():
    global camera
    if request.endpoint != 'video_feed':
        if camera is not None and camera.cam.isOpened():
            camera.cam.release()
            camera = None

####################################################### For Upload File #######################################################

def allowed_file(filename):
    return '.' in filename and os.path.splitext(filename)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload_file', methods=['POST'])
def upload_file():
    global camera, streaming_mode
    global target_height, target_width
    if 'uploadedFile' not in request.files:
        flash('No file part')
        return redirect(url_for('PersonalProtectiveEquipment'))
    
    file = request.files['uploadedFile']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('PersonalProtectiveEquipment'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_DIRECTORY'], filename)
        file.save(filepath)
        uploadFile.append(filepath)
        
        streaming_mode = 'file'
        if camera is not None and camera.cam.isOpened():
            camera.cam.release()
        camera = Detector(videoPath=filepath, target_video_width=target_width)
        target_width = camera.target_width
        target_height = camera.target_height

        print(f"width: {target_width}, height:{target_height}")
        return jsonify({'status': 'file_uploaded', 'target_width': target_width, 'target_height': target_height})
    
    flash('Invalid file type')
    return redirect(url_for('PersonalProtectiveEquipment'))


# for live stream detection
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
