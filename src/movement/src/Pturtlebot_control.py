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
from std_msgs.msg import String
import math as mt 
from tf.transformations import euler_from_quaternion


goals = []
pathFound = False
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
  global goals
  global pathFound
  
  #Create a publisher and a tf buffer, which is primed with a tf listener
  pub = rospy.Publisher('cmd_vel' , Twist, queue_size=10)
  sub = rospy.Subscriber('waypoints', String, callback)
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
  
  while True:
    try:
      goalX, goalY = goals.pop(0)
      break
    except:
      pass
  
  # finishedRotation = False
  aligned = False
  oriented = False
  arrived = False
  pointNumber = 0
  # Loop until the node is killed with Ctrl-C
  while not rospy.is_shutdown():
    try:
      # GETTING CURRENT STATE OF ROBOT
      trans = tfBuffer.lookup_transform("odom","base_link", rospy.Time())
      (roll, pitch, yaw) = euler_from_quaternion(
              [trans.transform.rotation.x, trans.transform.rotation.y,
                trans.transform.rotation.z, trans.transform.rotation.w])

      curX = trans.transform.translation.x
      curY = trans.transform.translation.y
      diffX = goalX - curX
      diffY = goalY - curY
      print("waypoint number:", pointNumber,"goal X: ", goalX, " goal Y: ", goalY)
      print("current X: ", curX, " current Y: ", curY)
      # ALIGNING STEP
      """
      if not aligned:
        targetYaw = 0
        yawDiff = abs(yaw - targetYaw)
  
        if yawDiff >= 0.1: 
          control_command = Twist()
          control_command.angular.z = 0.5
          pub.publish(control_command)

        if yawDiff < 0.1:
          print("Aligning Step Done")
          aligned = True
      """
      # ORIENTATION STEP
      if not oriented:
        targetYaw = mt.atan2(diffY, diffX)
        yawDiff = abs(yaw - targetYaw)
        if yawDiff >= 0.05:
          control_command = Twist()
          control_command.angular.z = 0.5
          pub.publish(control_command)

        if yawDiff < 0.05:
          print("Orientation Step Done")
          oriented = True

      # MOVEMENT STEP
      elif not arrived:
        distance = mt.sqrt((goalX - curX) ** 2 + (goalY - curY) ** 2)
        #diffX = goalX - curX
        print("distance: ", distance)
        if distance >= 0.03:
          wX = K1*distance
          control_command = Twist()
          control_command.linear.x = wX
          pub.publish(control_command)
        if distance < 0.03:
          print("Movement Step Done")
          arrived = True

      if arrived:
        arrived = False
        oriented = False
        aligned = False
        print("Arrived at checkpoint, moving onto next")
        pointNumber += 1
        if len(goals) != 0:
          goalX, goalY = goals.pop(0)
        else:
          print("Arrived at end.")
          break
      
    except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
      pass
    # Use our rate object to sleep until it is time to publish again
    r.sleep()


def callback(data):
  global goals
  global pathFound
  if not pathFound:
    print("in here")
    strNumbers = data.data[1:-1].replace('(', '').replace(')', '').split(', ')
    nums = [int(x) for x in strNumbers][2:]
    a = iter(nums)
    goals = [(y * 0.0045, x * 0.0045) for x, y in zip(a, a)] # change this factor
    print("set goals")
    pathFound = True
  


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
