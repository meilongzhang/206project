from RRTbasePy import RRTGraph
from RRTbasePy import RRTMap
import pathSmooth
import sys
import pygame

def main(type):
    dimensions=(600,1000)
    start=(50,50)
    goal=(510,510)
    obsdim=30
    obsnum=50
    iteration = 0
    radius=100

    pygame.init()
    map=RRTMap(start,goal,dimensions,obsdim,obsnum)
    graph=RRTGraph(start,goal,dimensions,obsdim,obsnum,radius)

    #obstacles=graph.makeobs()
    obstacles = graph.convertobs([(500,400), (200,130)])
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
    print(graph.getPathCoords()[::-1])
    #smoothedPath = pathSmooth.B_spline(graph.getPathCoords(), style='waypoint')
    #print(len(smoothedPath), len(graph.getPathCoords()))
    #map=RRTMap(start,goal,dimensions,obsdim,obsnum)
    #map.drawMap(obstacles, dim=True)
    #map.drawPath(smoothedPath)
    pygame.display.update()
    pygame.event.clear()
    pygame.event.wait(0)


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
    main(input)

    
    