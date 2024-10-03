# client/capture_and_stream.py
import cv2
import requests
import time

def stream_video(server_url):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("Streaming video... Press 'q' to stop.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        try:
            response = requests.post(server_url, files={'frame': frame_bytes})
            if response.status_code != 200:
                print(f"Failed to send frame: {response.status_code}")
        except Exception as e:
            print(f"Error sending frame: {e}")
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.03)  # 30 FPS로 전송

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    server_url = 'http://127.0.0.1:3333/stream'
    stream_video(server_url)
