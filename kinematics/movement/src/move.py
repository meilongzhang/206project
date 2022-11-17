#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist

def talker():
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        control_command = Twist()
        
        control_command.linear.x = 0.1#constant value when z=0, 0 when z!=0
        control_command.linear.y = 0
        control_command.linear.z = 0
        control_command.angular.x = 0
        control_command.angular.y = 0
        control_command.angular.z = 0#odom and position of next point

        pub.publish(control_command)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
