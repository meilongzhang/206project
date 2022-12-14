import matplotlib.pyplot as plt
import numpy as np
from numpy.random import uniform 
import scipy
from filterpy.monte_carlo import systematic_resample
from numpy.linalg import norm
from numpy.random import randn
import scipy.stats

# import rospy
# import tf2_ros
# import tf

# from sensor_msgs.msg import LaserScan
# from visualization_msgs.msg import Marker
# from geometry_msgs.msg import Point
# from std_msgs.msg import ColorRGBA

import numpy as np
#create uniform gaussian particles 
def particle_creation(x_range, y_range, hdg_range, N):
    particles = np.empty((N, 3))
    particles[:, 0] = uniform(x_range[0], x_range[1], size=N)
    particles[:, 1] = uniform(y_range[0], y_range[1], size=N)
    particles[:, 2] = uniform(hdg_range[0], hdg_range[1], size=N)
    particles[:, 2] %= 2 * np.pi
    return particles

def create_gaussian_particles(mean, std, N):
    particles = np.empty((N, 3))
    particles[:, 0] = mean[0] + (randn(N) * std[0])
    particles[:, 1] = mean[1] + (randn(N) * std[1])
    particles[:, 2] = mean[2] + (randn(N) * std[2])
    particles[:, 2] %= 2 * np.pi
    return particles
    
def predict_turtle(particles, u, std, dt=1.):
    """ move according to control input u (heading change, velocity)
    with noise Q (std heading change, std velocity)`"""

    N = len(particles)
    # update heading
    particles[:, 2] += u[0] + (randn(N) * std[0])
    particles[:, 2] %= 2 * np.pi

    # move in the (noisy) commanded direction
    dist = (u[1] * dt) + (randn(N) * std[1])
    particles[:, 0] += np.cos(particles[:, 2]) * dist
    particles[:, 1] += np.sin(particles[:, 2]) * dist

def update_turtle(particles, weights, z, R, landmarks):
    for i, landmark in enumerate(landmarks):
        distance = np.linalg.norm(particles[:, 0:2] - landmark, axis=1)
        weights *= scipy.stats.norm(distance, R).pdf(z[i])

    weights += 1.e-300      # avoid round-off to zero
    weights /= sum(weights) # normalize

def turtle_estimate(particles, weights):
    """returns mean and variance of the weighted particles"""

    pos = particles[:, 0:2]
    mean = np.average(pos, weights=weights, axis=0)
    var  = np.average((pos - mean)**2, weights=weights, axis=0)
    return mean, var


def neff(weights):
    return 1. / np.sum(np.square(weights))

def resample_from_index(particles, weights, indexes):
    particles[:] = particles[indexes]
    weights.resize(len(particles))
    weights.fill (1.0 / len(weights))

####### EXAMPLE PARTICLE FILTER ########
#get topics 
self._sensor_topic = rospy.get_param("~topics/sensor")
# -- self._vis_topic
self._vis_topic = rospy.get_param("~topics/vis")
# Frames.

# TODO! You'll need to set values for class variables called:
# self._sensor_frame = rospy.get_param("sensor_frame")
self._sensor_frame = rospy.get_param("~frames/sensor")
# self._sensor_frame = rospy.get_param("base_link")
self._fixed_frame = rospy.get_param("~frames/fixed")
###
def turtlebot_particle(N, iters=18, sensor_std_err=.1, 
            do_plot=True, plot_particles=False,
            xlim=(0, 20), ylim=(0, 20),
            initial_x=None):
    #these can be the obatacles (i.e landmarks - this will be given by the image segmentation node)(#TODO) 
    landmarks = np.array([[-1, 2], [5, 10], [12,14], [18,21]])
    NL = len(landmarks)
    
    plt.figure()
 
    # create particles and weights
    if initial_x is not None:
        particles = create_gaussian_particles(
            mean=initial_x, std=(5, 5, np.pi/4), N=N)
    else:
        particles = particle_creation((0,20), (0,20), (0, 6.28), N)
    weights = np.ones(N) / N

    if plot_particles:
        alpha = .20
        if N > 5000:
            alpha *= np.sqrt(5000)/np.sqrt(N)           
        plt.scatter(particles[:, 0], particles[:, 1], 
                    alpha=alpha, color='g') 
    xs = []
    #get the robot pose 
    pose = self._tf_buffer.lookup_transform(
            self._fixed_frame, self._sensor_frame, rospy.Time())
    #give robot pose by initial robot position (#TODO)
    sensor_x = pose.transform.translation.x
    sensor_y = pose.transform.translation.y
    robot_pos = np.array([0., 0.])
    for x in range(iters):
        #derived fron sensor measurments 
        robot_pos = (sensor_x, sensor_y)

        # distance from robot to each landmark
        zs = (norm(landmarks - robot_pos, axis=1) + 
              (randn(NL) * sensor_std_err))

        # move diagonally forward to (x+1, x+1)
        predict_turtle(particles, u=(0.00, 1.414), std=(.2, .05))
        
        # incorporate measurements
        update_turtle(particles, weights, z=zs, R=sensor_std_err, 
               landmarks=landmarks)
        
        # resample if too few effective particles
        if neff(weights) < N/2:
            indexes = systematic_resample(weights)
            resample_from_index(particles, weights, indexes)
            assert np.allclose(weights, 1/N)
        mu, var = turtle_estimate(particles, weights)
        xs.append(mu)

        if plot_particles:
            plt.scatter(particles[:, 0], particles[:, 1], 
                        color='k', marker=',', s=1)
        p1 = plt.scatter(robot_pos[0], robot_pos[1], marker='+',
                         color='k', s=180, lw=3)
        p2 = plt.scatter(mu[0], mu[1], marker='s', color='r')
    
    xs = np.array(xs)
    #plt.plot(xs[:, 0], xs[:, 1])
    plt.legend([p1, p2], ['Actual', 'PF'], loc=4, numpoints=1)
    plt.xlim(*xlim)
    plt.ylim(*ylim)
    print('final position error, variance:\n\t', mu - np.array([iters, iters]), var)
    plt.show()

from numpy.random import seed
# seed(2) 
# run_pf1(N=5000, plot_particles=False)
seed(2)
turtlebot_particle(N=5000, iters=8, plot_particles=True, 
        xlim=(0,8), ylim=(0,8))