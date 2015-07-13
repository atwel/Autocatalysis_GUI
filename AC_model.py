""" This is the model initializer and controller. Parameters are specified
herein and the progression through the different combinations of 
parameters happens here as well. The final data from the run are gathered
and printed to file.


Written by Jon Atwell
"""


import AC_Products
import AC_ProductRules
import AC_ProductRuleNet
import AC_Cells 
import AC_Space
import AC_grapher
import random
import networkx as nx
import sys
import pyglet as pyg
from pyglet import window, image, graphics, text
from pyglet.text import caret, layout




class control_Sprite(pyg.sprite.Sprite):

    def __init__(self, cell_image, x, y, scale, name,batch):
        self.name = name
        pyg.sprite.Sprite.__init__(self, cell_image, batch=batch)
        self.scale = scale
        self.x = x
        self.y = y
        control_window.push_handlers(self.on_mouse_press)

    def on_mouse_press(self, x, y, button, modifiers):
        global action_scheduled
        global action_rate
        global product_bars_data
        anchor = self.position

        # now we'll get the visual center
        center = (anchor[0] + self.width/2., anchor[1] +self.height/2.)

        # figuring out if the click was within the visual representation 
        # of the cell
        dis = ((x-center[0])**2 + (y-center[1])**2)**.5
        rad = self.width/2.

        if dis <= rad:
            if self.name == "pause":
                pyg.clock.unschedule(cell_action)
                pyg.clock.unschedule(update_product_count)
                action_scheduled = False
            elif self.name == "play": 
                if not action_scheduled:
                    pyg.clock.schedule_interval(cell_action, action_rate)
                    pyg.clock.schedule_interval(update_product_count, 1, product_bars_data, 255)
                    action_scheduled = True
            elif self.name == "stop":
                pyg.app.exit()


class cell_Sprite(pyg.sprite.Sprite):

    def __init__(self, cell_image, batch, name):
        self.cell = None
        self.name = name
        pyg.sprite.Sprite.__init__(self, cell_image, batch=batch)
        main_window.push_handlers(self.on_mouse_press)

    def add_cell(self, cell):
        self.cell = cell

    def on_mouse_press(self, x, y, button, modifiers):
        """ This allows us to click on the cell and see its contents in a 
        side window. Every cell goes through this when the mouse is 
        clicked so we have to match the cursor to a single cell. We do
        this with a simple distance check."""
        
        # this is the cell's true position in the window, which is not 
        # the visual center. 
        anchor = self.position

        # now we'll get the visual center
        center = (anchor[0] + self.width/2., anchor[1] +self.height/2.)

        # figuring out if the click was within the visual representation 
        # of the cell
        dis = ((x-center[0])**2 + (y-center[1])**2)**.5
        rad = self.width/2.

        if dis <= rad:
            # We now have the one cell that was clicked and we add the label
            lbl = pyg.text.Label(str(self.name), x=center[0]-6, y=center[1]-6, color=(0,0,0,150))
            cell_labels_list[0] = lbl

            # We also schedule to remove the label in 1 seconds.
            pyg.clock.schedule_once(remove_label, 2, lbl)

            
            rule_str = []
            total_rules = 0
            for input_key in self.cell.product_rules.keys():
                for output_key in self.cell.product_rules[input_key].keys():
                    rls = len(self.cell.product_rules[input_key][output_key])
                    total_rules += rls
                    rule_str.append(str(input_key) +"->" + str(output_key)+ ": " + str(rls))

            data_labels_list[0] = pyg.text.Label("Cell: " + str(self.name) + "  # rules: " +str(total_rules), x=5, y=75,color=(0,0,0,150))

            dataA = []
            dataB = []
            cnt = 0
            for index, string in enumerate(rule_str):
                if cnt < 30:
                    cnt += len(string)
                    dataA.append(string)
                else:
                    dataB.append(string)
            
            try:
                rule_strA = "  ".join(dataA)
            except:
                rule_strA = " "
            try:
                rule_strB = "  ".join(dataB)
            except :
                rule_strB = " "

            data_labels_list[1] = pyg.text.Label(rule_strA, x=5, y=55,color=(0,0,0,150))
            data_labels_list[2] = pyg.text.Label(rule_strB, x=5, y=35,color=(0,0,0,150))
            hld = ""
            for i in self.cell.products.keys():
                cnt = len(self.cell.products[i])
                if cnt != 0:
                    hld += (str(i) + ": " + str(cnt) + "  ")

            data_labels_list[3] = pyg.text.Label("Storage - "+ hld, x=5, y=15,color=(0,0,0,150))
            
 
         

def get_step_count(PRODUCT_TYPES):
    """A utility function to determine how long to run the model.
    """

    STEPS = 270000
    
    if PRODUCT_TYPES == 3:
        STEPS = 410000
    elif PRODUCT_TYPES == 4:
        STEPS = 580000
    elif PRODUCT_TYPES == 5:
        STEPS = 770000
    elif PRODUCT_TYPES == 6:
        STEPS = 980000
    elif PRODUCT_TYPES == 7:
        STEPS = 1210000
    elif PRODUCT_TYPES == 8:
        STEPS = 1460000
    elif PRODUCT_TYPES == 9:
        STEPS = 1720000
                         
    return STEPS
    
def get_parameters():
    print "Please input the run parameters."
    captured = False
    while not captured:
        t = raw_input("\n\nHow many Product Types are there? [Integer between 2 and 9] ")
        try:
            if 2<=int(t)<=9:
                PRODUCT_TYPES = int(t)
                captured = True
            else:
                print "Sorry, invalid input. Please answer again."
        except:
            print "Sorry, invalid input. Please answer again."
   
    captured = False
    while not captured:
        t = raw_input("\n\nWhat is the environment type? [fixed-rich, fixed-poor, endo-rich, endo-poor]  ")
        try:
            if t in  ["fixed-rich", "fixed-poor", "endo-rich", "endo-poor"]:
                env = t + "-"
                captured = True
            else:
                print "Sorry, invalid input. Please answer again."
        except:
            print "Sorry, invalid input. Please answer again."

    captured = False
    while not captured:
        t = raw_input("\n\nWhat is the learning/reproduction type? [target, source]   ")
        try:
            if t in  ["target", "source"]:
                learn = t
                captured = True
            else:
                print "Sorry, invalid input. Please answer again."
        except:
            print "Sorry, invalid input. Please answer again."
                    
    captured = False
    while not captured:
        t = raw_input("\n\nWhat fraction of the run should be without visuals? [0,1]   ")
        try:
            if 0 <=float(t) <=1:
                non_viz_steps = int(float(t)*get_step_count(PRODUCT_TYPES))
                captured = True
            else:
                print "Sorry, invalid input. Please answer again."
        except:
            print "Sorry, invalid input. Please answer again."

    return [PRODUCT_TYPES, env, learn, non_viz_steps]

def print_data(name, myspace, myRuleNet, cells):

    try:
        output_file = open(name+".csv", "a+")
    except:
        output_file = open(name+".csv", "w+")

    if (myspace.last_added_rule + STEPS*.1 > myspace.master_count):  

    #Creating a network object for compatible rules
        myRuleNet = AC_ProductRuleNet.ProductRuleNet()

        for cell in cells:
            for inpt in cell.product_rules.keys():
                for otpt in cell.product_rules[inpt].keys():
                    cell.add_ProductNetRule(
                        cell.product_rules[inpt][otpt][0])

    #Filling in the actual compatible rule network. 
        for cell in cells:
            if cell.product_netrules.values() != {}:
                for ngh in cell.neighbors:
                    if ngh.product_netrules.values() != {}:
                        for r1 in cell.product_netrules.values():
                            for r2 in ngh.product_netrules.values():
                                # check of compatibility in funct.
                                myRuleNet.add_edge(r1,r2) 

        myRuleNet.net.edges()
        myRuleNet.update_cycle_counts(myspace.master_count)

        count_alive = 0

        for cell in cells:
            if cell.count_rules  > 0:
                count_alive += 1

        # Quick output of key data for sweep analysis

        data =  (str(count_run)+","+ 
            str(myRuleNet.cycle_counts)+","+
            str(myRuleNet.get_plus3cell_complexity())+","+
            str(myRuleNet.get_plus3rule_complexity())+","+
            str(count_alive)+","+str(myspace.last_added_rule)+"\n")
        output_file.write(data)
        output_file.close()

        print "writing html"
        for cell in myspace.cells:
            x,y = cell.get_location()
            cell.set_location(x*.5, y*.5)
        # Creating an HTML file to visualize the network
        AC_grapher.output_JSON(myspace,myRuleNet, name 
            +"-"+str(count_run)+ ".html")

    else:
        data =  (str(count_run)+","+ 
            str(0)+","+
            str(0)+","+
            str(0)+","+
            str(0)+","+str(myspace.last_added_rule)+"\n")
        output_file.write(data)
        output_file.close()





#******************************
# Above are a bunch of utility functions. Below is everything that runs the model and graphics
#
#******************************

TYPES, URN, REPRO, non_viz_steps = [2, "endo-rich", "target",1000]# get_parameters()  


CHEM = "ALL"
INTEL= False
TOPO = "spatial"
CELL_COUNT = 100
PRODUCT_COUNT = 200
RULE_COUNT = 200

ENERGY_COSTS = {"pass":1/3., "transform":1/3., "reproduce": 1/3.}
INITIAL_ENERGY = 10
RADIUS = 1.5
action_rate = 1/10.


 ## Start setting up the run                       
name =  "-".join([str(TYPES), CHEM, str(INTEL), URN, TOPO])
print name

# as rng to reproduce runs if desired
seed = random.randint(0,sys.maxint)
RNG = random.Random(seed)

window_width = 700
window_height = 700
space_width = 10
space_height = 10
border_size = int(700 / float(space_width*1.1))



# At this point, we have everything for the model. Now we need to start up the graphics
main_window = window.Window(width=window_width, height=window_height, caption="Cartesian Space",style=window.Window.WINDOW_STYLE_TOOL)
main_window.set_location(0,40)
pyg.gl.glClearColor(.85, .85, .85, .2)
main_window.clear()

rule_plot_window = window.Window(width=400, height=285, caption="Count Rule Types",style=window.Window.WINDOW_STYLE_TOOL)
rule_plot_window.set_location(705,155)
rule_plot_window.clear()
pyg.gl.glClearColor(.85, .85, .85, .2)


product_plot_window = window.Window(width=400, height=285, caption="Count Product Types",style=window.Window.WINDOW_STYLE_TOOL)
product_plot_window.set_location(705,455)
product_plot_window.clear()
pyg.gl.glClearColor(.85, .85, .85, .2)

control_window = window.Window(width=105, height=95, caption="Pause",style=window.Window.WINDOW_STYLE_TOOL)
control_window.set_location(1000,40)
control_window.clear()
pyg.gl.glClearColor(.85, .85, .85, .2)

data_window = window.Window(width=290, height=95, caption="Cell Data",style=window.Window.WINDOW_STYLE_TOOL)
data_window.set_location(705, 40)
data_window.clear()
pyg.gl.glClearColor(.85, .85, .85, .2)


STEPS = 0
cell_batch = graphics.Batch()
product_label_batch = graphics.Batch()
rule_bar_batch = graphics.Batch()
control_batch = graphics.Batch()
data_batch = graphics.Batch()

cell_list = []
hld = pyg.text.Label(" ", x=5, y=55, color=(0,0,0,150))
cell_labels_list = [hld]
data_labels_list = [hld, hld, hld, hld]

control_list = []

control_list.append(control_Sprite(image.load("pause.png"), x=45, y=35, scale=.5, name="pause", batch=control_batch))
control_list.append(control_Sprite(image.load("stop.png"),x=20, y=-5,scale=.5, name="stop", batch=control_batch))
control_list.append(control_Sprite(image.load("play.png"), x=-5, y=35,scale=.5, name="play", batch=control_batch))

@main_window.event
def on_draw():
    main_window.clear()
    steps = pyg.text.Label("Steps:  " + str(myspace.master_count), x=2, y=2, color=(0,0,0,150), font_size=20, bold=True)
    steps.draw()
    for i in cell_list:
        i.draw()
        if i.cell.isAlive == False:
            cell_list.remove(i)
            i.delete
            i.x = 0
            print i.cell.id, " died"
            cells.remove(i.cell)
    for i in cell_labels_list:
        i.draw()


@rule_plot_window.event
def on_draw():
    rule_plot_window.clear()
    for bar in rule_bars:
        graphics.glColor3f(0, 0, 255)
        graphics.draw(4, pyg.gl.GL_QUADS, ('v2f', bar))

    graphics.glColor3f(0, 0, 0)
    graphics.glLineWidth(3)
    graphics.draw(2, pyg.gl.GL_LINES, ('v2f', (10.,30., 380., 30.)))
    graphics.draw(2, pyg.gl.GL_LINES, ('v2f',(10.,29., 10., 255)))


@product_plot_window.event
def on_draw():
    product_plot_window.clear()
    for bar in product_bars:
        graphics.glColor3f(0, 0, 255)
        graphics.draw(4, pyg.gl.GL_QUADS, ('v2f', bar))

    graphics.glColor3f(0, 0, 0)
    graphics.glLineWidth(3)
    graphics.draw(2, pyg.gl.GL_LINES, ('v2f', (10.,30., 380., 30.)))
    graphics.draw(2, pyg.gl.GL_LINES, ('v2f',(10.,29., 10., 255)))
    product_label_batch.draw()
    


@data_window.event
def on_draw():
    data_window.clear()
    for i in data_labels_list:
       i.draw()



@control_window.event
def on_draw():
    control_window.clear()
    control_batch.draw()


@main_window.event
def on_close():
    pyg.app.exit()



def update_product_count(inc, product_bars_data, max_prod_height):
    

    run_count = 0
    prods = len(product_bars_data)
    for index, product, points in product_bars_data:
        if index < prods-1:
            count = float(len(myurn.collection[product]))
            height = (count/200.) * max_prod_height

            product_bars[index]= (points[0], 30., points[1], 30., points[1], 
                height+30., points[0], height+30.)
            run_count += count
        else:
            height = ((200-run_count)/200.) * max_prod_height
            product_bars[index]= (points[0], 30., points[1], 30., points[1], 
                height+30., points[0], height+30.)


def update_rule_count(inc,max_prod_height):
    global rule_bars
    rule_bars=[]
    count_cells = len(cells)
    width_space = 370/((count_cells + 1)  + (2 * count_cells))
    for i, cell in enumerate(cells):
            count = cell.count_rules
            points = ((width_space+10 + (i * 3 * width_space), width_space +10 + (i*3*width_space) + (2 * width_space)))
            height = (count/200.) * max_prod_height
            rule_bars.append((points[0], 30., points[1], 30., points[1], 
                height+30., points[0], height+30.))


def cell_action(inc):
    n = int(1/float(inc))*10
    for i in range(n):
        myspace.activate_random_rule()
    if myspace.master_count > TOTAL_STEPS:
        pyg.clock.unschedule(cell_action)
        pyg.clock.unschedule(update_product_count)
        action_scheduled = False


def remove_label(time, label):

    cell_labels_list[0] = hld = pyg.text.Label(" ")


#Setting up the environment including the products
myurn = AC_Products.Urn(URN+"-"+REPRO, TYPES, RNG,INITIAL_ENERGY, 
    PRODUCT_COUNT)

# Creating all of the rules 
myrules = AC_ProductRules.create_RuleSet(CHEM,TYPES, RULE_COUNT, RNG)

#Creating a network object for compatible rules
myRuleNet = AC_ProductRuleNet.ProductRuleNet()



# creating the actual cells with Sprites
cell_image = image.load("cell.png")
cells = []
cell_radius = .005
for i in range(20):
    sprite = cell_Sprite(cell_image,cell_batch, str(i+1))
    sprite.scale = 3./ (space_width)
    sprite.color = (150,150,150)
    cell_list.append(sprite)
    new_cell = AC_Cells.Cell(myurn, myRuleNet, RNG, i+1, sprite, (window_width, window_height), (space_width, space_height), border_size, INTEL, REPRO, TOPO, RADIUS)
    cells.append(new_cell)
    sprite.add_cell(new_cell)

print "made cells"
#passing out the myrules to cells at random
for i in range(len(myrules)):
    cell = RNG.choice(cells)
    cell.add_ProductRule(myrules.pop(0))


# Creating a network of neighbors on torus grid
myspace= AC_Space.Space(cells, cell_radius, RNG, RADIUS, ENERGY_COSTS, dimensions=(space_width, space_height) )




print "Running the first %d steps headless . . . " %non_viz_steps
while myspace.master_count < non_viz_steps:
    myspace.activate_random_rule()


TOTAL_STEPS = get_step_count(TYPES)
pyg.clock.schedule_interval(cell_action, action_rate)
action_scheduled = True

# Setting up the bars for plotting product counts
count_products = len(myurn.collection.keys()) + 1
width_space = 370/((count_products + 1)  + (2 * count_products))
product_bars = [(0.,0.,0.,0.,0.,0.,0.,0.) for i in range(count_products)]
rule_bars=[]
product_bars_data = []

for i in range(count_products):
    product_bars_data.append((i, i+1, (width_space + (i * 3 * width_space), width_space + (i*3*width_space) + (2 * width_space))))
    if i < count_products - 1:
        pyg.text.Label(str(i+1), x=(width_space*1.75 + (i * 3 * width_space)), y=5, color=(0,0,0,150), font_size=15, bold=True, batch=product_label_batch)
    else:
        pyg.text.Label("Circ.", x=(width_space*1.1 + (i * 3 * width_space)), y=5, color=(0,0,0,150), font_size=15, bold=True, batch=product_label_batch)
pyg.text.Label("-200", x=9, y=249, color=(0,0,0,150), font_size=15, bold=True, batch=product_label_batch)


pyg.clock.schedule_interval_soft(update_product_count, 1, product_bars_data, 225)
pyg.clock.schedule_interval_soft(update_rule_count, 1,225)    

pyg.app.run()


print "Stopped at step: %d" %(myspace.master_count)

# print_data(name, myspace, myRuleNet, cells)

                        
                            

                            



