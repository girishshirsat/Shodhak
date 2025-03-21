import cv2
import os
import exifread
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from ultralytics import YOLO
import numpy as np

# Load YOLO model
model = YOLO("yolov8n.pt")

def home(request):
    return render(request, 'detection/home.html') 

def upload(request):
    return render(request, 'detection/upload.html') 

def get_gps_info(image_path):
    """Extract GPS coordinates from image metadata if available"""
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)

    if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
        lat_values = tags['GPS GPSLatitude'].values
        lon_values = tags['GPS GPSLongitude'].values

        lat = float(lat_values[0]) + (float(lat_values[1]) / 60) + (float(lat_values[2]) / 3600)
        lon = float(lon_values[0]) + (float(lon_values[1]) / 60) + (float(lon_values[2]) / 3600)

        return lat, lon

    return None, None  # Return None if no GPS data is found

def analyze_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        file_path = default_storage.save('uploads/' + image_file.name, image_file)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        # Initialize latitude and longitude before using them
        latitude, longitude = None, None

        # Extract GPS coordinates
        latitude, longitude = get_gps_info(full_path)

        # Load and process image
        image = cv2.imread(full_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Run YOLO object detection
        results = model(image)
        detected_objects = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = model.model.names[class_id]
                detected_objects.append(label)

        return render(request, 'detection/result.html', {
            'image_url': settings.MEDIA_URL + file_path,
            'detected_objects': detected_objects,
            'latitude': latitude,  # Now this is always defined
            'longitude': longitude
        })

    return render(request, 'detection/upload.html')
