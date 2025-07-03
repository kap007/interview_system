import cv2
import numpy as np
import math
from collections import deque
import time
import json
import os
from datetime import datetime

# Initialize camera
cap = cv2.VideoCapture(0)

# Get camera properties for video recording
fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Setup video recording
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
video_output_path = f"E:/Internship/Project 2/interview_system/video_files_{timestamp}.avi"
fourcc = cv2.VideoWriter_fourcc(*'XVID')
video_writer = cv2.VideoWriter(video_output_path, fourcc, fps, (width, height))

# Load cascade classifiers
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Phase 3 - Final Assessment Variables (More lenient settings)
frame_count = 0
assessment_duration = 450  # 15 seconds at 30fps for more comprehensive assessment
start_time = time.time()

# Initialize eyeball tracking variables (More lenient thresholds)
left_eye_positions = deque(maxlen=30)
right_eye_positions = deque(maxlen=30)
gaze_direction = "Center"
eye_movement_count = 0
excessive_eye_movement = False
GAZE_THRESHOLD = 25  # Increased from 15 to allow more natural eye movement

# Initialize lip movement tracking variables (More lenient thresholds)
mouth_positions = deque(maxlen=20)
lip_movement_intensity = 0
speaking_detected = False
silent_periods = 0
speaking_periods = 0
LIP_MOVEMENT_THRESHOLD = 6  # Reduced from 8 to detect subtler speech

# Initialize comprehensive confidence scoring variables (More lenient scoring)
stability_score = 100
attention_score = 100
naturalness_score = 100
overall_confidence = 0
behavioral_flags = []
movement_tolerance_frames = 0  # Track frames of acceptable movement

# Movement tracking with increased tolerance
MOVEMENT_THRESHOLD = 35  # Increased from 20 to allow natural movement
EXCESSIVE_MOVEMENT_THRESHOLD = 50  # New threshold for truly excessive movement
MOVEMENT_TOLERANCE_PERIOD = 60  # Allow movement bursts for 2 seconds

def detect_eye_centers(eye_region):
    """Detect pupil/eye center using contour detection"""
    gray_eye = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_eye, 50, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Find largest contour (likely the pupil)
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return (cx, cy)
    return None

def analyze_lip_movement(mouth_region):
    """Analyze lip movement patterns"""
    gray_mouth = cv2.cvtColor(mouth_region, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray_mouth, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Calculate total contour area as movement indicator
    total_area = sum(cv2.contourArea(contour) for contour in contours)
    return total_area

def calculate_gaze_direction(left_eye_center, right_eye_center, face_center):
    """Calculate overall gaze direction with more tolerance"""
    if left_eye_center and right_eye_center:
        avg_eye_x = (left_eye_center[0] + right_eye_center[0]) / 2
        face_center_x = face_center[0]
        
        if avg_eye_x < face_center_x - GAZE_THRESHOLD:
            return "Left"
        elif avg_eye_x > face_center_x + GAZE_THRESHOLD:
            return "Right"
        else:
            return "Center"
    return "Unknown"

def update_confidence_scores(frame_data):
    """Update all confidence metrics based on current frame data with more lenient scoring"""
    global stability_score, attention_score, naturalness_score, behavioral_flags, movement_tolerance_frames
    
    # More lenient stability score - allow natural movement
    head_movement = frame_data.get('head_movement', 0)
    if head_movement > EXCESSIVE_MOVEMENT_THRESHOLD:
        # Only penalize truly excessive movement
        stability_score = max(30, stability_score - 0.3)  # Reduced penalty and minimum score
        movement_tolerance_frames = 0
        if stability_score < 50 and "Excessive head movement" not in behavioral_flags:
            behavioral_flags.append("Excessive head movement")
    elif head_movement > MOVEMENT_THRESHOLD:
        # Track moderate movement but with tolerance
        movement_tolerance_frames += 1
        if movement_tolerance_frames > MOVEMENT_TOLERANCE_PERIOD:
            stability_score = max(50, stability_score - 0.1)  # Very small penalty
        else:
            stability_score = min(100, stability_score + 0.05)  # Small recovery
    else:
        # Good stability
        movement_tolerance_frames = max(0, movement_tolerance_frames - 2)
        stability_score = min(100, stability_score + 0.2)
    
    # More lenient attention score - allow natural gaze patterns
    gaze_direction = frame_data.get('gaze_direction', 'Center')
    if gaze_direction != "Center":
        # Much smaller penalty for looking away (natural during thinking/speaking)
        attention_score = max(40, attention_score - 0.1)  # Reduced from 0.3
        if attention_score < 40 and "Poor eye contact" not in behavioral_flags:
            behavioral_flags.append("Poor eye contact")
    else:
        attention_score = min(100, attention_score + 0.3)  # Increased recovery rate
    
    # More lenient naturalness score
    excessive_blinking = frame_data.get('eye_movement_count', 0) > 80  # Increased threshold
    no_lip_movement = frame_data.get('speaking_periods', 0) == 0 and frame_count > 200  # More time allowed
    
    if excessive_blinking:
        naturalness_score = max(40, naturalness_score - 0.1)  # Reduced penalty
        if "Excessive blinking" not in behavioral_flags:
            behavioral_flags.append("Excessive blinking")
    elif no_lip_movement and frame_count > 200:
        naturalness_score = max(60, naturalness_score - 0.05)  # Very small penalty for silence
        if "Limited verbal response" not in behavioral_flags:
            behavioral_flags.append("Limited verbal response")
    else:
        naturalness_score = min(100, naturalness_score + 0.15)

def calculate_final_confidence():
    """Calculate overall confidence level with adjusted thresholds"""
    # Adjusted weighting to reduce movement impact
    weighted_score = (stability_score * 0.2 + attention_score * 0.4 + naturalness_score * 0.4)  # Reduced stability weight
    
    if weighted_score >= 80:  # Reduced from 85
        return weighted_score, "HIGHLY CONFIDENT", "Excellent candidate behavior"
    elif weighted_score >= 65:  # Reduced from 70
        return weighted_score, "CONFIDENT", "Good candidate behavior"
    elif weighted_score >= 50:  # Reduced from 55
        return weighted_score, "MODERATE", "Acceptable with minor concerns"
    else:
        return weighted_score, "NEEDS REVIEW", "Some behavioral concerns noted"

# Face position tracking for head movement calculation
previous_face_center = None

print("Phase 3: Enhanced Final Assessment - Eyeball & Lip Tracking with Video Recording")
print("This phase will analyze eye movements, lip movements, and provide final confidence assessment")
print("Natural movement during answers is expected and accounted for")
print(f"Recording video to: {video_output_path}")
print("="*50)
print("CONTROLS (Remove for production):")
print("Press 'q' to quit early and generate report")
print("Assessment will auto-end after 15 seconds")
print("="*50)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    cv2.flip(frame, 1, frame)
    frame_count += 1
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Write frame to video file
    video_writer.write(frame)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=6,
        minSize=(50, 50)
    )
    
    frame_data = {}
    
    if len(faces) > 0:
        # Process main face
        x, y, w, h = faces[0]
        face_center = (x + w//2, y + h//2)
        frame_data['face_detected'] = True
        
        # Calculate head movement with more sophisticated tracking
        head_movement = 0
        if previous_face_center:
            head_movement = math.sqrt(
                (face_center[0] - previous_face_center[0])**2 + 
                (face_center[1] - previous_face_center[1])**2
            )
        previous_face_center = face_center
        frame_data['head_movement'] = head_movement
        
        # Draw face rectangle with color coding based on movement
        if head_movement < MOVEMENT_THRESHOLD:
            face_color = (0, 255, 0)  # Green - good
        elif head_movement < EXCESSIVE_MOVEMENT_THRESHOLD:
            face_color = (0, 255, 255)  # Yellow - acceptable
        else:
            face_color = (0, 0, 255)  # Red - excessive
        
        cv2.rectangle(frame, (x, y), (x+w, y+h), face_color, 2)
        
        # Extract regions of interest
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        # Detailed eye tracking and analysis
        eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20))
        
        left_eye_center = None
        right_eye_center = None
        
        for i, (ex, ey, ew, eh) in enumerate(eyes[:2]):
            eye_region = roi_color[ey:ey+eh, ex:ex+ew]
            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)
            
            # Detect eye center
            eye_center = detect_eye_centers(eye_region)
            if eye_center:
                adjusted_center = (ex + eye_center[0], ey + eye_center[1])
                cv2.circle(roi_color, adjusted_center, 3, (0, 255, 255), -1)
                
                if i == 0:
                    left_eye_center = adjusted_center
                    left_eye_positions.append(adjusted_center)
                else:
                    right_eye_center = adjusted_center
                    right_eye_positions.append(adjusted_center)
        
        # Calculate gaze direction
        gaze_direction = calculate_gaze_direction(left_eye_center, right_eye_center, face_center)
        frame_data['gaze_direction'] = gaze_direction
        
        # Track eye movement with more tolerance
        if len(left_eye_positions) > 1:
            last_left = left_eye_positions[-2]
            current_left = left_eye_positions[-1]
            movement = math.sqrt((current_left[0] - last_left[0])**2 + (current_left[1] - last_left[1])**2)
            if movement > 7:  # Increased threshold for significant eye movement
                eye_movement_count += 1
        
        frame_data['eye_movement_count'] = eye_movement_count
        
        # Mouth/lip region analysis
        mouth_y = y + int(h * 0.65)
        mouth_h = int(h * 0.25)
        mouth_x = x + int(w * 0.3)
        mouth_w = int(w * 0.4)
        
        if mouth_y + mouth_h < frame.shape[0] and mouth_x + mouth_w < frame.shape[1]:
            mouth_region = frame[mouth_y:mouth_y+mouth_h, mouth_x:mouth_x+mouth_w]
            cv2.rectangle(frame, (mouth_x, mouth_y), (mouth_x+mouth_w, mouth_y+mouth_h), (0, 0, 255), 2)
            
            current_lip_movement = analyze_lip_movement(mouth_region)
            mouth_positions.append(current_lip_movement)
            
            # Detect speaking with improved sensitivity
            if len(mouth_positions) > 3:
                recent_movement = list(mouth_positions)[-3:]
                avg_movement = sum(recent_movement) / len(recent_movement)
                if avg_movement > LIP_MOVEMENT_THRESHOLD:
                    speaking_detected = True
                    speaking_periods += 1
                    cv2.putText(frame, "SPEAKING", (mouth_x, mouth_y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                else:
                    speaking_detected = False
                    silent_periods += 1
        
        frame_data['speaking_periods'] = speaking_periods
        frame_data['silent_periods'] = silent_periods
    
    # Update confidence scores
    update_confidence_scores(frame_data)
    
    # Calculate current confidence
    current_confidence, confidence_level, confidence_desc = calculate_final_confidence()
    overall_confidence = current_confidence
    
    # Display comprehensive information
    elapsed_time = int((frame_count / fps))
    remaining_time = max(0, int((assessment_duration - frame_count) / fps))
    
    info_text = [
        f"Time: {elapsed_time}s / {int(assessment_duration/fps)}s (Remaining: {remaining_time}s)",
        f"Gaze: {gaze_direction} | Eye Movements: {eye_movement_count}",
        f"Speaking: {speaking_periods} | Silent: {silent_periods}",
        f"Head Movement: {frame_data.get('head_movement', 0):.1f}px",
        "",
        "CONFIDENCE SCORES:",
        f"Stability: {stability_score:.1f}%",
        f"Attention: {attention_score:.1f}%",
        f"Naturalness: {naturalness_score:.1f}%",
        f"Overall: {overall_confidence:.1f}% - {confidence_level}"
    ]
    
    # Color coding based on movement and confidence
    if overall_confidence >= 80:
        info_color = (0, 255, 0)  # Green
    elif overall_confidence >= 65:
        info_color = (0, 255, 255)  # Yellow
    elif overall_confidence >= 50:
        info_color = (0, 165, 255)  # Orange
    else:
        info_color = (0, 0, 255)  # Red
    
    # Display info on frame
    y_offset = 30
    for i, text in enumerate(info_text):
        cv2.putText(frame, text, (10, y_offset + i*25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, info_color, 2)
    
    # Add recording indicator
    cv2.putText(frame, "REC", (width-60, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.circle(frame, (width-80, 25), 5, (0, 0, 255), -1)
    
    cv2.imshow('Candidate Assessment with Recording', frame)
    
    # DEVELOPMENT CONTROLS - Remove this section for production
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print(f"\nManual exit triggered at {frame_count/fps:.1f} seconds")
        print("Generating assessment report...")
        break
    # END DEVELOPMENT CONTROLS
    
    # Auto-exit after assessment duration
    if frame_count >= assessment_duration:
        print(f"\nAssessment completed - Full duration reached ({assessment_duration/fps:.1f} seconds)")
        break

# Cleanup
cap.release()
video_writer.release()
cv2.destroyAllWindows()

# Generate comprehensive final report
print("\n" + "="*80)
print("ENHANCED CANDIDATE ASSESSMENT REPORT")
print("="*80)

final_confidence, final_level, final_desc = calculate_final_confidence()

print(f"\nOVERALL CONFIDENCE: {final_confidence:.1f}% - {final_level}")
print(f"Assessment: {final_desc}")
print(f"Recording Duration: {frame_count/fps:.1f} seconds")

print(f"\nDETAILED SCORES (Adjusted for Natural Behavior):")
print(f"├─ Stability Score: {stability_score:.1f}% (Movement tolerance applied)")
print(f"├─ Attention Score: {attention_score:.1f}% (Natural gaze patterns considered)")
print(f"└─ Naturalness Score: {naturalness_score:.1f}% (Speaking patterns & behavior)")

print(f"\nBEHAVIORAL ANALYSIS:")
print(f"├─ Total Eye Movements: {eye_movement_count} (Threshold: 80)")
print(f"├─ Speaking Periods: {speaking_periods}")
print(f"├─ Silent Periods: {silent_periods}")
print(f"├─ Average Head Movement: {head_movement:.1f}px per frame")
print(f"└─ Frames Analyzed: {frame_count}")

if behavioral_flags:
    print(f"\nFLAGS & OBSERVATIONS:")
    for flag in set(behavioral_flags):
        print(f"⚠  {flag}")
else:
    print(f"\n✓ No significant behavioral concerns detected.")

print(f"\nRECOMMENDATION:")
if final_confidence >= 80:
    print("✓ PROCEED - Candidate demonstrates excellent behavioral indicators")
    print("  Natural movement patterns observed and accounted for")
elif final_confidence >= 65:
    print("✓ PROCEED - Candidate shows good behavioral patterns")
    print("  Some natural variations in behavior noted")
elif final_confidence >= 50:
    print("⚠ REVIEW RECOMMENDED - Consider additional human assessment")
    print("  Video recording available for detailed review")
else:
    print("⚠ DETAILED REVIEW REQUIRED - Behavioral concerns noted")
    print("  Human review of video recording strongly recommended")

print(f"\nVIDEO RECORDING:")
print(f"✓ Saved to: {video_output_path}")
print(f"  Duration: {frame_count/fps:.1f} seconds")
print(f"  Resolution: {width}x{height}")
print(f"  Format: AVI (XVID codec)")

# Save enhanced reports with video reference
timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json_report_path = f"_{timestamp}.json"
txt_report_path = f"E:/Internship/Project 2/interview_system/video_files_{timestamp}.txt"

# Enhanced JSON report
report_data = {
    "assessment_info": {
        "timestamp": timestamp_str,
        "duration_seconds": frame_count/fps,
        "video_file": video_output_path,
        "frames_analyzed": frame_count
    },
    "overall_confidence": {
        "score": final_confidence,
        "level": final_level,
        "description": final_desc
    },
    "detailed_scores": {
        "stability_score": stability_score,
        "attention_score": attention_score,
        "naturalness_score": naturalness_score
    },
    "behavioral_analysis": {
        "eye_movements": eye_movement_count,
        "speaking_periods": speaking_periods,
        "silent_periods": silent_periods,
        "average_head_movement": head_movement,
        "movement_threshold_used": MOVEMENT_THRESHOLD,
        "excessive_movement_threshold": EXCESSIVE_MOVEMENT_THRESHOLD
    },
    "flags_and_observations": list(set(behavioral_flags)),
    "recommendation": {
        "action": "PROCEED" if final_confidence >= 65 else "REVIEW",
        "human_review_recommended": final_confidence < 65,
        "video_available": True
    },
    "assessment_parameters": {
        "movement_tolerance_applied": True,
        "natural_behavior_considerations": True,
        "gaze_threshold": GAZE_THRESHOLD,
        "lip_movement_threshold": LIP_MOVEMENT_THRESHOLD
    }
}

# Write enhanced JSON report
with open(json_report_path, "w") as json_file:
    json.dump(report_data, json_file, indent=4)

print(f"\nREPORTS SAVED:")
print(f"├─ JSON Report: {json_report_path}")
print(f"├─ Video Recording: {video_output_path}")
print(f"└─ Ready for human review if needed")

print("="*80)
print("Enhanced Assessment Complete - Video Available for Review")
print("="*80)