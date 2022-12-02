#!/usr/bin/env python
#The line above tells Linux that this file is a Python script,
#and that the OS should use the Python interpreter in /usr/bin/env
#to run it. Don't forget to use "chmod +x [filename]" to make
#this script executable.

#Import the rospy package. For an import to work, it must be specified
#in both the package manifest AND the Python file in which it is used.
import rospy
import tf2_ros
import sys
import numpy as np 
from geometry_msgs.msg import Twist
import math as mt 
from tf.transformations import euler_from_quaternion

#Define the method which contains the main functionality of the node.
def controller():
  """
  Controls a turtlebot whose position is denoted by turtlebot_frame,
  to go to a position denoted by target_frame
  Inputs:
  - turtlebot_frame: the tf frame of the AR tag on your turtlebot
  - target_frame: the tf frame of the target AR tag
  """

  ################################### YOUR CODE HERE ##############

  #Create a publisher and a tf buffer, which is primed with a tf listener
  pub = rospy.Publisher('cmd_vel' , Twist, queue_size=10)
  tfBuffer = tf2_ros.Buffer()
  tfListener = tf2_ros.TransformListener(tfBuffer)
  
  # Create a timer object that will sleep long enough to result in
  # a 10Hz publishing rate
  r = rospy.Rate(10) # 10hz


  K1 = 0.3
  K2 = 1

  KI = 0.2
  KP = 0.3
  KD = 0.02
  KP_a = 0.3
  KI_a = 0.2
  KD_a = 0.02
  dt = 0.01

  goalX = 0
  goalY = 0

  # Loop until the node is killed with Ctrl-C
  while not rospy.is_shutdown():
    try:
      

    # we used this to trouble shoot
      trans = tfBuffer.lookup_transform("odom","base_link", rospy.Time())
      (roll, pitch, yaw) = euler_from_quaternion(
              [trans.transform.rotation.x, trans.transform.rotation.y,
                trans.transform.rotation.z, trans.transform.rotation.w])
      """ if yaw is negative, then bot is not facing goal. 
      do angle rotation until yaw is positive, then move forward."""
      print(yaw)
      curX = trans.transform.translation.x
      curY = trans.transform.translation.y
      print(curX, curY, goalX, goalY)
      err_t = goalX - curX
      angl_t = goalY - curY
      wX = K1*err_t
      Wz = K2 * angl_t
      print("wx: ", wX, " wz: ", Wz)
      control_command = Twist()
      control_command.linear.x = wX
      control_command.angular.z = Wz
      pub.publish(control_command)
      
      # i = 0
      # while i < 100:
      #   trans = tfBuffer.lookup_transform("odom","base_link", rospy.Time())
      #   curX = trans.transform.translation.x
      #   curY = trans.transform.translation.y
      #   print(curX, curY, goalX, goalY)
      #   err_t = goalX - curX
      #   angl_t = goalY - curY
      #   wX = K1*err_t
      #   Wz = K2 * angl_t
      #   print("wx: ", wX, " wz: ", Wz)
      #   control_command = Twist()
      #   control_command.linear.x = wX
      #   control_command.linear.y = 0
      #   control_command.linear.z = 0
      #   control_command.angular.x = 0
      #   control_command.angular.y = 0
      #   control_command.angular.z = Wz
      #   i += 1
      #   pub.publish(control_command)
      
    except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
      pass
    # Use our rate object to sleep until it is time to publish again
    r.sleep()

      
# This is Python's sytax for a main() method, which is run by default
# when exectued in the shell
if __name__ == '__main__':
  # Check if the node has received a signal to shut down
  # If not, run the talker method

  #Run this program as a new node in the ROS computation graph 
  #called /turtlebot_controller.
  rospy.init_node('turtlebot_controller', anonymous=True)

  try:
    controller()
  except rospy.ROSInterruptException:
    pass
