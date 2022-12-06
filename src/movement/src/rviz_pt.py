import rospy
from geometry_msgs.msg import PointStamped 
from visualization_msgs.msg import Marker 
import tf
import random
import numpy as np

global x,y,z
x = 0.0
y = 0.0
z = 0.0

def listener():
    rospy.init_node('rviz_marker', anonymous=True)
    pub = rospy.Publisher('/visualization_marker', Marker, queue_size= 10)
    marker = Marker()

    marker.header.frame_id = "/odom"
    marker.header.stamp = rospy.Time.now()

    # set shape, Arrow: 0; Cube: 1 ; Sphere: 2 ; Cylinder: 3
    marker.type = 2
    marker.id = 0

    # Set the scale of the marker
    marker.scale.x = 1.0
    marker.scale.y = 1.0
    marker.scale.z = 1.0

    # Set the color
    marker.color.r = 0.0
    marker.color.g = 1.0
    marker.color.b = 0.0
    marker.color.a = 1.0

    # Set the pose of the marker
    marker.pose.position.x = x
    marker.pose.position.y = y
    marker.pose.position.z = z
    marker.pose.orientation.x = 0.0
    marker.pose.orientation.y = 0.0
    marker.pose.orientation.z = 0.0
    marker.pose.orientation.w = 1.0

    while not rospy.is_shutdown():
        pub.publish(marker)
        # rospy.rostime.wallsleep(1.0)

if __name__ == '__main__':
    listener()