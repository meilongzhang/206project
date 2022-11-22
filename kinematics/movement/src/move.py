#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import nav_msgs
from nav_msgs.msg import Odometry

def talker():
    global diffX
    global diffY
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    sub = rospy.Subscriber('/odom', Odometry, callback)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    K1 = 0.3
    K2 = 1
    while not rospy.is_shutdown():
        #PID control equations here
        control_command = Twist()
        print(diffX, diffY)
        control_command.linear.x = K1 * diffX#constant value when z=0, 0 when z!=0
        control_command.linear.y = 0
        control_command.linear.z = 0
        control_command.angular.x = 0
        control_command.angular.y = 0
        control_command.angular.z = K2 * diffY#odom and position of next point

        pub.publish(control_command)
        rate.sleep()

def callback(data):
    global goalX
    global goalY
    global diffX
    global diffY
    global goalChanged
    if not goalChanged:
        goalX = data.pose.pose.position.x + 0.5
        goalY = data.pose.pose.position.y + 0.5
        goalChanged = True
    diffX = goalX - data.pose.pose.position.x
    diffY = goalY - data.pose.pose.position.y

if __name__ == '__main__':
    try:
        goalX = 0
        goalY = 0
        diffX = 0
        diffY = 0
        goalChanged = False
        talker()
    except rospy.ROSInterruptException:
        pass
