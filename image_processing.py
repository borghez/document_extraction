import os
import cv2
import imutils
import numpy as np


def preprocessing(image_path):
    original_image = cv2.imread(image_path)

    (H, W) = original_image.shape[:2]
    # Necessario fare resize se l'immagine supera determinati valori, altrimenti ritorna "unknown C## error"
    if H > 2000 or W > 1500:
        if H > 2000:
            H = 2000
        if W > 1500:
            W = 1500
        try:
             preprocessed_image = cv2.resize(original_image, [W, H], interpolation=cv2.INTER_CUBIC)
        except Exception as ex:
             raise Exception(str(ex))
    else:
        preprocessed_image = original_image

    return preprocessed_image


def base_alignement(image, doc):

    ref_image_path = os.path.join(os.path.dirname(__file__), f"./resources/ref_{doc.lower()}.jpg")
    reference_image = cv2.imread(ref_image_path)

    reference = cv2.resize(reference_image, [986, 657], interpolation=cv2.INTER_CUBIC)
    reference = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)

    image_to_move = cv2.resize(image, [986, 657], interpolation=cv2.INTER_CUBIC)
    image_to_move = cv2.cvtColor(image_to_move, cv2.COLOR_BGR2GRAY)

    # Rileva i punti chiave e descrittori usando SIFT
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(reference, None)
    kp2, des2 = sift.detectAndCompute(image_to_move, None)

    # Usa FLANN per trovare le corrispondenze tra i punti chiave
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params,search_params)
    matches = flann.knnMatch(des1,des2,k=2)

    # Filtra le corrispondenze usando il rapporto di Lowe
    good_matches = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good_matches.append(m)

    # Estrae le coordinate dei punti chiave corrispondenti
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good_matches ]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)

    # Calcola la matrice di omografia
    M, _ = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

    # Applica la trasformazione all'immagine
    h, w= reference.shape
    aligned_img = cv2.warpPerspective(image_to_move, M, (w, h))

    return aligned_img


def mrz_filter(img):
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(img, 0, 255,
	    cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    kernel = np.ones((2,2),np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    return opening

def cartaceo_filter(img):
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    thresh = cv2.threshold(img, 0, 255,
	    cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    #kernel = np.ones((2, 2),np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    blurred = cv2.medianBlur(opening, 3)

    return blurred


def order_points(pts):
	# initialzie a list of coordinates that will be ordered such that the first entry in the list is the top-left, the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
	# the top-left point will have the smallest sum, whereas the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	# now, compute the difference between the points, the top-right point will have the smallest difference, whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	# return the ordered coordinates
	return rect


def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the maximum distance between bottom-right and bottom-left x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	# compute the height of the new image, which will be the maximum distance between the top-right and bottom-right y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	# now that we have the dimensions of the new image, construct the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points in the top-left, top-right, bottom-right, and bottom-left order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped


def contouring_image(original_image):
    original = original_image.copy()
    
    ratio = original_image.shape[0] / 500.0
    original_image_resized = imutils.resize(original_image, height = 500)
    
    gray = cv2.cvtColor(original_image_resized, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    edged = cv2.Canny(gray, 75, 200)
    
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

    screenCnt = None

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # if our approximated contour has four points, then we can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            break

    # if screenCnt is None:
    #     print("Could not find a contour with four points")
        
    warped = four_point_transform(original, screenCnt.reshape(4, 2) * ratio)
    warped = cv2.resize(warped, [986, 657], interpolation=cv2.INTER_CUBIC)

    return warped


def contouring_image_nn(original_image, hed_path):
    original = original_image
    final_image = cv2.imread(hed_path)

    ratio = final_image.shape[0] / 500.0
    final_image_res = imutils.resize(final_image, height = 500)
    
    gray = cv2.cvtColor(final_image_res, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    edged = cv2.Canny(gray, 75, 200)
    
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

    screenCnt = None

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # if our approximated contour has four points, then we can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            break

    # if screenCnt is None:
    #     print("Could not find a contour with four points")
        
    warped = four_point_transform(original, screenCnt.reshape(4, 2) * ratio)
    warped = cv2.resize(warped, [986, 657], interpolation=cv2.INTER_CUBIC)

    return warped

