def output_JSON(space, rulenet, filename):
    """This stuff is about to get real nasty. We need to get a whole bunch of information 
    into a very specific format for visualization and unfortunately that format has info 
    that doesn't yet exist."""
    
    # given that cycles are most relevant and that our scheme to labeling the data needs 
    # cycle names, we'll start with cycles. We get them from networkx's 
    # recursive_simple_path() function which returns a list of ProductRules as nodes in               
    # the path. We need to get cells and links from that.
    cycles = rulenet.return_cycles() #uses recursive_simple_path()

    # We'll be populating these as we go along
    cell_list = {} # dict with cells as key, targeted neiughbors 1st, type of rule 2nd, 
                   # link_id 3rd, count of rules for link 4th
    renamed_cycles = {} # dict with cycle name as key, list of renamed links as values
    link_list = {} # master list of link with info. Detailed later.
    rule_list = {} # rules != links, so we keep track of the rules in the cycles so that                 
                   # later we can make sure we get all rules.
    link_name = 0  # Used to name the links for the JSON structure.
    locations ={}
    
    # Now we'll go through the cycles and pull out the right info.
    for cyc in range(len(cycles)):
        
        start = cycles[cyc][0] #cycles don't have the endpoint, so need this node later
        cycle = cycles[cyc] # the cycle we're working with this loop.
        
        new_names = [] # to rename the links for the cycle plotting.
        
        for j in range(len(cycle)):
            source = cycle[j].get_owner() # owner of the rule, i.e. source of the link
            
            if j < len(cycle)-1:
                target = cycle[j+1].get_owner() # next cell
            else:
                target = start.get_owner() # or very first cell, i.e. start/end of cycle.
                
            # 'type' of link for text display later and identification now. 
            type = str(cycle[j].get_input()) + " -> " + str(cycle[j].get_output())
            
            # Getting list of rules so we can more easily find those not in cycles later.
            name_r = "-".join([str(x) for x in [source.id,type]]) # at most one of NetRule of a given type per cell
            try:
                rule_list[name_r] += 1 # dummy counter 
            except:
                rule_list[name_r] = 1 # adding new rule
            
            name = "-".join([str(x) for x in [source.id,target.id,type]])
                                              # The same NetRule can be a part of several 
                                              # links because it can connect with several 
                                              # neighbors so linking are distinguished by 
                                              # source, target and type. 
            
            count = cycle[j].get_count()
            
            # Links probably exist in several cycles so there is a good chance any given     
            # link is already in the dictionary of links. We check that here. 
            try:
                link_list[name]["cycles"].append(cyc) # just number linked to this cycle.
                new_names.append(link_list[name]["name"]) # for the cycle dictionary.
            except:
                
                dict = {"current":-1, "name":link_name, "count":count}
                dict["cycles"] = [cyc] # list of cycles this link is a part of.
                dict["source"] = source.id
                dict["target"] = target.id
                dict["type"] = type 
                dict["count"] = 0 # to be filled once we know all the links between source 
                                  # and target. 
                dict["number"] = 0 # ditto
                link_list[name] = dict # passing the info to the big list.
                new_names.append(link_name) # for the cycle dictionary.
                link_name += 1 # next link's name is next number
                print "Named " + str(link_name-1) 
                
            
            # At this point, we have the information for the link. Now we want to let the 
            # cell's know what links they have so that we can space things out better 
            # visualization in the end.      
            
            try:
                # same link, different cycle.
                cell_list[source.id][target.id][type]["cycles"].append(cyc) 
            except:
                # means we haven't seen this particular link before.
                try:
                    # this works if source-target combo has other links already.
                    cell_list[source.id][target.id][type] = {}
                    cell_list[source.id][target.id][type]["cycles"] = [cyc]
                    cell_list[source.id][target.id][type]["count"] = count
                except:
                    # if not, we need try to add the target
                    try:
                        # source is there, target, type, cycles are new
                        cell_list[source.id][target.id] = {}
                        cell_list[source.id][target.id][type] = {}
                        cell_list[source.id][target.id][type]["cycles"] = [cyc]
                        cell_list[source.id][target.id][type]["count"] = count
                    except:
                        # everything is new.
                        cell_list[source.id] = {}
                        cell_list[source.id][target.id] = {}
                        cell_list[source.id][target.id][type] = {}
                        cell_list[source.id][target.id][type]["cycles"] = [cyc]
                        cell_list[source.id][target.id][type]["count"] = count
            
            """ Ok. At this point, we've added the link to the link list and let 'the        
            cell' know that it has the link. Importantly, the link knows what cycles it is 
            associated with. Once we've gone through the whole cycle, we need to add the 
            named cycle to the dictionary of cycles. The value for the dictionary is a 
            list of the named links we've been creating as we go along.
            """
            
        renamed_cycles[cyc] = new_names
        
    # At this point, we've gone through the list of cycles. It'd be nice to quit here, but 
    # there are probably more cells and links that aren't a part of any cycles. We need to
    # find and add those. Boo.

    for cell in space.cells:
        if cell.isAlive:
            locations[cell.id] = cell.location
            for rule in cell.product_netrules.values(): # is a dictionary (key = 'type')
                source = rule.get_owner()
                type = str(rule.get_input()) +" -> "+str(rule.get_output())
                name2 = "-".join([str(x) for x in [source.id,type]]) 
                                                #unique identification of the rule.
                
                try: 
                    yes = rule_list[name2] # great, cell and link are already there. 
                except:
                    # darn it, new rule/link(s) to add. We're going to have to find which 
                    # neighbors can actually use the rule's output (i.e. a viable link)
                     
                    nghbrs = source.neighbors
                    output = rule.get_output()

                    for ngh in nghbrs:
                        if ngh.has_rule(output):
                            
                            
                            # now we add the link to the big dictionary of links.
                            target = ngh
                            name = "-".join([str(x) for x in [source.id,target.id,type]])
                            count = rule.get_count()
                            dict = {"current":-1, "name":link_name, "count":count}
                            dict["cycles"] = []
                            dict["source"] = source.id
                            dict["target"] = target.id
                            dict["type"] = type
                            dict["count"] = 0
                            dict["number"] = 0
                            link_list[name] = dict
                                
                            try:
                                cell_list[source.id] # checking if source cell is new
                            except:
                                cell_list[source.id] = {}  # if so, adding. 
                        
                            # adding the link to the cell's info.             
                            try:
                                cell_list[source.id][target.id][type] = {}
                                cell_list[source.id][target.id][type]["links"]=[link_name]
                                cell_list[source.id][target.id][type]["count"] = count
                            except:
                                cell_list[source.id][target.id] = {}
                                cell_list[source.id][target.id][type] = {}
                                cell_list[source.id][target.id][type]["links"]=[link_name]
                                cell_list[source.id][target.id][type]["count"] = count
                            
                            try:
                                a = cell_list[target.id]
                            except:
                                cell_list[target.id] = {}
                                
                        link_name += 1 # same naming scheme still works.
                        #print "Named " + str(link_name-1)
                    rule_list[name2] = 1 # just keeping track of rules.
                    
                # onto the next rule the cell owns.
        # onto the next cell.
    
    
    """ At this point we have all cells, links, and cycles. Now we have to figure out what 
    links the cells have and pass that information back to the links. We also need to 
    update the names of the cells because the D3 JSON reader names them by their index.
    The cycle list (i.e. renamed cycles) is already. The cell list needs some summary 
    info. As we create that, we'll rename them.
    """                        
    name_mapper = {}  # for renaming   
    final_cell_list = [] # the collection we'll create the JSON data from.
    
    new_name_counter = 0
    for source in cell_list.keys():
        print source
        # renaming bizness
        new_name = new_name_counter
        new_name_counter += 1
        print "Name pair", source, new_name
        name_mapper[source] = new_name
        
        source_basic_type = {} 
        
        for alter in cell_list[source].keys():
            source_to_target_types = {}
            for type in cell_list[source][alter].keys():
                try: 
                    b = source_basic_type[type]
                except:
                    source_basic_type[type] = cell_list[source][alter][type]["count"]
                
                try:
                    a = source_to_target_types[type]
                except:
                    source_to_target_types[type] = cell_list[source][alter][type]["count"]
            
            count_links_between = len(source_to_target_types.keys())
            
            counter = 1
            for type in source_to_target_types.keys():
                
                link_list_name = "-".join([str(x) for x in [source, alter, type]])
                link_list[link_list_name]["count"] = count_links_between
                link_list[link_list_name]["number"] = counter
                counter += 1
                
                
        type_list = "Rules:<br>"
        for type in source_basic_type.keys():
            type_list += str(type)+": "+str(source_basic_type[type])+"<br>"
        
        entry = {"name":new_name, "rules_text":type_list, "location_x":locations[source][0] ,"location_y":locations[source][1] } 
        final_cell_list.append(entry)
        
    
    naming_dict = {}     
    print "Link list keys", link_list.keys()      
    for link in link_list.keys():
        source,target,type1,type2 = link.split("-")  
        link_list[link]["source"] = name_mapper[int(source)]
        link_list[link]["target"] = name_mapper[int(target)]
        count_name = link_list[link]["name"]
        naming_dict[count_name] = link_list[link]
        
    #all renamed now. Just need to pack the link_list up into the correct order
            
    final_link_list = []
    print "Naming dict keys: "+ str(naming_dict.keys())
    for i in naming_dict.keys():
        final_link_list.append(naming_dict[i])
            

    cycles_strg = "var cycles = {"  
    for cyc in renamed_cycles.keys():
         vals = renamed_cycles[cyc]
         the_dict = str(cyc)+":"+str(vals)+","
         cycles_strg += the_dict
    cycles_strg = cycles_strg[:-1] + "};\n"
            
    
    nodes_strg = "var nodes = [\n" 
    for cell in final_cell_list:
        addition = str(cell) + ",\n"
        nodes_strg += addition
    nodes_strg = nodes_strg[:-2] + "];\n"
    
    links_strg = "var links = [\n" 
    for link in final_link_list:
        addition = str(link) + ",\n"
        links_strg += addition
    links_strg = links_strg[:-2] + "];\n"
        
    
    master_strg = nodes_strg + links_strg + cycles_strg + "\n"


    html_file = open(filename, "w+")
    pre_file = open("graphing.html","r")

    for i in range(11):
        html_file.write(pre_file.readline())
    print master_strg
    html_file.write(master_strg)

    for line in pre_file:
        html_file.write(line)

    html_file.close()
    pre_file.close()


