import os
import sys
from skin_diseases.predictor import predictor

def main():
    if len(sys.argv) < 2:
        print("Usage: python predict_new.py <path_to_image>")
        return

    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return

    print(f"Analyzing image: {image_path}...")
    
    # Run prediction
    disease, confidence = predictor.predict(image_path)
    
    print("\n--- Prediction Result ---")
    print(f"Class: {disease}")
    print(f"Confidence: {confidence:.2f}%")
    print("-------------------------\n")

if __name__ == "__main__":
    main()
