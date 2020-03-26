import numpy as np
import cv2 as cv
img = cv.imread("./images/gauge-3.jpg")
output = img.copy()
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
gray = cv.medianBlur(gray, 5)
circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, 20  # param1=50, param2=30
                          , minRadius=260, maxRadius=310
                          )
detected_circles = np.uint16(np.around(circles))

# find the centroid of the circles
Σr, Σx, Σy, count = 0, 0, 0, 0
for (x, y, r) in detected_circles[0, :]:
    count += 1
    Σr += r
    Σx += x
    Σy += y

x̄ = int(Σx/count)
ȳ = int(Σy/count)
mean_r = Σr/count
cv.circle(output, (x̄, ȳ), r, (0, 255, 0), 3)
cv.circle(output, (x̄, ȳ), 5, (0, 0, 255), 3)

print("########## x, y, r of centroid", (x̄, ȳ, mean_r))

cv.imshow('output',output)
cv.waitKey(0)
cv.destroyAllWindows()
