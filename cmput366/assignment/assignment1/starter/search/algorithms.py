import heapq
import math


class State:
    """
    Class to represent a state on grid-based pathfinding problems. The class contains two static variables:
    map_width and map_height containing the width and height of the map. Although these variables are properties
    of the map and not of the state, they are used to compute the hash value of the state, which is used
    in the CLOSED list. 

    Each state has the values of x, y, g, h, and cost. The cost is used as the criterion for sorting the nodes
    in the OPEN list for both Dijkstra's algorithm and A*. For Dijkstra the cost should be the g-value, while
    for A* the cost should be the f-value of the node. 
    """
    map_width = 0
    map_height = 0
    
    def __init__(self, x, y):
        """
        Constructor - requires the values of x and y of the state. All the other variables are
        initialized with the value of 0.
        """
        self._x = x
        self._y = y
        self._g = 0
        self._h = 0
        self._cost = 0
        
    def __repr__(self):
        """
        This method is invoked when we call a print instruction with a state. It will print [x, y],
        where x and y are the coordinates of the state on the map. 
        """
        state_str = "[" + str(self._x) + ", " + str(self._y) + "]"
        return state_str
    
    def __lt__(self, other):
        """
        Less-than operator; used to sort the nodes in the OPEN list
        """
        return self._cost < other._cost
    
    def state_hash(self):
        """
        Given a state (x, y), this method returns the value of x * map_width + y. This is a perfect 
        hash function for the problem (i.e., no two states will have the same hash value). This function
        is used to implement the CLOSED list of the algorithms. 
        """
        return self._y * State.map_width + self._x
    
    def __eq__(self, other):
        """
        Method that is invoked if we use the operator == for states. It returns True if self and other
        represent the same state; it returns False otherwise. 
        """
        return self._x == other._x and self._y == other._y

    def get_x(self):
        """
        Returns the x coordinate of the state
        """
        return self._x
    
    def get_y(self):
        """
        Returns the y coordinate of the state
        """
        return self._y
    
    def get_g(self):
        """
        Returns the g-value of the state
        """
        return self._g
        
    def get_h(self):
        """
        Returns the h-value of the state
        """
        return self._h
    
    def get_cost(self):
        """
        Returns the cost of the state (g for Dijkstra's and f for A*)
        """
        return self._cost
    
    def set_g(self, cost):
        """
        Sets the g-value of the state
        """
        self._g = cost
    
    def set_h(self, h):
        """
        Sets the h-value of the state
        """
        self._h = h
    
    def set_cost(self, cost):
        """
        Sets the cost of a state (g for Dijkstra's and f for A*)
        """
        self._cost = cost


class Search:
    """
    Interface for a search algorithm. It contains an OPEN list and a CLOSED list.

    The OPEN list is implemented with a heap, which can be done with the library heapq
    (https://docs.python.org/3/library/heapq.html).    
    
    The CLOSED list is implemented as a dictionary where the state hash value is used as key.
    """
    def __init__(self, gridded_map):
        self.map = gridded_map
        self.OPEN = []
        self.CLOSED = {}
    
    def search(self, start, goal):
        """
        Search method that needs to be implemented (either Dijkstra or A*).
        """
        raise NotImplementedError()


class Dijkstra(Search):
            
    def search(self, start, goal):
        """
        Disjkstra's Algorithm: receives a start state and a goal state as input. It returns the
        cost of a path between start and goal and the number of nodes expanded.

        If a solution isn't found, it returns -1 for the cost.
        """

        # insert initial state into OPEN and CLOSED
        heapq.heappush(self.OPEN, start)
        self.CLOSED[start.state_hash()] = start
        self.node_expanded = 0

        # keep poping
        while len(self.OPEN) != 0:
            node = heapq.heappop(self.OPEN)
            self.node_expanded += 1
            # if reaches the goal
            if node == goal:
                self.OPEN = []
                self.CLOSED = {}
                return node.get_cost(), self.node_expanded

            for child in self.map.successors(node):
                # if child is not expanded
                if child.state_hash() not in self.CLOSED:
                    child.set_cost(child.get_g())
                    heapq.heappush(self.OPEN, child)
                    self.CLOSED[child.state_hash()] = child
                # if child is expanded but there is a cheaper cost
                if child.state_hash() in self.CLOSED and (child.get_g() < self.CLOSED[child.state_hash()].get_cost()):
                    self.CLOSED[child.state_hash()].set_g(child.get_g())
                    self.CLOSED[child.state_hash()].set_cost(child.get_g())
                    heapq.heapify(self.OPEN)

        self.OPEN = []
        self.CLOSED = {}

        return -1, 0


class AStar(Search):
    
    def h_value(self, state, goal):
        x = abs(state.get_x() - goal.get_x())
        y = abs(state.get_y() - goal.get_y())
        return max(x, y) + 0.5 * min(x, y)
            
    def search(self, start, goal):
        """
        A* Algorithm: receives a start state and a goal state as input. It returns the
        cost of a path between start and goal and the number of nodes expanded.

        If a solution isn't found, it returns -1 for the cost.
        """

        # insert initial state into OPEN and CLOSED
        start.set_h(self.h_value(start, goal))
        start.set_cost(start.get_h())
        heapq.heappush(self.OPEN, start)
        self.CLOSED[start.state_hash()] = start
        self.node_expanded = 0

        # keep poping
        while len(self.OPEN) != 0:
            node = heapq.heappop(self.OPEN)
            self.node_expanded += 1
            # if reaches the goal
            if node == goal:
                self.OPEN = []
                self.CLOSED = {}
                return node.get_cost(), self.node_expanded

            for child in self.map.successors(node):
                child.set_h(self.h_value(child, goal))
                child.set_cost(child.get_g() + child.get_h())
                # if child is not expanded
                if child.state_hash() not in self.CLOSED:
                    heapq.heappush(self.OPEN, child)
                    self.CLOSED[child.state_hash()] = child
                # if child is expanded but there is a cheaper cost
                if child.state_hash() in self.CLOSED and (child.get_g() + child.get_h() < self.CLOSED[child.state_hash()].get_cost()):
                    self.CLOSED[child.state_hash()].set_g(child.get_g())
                    self.CLOSED[child.state_hash()].set_h(child.get_h())
                    self.CLOSED[child.state_hash()].set_cost(child.get_g() + child.get_h())
                    heapq.heapify(self.OPEN)

        self.OPEN = []
        self.CLOSED = {}

        return -1, 0
    