#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist, Point 
import tf2_ros
import nav_msgs
from nav_msgs.msg import Odometry
import math as mt 

def talker():
    # global curX
    # global curY
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    # sub = rospy.Subscriber('/odom', Odometry, callback)
    #get  tf to enable getting the robot pose 
    tfBuffer = tf2_ros.Buffer()
    # tfListener = tf2_ros.TransformListener(tfBuffer)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    K1 = 0.2
    K2 = 1
    KP = 0.3
    KD = 0.02
    dt = 0.01
    goalX = 2.5
    goalY = 0.4
    goalZ = 0.5
    # prevX = 0
    # prevY = 0
    # sumX = 0
    # sumY = 0
    sum_err_t = 0 
    prev_err_t = 0
    sum_err_r = 0 
    prev_err_r = 0
    trans, rot = tfBuffer.lookup_transform('base_link','odom', rospy.Time())
    curX = trans.tranform.translation.x
    curY = trans.tranform.translation.y
    while not rospy.is_shutdown():
        #PID control equations here
        control_command = Twist()
        # errX = curX - goalX
        # errY = curY - goalY
        # print(errX, errY)
        # while (abs(errX) > 0.01 and abs(errY) > 0.01):
        #     sumX += errX * dt
        #     dedtX = (errX - prevX) / dt
        #     wX = KP*errX + K1 * sumX + KD * dedtX
        #     prevX = errX

            
        #     sumY += errY * dt
        #     dedtY = (errY - prevY) / dt
        #     wY = KP*errY + K1 * sumY + KD * dedtY
        #     prevY = errY


        

        #     #if (diffX < 0.01, and diffY < 0.01):

        #     control_command.linear.x = wX
        #     control_command.linear.y = 0
        #     control_command.linear.z = 0
        #     control_command.angular.x = 0
        #     control_command.angular.y = 0
        #     control_command.angular.z = -1 * wY

        #     pub.publish(control_command)
        # rate.sleep()

        #calulate the translation error 
        err_r = abs(goalZ - rot[2]) 
        while err_r > 0.1:
            #PID for err_t 
            sum_err_r += err_r * dt
            dedt_err_r = (err_r - prev_err_r) / dt
            wZ = KP*err_r + K1 * sum_err_r + KD * dedt_err_r
            prev_err_t = err_t

            #if (diffX < 0.01, and diffY < 0.01):

            control_command.linear.x = 0
            control_command.linear.y = 0
            control_command.linear.z = 0
            control_command.angular.x = 0
            control_command.angular.y = 0
            control_command.angular.z = 1 * wZ

            pub.publish(control_command)
        rate.sleep()
        err_t = mt.sqrt((goalX - curX)**2 + (goalY - curY)**2)
        while err_t > 0.05:
            #PID for err_t 
            sum_err_t += err_t * dt
            dedt_err_t = (err_t - prev_err_t) / dt
            wX = KP*err_t + K1 * sum_err_t + KD * dedt_err_t
            prev_err_t = err_t

            #if (diffX < 0.01, and diffY < 0.01):

            control_command.linear.x = wX
            control_command.linear.y = 0
            control_command.linear.z = 0
            control_command.angular.x = 0
            control_command.angular.y = 0
            control_command.angular.z = 0

            pub.publish(control_command)
        rate.sleep()

# def callback(data):
#     global curX
#     global curY
    
#     curX = data.pose.pose.position.x
#     curY = data.pose.pose.position.y
#     print(f"current x = {curX}, current y = {curY}")

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
