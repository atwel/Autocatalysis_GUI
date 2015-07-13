import matplotlib.pyplot as plt



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




PRODUCT_TYPES = [2,3,4,5,6,7,8,9]
CHEMISTRY = ["ALL"] # "SOLOH"
INTEL_TYPE = [False] # => "selective"
URN_TYPE = ["fixed-rich-target","fixed-poor-target", "fixed-rich-source","fixed-poor-source", "endo-rich-source","endo-poor-source"]
TOPOLOGY = ["spatial"] # "well-mixed"

stack = {}
#graph_type = "Cycles Alive"
#graph_type = "3+ Cycles Alive"
graph_type = "3+ Rules Alive"
#graph_type = "Cell Count"
x = [2,3,4,5,6,7,8,9]
for TYPES in PRODUCT_TYPES:
	for CHEM in CHEMISTRY:
		for INTEL in INTEL_TYPE:
			for URN in URN_TYPE:
				for TOPO in TOPOLOGY:
					mystr = "-".join([str(TYPES), CHEM, str(INTEL), URN, TOPO])
					datafile = open(mystr+".csv","r+")
					vals = []
					three_vals = []
					cells = []
					rules = []
					count_runs = 0.
					step_count = get_step_count(TYPES)
					
					for line in datafile:
						count_runs += 1
						pre = line.replace("{","|").replace("}","|")
						raw = pre.strip().split("|")
						run = int(raw[0].replace(",",""))
						precycles = raw[1].split(",")
						cycles = {}
						for i in precycles:
							try:
								j,k = i.split(":")
								cycles[int(j)] = int(k)
							except:
								cycles = {}

						after = raw[2].split(",")

						if graph_type == "Cycles Alive":			
							if int(after[4]) > step_count*.95:
								if len(cycles.keys()) > 0:
									vals.append(1)
								else:
									vals.append(0)

						elif graph_type == "3+ Cycles Alive":
							if cycles != {}:
								if len(cycles.keys()) > 1:
									vals.append(1)
								else:
									vals.append(0)
							else:		
								vals.append(0)

						elif graph_type == "3+ Rules Alive":
							if after[2]=='False':
								vals.append(0)
							else:
								vals.append(1)

						elif graph_type == "Cell Count":
							cnt = 0
							if int(after[4]) > step_count*.95:
								if len(cycles.keys()) > 0:
									vals.append(int(after[3]))
									cnt += 1
							count_runs = cnt


              				try:
              					stack[URN].append(sum(vals)/count_runs)
              				except:
              					stack[URN] = [sum(vals)/count_runs]

print stack
x = [2,3,4,5,6,7,8,9]

plt.axis([1,10,-.05,1.1])
plt.plot(x,stack["fixed-rich-source"], label="source-rich", color="k", marker="s",markeredgecolor="k",ms=8,linestyle="solid", linewidth=2)
plt.plot(x,stack["fixed-poor-source"], label="souce-poor", color="k", marker="^",linestyle="solid",linewidth=2,markeredgecolor="k",ms=8)
plt.plot(x,stack["endo-rich-source"], label="stigmergy-rich", color="r", marker="s",linestyle="solid",linewidth=2,markeredgecolor="r",ms=8)
plt.plot(x,stack["endo-poor-source"], label="stigmergy-poor", color="r", marker="^",linestyle="solid",linewidth=2,markeredgecolor="r",ms=8)
plt.plot(x,stack["fixed-rich-target"], label="target-rich", color="b", marker="s",linestyle="solid",linewidth=2,markeredgecolor="b",ms=8)
plt.plot(x,stack["fixed-poor-target"], label="target-poor", color="b", marker="^",linestyle="solid",linewidth=2,markeredgecolor="b",ms=8)
#plt.plot(x,nonspatial, label="nonspatial", color="g", marker="s",linestyle="solid",linewidth=2,markeredgecolor="g",ms=8)


plt.title("ALL Chem - No Pass Back - " + graph_type)
plt.ylabel("Fraction of 100 runs w/ Hypercycles")
plt.xlabel("Types of Products in Chemistry")
legend = plt.legend(bbox_to_anchor=(.01, -0.3, 1., .102), loc=3,ncol=3, mode="expand", borderaxespad=1.)
plt.savefig(graph_type, bbox_extra_artists=(legend,), bbox_inches='tight')

#plt.show()