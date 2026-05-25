import os
import cv2
import time
import sys

try:
    from google import genai
except ImportError:
    print("Please install the Google GenAI SDK to run this prototype:")
    print("pip install google-genai")
    sys.exit(1)

# Ensure this points to an actual video in your project
VIDEO_PATH = os.path.join(os.path.dirname(__file__), 'static', 'videos', 'wallball.mp4')
TEMP_CLIP_PATH = os.path.join(os.path.dirname(__file__), 'temp_suspicious_rep.mp4')

def extract_clip(input_video_path, output_clip_path, start_sec, end_sec):
    """
    Simulates the Programmatic 'Trigger': 
    Extracts a short clip from a larger video, representing a single rep or a 'suspicious' rep.
    """
    print(f"--- 1. PROGRAMMATIC TRIGGER ---")
    print(f"Extracting video clip from {start_sec}s to {end_sec}s...")
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
         raise ValueError(f"Could not open {input_video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30.0 # fallback
        
    start_frame = int(start_sec * fps)
    end_frame = int(end_sec * fps)
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_clip_path, fourcc, fps, (width, height))
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    current_frame = start_frame
    
    while current_frame <= end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        current_frame += 1
        
    cap.release()
    out.release()
    print(f"Extracted clip saved locally -> {output_clip_path}\n")


def get_agent_review(video_path):
    """
    Simulates the Agentic 'Judge':
    Passes the localized clip to a Video-capable Vision Language Model.
    """
    print(f"--- 2. AGENTIC JUDGE ---")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
         print("ERROR: Please set your GEMINI_API_KEY environment variable.")
         print("Example: export GEMINI_API_KEY='your_api_key_here'")
         return None

    print(f"Connecting to Gemini API...")
    client = genai.Client(api_key=api_key)
    
    print(f"Uploading file {os.path.basename(video_path)} for agent review (this may take a moment)...")
    video_file = client.files.upload(file=video_path)
    
    # Video files require processing server-side before they can be used in generation.
    while video_file.state.name == "PROCESSING":
        print('.', end='', flush=True)
        time.sleep(2)
        video_file = client.files.get(name=video_file.name)
        
    if video_file.state.name == "FAILED":
        print("\nVideo processing failed.")
        return None
        
    print(f"\nFile ready! Agent is reviewing the movement...")
    
    # This prompt completely replaces your heuristic state machine and threshold variables
    prompt = (
        "You are an expert CrossFit judge. Review this short clip of a single Wall Ball attempt. "
        "The movement standard is firmly: "
        "1. At the bottom of the squat, the athlete's hip crease must clearly drop under the top of the knee. "
        "2. The ball must hit the designated target line/area cleanly. "
        "Please provide: "
        "- A detailed assessment of their squat depth. "
        "- A detailed assessment of the ball hitting the target. "
        "- Final Result: 'GOOD REP' or 'NO REP'. "
        "- If 'NO REP', provide 1 sentence on what the athlete must focus on to fix it."
    )
    
    # We use Gemini 2.5 Pro as it is state of the art for video comprehension
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=[video_file, prompt]
    )
    
    print("\n--- JUDGE VERDICT ---")
    print(response.text)
    
    # Optional cleanup
    client.files.delete(name=video_file.name)
    return response.text


def main():
    if not os.path.exists(VIDEO_PATH):
        print(f"Video not found: {VIDEO_PATH}")
        print("Please point VIDEO_PATH to a valid MP4 file to test this out.")
        sys.exit(1)
        
    # In a full hybrid pipeline, these timestamps would be passed dynamically 
    # from your WallBallCounter logic when it detects a completed/failed phase loop.
    mock_rep_start_seconds = 2.0
    mock_rep_end_seconds = 6.0
    
    extract_clip(VIDEO_PATH, TEMP_CLIP_PATH, mock_rep_start_seconds, mock_rep_end_seconds)
    
    get_agent_review(TEMP_CLIP_PATH)
    
    # Clean up local file
    if os.path.exists(TEMP_CLIP_PATH):
         os.remove(TEMP_CLIP_PATH)

if __name__ == '__main__':
    main()
