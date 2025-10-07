# main.py
from fastapi import FastAPI, WebSocket, UploadFile, File, Form, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import face_recognition
import numpy as np
import cv2
import os
import shutil
import json
import base64
from io import BytesIO
from PIL import Image

# --- Configuration & File Setup ---
app = FastAPI(title="Face Recognition API (File-Based)")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# File paths for simple persistence
ENCODINGS_FILE = "faces_data.npy"
META_FILE = "faces_meta.json"

# In-memory data structures
known_face_encodings = []
known_face_names = []


# --- Helper Functions ---
def save_faces():
    """Saves current state to disk for persistence."""
    try:
        # Save as a structured NumPy array of objects
        # This handles saving the list of NumPy arrays correctly
        np.save(ENCODINGS_FILE, np.array(known_face_encodings, dtype=object))
        
        with open(META_FILE, "w") as f:
            json.dump(known_face_names, f)
    except Exception as e:
        print(f"Error saving data: {e}")


def load_faces():
    """Loads saved state from disk on startup."""
    global known_face_encodings, known_face_names
    
    if os.path.exists(ENCODINGS_FILE) and os.path.exists(META_FILE):
        try:
            loaded_encodings = np.load(ENCODINGS_FILE, allow_pickle=True)
            
            # Convert the loaded NumPy array back into a list of NumPy arrays
            known_face_encodings = list(loaded_encodings)
            
            with open(META_FILE, "r") as f:
                known_face_names = json.load(f)
            
            print(f"✅ Loaded {len(known_face_names)} faces from storage.")
            
        except Exception as e:
            # This happens if the file is corrupted or empty
            print(f"Error loading data: {e}. Starting with empty list.")
            known_face_encodings = []
            known_face_names = []
            
# Load data on startup
load_faces()


# 1. Combined Enrollment Endpoint
@app.post("/upload", tags=["Enrollment"])
async def upload_photo(
    name: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...)
):
    """Registers a new user and face embedding in a single request."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # Save file temporarily
        with open(file_path, "wb") as buffer:
            file.file.seek(0) 
            shutil.copyfileobj(file.file, buffer)

        # Load image (Pillow/face_recognition handles RGB conversion)
        image = face_recognition.load_image_file(file_path)
        encodings = face_recognition.face_encodings(image)

    except Exception as e:
        # Catches general image processing errors (e.g., corrupted file)
        raise HTTPException(status_code=500, detail=f"Image processing failed: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

    # Store the result
    if len(encodings) > 0:
        known_face_encodings.append(encodings[0]) 
        known_face_names.append(f"{name} ({email})")
        save_faces()
        return {"message": "Face registered successfully", "name": name, "email": email}
    else:
        raise HTTPException(status_code=400, detail="No face detected in uploaded image.")


# 2. WebSocket for real-time recognition
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    TOLERANCE = 0.6 
    
    try:
        while True:
            try:
                # --- CORE LOGIC BLOCK ---
                
                # Receive base64 image data from frontend
                data = await websocket.receive_text()
                
                # Image Processing: Convert base64 -> Bytes -> PIL (RGB) -> NumPy Array
                header, encoded = data.split(",", 1)
                img_bytes = base64.b64decode(encoded)
                
                # Pillow loads image, converts to RGB, and then to NumPy array
                img = Image.open(BytesIO(img_bytes)).convert("RGB")
                frame = np.array(img)

                # Detect and encode faces
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)
                
                # Recognition Logic
                response = {"faces": []}
                
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    name = "Unknown"
                    min_distance = None

                    if known_face_encodings:
                        # This line requires all elements in the list to be numpy arrays!
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        
                        best_match_index = np.argmin(face_distances)
                        min_distance = face_distances[best_match_index]

                        if min_distance < TOLERANCE:
                            name = known_face_names[best_match_index]

                    # Prepare the data packet for the frontend
                    response["faces"].append({
                        "name": name,
                        "distance": float(min_distance) if min_distance is not None else None,
                        "location": [top, right, bottom, left]
                    })

                await websocket.send_json(response)

            # --- ERROR HANDLING ---
            except RuntimeError as e:
                # Catch specific errors like Dlib's image processing failures
                print(f"Dlib/Face Recognition Runtime Error: {e}. Skipping frame.")
            
            except Exception as e:
                # Catch ANY other error, log it, and cleanly break the connection
                print(f"CRITICAL WS LOOP ERROR: {e}. Closing connection.")
                break # Exit the while True loop cleanly

    except WebSocketDisconnect:
        # Normal client disconnection event
        print("INFO: Client disconnected normally.")
    
    except Exception as e:
        # Final catch for closure errors, suppressing the framework's own RuntimeError
        print(f"INFO: Error during final socket closure caught: {e}")
    
    finally:
        # Attempt to close the socket if it hasn't been closed already
        try:
             await websocket.close()
        except RuntimeError:
             pass # Suppress 'Cannot call "send" once a close message has been sent.'