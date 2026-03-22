#!/usr/bin/env python3
"""Video Thumbnail Generator - Extract thumbnails from videos"""

import argparse
import cv2
import os
from pathlib import Path

def generate_thumbnail(video_path, output_path=None, timestamp=1, width=None):
    """Extract a thumbnail frame from a video."""
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return False
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return False
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    # Seek to timestamp (in seconds)
    frame_number = int(timestamp * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print(f"Error: Could not read frame at {timestamp}s")
        return False
    
    # Resize if width specified
    if width:
        h, w = frame.shape[:2]
        new_width = width
        new_height = int(h * (width / w))
        frame = cv2.resize(frame, (new_width, new_height))
    
    # Default output path
    if output_path is None:
        video_name = Path(video_path).stem
        output_path = f"{video_name}_thumb.jpg"
    
    cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"✓ Thumbnail saved: {output_path}")
    print(f"  Timestamp: {timestamp}s | Resolution: {frame.shape[1]}x{frame.shape[0]}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Generate thumbnail from video")
    parser.add_argument("video", help="Input video file")
    parser.add_argument("-o", "--output", help="Output thumbnail path")
    parser.add_argument("-t", "--timestamp", type=float, default=1.0,
                        help="Timestamp in seconds (default: 1)")
    parser.add_argument("-w", "--width", type=int,
                        help="Resize to this width")
    parser.add_argument("-l", "--list-timestamps", action="store_true",
                        help="List common timestamps (0s, 10s, 30s, 1min, etc.)")
    
    args = parser.parse_args()
    
    if args.list_timestamps:
        cap = cv2.VideoCapture(args.video)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            cap.release()
            print(f"Video duration: {duration:.1f}s")
            print("Suggested timestamps:")
            for t in [0, 1, 5, 10, 30, 60, 120]:
                if t < duration:
                    print(f"  {t}s")
        return
    
    generate_thumbnail(args.video, args.output, args.timestamp, args.width)

if __name__ == "__main__":
    main()
