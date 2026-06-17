import cv2
import json
import time
from pathlib import Path
from PIL import Image
from google import genai
print("NEW CAMERA FILE LOADED")


def get_api_key():
    config_path = (
        Path(__file__).resolve().parent.parent
        / "config"
        / "api_keys.json"
    )

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def capture_image():
    print("CAMERA_VISION OPENING CAMERA")
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    if not cap.isOpened():
        return None

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None

    image_path = "camera_capture.jpg"
    cv2.imwrite(image_path, frame)

    return image_path


def analyze_image(prompt="Describe what you see in this image."):

    try:
        image_path = capture_image()

        if not image_path:
            return "Could not capture image."

        client = genai.Client(api_key=get_api_key())

        image = Image.open(image_path)

        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        prompt,
                        image
                    ]
                )

                return response.text

            except Exception as e:
                error_text = str(e)

                if "503" in error_text or "UNAVAILABLE" in error_text:
                    print(
                        f"[CameraVision] Gemini busy "
                        f"(attempt {attempt + 1}/3)"
                    )
                    time.sleep(3)
                    continue

                raise

        return (
            "Gemini vision service is currently busy. "
            "Please try again in a moment."
        )

    except Exception as e:
        print("[CameraVision Error]", e)
        return f"Camera vision failed: {e}"


if __name__ == "__main__":
    while True:
        result = analyze_image(
            "Describe everything visible in the image. Read all text exactly as written. Identify products, brands, objects, and labels"
        )

        print("\n====================")
        print(result)
        print("====================\n")

        cmd = input(
            "Press ENTER for next scan or q to quit: "
        )

        if cmd.lower() == "q":
            break