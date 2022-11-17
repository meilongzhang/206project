#!/usr/bin/env python
import rospy
import sensor_msgs
from sensor_msgs.msg import JointState
import nav_msgs
from nav_msgs.msg import Odometry


def listener():
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("/odom", Odometry, callback)

    rospy.spin()

def callback(data):
    print(data)

if __name__ == '__main__':
    listener()