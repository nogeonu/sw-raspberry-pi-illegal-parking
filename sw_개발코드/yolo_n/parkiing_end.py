import datetime
import time
import os
from PIL import Image
import cv2
import numpy as np
import easyocr
from ultralytics import YOLO
import pymysql
import re

# Configuration
CONFIDENCE_THRESHOLD = 0.6
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
SAVE_DIR = 'detected_plates'
os.makedirs(SAVE_DIR, exist_ok=True)

# Load the custom YOLO model
model = YOLO('/Users/nogeon-u/Desktop/New_car2_pt/train2/weights/best.pt')

# Initialize EasyOCR Reader with Korean language support
reader = easyocr.Reader(['en', 'ko'])

# Initialize the webcam using OpenCV just for video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

last_plate_text = ""
plate_start_time = {}
last_sent_time = {}

# Database connection
def connect_to_database():
    try:
        conn = pymysql.connect(
            host="best.hnu.kr",
            user="user_sw2024",
            passwd="sw2024",
            db="db_sw2024",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        print("Database connected.")
        return conn
    except pymysql.Error as e:
        print(f"Database connection failed: {e}")
        return None

def insert_into_database(conn, datetime, license_plate, parking_status, stopping_time):
    try:
        with conn.cursor() as cur:
            sql = "INSERT INTO illegal_parking (datetime, license_plate, parking_status, stopping_time) VALUES (%s, %s, %s, %s)"
            cur.execute(sql, (datetime, license_plate, parking_status, stopping_time))
            conn.commit()
            print(f"Inserted into database: {datetime}, {license_plate}, {parking_status}, {stopping_time}")
    except pymysql.Error as e:
        print(f"Failed to insert data: {e}")

def clean_plate_text(text):
    match = re.match(r'\d{2,3}[가-힣] \d{4}', text)
    if match:
        return match.group(0)
    return None

def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

# 이미지 밝기와 대비를 조정하는 함수 
def adjust_brightness_contrast(image, alpha=1.5, beta=0):
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

def detect_and_recognize(frame, conn):
    global last_plate_text, plate_start_time, last_sent_time

    # Convert the frame to RGB (PIL format)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_frame)

    # Run YOLO detection
    detection = model(rgb_frame)[0]

    detected_any = False

    for data in detection.boxes.data.tolist():  # data : [xmin, ymin, xmax, ymax, confidence_score, class_id]
        confidence = float(data[4])
        if confidence < CONFIDENCE_THRESHOLD:
            continue

        detected_any = True

        xmin, ymin, xmax, ymax = map(int, data[:4])

        # Crop the detected license plate
        cropped_image = pil_image.crop((xmin, ymin, xmax, ymax))
        cropped_array = np.array(cropped_image)

        # Enhance the cropped image by adjusting brightness and contrast
        enhanced_image = adjust_brightness_contrast(cropped_array)

        # Convert to grayscale and apply binary thresholding for OCR
        gray_image = cv2.cvtColor(enhanced_image, cv2.COLOR_RGB2GRAY)
        _, binary_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # OCR using EasyOCR
        result = reader.readtext(binary_image)
        for (bbox, text, prob) in result:
            print(f'Detected text: {text} (Confidence: {prob:.2f})')

            # Clean the detected text
            cleaned_text = clean_plate_text(text)
            if cleaned_text is None:
                continue

            current_time = time.time()
            
            # Check if this is the same plate as before
            if cleaned_text == last_plate_text:
                # Calculate the parking duration
                duration = current_time - plate_start_time[cleaned_text]
                stopping_time = format_duration(duration)
                print(f'Plate {cleaned_text} has been parked for {duration:.2f} seconds')
                parking_status = '불법주차' if duration >= 30 else '불법정차'
            else:
                # New plate detected
                last_plate_text = cleaned_text
                plate_start_time[cleaned_text] = current_time
                stopping_time = format_duration(0)
                parking_status = '불법정차'

            # Check if 5 seconds have passed since the last insert
            if cleaned_text not in last_sent_time or current_time - last_sent_time[cleaned_text] > 5:
                last_sent_time[cleaned_text] = current_time

                # Save the cropped image
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                detected_plate_path = os.path.join(SAVE_DIR, f'detected_plate_{timestamp}.png')
                cv2.imwrite(detected_plate_path, cv2.cvtColor(enhanced_image, cv2.COLOR_RGB2BGR))
                print(f'Saved image: {detected_plate_path}')

                # Save the detected text to a file
                with open(os.path.join(SAVE_DIR, 'detected_plates.txt'), 'a') as f:
                    f.write(f'{timestamp} {cleaned_text}\n')
                print(f'Saved text to file: {cleaned_text}')

                # Insert detected text, timestamp, parking status, and stopping time into database
                current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                insert_into_database(conn, current_datetime, cleaned_text, parking_status, stopping_time)

            # Draw bounding box and text on the frame
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), GREEN, 2)
            cv2.putText(frame, cleaned_text, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, WHITE, 2)

    if not detected_any:
        print('No license plate detected in this frame.')

def main():
    conn = connect_to_database()
    if conn is None:
        print("Failed to connect to the database. Exiting.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print('Cam Error')
                break

            start = datetime.datetime.now()

            # Perform detection and recognition
            detect_and_recognize(frame, conn)

            end = datetime.datetime.now()
            total = (end - start).total_seconds()
            print(f'Time to process 1 frame: {total * 1000:.0f} milliseconds')

            # Display the frame with OpenCV (optional)
            cv2.imshow('frame', frame)
            
            if cv2.waitKey(1) == ord('q'):
                break
    except KeyboardInterrupt:
        print("Exit")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        conn.close()

if __name__ == "__main__":
    main()
