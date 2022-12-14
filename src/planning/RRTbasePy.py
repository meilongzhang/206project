import random 
import math
import pygame

class RRTMap:
    def __init__(self,start,goal,MapDimensions,obsdim,obsnum):
        self.start = start
        self.goal = goal
        self.MapDimensions = MapDimensions
        self.Maph,self.Mapw = self.MapDimensions

        self.MapWindowName = 'RRT path planning'
        pygame.display.set_caption(self.MapWindowName)
        self.map = pygame.display.set_mode((self.Mapw,self.Maph))
        self.map.fill((255,255,255))
        self.nodeRad = 2
        self.nodeThickness = 0
        self.edgeThickness = 1

        self.obstacles = []
        self.obsdim = obsdim
        self.obsNumber = obsnum

        self.Grey = (70,70,70)
        self.Blue = (0,0,255)
        self.Green = (0,255,0)
        self.Red = (255,0,0)
        self.White = (255,255,255)

    def drawMap(self,obstacles, dim=False):
        pygame.draw.circle(self.map,self.Green,self.start,self.nodeRad+5,0)
        pygame.draw.circle(self.map,self.Green,self.goal,self.nodeRad+20,1)
        self.drawObs(obstacles, dim)

    def drawPath(self,path):
        for node in path:
            pygame.draw.circle(self.map, self.Red, node, self.nodeRad+3,0)

    def drawObs(self,obstacles, dim):
        obstaclesList=obstacles.copy()
        while(len(obstaclesList)>0):
            obstacle = obstaclesList.pop(0)
            if dim:
                obstacle[0] += 30
                obstacle[1] += 30
                obstacle[2] -= 30
                obstacle[3] -= 30
            pygame.draw.rect(self.map, self.Grey, obstacle)

# (0,0), (0,500), (600,0) (600,500)
# (500,400), (200,130)
class RRTGraph:
    def __init__(self,start,goal,MapDimensions,obsdim,obsnum,radius):
        (x,y) = start
        self.start = start
        self.goal = goal
        self.goalFlag = False
        self.maph,self.mapw = MapDimensions
        self.x = []
        self.y = []
        self.parent = []
        self.costs = []

        self.x.append(x)
        self.y.append(y)
        self.parent.append(0)
        self.obstacles = []
        self.obsDim = obsdim
        self.obsNum = obsnum

        self.goalstate = None
        self.path = []

        self.radius=radius

    def makeRandomRect(self):
        uppercornerx = int(random.uniform(0,self.mapw-self.obsDim))
        uppercornery = int(random.uniform(0,self.maph-self.obsDim))
        return (uppercornerx,uppercornery)


    def convertobs(self, coordinates):
        obs = []

        for coords in coordinates:
            rectang = None
            startgoalcol = True
            while startgoalcol:
                rectang = pygame.Rect(coords,(self.obsDim,self.obsDim))
                if rectang.collidepoint(self.start) or rectang.collidepoint(self.goal):
                    startgoalcol = True
                else:
                    startgoalcol=False
            obs.append(rectang)
        self.obstacles=obs.copy()
        return obs

    def makeobs(self):
        obs = []

        for i in range(0, self.obsNum):
            rectang = None
            startgoalcol = True
            while startgoalcol:
                upper = self.makeRandomRect()
                rectang = pygame.Rect(upper,(self.obsDim,self.obsDim))
                if rectang.collidepoint(self.start) or rectang.collidepoint(self.goal):
                    startgoalcol = True
                else:
                    startgoalcol=False
            obs.append(rectang)
        self.obstacles=obs.copy()
        return obs

    def add_node(self,n,x,y):
        self.x.insert(n,x)
        self.y.append(y)

    def remove_node(self,n):
        self.x.pop(n)
        self.y.pop(n)

    def add_edge(self,parent,child):
        self.parent.insert(child,parent)
        self.costs.insert(child, self.cost(child))

    def remove_edge(self,n):
        self.parent.pop(n)
        self.costs.pop(n)

    def number_of_nodes(self):
        return len(self.x)

    def distance(self,n1,n2):
        (x1,y1) = (self.x[n1], self.y[n1])
        (x2,y2) = (self.x[n2], self.y[n2])
        px = (float(x1) - float(x2))**2
        py = (float(y1) - float(y2))**2
        return (px+py)**(0.5)

    def sample_envir(self):
        x=int(random.uniform(0,self.mapw))
        y=int(random.uniform(0,self.maph))
        return x,y

    def nearest(self,n):
        dmin=self.distance(0,n)
        nnear=0
        for i in range(n):
            if self.distance(i,n) < dmin:
                dmin=self.distance(i,n)
                nnear=i
        return nnear

    def isFree(self):
        n = self.number_of_nodes() - 1
        (x,y) = (self.x[n], self.y[n])
        obs=self.obstacles.copy()
        while len(obs) > 0:
            rectang=obs.pop(0)
            if rectang.collidepoint(x,y):
                self.remove_node(n)
                return False
        return True

    def crossObstacle(self,x1,x2,y1,y2):
        obs=self.obstacles.copy()
        while(len(obs)>0):
            rectang=obs.pop(0)
            for i in range(0,101):
                for i in range(0,101):
                    u=i/100
                    x=x1*u + x2*(1-u)
                    y=y1*u + y2*(1-u)
                    if rectang.collidepoint(x,y):
                        return True
        return False

    def connect(self,n1,n2):
        (x1,y1) = (self.x[n1], self.y[n1])
        (x2,y2) = (self.x[n2], self.y[n2])
        if self.crossObstacle(x1,x2,y1,y2):
            self.remove_node(n2)
            return False
        else:
            self.add_edge(n1,n2)
            return True

    def step(self,nnear,nrand,dmax=30):
        d = self.distance(nnear,nrand)
        if d>dmax:
            u=dmax/d
            (xnear,ynear) = (self.x[nnear], self.y[nnear])
            (xrand,yrand) = (self.x[nrand], self.y[nrand])
            (px,py) = (xrand-xnear,yrand-ynear)
            theta=math.atan2(py,px)
            (x,y) = (int(xnear + dmax*math.cos(theta)),
                    int(ynear + dmax*math.sin(theta)))
            self.remove_node(nrand)
            if (abs(x-self.goal[0]) <= dmax) and (abs(y-self.goal[1]) <= dmax):
                self.add_node(nrand,self.goal[0],self.goal[1])
                self.goalstate=nrand
                self.goalFlag=True
                #self.connect(nnear, nrand)
            else:
                self.add_node(nrand,x,y)

    def path_to_goal(self):
        if self.goalFlag:
            self.path=[]
            self.path.append(self.goalstate)
            newpos=self.parent[self.goalstate]
            while (newpos != 0):
                self.path.append(newpos)
                newpos=self.parent[newpos]
            self.path.append(0)
        return self.goalFlag

    def getPathCoords(self):
        pathCoords = []
        for node in self.path:
            x,y=(self.x[node], self.y[node])
            pathCoords.append((x,y))
        return pathCoords

    def expand(self,type):
        n=self.number_of_nodes()
        x,y=self.sample_envir()
        self.add_node(n,x,y)
        if self.isFree():
            xnearest=self.nearest(n)
            self.step(xnearest,n)
            
            if type=='rrt-star':
                if self.goalFlag:
                    self.connect(xnearest,n)
                    return self.x, self.y, self.parent
                
                xnearest,neighbors=self.findNeighbor(xnearest, n)
                if self.connect(xnearest,n):
                    self.rewire(n,xnearest,neighbors)
            elif type=='rrt':
                self.connect(xnearest,n)
        return self.x,self.y,self.parent

    def bias(self,ngoal,type):
        n=self.number_of_nodes()
        self.add_node(n,ngoal[0],ngoal[1])
        nnear=self.nearest(n)
        self.step(nnear,n)
        
        if type=='rrt-star':
            if self.goalFlag:
                self.connect(nnear,n)
                return self.x, self.y, self.parent
            
            nnear,neighbors=self.findNeighbor(nnear, n)
            if self.connect(nnear,n):
                self.rewire(n,nnear,neighbors)
        elif type=='rrt':
            self.connect(nnear, n)
        return self.x,self.y,self.parent

    def cost(self, node):
        n = node
        tot = 0
        while n != 0:
            tot += self.distance(n, self.parent[n])
            n = self.parent[n]
        return tot

    def findNeighbor(self, nnear, node):
        lowestCost = self.cost(nnear) + self.distance(node, nnear)
        bestNode = nnear
        neighbors = []
        for n in range(self.number_of_nodes()):
            if n == node:
                continue
            else:
                if (self.distance(n, node) <= self.radius) and (self.cost(n) + self.distance(n, node) < lowestCost):
                    neighbors.append(n)
                    bestNode = n
                    lowestCost = self.cost(n)
                elif (self.distance(n, node) <= self.radius):
                    neighbors.append(n)
        
        return bestNode, neighbors

    def rewire(self,node,nearest,neighbors):
        for n in neighbors:
            if n == nearest:
                continue
            if self.distance(node, n)+self.cost(node) < self.cost(n):
                (x1,y1) = (self.x[n], self.y[n])
                (x2,y2) = (self.x[node], self.y[node])
                if not self.crossObstacle(x1, x2, y1, y2):
                    self.parent[n] = node
                    self.costs[n] = self.cost(n)


        
    
