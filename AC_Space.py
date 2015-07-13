""" This is a module that constructs a 2-dimensional space the cells can move
around in. Currently, it only supports Brownian motion with a periodic
boundary condition.


Written by Jon Atwell
"""

import random
import numpy


def within_radius(radius, point):

    # need to clean with the taurus map
    the_list = []
    for x in range(int(point[0] - numpy.ceil(radius)),int(point[0] + numpy.ceil(radius) + 1)):
        for y in range(int(point[1]- numpy.ceil(radius)), int(point[1] + numpy.ceil(radius) + 1)):
            if ((point[0]-x)**2 + (point[1]-y)**2)**.5 <= radius:
                the_list.append((x,y))
    return the_list



def create_overlap_lists(radius):
        vals = {}
        for i in range(-1,2):
            for j in range(-1,2):
                original = within_radius(radius, (0,0))
                new = within_radius(radius, (i,j))
                diffs = []
                for nw in new:
                    if nw not in original:
                        diffs.append(nw)
                vals[(i,j)] = diffs

        return vals



class Space:
    """ The  grid the cells move around on.
    """

    def __init__(self, cells, cell_radius, RNG, vision_radius, energy_costs, dimensions=(10,10), motion="Brownian"):
    
        self.cells = cells
        # we control the random number generator to be able to reproduce runs.
        self.RNG = RNG
        self.cell_radius = cell_radius
        self.radius = vision_radius
        # we keep track of the number of steps taken with this
        self.master_count = 0
        self.max_x = dimensions[0]
        self.max_y = dimensions[1]
        self.depth = 0
        self.last_added_rule = 0
        self.rules = []
        self.energy_costs = energy_costs
        self.debug = None
        self.neighbor_grid = numpy.empty(shape = (self.max_y, self.max_x), dtype = list)
        self.change_vals = None
        self.overlap_lists = create_overlap_lists(self.radius)
        print "made overlap_lists"

        # A kludgy way to allow the cells to call Space functions.
        for cl in self.cells:
            cl.add_Space(self)

        self.distribute_into_space(cells)
        print "distribute_into_space"


    def taurus_map(self, (new_x, new_y)):
        """ A method the establishes the periodic boundary condition."""

        if self.max_x < new_x:    
            new_x = new_x - self.max_x
        elif new_x < 1:
            new_x = self.max_x + new_x

        if self.max_y < new_y:
            new_y = new_y - self.max_y
        elif new_y < 1:
            new_y = self.max_y + new_y

        return new_x, new_y


    def map_list(self, loc, the_list):

        new_list = []

        for spot in the_list:
            x = spot[0] + loc[0]
            y = spot[1] + loc[1]
            new_list.append(self.taurus_map((x, y)))

        return new_list


    def distribute_into_space(self, cells):
        """ A method to array the cells onto the space. There is 
        no problem with multiple cells occupying the same 
        spot, so they are distributed uniform-at-random.
        """

        for cl in self.cells:
            someone_here = True
            while someone_here:
                x = self.RNG.randint(1, self.max_x)
                y = self.RNG.randint(1, self.max_y)
                someone_here = self.is_some_one_here(x,y, self.cell_radius)

            cl.set_location(x,y)
            try:
                self.neighbor_grid[y-1][x-1].append(cl)
            except:
                self.neighbor_grid[y-1][x-1] = [cl]

        #Setting up an initial list of neighbors    
        for cl in self.cells:      
            area = within_radius(self.radius, cl.get_location())
            for point in area:
                x, y = self.taurus_map(point)
                try:
                    cl.neighbors.extend(self.neighbor_grid[y-1][x-1])
                except:
                    pass

        #self.print_grid()
    def is_some_one_here(self, x,y, cell_radius):
        the_list = []
        area = within_radius(cell_radius, (x, y))
        for point in area:
            x, y = self.taurus_map(point)
            try:
                the_list.extend(self.neighbor_grid[y-1][x-1])
            except:
                pass

        if the_list == []:
            return False
        return True


    def print_grid(self):
        y,x = self.neighbor_grid.shape
        for i in range(y):
            row = ""
            for j in range(x):
                cells = self.neighbor_grid[i][j]
                
                if cells== None:
                    row += "|______|"
                else:
                    if cells== []:
                        row += "|______|"
                    
                    cnt = len(cells)
                    if cnt == 1:
                        row += "|__" + str(cells[0].id)+"___|"
                    elif cnt == 2:
                        row += "|_"
                        for k in cells:
                            row += str(k.id) + "-"
                        row += "_|"
                    elif cnt == 3:
                        row += "|"
                        for k in cells:
                            row += str(k.id) + "-"
                        row += "|"
            print row

    
    def move_cell(self, cell):

        current = cell.get_location()

        # The boring essence of Brownian motion
        someone_here = True
        tries = 4
        while someone_here and tries >= 1:
            x_move =  self.RNG.randint(-1,1)
            y_move =  self.RNG.randint(-1,1)
            new_x, new_y = self.taurus_map((current[0] + x_move,
                current[1] +  y_move))
            someone_here = False #self.is_some_one_here(self.cell_radius, new_x, new_y)
            tries -=1

        cell.set_location(new_x, new_y)

        self.update_grid(current, cell, x_move, y_move)


    def update_grid(self, old_spot, cell, x_move, y_move):

        new = cell.get_location()
        self.neighbor_grid[old_spot[1]-1][old_spot[0]-1].remove(cell)
        try:
            self.neighbor_grid[new[1]-1][new[0]-1].append(cell)
        except:
            self.neighbor_grid[new[1]-1][new[0]-1] = [cell]

        
        old_spots= self.map_list(cell.get_location(), 
            self.overlap_lists[(-1*x_move, -1*y_move)])
        #print old_spots

        to_remove = []
        for ngh in cell.neighbors:
            if ngh.get_location() in old_spots:
                ngh.neighbors.remove(cell)
                #print "removed ", ngh.id, " at ", ngh.get_location()
                to_remove.append(ngh)

        for ngh in to_remove:
                cell.neighbors.remove(ngh)
        
        new_spots = self.map_list(old_spot, 
            self.overlap_lists[(x_move,y_move)])
        #print new_spots
        
        for loc in new_spots:
            try:
                news = self.neighbor_grid[loc[1]-1][loc[0]-1]
                for ngh in news:
                    if ngh not in cell.neighbors:
                        cell.neighbors.append(ngh)
                        ngh.neighbors.append(cell)
                        #print "added ", ngh.id, ngh.get_location()
            except:
                pass
                #print "error:", self.neighbor_grid[loc[1]-1][loc[0]-1]


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
        self.move_cell(candidate)
        candidate.chain_step(debug)


    def activate_random_cell(self, debug=False):
        """A function to select a random rule from within a cell. It first
        randomly selects a cell, weighted by rule counts. Then it selects
        a rule from that cell, weighted by the rules' frequencies."""

        candidate = self.get_random_cell()
        self.move_cell(candidate)
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
        
