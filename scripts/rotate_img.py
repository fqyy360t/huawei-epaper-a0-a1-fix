import cv2
import sys

src, dst, angle = sys.argv[1], sys.argv[2], float(sys.argv[3])
im = cv2.imread(src)
h, w = im.shape[:2]
m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
cos, sin = abs(m[0, 0]), abs(m[0, 1])
nw, nh = int(h * sin + w * cos), int(h * cos + w * sin)
m[0, 2] += nw / 2 - w / 2
m[1, 2] += nh / 2 - h / 2
out = cv2.warpAffine(im, m, (nw, nh), borderValue=(20, 20, 20))
cv2.imwrite(dst, out)
