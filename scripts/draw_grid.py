import cv2
import sys

src = sys.argv[1]
dst = sys.argv[2]
im = cv2.imread(src)
for x in range(0, im.shape[1], 50):
    cv2.line(im, (x, 0), (x, im.shape[0]), (0, 255, 0), 1)
    cv2.putText(im, str(x), (x + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
for y in range(0, im.shape[0], 50):
    cv2.line(im, (0, y), (im.shape[1], y), (0, 255, 0), 1)
    cv2.putText(im, str(y), (2, y + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
cv2.imwrite(dst, im)
