import cv2
import os
import shutil

# --- Configuration (Must match attendance.py) ---
HAAR_CASCADE_PATH = "haarcascade_frontalface_default.xml"
TRAIN_IMAGE_PATH = "TrainingImage"

# Ensure the Haar Cascade file is available
if not os.path.exists(HAAR_CASCADE_PATH):
    print("Error: Haar Cascade file not found.")
    print(f"Please place '{HAAR_CASCADE_PATH}' in the current directory.")
    exit()

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)

def takeImages(Id, name):
    """
    Captures 30 face images for the given student ID and name.
    Images are saved to the TrainingImage directory.
    """
    
    # 1. Input Validation
    Id = str(Id).strip()
    name = str(name).strip()
    if not Id or not name:
        print("Error: Enrollment ID and Name must be provided.")
        return False
        
    # 2. Setup Directories
    image_dir = os.path.join(TRAIN_IMAGE_PATH, Id + "_" + name)
    
    # Check if the directory already exists (suggesting data overwrite)
    if os.path.exists(image_dir):
        choice = input(f"Warning: Data for {name} ({Id}) already exists. Overwrite? (y/n): ").lower()
        if choice != 'y':
            print("Image capture aborted by user.")
            return False
        shutil.rmtree(image_dir) # Delete existing directory if overwriting
    
    os.makedirs(image_dir, exist_ok=True)
    
    # 3. Camera Setup
    cam = cv2.VideoCapture(0) # Open the default camera (0)
    if not cam.isOpened():
        print("Error: Could not open video stream.")
        return False

    sampleNum = 0
    maxSamples = 30
    
    print(f"\n--- Capturing Images for {name} ({Id}) ---")
    print(f"Please look directly at the camera. Capturing {maxSamples} images...")

    while(True):
        ret, img = cam.read() # Read frame
        if not ret:
            print("Error reading frame.")
            break
            
        # Flip image horizontally for a natural 'mirror' view
        img = cv2.flip(img, 1) 
        
        # Convert frame to grayscale for face detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the grayscale image
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.3, 
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # 4. Draw Rectangle and Capture Images
        for (x, y, w, h) in faces:
            # Draw a green rectangle around the detected face
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Increment sample number and save the face region
            if sampleNum < maxSamples:
                sampleNum += 1
                # Save the detected face region (cropped from grayscale)
                # Note: Saving grayscale images is common for training
                cv2.imwrite(
                    os.path.join(image_dir, f"{Id}.{sampleNum}.jpg"), 
                    gray[y:y+h, x:x+w]
                )

            # Display counter on the image
            cv2.putText(img, f"Samples: {sampleNum}/{maxSamples}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # 5. Display the camera feed
        cv2.imshow('Face Capturing', img)
        
        # Break loop if 'q' is pressed or max samples reached
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
        elif sampleNum >= maxSamples:
            # Pause briefly to ensure the final frame is visible
            cv2.waitKey(2000) 
            break

    # 6. Cleanup
    cam.release()
    cv2.destroyAllWindows()
    
    if sampleNum == maxSamples:
        print(f"\nSuccessfully captured {maxSamples} images for {name} ({Id}).")
        return True
    else:
        print("\nImage capture finished prematurely.")
        return False

if __name__ == '__main__':
    # Example usage when running script directly
    takeImages("2025101", "John_Doe")