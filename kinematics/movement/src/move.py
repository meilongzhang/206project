#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import nav_msgs
from nav_msgs.msg import Odometry

def talker():
    global curX
    global curY
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    sub = rospy.Subscriber('/odom', Odometry, callback)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    K1 = 0.2
    K2 = 1
    KP = 0.3
    KD = 0.02
    dt = 0.01
    goalX = 2.5
    goalY = 0.4
    prevX = 0
    prevY = 0
    sumX = 0
    sumY = 0
    while not rospy.is_shutdown():
        #PID control equations here
        control_command = Twist()


        errX = curX - goalX
        errY = curY - goalY
        print(errX, errY)
        while (abs(errX) > 0.01 and abs(errY) > 0.01):
            sumX += errX * dt
            dedtX = (errX - prevX) / dt
            wX = KP*errX + K1 * sumX + KD * dedtX
            prevX = errX

            
            sumY += errY * dt
            dedtY = (errY - prevY) / dt
            wY = KP*errY + K1 * sumY + KD * dedtY
            prevY = errY


        

            #if (diffX < 0.01, and diffY < 0.01):

            control_command.linear.x = wX
            control_command.linear.y = 0
            control_command.linear.z = 0
            control_command.angular.x = 0
            control_command.angular.y = 0
            control_command.angular.z = -1 * wY

            pub.publish(control_command)
        rate.sleep()

def callback(data):
    global curX
    global curY
    
    curX = data.pose.pose.position.x
    curY = data.pose.pose.position.y
    print(f"current x = {curX}, current y = {curY}")

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
