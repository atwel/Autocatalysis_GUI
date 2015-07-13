""" This module contains the classes Product and Urn. The former is the core
object of exchange, the latter is a collection of individual units dispersed
according to the rules of the Urn. See EOM (Padgett and Powell 2012)
p.76 for definitions of Urn rules.


Written by Jon Atwell
"""


class Product:
    """ This class is for the fundamental extra-cellular unit, some sort of
    distinguishable goods that are passed around by the cells and transformed
    along the way.
    """
    
    
    def __init__(self, owning_Urn, type, energy):
        self.owner = owning_Urn 
        self.energy = energy
        try:
            self.type = int(type)
        except:
            raise ValueError("%d is an invalid product type" %type)
        
    def __str__(self):
        return self.type

        
    def get_type(self):
        """ Simple reporter for the product's current type."""
        return self.type
    
    
    def apply_ProductRule(self, product_rule, cost):
        """ A method for transforming the Product's type based on the skill
        embodied in the ProductRule argument 'product_rule'.
        """
        try:
            if self.type != product_rule.get_input():
                print "This ProductRule can't transform this Product."
            else:
                self.type = product_rule.get_output()
                self.use_energy(cost)
        except:
            a = ("%s is not a ProductRule and therefore can't transform"+
                " a Product.") %type(product_rule)
            raise TypeError(a)

        
    def replenish_energy(self):
        self.energy = self.owner.initial_energy


    def use_energy(self, amount):
        self.energy -= amount


    def get_energy(self):
        return self.energy


    def __str__(self):
        a = "Product is type %d and owned by Urn %d" %(self.type, self.owner)
        return a
    

class Urn:
    """ An Urn is a collection of products that has 8 different possible
    search methods for determining whether the the input product is available
    when requested. Definitions appear in EOM, p.76. The constructor creates
    the appropriate collection of products but the request_product() method is
    what really implements the search methods based on the Urn type
    (fixed-rich, fixed-poor, endo-rich and endo-poor) [where 'endo' means
    endogenous] and the calling Cell's search intelligence 
    (selective or random).
    """
    
    def __init__(self, urn_type, count_product_types, RNG, energy, 
        count_products=200):
        """ urn_type = rule structure for determining product availability
            count_product_types = number of possible products
            count_products = how many actual units in the collection
        """
        self.initial_energy = energy
        self.RNG = RNG 
        self.maxtype = count_product_types
        self.count_products = count_products
        self.collection = {}
        
        if  "fixed-rich" in urn_type:
            self.type = 1
            self.probability = (self.count_products/
                float(self.maxtype))/float(self.count_products)
            
        elif "fixed-poor" in urn_type :
            self.type = 2
            
        elif "endo-rich" in urn_type:
            self.type = 3
            for i in range(self.maxtype):
                self.collection[i+1] = ([Product(self, (i+1), 
                    self.initial_energy) for j in range(int(count_products/float(self.maxtype)))])
            
        elif  "endo-poor" in urn_type:
            self.type = 4
            self.collection = ({1:[Product(self,1, self.initial_energy) 
                for i in range(count_products)]})
            for i in range(self.maxtype-1):
                self.collection[i+2] = []

        else:
            raise ValueError("%s is an invalid Urn type" %type)
            
    
    def request_product(self, desired_output, selective=False):
        """ The method for cells to request the specific product the activate
        rule calls for. It returns a Product instance of type DESIRED_OUTPUT
        if it is available (i.e. selective search)."""
        
        if not(0 < desired_output <= self.maxtype):
            raise ValueError("%s is an invalid Product type" %desired_output)
         
        # Selective search always get exactly what the active rule calls for
        if selective:
            
            if self.type == 1: # type = Rich
                return Product(self, desired_output, self.initial_energy)
                    
            # if the active rule calls for a 1, hand one over
            elif self.type == 2: # type = Poor
                if desired_output == 1:
                    return Product(self, 1, self.initial_energy)
                else:
                    return None
                     
            # This urn started with all products. 
            elif self.type == 3: # type = Endo-Rich
                    try:
                        return self.collection[desired_output].pop()
                    except:
                        return None
                        
            # Return what is asked for if it is available.      
            elif self.type == 4: #Type = Endo-Poor
                try:
                    return self.collection[desired_output].pop()
                except:
                    return None
        
        # random search returns the desired product with uniform probability
        elif selective == False:
            
            if self.type == 1: #type=rich
                if self.RNG.random() <= self.probability:
                    return Product(self, desired_output, self.initial_energy)
                else:
                    return None
            
                    
            # Return a 1-product if it is asked for (there is only 
            # 1-product so random search is still intelligent search.        
            elif self.type == 2: #type=poor
                if desired_output == 1:
                    return Product(self, 1, self.initial_energy)
                else:
                    return None
            
                    
            # If the urn isn't filled, return the desired product with uniform
            # probability. If it is filled, return desired product with a
            # probability proportional to the current distribution of product
            # types.

            elif self.type == 3: #type=Endo-rich
                if desired_output in self.collection.keys():
                    count = len(self.collection[desired_output])
                    try:
                        if self.RNG.randint(1, self.count_products) <= count:
                            return self.collection[desired_output].pop()
                    except:
                        return None
                else:
                    return None
            
                        
            # Returns the desired product with probability proportional to
            # the current distribution of product types. The initial 
            # distribution is all ones.
            elif self.type == 4: #type=Endo-poor
                poss = []
                for i in self.collection.keys():
                    for j in range(len(self.collection[i])):
                        poss.append(i)
                try:
                        if self.RNG.sample(poss,1)[0] == desired_output:
                            return self.collection[desired_output].pop()
                except:
                        return None
            else:
                raise ValueError("%s is an invalid Urn type" %self.type)
                    
        else:
            raise ValueError("%s is an invalid intelligence type" %selective)

    
    def return_product(self, product):
        """ A method for placing transformed Products back into the Urn.
        This only really matters when the Urn is of the endogenous type
        because we need to change the distribution of available Products.
        If the Urn is of type fix, we just 'drop the ball'.
        """
        if self.type == 3 or self.type == 4:
            product.replenish_energy()
            self.collection[product.get_type()].append(product)
        
        else:
            try:
                if  product.get_type() <0 or product.get_type() >self.maxtype:
                    raise ValueError("Type is invalid for this chemistry.")
                # if the if-statement is false, ball is "dropped" by now. 
            except:
                raise TypeError("Argument is not a Product instance")
        
        
    def __str__(self):
        return str(self.collection)
    

    