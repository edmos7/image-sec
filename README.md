# image-sec
Object detection processing pipeline for confirming overnight surveillance service, using OpenCV and Yolov8

## Example

A camera would take pics, the goal is to confirm a certain car does in fact pass by...

| Frame | Image | Comment |
|-------|--------|----------|
| 1 | ![Step 1](imgs/img1.jpg) | _Snap pic if movement_ |
| 2 | ![Step 2](imgs/img2.jpg) | _Parked cars don't help_ |
| 3 | ![Step 3](imgs/img3.jpg) | _Occlude other cars with cv2_ |
| 4 | ![Step 4](imgs/img4.jpg) | _Detections now relevant_ |

> The source code would process the images and send informative emails accordingly
