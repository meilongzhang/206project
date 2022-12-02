#!/usr/bin/env python
# license removed for brevity
# import rospy
# from std_msgs.msg import String
# from geometry_msgs.msg import Twist, Point 
from tf.transformations import euler_from_quaternion
# import tf2_ros
# import nav_msgs
# from nav_msgs.msg import Odometry
import math as mt 

import rospy
import tf2_ros
import sys
import numpy as np 
from geometry_msgs.msg import Twist

def talker():
    # global curX
    # global curY
    # sub = rospy.Subscriber('/odom', Odometry, callback)
    #get  tf to enable getting the robot pose 
    pub = rospy.Publisher('cmd_vel' , Twist, queue_size=10)
    tfBuffer = tf2_ros.Buffer()
    tfListener = tf2_ros.TransformListener(tfBuffer)
  
    # tfListener = tf2_ros.TransformListener(tfBuffer)
    rate = rospy.Rate(10) # 10hz
    KI = 0.2
    KP = 0.3
    KD = 0.02
    KP_a = 0.3
    KI_a = 0.2
    KD_a = 0.02
    dt = 0.01
    
    goalX = 2.5
    goalY = 0.4
    goalZ = 0.5
    # prevX = 0
    # prevY = 0
    # sumX = 0
    # sumY = 0
    # sum_err_t = 0 
    # prev_err_t = 0
    # sum_err_r = 0 
    # prev_err_r = 0
    # trans, rot = tfBuffer.lookup_transform('odom','base_link', rospy.Time())
    # rot = euler_from_quaternion(rot)
    # trans = Point(*trans)
    # curX = trans.x
    # curY = trans.y

    while not rospy.is_shutdown():
        try: 
            pose = tfBuffer.lookup_transform("odom","base_link", rospy.Time())
            print('passed lookup transform')
            (roll, pitch, yaw) = euler_from_quaternion(
            [pose.transform.rotation.x, pose.transform.rotation.y,
             pose.transform.rotation.z, pose.transform.rotation.w])
            trans = pose.transform.translation
            curX = trans.x
            curY = trans.y
            err_t = mt.sqrt((goalX - curX)**2 + (goalY - curY)**2)
            angl_t = mt.atan2(goalY - curY, goalX - curX)
            prev_angle = 0 
            total_angle = 0
            sum_err_t = 0 
            prev_err_t = 0
            while err_t > 0.05 and angl_t > 0.2 :
                #PID for err_t 
                # sum_err_t += err_t * dt
                # dedt_err_t = (err_t - prev_err_t) / dt
                # wX = KP*err_t + KI * sum_err_t + KD * dedt_err_t
                # prev_err_t = err_t
                sum_err_t += err_t 
                dedt_err_t = (err_t - prev_err_t)
                wX = KP*err_t + KI * sum_err_t + KD * dedt_err_t
                prev_err_t = err_t
                #PID for err_angl
                diff_angle = (angl_t - prev_angle)/dt
                total_angle += angl_t * dt
                Wz = KP_a * angl_t + KI_a * total_angle + KD_a * diff_angle
                prev_angle = angl_t
                control_command = Twist()
                control_command.linear.x = 0
                control_command.linear.y = 0.4
                control_command.linear.z = 0
                control_command.angular.x = 0
                control_command.angular.y = 0
                control_command.angular.z = 0.03
                print(control_command)
                pub.publish(control_command)
            err_r = abs(goalZ - yaw) # potential error 
            # while err_r > 0.1:
            #     #PID for err_t 
            #     sum_err_r += err_r * dt
            #     dedt_err_r = (err_r - prev_err_r) / dt
            #     wZ = KP*err_r + KI * sum_err_r + KD * dedt_err_r
            #     prev_err_t = err_t

            #     #if (diffX < 0.01, and diffY < 0.01):

            #     control_command.linear.x = 0
            #     control_command.linear.y = 0
            #     control_command.linear.z = 0
            #     control_command.angular.x = 0
            #     control_command.angular.y = 0
            #     control_command.angular.z = 1 * wZ

            #     pub.publish(control_command)
            # rate.sleep()
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
            print(e)
            pass
        # Use our rate object to sleep until it is time to publish again
        rate.sleep()  

# def callback(data):
#     global curX
#     global curY
    
#     curX = data.pose.pose.position.x
#     curY = data.pose.pose.position.y
#     print(f"current x = {curX}, current y = {curY}")

if __name__ == '__main__':
    rospy.init_node('talker', anonymous=True)
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
