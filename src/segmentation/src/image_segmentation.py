#!/usr/bin/env python
"""Segmentation skeleton code for Lab 6
Course: EECS C106A, Fall 2022
Author: Grant Wang, Emma Stephan, Jewook Ryu

This Python file is the skeleton code for Lab 6. You are expected to fill in
the body of the incomplete functions below to complete the lab. The 'test_..'
functions are already defined for you for allowing you to check your 
implementations.

When you believe you have completed implementations of all the incompeleted
functions, you can test your code by running python segmentation.py at the
command line and step through test images
"""

import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import rospy
from sensor_msgs.msg import Image
import cv2, time, sys
from cv_bridge import CvBridge, CvBridgeError
from cv2 import VideoCapture
import pygame
import pygame.camera
from std_msgs.msg import String

"""
sys.path.append('../../')
from lab4_cam.srv import ImageSrv, ImageSrvResponse
"""
this_file = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = '/'.join(this_file.split('/')[:-2]) + '/img'
#grab an imae from the image node
def ros_to_np_img(ros_img_msg):
  return np.array(bridge.imgmsg_to_cv2(ros_img_msg,'bgr8'))


def read_image(img_name, grayscale=False):
    """ reads an image

    Parameters
    ----------
    img_name : str
        name of image
    grayscale : boolean
        true if image is in grayscale, false o/w
    
    Returns
    -------
    ndarray
        an array representing the image read (w/ extension)
    """

    if not grayscale:
        img = cv2.imread(img_name)
    else:
        img = cv2.imread(img_name, 0)

    return img

def write_image(img, img_name):
    """writes the image as a file
    
    Parameters
    ----------
    img : ndarray
        an array representing an image
    img_name : str
        name of file to write as (make sure to put extension)
    """

    cv2.imwrite(img_name, img)

def show_image(img_name, title='Fig', grayscale=False):
    """show the  as a matplotlib figure
    
    Parameters
    ----------
    img_name : str
        name of image
    tile : str
        title to give the figure shown
    grayscale : boolean
        true if image is in grayscale, false o/w
    """

    if not grayscale:
        plt.imshow(img_name)
        plt.title(title)
        plt.show()
    else:
        plt.imshow(img_name, cmap='gray')
        plt.title(title)
        plt.show()


def threshold_segment_naive(gray_img, lower_thresh, upper_thresh):
    """perform grayscale thresholding using a lower and upper threshold by
    blacking the background and whitening lying between the threholds (the
    foreground)

    Parameter
    ---------
    gray_img : ndarray
        grayscale image array
    lower_thresh : float or int
        lowerbound to threshold (an intensity value between 0-255)
    upper_thresh : float or int
        upperbound to threshold (an intensity value between 0-255)

    Returns
    -------
    ndarray
        thresholded version of gray_img
    """
    # TODO: Implement threshold segmentation by setting pixels of gray_img inside the 
    # lower_thresh and upper_thresh parameters to 1
    # Then set any value that is outside the range to be 0 
    # Hints: make a copy of gray_img so that we don't alter the original image
    # Boolean array indexing, or masking will come in handy. 
    # See https://docs.scipy.org/doc/numpy-1.13.0/user/basics.indexing.html

    img_copy = gray_img.copy()
    print(len(img_copy))
    img_copy = 1 - ((img_copy >= lower_thresh) & (img_copy <= upper_thresh))
    return img_copy

def edge_detect_naive(gray_img):
    """perform edge detection using first two steps of Canny (Gaussian blurring and Sobel
    filtering)

    Parameter
    ---------
    gray_img : ndarray
        grayscale image array

    Returns
    -------
    ndarray
        gray_img with edges outlined
    """

    gray_s = gray_img.astype('int16') # convert to int16 for better img quality 
    # TODO: Blur gray_s using Gaussian blurring, convole the blurred image with
    # Sobel filters, and combine to compute the intensity gradient image (image with edges highlighted)
    # Hints: open-cv GaussianBlur will be helpful https://medium.com/analytics-vidhya/gaussian-blurring-with-python-and-opencv-ba8429eb879b 
    # Use opencv's filter2D to perform the convolution.

    # Steps
    # 1. apply a gaussian blur with a 5x5 kernel.
    # 2. define the convolution kernel Kx and Ky as defined in the doc.
    # 3. compute Gx and Gy by convolving Kx and Ky respectively with the blurred image.
    # 4. compute G = sqrt(Gx ** 2 + Gy ** 2)
    # 5. Return G

    # Comment out this line after you implement the function.
    #raise NotImplementedError()

    # First, apply a gaussian blur with a 5x5 kernel.
    blur = cv2.GaussianBlur(gray_s, (5,5), cv2.BORDER_DEFAULT)
    # Next, define the convolution kernel Kx and Ky as defined in the doc.
    Kx = np.array([-1, 0, 1, -2, 0, 2, -1, 0, 1]).reshape((3,3))
    Ky = np.array([-1, -2, -1, 0, 0, 0, 1, 2, 1]).reshape((3,3))

    # Now, compute Gx and Gy by convolving Kx and Ky respectively with the blurred image.
    G_x = cv2.filter2D(blur, -1, Kx)
    G_y = cv2.filter2D(blur, -1, Ky)

    # Finally, compute G = sqrt(Gx ** 2 + Gy ** 2)
    # If you have errors computing the square root, you may be encountering overflow - change datatype to int64
    G = np.sqrt(np.square(G_x) + np.square(G_y))

    # Return G
    return G


def edge_detect_canny(gray_img):
    """perform Canny edge detection

    Parameter
    ---------
    gray_img : ndarray
        grayscale image array

    Returns
    -------
    ndarray
        gray_img with edges outlined
    """

    edges = cv2.Canny(gray_img, 100, 200)

    return edges

def do_kmeans(data, n_clusters):
    """Uses opencv to perform k-means clustering on the data given. Clusters it into
       n_clusters clusters.

       Args:
         data: ndarray of shape (n_datapoints, dim)
         n_clusters: int, number of clusters to divide into.

       Returns:
         clusters: integer array of length n_datapoints. clusters[i] is
         a number in range(n_clusters) specifying which cluster data[i]
         was assigned to. 
    """
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, clusters, centers = kmeans = cv2.kmeans(data.astype(np.float32), n_clusters, bestLabels=None, criteria=criteria, attempts=1, flags=cv2.KMEANS_RANDOM_CENTERS)

    return clusters

def cluster_segment(img, n_clusters, random_state=0):
    """segment image using k_means clustering

    Parameter
    ---------
    img : ndarray
        rgb image array
    n_clusters : int
        the number of clusters to form as well as the number of centroids to generate
    random_state : int
        determines random number generation for centroid initialization

    Returns
    -------
    ndarray
        clusters of gray_img represented with similar pixel values
    """
    # Remove this line when you implement this function.
    print(len(img), len(img[0]), len(img[0][0]))
    # Downsample img by a factor of 2 first using the mean to speed up K-means
    img_d = cv2.resize(img, dsize=(int(img.shape[1]/2), int(img.shape[0]/2)), interpolation=cv2.INTER_NEAREST)

    # TODO: Generate a clustered image using K-means

    # first convert our 3-dimensional img_d array to a 2-dimensional array
    # whose shape will be (height * width, number of channels) hint: use img_d.shape
    img_r = img_d.reshape((img_d.shape[0] * img_d.shape[1], img_d.shape[2]))
    
    # fit the k-means algorithm on this reshaped array img_r using the
    # the do_kmeans function defined above.
    clusters = do_kmeans(img_r, n_clusters)

    # reshape this clustered image to the original downsampled image (img_d) width and height 
    cluster_img = clusters.reshape(img_d.shape[0], img_d.shape[1])

    # Upsample the image back to the original image (img) using nearest interpolation
    img_u = 1 - cv2.resize(src=cluster_img, dsize=(img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)

    return img_u.astype(np.uint8)


def to_grayscale(rgb_img):
    return np.dot(rgb_img[... , :3] , [0.299 , 0.587, 0.114])

def segment_image(img): 
    # ONLY USE ONE SEGMENTATION METHOD

    # perform thresholding segmentation
    #binary = threshold_segment_naive(to_grayscale(img), TODO, TODO).astype(np.uint8)

    # perform clustering segmentation.
    binary = cluster_segment(img, 2).astype(np.uint8)

    if np.mean(binary) > 0.5:
        binary = 1 - binary #invert the pixels if K-Means assigned 1's to background, and 0's to foreground

    return binary


"""
below are tests used for sanity checking you image, edit as you see appropriate

"""

def test_thresh_naive(img, lower_thresh, upper_thresh):
    thresh = threshold_segment_naive(img, lower_thresh, upper_thresh)
    show_image(thresh, title='thresh naive', grayscale=True)
    cv2.imwrite(IMG_DIR + "/thresh.jpg", thresh.astype('uint8') * 255)

def test_edge_naive(img):
    edges = edge_detect_naive(img)
    show_image(edges, title='edge naive', grayscale=True)
    cv2.imwrite(IMG_DIR + "/edges.jpg", edges)

def test_edge_canny(img):
    edges = edge_detect_canny(img)
    show_image(edges, title='edge canny', grayscale=True)
    cv2.imwrite(IMG_DIR + "/edges_canny.jpg", edges)

def test_cluster(img, n_clusters):
    # For visualization, we need to scale up the image so it
    # is in range(256) instead of range(n_clusters).
    clusters = (cluster_segment(img, n_clusters) * (255 / (n_clusters-1))).astype(np.uint8)

    cv2.imwrite(IMG_DIR + "/cluster.jpg", clusters)
    clusters = cv2.imread(IMG_DIR + '/cluster.jpg')
    show_image(clusters, title='cluster')

def kmeans_cluster(image):

    pixels = image.reshape((-1, 3))
    pixels = np.float32(pixels)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.85) #criteria
    k = 5 # Choosing number of cluster
    retval, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers) # convert data into 8-bit values 
    segmented_data = centers[labels.flatten()] # Mapping labels to center points( RGB Value)
    segmented_image = segmented_data.reshape((image.shape)) # reshape data into the original image dimensions
    return segmented_image, centers

def mask_red_lower(image):
    # Convert BGR to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # define range of red color in HSV
    lower_red = np.array([0,50,50])
    upper_red = np.array([10,255,255])
    # Threshold the HSV image to get only red colors
    mask = cv2.inRange(hsv, lower_red, upper_red)
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(image,image, mask= mask)
    return mask


def mask_red_upper(image):
    # Convert BGR to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # define range of red color in HSV
    lower_red = np.array([170,50,50])
    upper_red = np.array([180,255,255])
    # Threshold the HSV image to get only red colors
    mask = cv2.inRange(hsv, lower_red, upper_red)
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(image,image, mask= mask)
    return mask

def mask_green(image):
    # Convert BGR to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # define range of red color in HSV
    lower_red = np.array([20,50,50])
    upper_red = np.array([50,255,255])
    # Threshold the HSV image to get only red colors
    mask = cv2.inRange(hsv, lower_red, upper_red)
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(image,image, mask= mask)
    return mask

def mask_blue(image):
    # Convert BGR to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # define range of red color in HSV
    lower_g = np.array([80,50,50])
    upper_g = np.array([120,255,255])
    # Threshold the HSV image to get only red colors
    mask = cv2.inRange(hsv, lower_g, upper_g)
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(image,image, mask= mask)
    return mask

def drawCenters(ima, mask, label):
# change it with your absolute path for the image
    kernel = np.ones((3,3), np.uint8)
    eroded = cv2.erode(mask, kernel, iterations=1)
    image = cv2.dilate(eroded, kernel, iterations=5)
    
    #cv2.imshow("erode+dilate",image)
    #cv2.waitKey()
    
     
    blur = cv2.GaussianBlur(image, (5, 5),
                           cv2.BORDER_DEFAULT)
    ret, thresh = cv2.threshold(blur, 200, 255,
                               cv2.THRESH_BINARY_INV)

    contours, hierarchies = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    coordinate_points = []
    areas = []
    for i in contours:
        areas.append(cv2.contourArea(i))

    for i in contours:
        if cv2.contourArea(i) == max(areas): continue
        M = cv2.moments(i)

        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            coordinate_points.append((cx,cy))
            cv2.drawContours(ima, [i], -1, (0, 255, 0), 2)
            cv2.circle(ima, (cx, cy), 7, (0, 0, 255), -1)
            cv2.putText(ima, label, (cx - 20, cy - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            print(f"x: {cx} y: {cy}")

    return ima, coordinate_points
    

def main():   
    pub = rospy.Publisher('layout', String, queue_size=10)
   
    cam = VideoCapture(0)
    result, image = cam.read()
    if result:
        image = cv2.resize(image, (600, 400)) # need to find better values for these
        #cv2.imshow("image", image)
        #cv2.waitKey()

    image = image[0:500, 100:500]
    im = image.copy()
    ima = image.copy()
    
    mask = mask_red_lower(im)
    ima, waypoints = drawCenters(ima, mask, 'red')

    mask = mask_red_upper(im)
    ima, waypoints2 = drawCenters(ima, mask, 'red')

    waypoints = waypoints + waypoints2

    mask = mask_blue(im)
    ima, corners = drawCenters(ima, mask, 'blue')
    
    
    message = String()
    cs = []
    ws = []

    for c in corners:
        cs.append((c[1], c[0]))

    for w in waypoints:
        ws.append((w[1], w[0]))
    message.data = str(cs) + " + " + str(ws)

    cv2.imshow("", ima)
    cv2.waitKey(0)
    while not rospy.is_shutdown():
        pub.publish(message)
    #print(f"these are the corners: {corners}")
    #print(f"these are the waypoints: {waypoints}")

    

if __name__ == '__main__':
    # adjust the file names here
    """
    last_image_service = rospy.ServiceProxy('last_image', ImageSrv)
    ros_img_msg = last_image_service().image_data
    # Convert the ROS message to a NumPy image
    np_image = ros_to_np_img(ros_img_msg)
     #TODO - pass the image from service to the fucntions below as an array 
    # Display the CV Image
    cv2.imshow("CV Image", np_image)
    """
    rospy.init_node('segmentation', anonymous=True)
    main()





