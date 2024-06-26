from flask import Flask, render_template, request, Response, jsonify, url_for
import serial
import cv2
import numpy as np
import time
import os
from threading import Thread

global track_distance 
track_distance = 50
global distance
distance = 0  # Initialize the distance variable

try:
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    print('Serial Connection established')
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    ser = None
ser.flushInput()
camera = cv2.VideoCapture(0)
# Load YOLOv3-tiny
net = cv2.dnn.readNet("yolov3-tiny.weights", "yolov3-tiny.cfg")
layer_names = net.getLayerNames()
try:
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
except IndexError:
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Filter for the class "person"
person_class_id = classes.index("person")

tracker = cv2.TrackerKCF_create()
initBB = None

# Variables pour la position de l'objet et les options de détection
object_position = {"x": None, "y": None, "centered": None}
auto_center = False
detect_person = True
self_distance = False

# Crée un dossier pour sauvegarder les photos
if not os.path.exists('photos'):
    os.makedirs('photos')

# Variable pour stocker le chemin de la dernière photo prise
last_photo_path = None

def convert_key(key):
    conversion = {'z': '10', 's': '11', 'q': '12', 'd': '13'}
    return conversion.get(key, None)

def generate_frames():
    global initBB, tracker, object_position, auto_center, detect_person, distance, self_distance, track_distance
    frame_skip = 0  # Skip frames to reduce processing load
    move_delay = 0.1  # Delay before moving again (seconds)
    last_move_time = time.time()  # Track the time of the last movement
    frame_counter = 0
    start_time = time.time()
    track1 = int(track_distance)+2
    track2 = int(track_distance)-2



    while True:
        track1 = int(track_distance)+2
        track2 = int(track_distance)-2
        
        print(track1,":", track2)
        if self_distance == True:
            
            if float(distance) >= track1:
                ser.write(b'10')
                            
            elif float(distance) <= track2:
                ser.write(b'11')
                            
            else:
                ser.write(b'15')
        
        
            
            
        success, frame = camera.read()  # Read the camera frame
        if not success:
            break
        else:
            frame = cv2.resize(frame, (320, 240))  # Reduce the resolution for faster processing
            height, width, channels = frame.shape
            frame_center_x, frame_center_y = width // 2, height // 2
            
            frame_skip += 1
            if frame_skip % 3 != 0:  # Skip every 3rd frame
                continue

            frame_counter += 1
            elapsed_time = time.time() - start_time
            fps = frame_counter / elapsed_time

            if initBB is not None:
                # Update tracker and get position of tracked object
                (success, box) = tracker.update(frame)
                if success:
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    center_x, center_y = x + w // 2, y + h // 2
                    object_position["x"], object_position["y"] = center_x, center_y
                    object_position["centered"] = abs(center_x - frame_center_x) < 20 and abs(center_y - frame_center_y) < 20

                    if auto_center:
                        current_time = time.time()
                        if center_x < frame_center_x - 20:
                            if current_time - last_move_time > move_delay:
                                ser.write(b'12')  # Move camera to the left
                                last_move_time = current_time
                                time.sleep(0.05)
                                ser.write(b'15')
                        elif center_x > frame_center_x + 20:
                            if current_time - last_move_time > move_delay:
                                ser.write(b'13')  # Move camera to the right
                                last_move_time = current_time
                                time.sleep(0.05)
                                ser.write(b'15')
                        else:
                            ser.write(b'15')  # Stop movement when centered
                        
                    
                    
                    
                else:
                    initBB = None  # Reset if tracking fails
                    object_position = {"x": None, "y": None, "centered": None}
            elif detect_person:
                # Detecting objects
                blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
                net.setInput(blob)
                outs = net.forward(output_layers)

                class_ids = []
                confidences = []
                boxes = []

                for out in outs:
                    for detection in out:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        if confidence > 0.2 and class_id == person_class_id:
                            center_x = int(detection[0] * width)
                            center_y = int(detection[1] * height)
                            w = int(detection[2] * width)
                            h = int(detection[3] * height)

                            x = int(center_x - w / 2)
                            y = int(center_y - h / 2)

                            boxes.append([x, y, w, h])
                            confidences.append(float(confidence))
                            class_ids.append(class_id)

                indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

                for i in range(len(boxes)):
                    if i in indexes:
                        x, y, w, h = boxes[i]
                        label = str(classes[class_ids[i]])
                        confidence = confidences[i]
                        color = (0, 255, 0)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(frame, f"{label} {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                        # Initialize tracker with the first detected object
                        if initBB is None:
                            initBB = (x, y, w, h)
                            tracker = cv2.TrackerKCF_create()
                            tracker.init(frame, initBB)
                            center_x, center_y = x + w // 2, y + h // 2
                            object_position["x"], object_position["y"] = center_x, center_y
                            object_position["centered"] = abs(center_x - frame_center_x) < 20 and abs(center_y - frame_center_y) < 20

            # Draw FPS on the frame
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
def read_distance_from_serial():
    global distance
    ser.flush()
    ser.flushInput()
    while True:
        if ser.in_waiting > 0:
            if distance != ser.readline().decode('utf-8').strip():
                line = ser.readline().decode('utf-8').strip()
                distance = line
                print(f"Distance: {line} cm")

            
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/key_press', methods=['POST'])
def key_press():
    data = request.json
    key = data.get('key')
    converted_key = convert_key(key)
    if converted_key and ser:
        ser.write(converted_key.encode())
        return 'Key press detected: {}'.format(key)
    return 'Invalid key press detected: {}'.format(key)

@app.route('/key_release', methods=['POST'])
def key_release():
    if ser:
        ser.write(b'15')
    return 'Key released'

@app.route('/capture_photo')
def capture_photo():
    global last_photo_path
    ret, frame = camera.read()
    if ret:
        timestamp = int(time.time())
        photo_path = os.path.join('photos', f'photo_{timestamp}.jpg')
        cv2.imwrite(photo_path, frame)
        last_photo_path = photo_path
        return jsonify({"message": "Photo captured successfully!"})
    return jsonify({"message": "Failed to capture photo."})

@app.route('/last_photo')
def last_photo():
    if last_photo_path:
        return jsonify({"path": url_for('static', filename=last_photo_path[len("static/"):] )})
    return jsonify({"path": ""})

@app.route('/object_position')
def get_object_position():
    # Assurez-vous que les valeurs dans object_position sont sérialisables
    position = {key: (value if value is not None else None) for key, value in object_position.items()}
    return jsonify(position)

@app.route('/toggle_auto_center', methods=['POST'])
def toggle_auto_center():
    global auto_center
    data = request.json
    auto_center = data.get('enabled', False)
    message = "Auto-center {}".format("enabled" if auto_center else "disabled")
    return jsonify({"message": message})

@app.route('/toggle_detect_person', methods=['POST'])
def toggle_detect_person():
    global detect_person
    data = request.json
    detect_person = data.get('enabled', True)
    message = "Person detection {}".format("enabled" if detect_person else "disabled")
    return jsonify({"message": message})

@app.route('/distance')
def get_distance():
    global distance
    return jsonify({"distance": distance})


@app.route('/auto_distance', methods=['POST'])
def auto_distance():
    global self_distance
    data = request.json
    self_distance = data.get('enabled', False)
    message = "Auto-center {}".format("enabled" if self_distance else "disabled")
    return jsonify({"message": message})

@app.route('/update_track_distance', methods=['POST'])
def update_track_distance():
    global track_distance
    data = request.json 
    track_distance = data.get('track_distance', 50)
    return jsonify({'status': 'success', 'track_distance': track_distance})

@app.route('/get_track_distance')
def get_track_distance():
    global track_distance
    return jsonify({'track_distance': track_distance})


"""
@app.route('/auto_distance', methods=['POST'])
def auto_distance():
    global distance
    if request.method == 'POST':
        try:
            data = request.get_json()
            enabled = data['enabled']

            if enabled:
                if float(distance) >= 105:
                    ser.write(b'10')
                    time.sleep(0.05)
                    ser.write(b'15')
                elif float(distance) <= 95:
                    ser.write(b'11')
                    time.sleep(0.05)
                    ser.write(b'15')
                return jsonify({"message": "Command sent successfully"})
            else:
                return jsonify({"message": "Auto distance is disabled"})
        except Exception as e:
            return jsonify({"message": str(e)})

    return jsonify({"message": "Invalid request method"})
"""
    

if __name__ == '__main__':
    os.makedirs('static/photos', exist_ok=True)
    serial_thread = Thread(target=read_distance_from_serial)

    serial_thread.start()

    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
