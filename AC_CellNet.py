""" This is a a module that controls the construction of relationships among 
the cells. It is modeled as a network because in the future it might make
more sense to conceive of neighbor-relationships as social ties that transcend
space.


Written by Jon Atwell
"""

import networkx
import math
import random


def measure_distance(cell1, cell2):
    """ This function maps distances in a cartesian plane of size 10X10 to a
    torus of the same size and then measures the Euclidean distance on
    the torus.
    """

    x1, y1 = cell1.location
    x2, y2 = cell2.location
    x_dist = abs(x1-x2)
    y_dist = abs(y1-y2)
    
    if x_dist > 5:
        x_dist = 10-x_dist
    if y_dist > 5:
        y_dist = 10-y_dist
    
    return math.sqrt(x_dist**2 + y_dist**2)


class CellNet:
    """ The cell net object is a NETWORKX network in which the individual
    cells are embedded. It is currently used to establish relationships 
    between cells. Currently, it overlays geographic space in a grid.
    """

    def __init__(self, cells, RNG, type="Moore"):
    
        self.net = networkx.Graph()

        # networkX function adds our cells (of the Cell class) to the network.
        self.net.add_nodes_from(cells)       
        self.cells = cells

        # we control the random number generator to be able to reproduce runs.
        self.RNG = RNG 

        # we keep track of the number of steps taken with this
        self.master_count = 0
        self.depth = 0
        self.last_added_rule = 0
        self.rules = []
        self.debug = None
        
        # A kludgy way to allow the cells to call cellNet functions.
        for cl in cells:
            cl.add_cellNet(self)

        self.distribute_onto_grid(cells, type)


    def distribute_onto_grid(self, cells,type):
        """ A method to array the cell onto a grid so that we can have
        a spatially constrained interaction topology.
        """

        # setting up the typology of the space the cells will be in
        if type == "Moore":
            size = 10
            count=0

            # moving them into a '10X10 grid'
            for i in range(1,size+1):
                for j in range(1, size+1):
                    cells[count].set_location(i,j)
                    count +=1

            # distances to get Moore neighbors of everyone in the network.
            for i in range(len(cells)):
                for j in range(len(cells)):
                    if j > i:
                        one = cells[i]
                        two = cells[j]
                        # special function to wrap edges of the torus around.
                        dist = measure_distance(one, two)
                        if dist < 1.5:
                            one.add_neighbor(two)
                            two.add_neighbor(one)
                            self.net.add_edge(one,two)


    def get_random_cell(self, who=None):
        """ A function to select a cell, weighted by the number
        of rules it has. The who argument is used to prevent self
        pass backs in the non-spatial variant."""

        candidates = []
        cnts = []
        for i in self.cells:
            if i != who:
                cnts.append(i.count_rules)
                for j in range(i.count_rules):
                        candidates.append(i)

        return self.RNG.sample(candidates, 1)[0]


    def activate_random_rule(self, debug=False):
        """A function to select a random rule from within a cell. It first
        randomly selects a cell, weighted by rule counts. Then it selects
        a rule from that cell, weighted by the rules' frequencies."""

        candidate = self.get_random_cell()
        candidate.set_active_rule(candidate.get_random_rule())
        candidate.chain_step(debug)


    def activate_random_cell(self, debug=False):
        """A function to select a random rule from within a cell. It first
        randomly selects a cell, weighted by rule counts. Then it selects
        a rule from that cell, weighted by the rules' frequencies."""

        candidate = self.get_random_cell()
        has = candidate.has_Product()
        if has != None:
            candidate.set_active_rule(candidate.get_random_rule_of_type(has))
            candidate.chain_step(debug)
        else:
            candidate.set_active_rule(candidate.get_random_rule())
            candidate.chain_step(debug)


    def remove_random_rule(self):
        """This method is the main way in which selection pressure is
        implemented. If a rule is reproduced, this method removes one
        uniform-at-random."""

        a = self.get_random_cell()
        a.remove_ProductRule(a.get_random_rule())
        
