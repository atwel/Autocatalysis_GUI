""" This module creates a NetworkX network only for keeping track of
autocatalytic networks. It uses instances of the ProductNetRule class for 
the nodes. Those objects are owned by cells.


Written by Jon Atwell
"""

import networkx
import AC_ProductRules


class ProductRuleNet:
    """ A NetworkX DiGraph object. The construction of the network is done
    by Cell instances who create a ProductNetRule for each type of rule they 
    have (not each rule, of which we expect duplicates).
    """
    
    def __init__(self):
        self.net = networkx.DiGraph()
        self.cycle_counts = {}
        self.has_cycles = True
        self.pos = None #filled in later
           
    def add_ProductNetRule(self, aProductNetRule):
        """ This turn the ProductNetRule to a node in the network.
        """
        
        if isinstance(aProductNetRule, AC_ProductRules.ProductNetRule):
            """ Yes, I know you aren't supposed to type-check in Python,
            but because a NetworkX network will take any hashable as a node,
            it seemed prudent."""
            self.net.add_node(aProductNetRule)

        else:
            a = ("%s is not a ProductNetRule and therefore can't"+
                "be added to the network") %type(aProductRule)
            raise TypeError()
            
    
    def remove_ProductNetRule(self, theProductNetRule,time_step):
        """ This removes the node/ProductNetRule from the network. NetworkX
        automatically removes adjacent edges in the network.
        """
        self.net.remove_node(theProductNetRule)
            
    
    def add_edge(self, rule1, rule2):
        """ This connects two ProductNetRules via a network edge so that their
        compatibility is included in the counting of autocatalytic cycles.
        """
    
        try:
            if rule1.get_output() == rule2.get_input():
                if self.net.has_edge(rule1, rule2) == False:
                    self.net.add_edge(rule1, rule2)
                else:
                    pass

            elif rule2.get_output() == rule1.get_input():
                if self.net.has_edge(rule2, rule1) == False:
                    self.net.add_edge(rule2, rule1)
                else:
                    pass

            else:
                pass

        except:
            a="An argument for the add_edge() method must be a ProductRule."
            raise TypeError(a)


    def return_cycles(self):
        """ A direct route to the NetworkX simple cycles finding function.
        This method is only ever used in debugging because the method
        update_cycle_counts() below packages the information in a more
        useful way
        """

        return networkx.recursive_simple_cycles(self.net)
        

    def update_cycle_counts(self, time_step):
        """ This method makes use of the recursive_simple_cycles() function of
        NetworkX to offload all the work of finding cycles in the graph. Yay!
        The lengths of the cycles are added to the ProductRuleNet's field
        named cycle_counts. NOTE: the list the algorithm returns is of list
        of nodes in the cycle where the last one is dropped because it is the
        same as the first. Thus a (sub) list of length 2 is not a self-loop, 
        but a path from one node to another and back and cycles must be
        of length two or greater. 
        """
        
        cycles = networkx.recursive_simple_cycles(self.net)

        self.cycle_counts = {}
        for i in cycles:
            length = len(i)
            try:
                self.cycle_counts[length] += 1
            except:
                self.cycle_counts[length] = 1
        
        # If there are no cycles, this run is dead and we need to send word
        if len(cycles) == 0:
            self.has_cycles = False
            return False
        else:
            return True
    
    
    def get_cycle_complexity(self):
        """ This function looks at the cycles that are longer than two.
        """

        cycles = networkx.recursive_simple_cycles(self.net)
        complexities = {} # keys are lengths, entries are # of distinct rules.
        rule_owners = {}
        for cycle in cycles:
            if len(cycle) > 2:
                length = len(cycle)
                types = {}
                owners = {}
                for rule in cycle:
                    type = str(rule.get_input()) + "-" +str(rule.get_output())
                    owner = rule.get_owner()
                    try:
                        types[type] += 1
                    except:
                        types[type] = 1
                    try:
                        owners[owner] +=1
                    except:
                        owners[owner] = 1
                
                count_owners = len(owners.keys())
                count_types = len(types.keys())
                
                try:
                    complexities[length].append((count_types,count_owners))
                except:
                    complexities[length] = [(count_types,count_owners)]
                    
        return complexities
        
    
    def get_plus3rule_complexity(self):
        """ Returns whether there is a cycle of length of at least 3
        that include at least 3 distinct rules.
        """ 
    
        for length_type in self.get_cycle_complexity().values():
            for instance in length_type:
                if instance[0] >= 3:
                    return True
        return False
                
    
    def get_plus3cell_complexity(self):
        """ Returns whether there is a cycle of length of at least 3
        that include at least 3 cells.
        """
    
        for length_type in self.get_cycle_complexity().values():
            for instance in length_type:
                if instance[1] >= 3:
                    return True
        return False
                
    
    
    def __str__(self):
        """Custom print method reporting the number of nodes,
        edges, and autocatalytic cycles.
        """
        counts = ",".join([str(i) for i in self.cycle_counts.values()])
        vals = (self.net.number_of_nodes(), self.net.number_of_edges(),counts)
        
        return "Net has %d nodes, %d edges and cycles of lengths %s" %vals


        
        