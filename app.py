from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from collections import deque
import threading
import time

# ----------------------------
# Load model
# ----------------------------
model_path = "emotion_cnn_model.h5"
model = load_model(model_path)
img_width, img_height = 48, 48
emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# ----------------------------
# Flask app
# ----------------------------
app = Flask(__name__)

# ----------------------------
# Video capture
# ----------------------------
cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# ----------------------------
# Emotion history for chart
# ----------------------------
history_len = 100
emotion_history = deque(maxlen=history_len)
running = False
lock = threading.Lock()
selected_filter = 'none'

# ----------------------------
# Filters
# ----------------------------
def apply_filter(frame, filter_type):
    if filter_type == 'sketch':
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray
        frame = cv2.cvtColor(inv, cv2.COLOR_GRAY2BGR)

    elif filter_type == 'emboss':
        kernel = np.array([[ -2, -1, 0],
                           [ -1, 1, 1],
                           [ 0, 1, 2]])
        frame = cv2.filter2D(frame, -1, kernel) + 128

    elif filter_type == 'sepia':
        sepia_filter = np.array([[0.272,0.534,0.131],
                                 [0.349,0.686,0.168],
                                 [0.393,0.769,0.189]])
        frame = cv2.transform(frame, sepia_filter)
        frame = np.clip(frame,0,255).astype(np.uint8)

    elif filter_type == 'invert':
        frame = 255 - frame

    elif filter_type == 'gray':
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    elif filter_type == 'blur':
        frame = cv2.GaussianBlur(frame, (25,25), 0)

    elif filter_type == 'cartoon':
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(gray, 255,
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(frame, 9, 250, 250)
        frame = cv2.bitwise_and(color, color, mask=edges)

    elif filter_type == 'pencil':
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray
        blur = cv2.GaussianBlur(inv, (21,21), 0)
        frame = cv2.divide(gray, 255 - blur, scale=256)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    elif filter_type == 'warm':
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_AUTUMN)

    elif filter_type == 'cool':
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_OCEAN)

    elif filter_type == 'hot':
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_HOT)

    elif filter_type == 'winter':
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_WINTER)

    elif filter_type == 'vintage':
        frame = frame.astype(np.float32)
        frame[:,:,0] *= 0.9  # Blue
        frame[:,:,1] *= 0.95 # Green
        frame[:,:,2] *= 0.8  # Red
        frame = np.clip(frame, 0, 255).astype(np.uint8)

    elif filter_type == 'lomo':
        frame = cv2.addWeighted(frame, 1.5, frame, 0, -100)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame[:,:,1] = cv2.equalizeHist(frame[:,:,1])
        frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)

    elif filter_type == 'cartoon2':
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 5)
        edges = cv2.Canny(blur, 50, 150)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        frame = cv2.bitwise_and(frame, edges)

    elif filter_type == 'posterize':
        levels = 4
        div = 256 // levels
        frame = frame // div * div + div // 2

    elif filter_type == 'solarize':
        thresh = 128
        frame = np.where(frame > thresh, 255 - frame, frame).astype(np.uint8)

    elif filter_type == 'cold':
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_COOL)

    elif filter_type == 'spring':
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_SPRING)

    return frame

# ----------------------------
# Video generator
# ----------------------------
def generate_frames():
    global running
    while True:
        if running:
            success, frame = cap.read()
            if not success:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            for (x, y, w, h) in faces:
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (img_width, img_height))
                face_img = face_img.astype("float32") / 255.0
                face_img = np.expand_dims(face_img, axis=0)
                face_img = np.expand_dims(face_img, axis=-1)

                predictions = model.predict(face_img, verbose=0)
                emotion_idx = np.argmax(predictions)
                emotion = emotion_labels[emotion_idx]

                with lock:
                    emotion_history.append(emotion)

                # Draw rectangle and label
                cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
                cv2.putText(frame, emotion, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

            # Apply selected filter
            frame = apply_filter(frame, selected_filter)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.1)

# ----------------------------
# Routes
# ----------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_stream', methods=['POST'])
def toggle_stream():
    global running
    running = not running
    return jsonify({'running': running})

@app.route('/set_filter', methods=['POST'])
def set_filter():
    global selected_filter
    data = request.get_json()
    selected_filter = data.get('filter', 'none')
    return jsonify({'filter': selected_filter})

@app.route('/get_emotion_history')
def get_emotion_history():
    with lock:
        history_list = list(emotion_history)
    counts = {label: history_list.count(label) for label in emotion_labels}
    return jsonify(counts)

@app.route('/get_dominant_emotion')
def get_dominant_emotion():
    """
    Returns the dominant emotion from the recent emotion history.
    This will be used by the frontend gamification to check if the
    user is matching the target emotion.
    """
    with lock:
        history_list = list(emotion_history)
    if history_list:
        dominant = max(set(history_list), key=history_list.count)
    else:
        dominant = None
    return jsonify({'dominant': dominant})

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
