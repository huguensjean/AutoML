import sys
import cv2

# importing auto-ml libraries
from google.cloud import automl_v1beta1
from google.cloud.automl_v1beta1.proto import service_pb2

if len(sys.argv) != 4:
    print("Usage: Detect-Cartoon.py VIDEO PROJECT_ID MODEL_ID")
    exit(1)

# input video file
video_file = sys.argv[1]

# project and model ID to run Auto-ML
project_id = sys.argv[2]
model_id = sys.argv[3]

# detects popular tv / movie / cartoon characters in given image
def detect_character(frame):
    model = automl_v1beta1.PredictionServiceClient()
    path = "projects/" + project_id + "/locations/us-central1/models/" + model_id
    result = model.predict(path, {'image': {'image_bytes': frame}})
    return result

# load video
stream = cv2.VideoCapture(video_file)

# assign color-codes based on class-labels
color_codes = { 'mickey_mouse': {'R': 255, 'G': 128, 'B': 0},
'donald_duck': {'R': 255, 'G': 102, 'B': 178},
'goofy': {'R': 153, 'G': 153, 'B': 0},
'Dorothy': {'R': 255, 'G': 128, 'B': 0},
'ScareCrow': {'R': 255, 'G': 102, 'B': 178},
'TinMan': {'R': 51, 'G': 153, 'B': 255},
}

# height and width of output video
w = 1280
h = 720

# for Mac OS, this is the codec for writing mp4 files
codec = cv2.VideoWriter_fourcc('m','p','4','v')
frame_rate = 15
# output video file
output = cv2.VideoWriter('output.mp4', codec, frame_rate, (w, h), True)

# process input video frame by frame
while 1:
    flag, frame = stream.read()
    if flag:

        # converting frame into base-64 format
        cv2.imwrite('test.png', frame)
        with open('test.png', 'rb') as image_file:
            image_data = image_file.read()

            # detecting characters in this frame
            result = detect_character(image_data)

            # parse API response
            for character in result.payload:
                # get character name
                label = character.display_name

                # get bounding box co-ordinates
                bbox = character.image_object_detection.bounding_box
                x1 = round(bbox.normalized_vertices[0].x * w)
                y1 = round(bbox.normalized_vertices[0].y * h)
                x2 = round(bbox.normalized_vertices[1].x * w)
                y2 = round(bbox.normalized_vertices[1].y * h)

                # get color code
                color = color_codes[label]

                # draw bounding-box around the character
                cv2.rectangle(frame, (x1, y1), (x2, y2), (color['B'], color['G'], color['R']), 2)

                # print character name
                label_width = len(label) * 10;
                if(y1-30 > 0):
                    # put label on top of the box
                    cv2.rectangle(frame, (x1, y1 - 30), (x1 + label_width, y1), (color['B'], color['G'], color['R']), cv2.FILLED)
                    cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))
                else:
                    # put label inside the box otherwise it won't be visible
                    cv2.rectangle(frame, (x1, y1), (x1 + label_width, y1 + 30), (color['B'], color['G'], color['R']), cv2.FILLED)
                    cv2.putText(frame, label, (x1, y1+20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))

        # display output frame and write to mp4 file
        cv2.imshow('Cartoon-Detector', frame)
        output.write(frame)

        if cv2.waitKey(1)&0xFF == ord('q'):
            break
    else:
        break

stream.release()
output.release()
cv2.destroyAllWindows()
