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
from geometry_msgs.msg import Twist , Point 
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
  # tfListener = tf2_ros.TransformListener(tfBuffer)
  
  # Create a timer object that will sleep long enough to result in
  # a 10Hz publishing rate
  r = rospy.Rate(10) # 10hz
  #set variables
  control_command = Twist()
  position = Point()
  #PID controller variables 
  KI = 0.02
  KP = 0.03
  KD = 0.01
  KP_a = 0.03
  KI_a = 0.02
  KD_a = 0.01
  dt = 0.01
  #goal positions 
  goalX = -0.3
  goalY = 0
  goalZ = 0
  #current positions 
  curX = 0 
  curY = 0 
  #translation errors 
  prev_err_t = 0
  sum_err_t = 0 
  #angular errors 
  prev_err_r = 0 
  sum_err_r = 0
  #functrions to minimize 
  #translation 
  err_t = mt.sqrt((goalX - curX)**2 + (goalY - curY)**2)
  #rotation 
  err_r = mt.atan2(goalY - curY, goalX - curX)
  # Loop until the node is killed with Ctrl-C
  print('i am running')
  while not rospy.is_shutdown():
    try:     
      while err_t > 0.05 or err_r > 0.05:
        #translation
        err_t = mt.sqrt((goalX - curX)**2 + (goalY - curY)**2)
        print('current error')
        print(err_t)
        trans = tfBuffer.lookup_transform("odom","base_link", rospy.Time())
        rot = euler_from_quaternion(
              [trans.transform.rotation.x, trans.transform.rotation.y,
                trans.transform.rotation.z, trans.transform.rotation.w])
        #convert rotation from quaterion to euler and get the Z component 
        rot = rot[2]
        #get the x and Y translation only
        curX = trans.transform.translation.x
        curY = trans.transform.translation.y
        print('current position')
        print(curX,curY)
        #tune the rotational error 
        err_r = mt.atan2(goalY - curY, goalX - curX)
        rot_l = mt.pi/4 
        #take into account robot orientation 
        if err_r < -rot_l or err_r > rot_l:
              if goalY < 0 and curY < goalY:
                err_r = -2*mt.pi + err_r
              elif goalY >= 0 and curY > goalY:
                err_r = 2*mt.pi + err_r
        if prev_err_r > mt.pi-0.1 and rot <= 0:
            rot = 2*mt.pi + rot
        elif prev_err_r < -mt.pi+0.1 and rot > 0:
            rot = -2*mt.pi + rot 

        angle_derv = err_r - prev_err_r
        trans_derv = err_t - prev_err_t 

        #PID controller for distance 
        p_distance = KP * err_t * KI * sum_err_t + KD*trans_derv
        print('current distance to target')
        print(p_distance)
        #PID controller for rotation
        print('current rotation to target')
        p_rot = KP_a * err_r * KI_a * sum_err_r + KD*angle_derv
        print(p_rot)

        # sum_err_t += err_t * dt
        # dedt_err_t = (err_t - prev_err_t) / dt
        # wX = KP*err_t + KI * sum_err_t + KD * dedt_err_t
        # prev_err_t = err_t
        # #PID for err_angl
        # diff_angle = (angl_t - prev_angle)/dt
        # total_angle += angl_t * dt
        # Wz = KP_a * angl_t + KI_a * total_angle + KD_a * diff_angle
        # prev_angle = angl_t
        # print("wx: ", wX, " wz: ", Wz)

        control_command.linear.x = p_distance
        control_command.linear.y = 0
        control_command.linear.z = 0
        control_command.angular.x = 0
        control_command.angular.y = 0
        control_command.angular.z = p_rot - rot

        prev_err_r = rot 
        pub.publish(control_command)
        r.sleep()
        prev_err_t = err_t
        sum_err_t += err_t
        sum_err_r += err_r
      
    except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
      print('not again')
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
