# server/server.py
from flask import Flask, request, Response, render_template
import cv2
import numpy as np
import threading

app = Flask(__name__)

current_frame = None

frame_lock = threading.Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream', methods=['POST'])
def stream():
    global current_frame

    if 'frame' not in request.files:
        return "No frame received", 400

    frame = request.files['frame'].read()

    np_frame = np.frombuffer(frame, np.uint8)
    decoded_frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)

    with frame_lock:
        current_frame = decoded_frame

    return "Frame received", 200

def generate():
    global current_frame

    while True:
        with frame_lock:
            if current_frame is not None:
                _, buffer = cv2.imencode('.jpg', current_frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        cv2.waitKey(1)

@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3333, debug=True)
