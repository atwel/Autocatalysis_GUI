


""" This module contains the constructor for Product rules, the skills that
cells possess for converting one Product type into another. It also contains
the constructor for a NetRule, a class of objects used to help keep track of
autocatalytic cycles. Finally, it has an algorithm for constructing the rule
sets that define the relevant "chemistries."

Written by Jon Atwell
"""

class ProductRule:
    """ The rule that defines a 'skill' a cell might possess. It can be used 
    to transform the type of a Product instance from type INPUT to 
    type OUTPUT.
    """
    
    def __init__(self, input, output):
        self.input = input
        self.output = output

        
    def get_input(self):
        return self.input
    
    def get_output(self):
        return self.output
    
    def get_name(self):
        """ Used as the key for the related ProductNetRules."""
        return "-".join([str(self.input), str(self.output)])
        
    def __str__(self):
        return "Rule has input %d and output %d" %(self.input, self.output)
        
    
        
class ProductNetRule:
    """ A class of object closely related to ProductRule but used to count 
    autocatalytic cycles. A cell will create a ProductNetRule for every type
    of ProductRule (i.e. unique input and output combination) they have.
    The ProductNetRule keeps track of how many actual ProductRules are of
    that type."""

    def __init__(self, input, output, count):
        self.input = input
        self.output = output
        self.count = count
        self.owner = None
        self.location = None #for visualization
        
    def set_location(self, location):
        self.location = location
        
    def set_owner(self,cell):
        self.owner = cell
        
    def get_owner(self):
        return self.owner
        
    def add_to_count(self):
        self.count += 1
        
    def subtract_from_count(self):
        self.count -= 1

    def get_input(self):
        return self.input
        
    def get_output(self):
        return self.output
        
    def get_count(self):
        return self.count
    
    def __str__(self):
        return "%d-%d" %(self.input, self.output)
        
        
        
def create_RuleSet(type="ALL", maxProductType=5, count=20, RNG=None):
    """ A function for creating a collection of ProductRules that define a
    "chemistry." A chemistry is defined by the number of possible products
    (maxProductType) and whether there is a unique progression of
    transformation required (1->2, 2->3,...n->1). The TYPE 'SOLOH'
    is for the unique progression variant. The function creates as uniform of
    a distribution as possible for the specified rule types.
    """

    myset = []
    
    if type == "ALL":
        print "making ALL chem"
        combos = maxProductType**2 - maxProductType
        count_each = 200/combos
        extras = 200-(combos*count_each)
        exs = []
        cnt = 0
        for i in range(maxProductType):
            for j in range(maxProductType):
                if i < j:
                    exs.append(ProductRule(i+1,j+1))
                    for k in range(count_each):
                        myset.append(ProductRule(i+1, j+1))
        for j in range(maxProductType):
            for i in range(maxProductType):
                if i > j:
                    exs.append(ProductRule(i+1,j+1))
                    for k in range(count_each):
                        myset.append(ProductRule(i+1, j+1))
    
        #randomly adding instances to get to 200.
        myset += RNG.sample(exs, extras) 
        
        return myset
        
    elif type == "SOLOH":
    
        #This count should be set so that there are 200 rules in total
        
        count_each = 200/maxProductType
        extras = 200-(maxProductType*count_each)
        exs = []
        print "making SOLOH chemistry"
        count = 0
        for i in range(1,maxProductType):
            for j in range(count_each):
                myset.append(ProductRule(i,i+1))
            exs.append(ProductRule(i,i+1))
            
        for i in range(count_each):
            myset.append(ProductRule(maxProductType,1))
        exs.append(ProductRule(maxProductType,1))

         #randomly adding instances to get to 200.
        myset = myset + RNG.sample(exs, extras)
        
        
        return myset
        
    else:
        raise ValueError("%s is not a valid RuleSet type" %type)



        