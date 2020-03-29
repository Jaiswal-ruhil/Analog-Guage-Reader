import cv2
import numpy as np
import math


def show(img, name="unnamed"):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def avg_circles(circles, b):
    avg_x = avg_y = avg_r = 0
    for i in range(b):
        # optional - average for multiple circles (can happen when a gauge is at a slight angle)
        avg_x = avg_x + circles[0][i][0]
        avg_y = avg_y + circles[0][i][1]
        avg_r = avg_r + circles[0][i][2]
    avg_x = int(avg_x/(b))
    avg_y = int(avg_y/(b))
    avg_r = int(avg_r/(b))
    return avg_x, avg_y, avg_r


def dist_2_pts(x1, y1, x2, y2):
    # print np.sqrt((x2-x1)^2+(y2-y1)^2)
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def calibrate_gauge(img, calibration_data, draw=True):
    '''
        This function should be run using a test image in order to calibrate the range available to the dial as well as the
        units.  It works by first finding the center point and radius of the gauge.  Then it draws lines at hard coded intervals
        (separation) in degrees.  It then prompts the user to enter position in degrees of the lowest possible value of the gauge,
        as well as the starting value (which is probably zero in most cases but it won't assume that).  It will then ask for the
        position in degrees of the largest possible value of the gauge. Finally, it will ask for the units.  This assumes that
        the gauge is linear (as most probably are).
        It will return the min value with angle in degrees (as a tuple), the max value with angle in degrees (as a tuple),
        and the units (as a string).
    '''

    _, _ = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to gray
    gray = cv2.medianBlur(gray, 5)

    # detect circles
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, 1, 20, minRadius=260, maxRadius=310)

    # detected_circles = np.uint16(np.around(circles))
    # average found circles, found it to be more accurate than trying to tune HoughCircles parameters to get just the right one
    _, b, _ = circles.shape
    x, y, r = avg_circles(circles, b)
    # draw center and circle
    if draw:
        cv2.circle(img, (x, y), r, (0, 0, 255), 3, cv2.LINE_AA)  # draw circle
        cv2.circle(img, (x, y), 2, (0, 255, 0), 3,
                   cv2.LINE_AA)  # draw center of circle

    '''
    goes through the motion of a circle and sets x and y values based on the set separation spacing.  Also adds text to each
    line.  These lines and text labels serve as the reference point for the user to enter
    NOTE: by default this approach sets 0/360 to be the +x axis (if the image has a cartesian grid in the middle), the addition
    (i+9) in the text offset rotates the labels by 90 degrees so 0/360 is at the bottom (-y in cartesian).  So this assumes the
    gauge is aligned in the image, but it can be adjusted by changing the value of 9 to something else.
    '''
    # TODO make i compute automatically
    separation = calibration_data["separation"]  # in degrees for LIN

    interval = int(360 / separation)
    p1 = np.zeros((interval, 2))  # set empty arrays
    p2 = np.zeros((interval, 2))
    for i in range(0, interval):
        for j in range(0, 2):
            if (j % 2 == 0):
                p1[i][j] = x + 0.9 * r * \
                    np.cos(separation * i * 3.14 / 180)  # point for lines
            else:
                p1[i][j] = y + 0.9 * r * np.sin(separation * i * 3.14 / 180)
    for i in range(0, interval):
        for j in range(0, 2):
            if (j % 2 == 0):
                p2[i][j] = x + r * np.cos(separation * i * 3.14 / 180)
            else:
                p2[i][j] = y + r * np.sin(separation * i * 3.14 / 180)

    # add the lines and labels to the image
    deviation = calibration_data["appx_deveation_zero"]
    deviation_end = calibration_data["appx_deveation_max"]
    start = int(interval/4+deviation)
    end = int(interval*3/4+deviation_end)

    zx, zy = int(p1[start][0]), int(p1[start][1])

    if draw:
        for i in range(start, end):
            cv2.line(img, (int(p1[i][0]), int(p1[i][1])),
                     (int(p2[i][0]), int(p2[i][1])), (0, 255-i-i+46, 0), 2)
        cv2.line(img, (x, y+r), (x, 0), (225, 225, 0), 2)
        cv2.line(img, (x, y), (x, 0), (225, 225, 0), 2)
        cv2.circle(img, (zx, zy), 5, (225, 225, 0), cv2.LINE_AA)

    # ('Min angle (lowest possible angle of dial) - in degrees: ') #the lowest possible angle
    min_angle = calibration_data["min_angle"]
    # ('Max angle (highest possible angle) - in degrees: ') #highest possible angle
    max_angle = calibration_data["max_angle"]
    min_value = calibration_data["min_value"]  # ('Min value: ') #usually zero
    # ('Max value: ') #maximum reading of the gauge
    max_value = calibration_data["max_value"]
    units = calibration_data["units"]  # ('Enter units: ')

    return min_angle, max_angle, min_value, max_value, units, x, y, r, (zx, zy)


def get_current_value(img, min_angle, max_angle, min_value, max_value, x, y, r, zero_point, calibration_data):

    zx, zy = zero_point
    cx, cy = x, y

    # for testing purposes
    # img = cv2.imread('gauge-%s.%s' % (gauge_number, file_type))
    gray2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Set threshold and maxValue for color
    thresh = 80
    maxValue = 190

    # apply thresholding which helps for finding lines
    _, dst2 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_BINARY)

    ########### FIND LINES ##########
    minLineLength = 100
    maxLineGap = 50
    # rho is set to 3 to detect more lines, easier to get more then filter them out later
    # lines = cv2.HoughLinesP(image=dst2, rho=3, theta=np.pi / 180,
    #                         threshold=100, minLineLength=minLineLength, maxLineGap=0)
    dst3 = cv2.Canny(dst2, 75, 100)
    # lines = cv2.HoughLinesP(image=dst3, rho=1, theta=1*np.pi/180,
    #                         threshold=100, minLineLength=minLineLength, maxLineGap=maxLineGap)

    lines = cv2.HoughLinesP(image=dst3, rho=2, theta=np.pi/180,
                            threshold=150, minLineLength=minLineLength, maxLineGap=maxLineGap)

    # TODO considering the bisecting line angle
    # assumes the first line is the best one
    x1, y1, x2, y2 = lines[0][0]
    cv2.line(img, (x1, y1), (cx, cy), (255, 0, 0), 2)
    cv2.circle(img, (x1, y1), 2, (255, 0, 0), cv2.LINE_AA)
    # paste
    # find the farthest point from the center to be what is used to determine the angle

    slopeZero = (zy-cy)/(zx-cx)
    slopeDail = (y1-cy)/(x1-cx)
    angle_dial_and_zero = math.atan(
        abs((slopeZero-slopeDail)/(1+slopeDail*slopeZero)))

    appx_value = math.degrees(
        angle_dial_and_zero) / calibration_data["separation"] * calibration_data["unitWeight"]
    return appx_value


def main(filelocation, calibration_data):
    img = cv2.imread(filelocation)
    raw_cropped_img = img[50:700, 0:800]
    min_angle, max_angle, min_value, max_value, units, x, y, r, zero = calibrate_gauge(
        raw_cropped_img, calibration_data, False)

    # r = r
    cropped_img = img[(x-r):(x+r), (y-r):(y+r)]
    # name the calibration image of your gauge 'gauge-#.jpg', for example 'gauge-5.jpg'.  It's written this way so you can easily try multiple images
    min_angle, max_angle, min_value, max_value, units, x, y, r, zero = calibrate_gauge(
        cropped_img, calibration_data)

    # feed an image (or frame) to get the current value, based on the calibration, by default uses same image as calibration
    # img = cv2.imread('./gauge-%s.%s' % (gauge_number, file_type))
    val = get_current_value(cropped_img, min_angle, max_angle,
                            min_value, max_value, x, y, r, zero, calibration_data)
    show(
        img, f'for gauge:{filelocation} -> Current reading: {val} {units}')
    return val


if __name__ == '__main__':
    calibration_data = {
        "separation": 3.0,
        "min_angle": 105,  # lowest possible angle of dial that can be reached
        # Max angle (highest possible angle) - in degrees: ') #highest possible angle
        "max_angle": 270,
        "min_value": 111,  # input('Min value: ') #usually zero
        "max_value": 264,  # input('Max value: ') #maximum reading of the gauge
        "units": "bar",  # input('Enter units: ')
        "unitWeight": 2,  # exery seperation in this amount of units
        "appx_deveation_zero": 16,  # deviation of zero from center in "x" units int
        "appx_deveation_max": 8  # deviation of zero from center in "x" units int
    }

    # main(3, calibration_data)
    for gauge_number in range(2, 8):
        filelocation = f'./analog_gauge_reader/images/gauge-{gauge_number}.jpg'
        print(filelocation)
        print(
            f"for gauge:{filelocation} -> Current reading: {main(filelocation, calibration_data)} {calibration_data['units']}")
