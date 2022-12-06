from RRTbasePy import RRTGraph
from RRTbasePy import RRTMap
import pathSmooth
import sys
import pygame
import rospy
from std_msgs.msg import String


corners = []
obstacles = []
layoutFound = False


def main(type):
    global corners
    global obstacles

    
    pub = rospy.Publisher('waypoints', String, queue_size=10)
    sub = rospy.Subscriber('layout', String, callback)


    while True:
        if len(corners) != 0:
            break
        else:
            print("waiting for corners")

    print("no longer waiting for corners")

    maxX = 0
    maxY = 0
    
    for corner in corners:
        if corner[0] > maxX:
            maxY = corner[0]
            maxX = corner[1]

    for corner in corners:
        if corner[0] == maxX:
            pass
        else:
            goalY = corner[0]
            goalX = corner[1]
    

    print(corners[0])
    dimensions=(maxX, maxY)
    start=(0,0)
    goal=(goalX,goalY)
    obsdim=30
    obsnum=len(obstacles)
    iteration = 0
    radius=100

    pygame.init()
    map=RRTMap(start,goal,dimensions,obsdim,obsnum)
    graph=RRTGraph(start,goal,dimensions,obsdim,obsnum,radius)

    #obstacles=graph.makeobs()
    obstacles = [(o[0] - obsdim/2, o[1] - obsdim/2) for o in obstacles]
    obstacles = graph.convertobs(obstacles)
    map.drawMap(obstacles)

    while (not graph.path_to_goal()):
        if iteration % 10 == 0:
            X,Y,Parent = graph.bias(goal,type)
        
        else:
            X,Y,Parent=graph.expand(type)

        map.map.fill((255,255,255))
        map.drawMap(obstacles)
        for i in range(len(graph.x)):
            pygame.draw.circle(map.map, map.Grey, (graph.x[i], graph.y[i]), map.nodeRad+2,0)
            pygame.draw.line(map.map, map.Blue, (graph.x[i], graph.y[i]), (graph.x[graph.parent[i]], graph.y[graph.parent[i]])) 
        
        if iteration % 5 == 0:
            pygame.display.update()
        
        iteration += 1
    
    map.drawPath(graph.getPathCoords())
    calculatedPath = graph.getPathCoords()[::-1]


    pygame.display.update()
    pygame.event.clear()
    while not rospy.is_shutdown():
        waypo = String()
        waypo.data = str(calculatedPath)
        pub.publish(waypo)
    
    



    #smoothedPath = pathSmooth.B_spline(graph.getPathCoords(), style='waypoint')
    #print(len(smoothedPath), len(graph.getPathCoords()))
    #map=RRTMap(start,goal,dimensions,obsdim,obsnum)
    #map.drawMap(obstacles, dim=True)
    #map.drawPath(smoothedPath)
    

def callback(data):
    if not layoutFound:
        data = data.data[1:-1].split(' + ')
        corners = data[0]
        obstacles = data[1]
        corners = corners.replace('(', '').replace(')', '').replace(']', '').split(', ')
        obstacles = obstacles.replace('(', '').replace(')', '').replace('[', '').split(', ')
        corners = [int(x) for x in corners]
        obstacles = [int(x) for x in obstacles]
        a = iter(corners)
        b = iter(obstacles)
        corners = [(x, y) for x, y in zip(a, a)]
        obstacles = [(x, y) for x, y in zip(b, b)]
        moveToZero(corners, obstacles)

def moveToZero(c, o):
    global corners
    global obstacles
    global layoutFound
    corners = []
    obstacles = []
    minX = float("inf")
    minY = float("inf")
    for corner in c:
        if corner[0] < minX or corner[1] < minY:
            minX = corner[0]
            minY = corner[1]

    for corner in c:
        if corner[0] - minX == 0:
            pass
        else:
            corners.append((corner[0] - minX, corner[1] - minY))

    for obstacle in o:
        obstacles.append((obstacle[0] - minX, obstacle[1] - minY))

    layoutFound = True

if __name__ == '__main__':
    """
    result=False
    while not result:
        try:
            main()
            result=True
        except:
            result=False
    """
    input = sys.argv[1]
    print(f"Algorithm Type: {input}")
    rospy.init_node('planning_talker', anonymous=True)
    main(input)

    
    