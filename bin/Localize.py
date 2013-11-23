'''
Created on Nov 13, 2013

@author: Matt Weber
@contact: matt.weber@berkeley.edu
'''
from z3 import *

x = Real('x')
y = Real('y')
s = Solver()

#TODO fill these in with meaningful stuff
freq_room_mapping = ["", "kitchen", "bedroom", "hockey rink"]

access_point_to_coord_mapping = {"access_point_1": (2, 8), "access_point_2": (-6, 0), "access_point_3": (61.3, 45.2) }

room_to_constraint_mapping = {"kitchen": And(x >= 5, x <= 8, y >= 8, y <= 10),
                              "bedroom": And(x >=-8.7, x <= -2, y >= -5, y <= 2.2),
                              "hockey rink": And(x >=10000, x <= 20000, y >= -88888, y <= -88293)}


### Returns the radius appropriate for a given signal strength at a particular
### access point. Right now it stupidly returns the strength as the radius.

#TODO refine this with experimentation
def radius_from_access_strength(access_point, signal_strength):
    return signal_strength

if __name__ == '__main__':
    
    # TODO In Sid's server we're going to need to run this in a while loop.
    # so we regularly report info to the webserver
    
    # TODO replce hardcoded phone id with dynamicaly specifiably value
    phone_id = "123abc"
    
    print "getting data for phone_id" , phone_id
    print "running query: SELECT microphone_data FROM table WHERE phone_id = table.phone_id and timestamp = latest "
    # TODO implement "timestamp = latest" in the sql query

    # TODO actually run this query and dump the value to microphone_data 
    # TODO import some signal processing object as the audio type
    microphone_data = "signal_type_placeholder_where_second_of_audio_will_go"
    
    print "Running IFFT analysis on microphone_data"

    # TODO actually do IFFT and write results to spectrum_variable
    spectrum = [ (20288, 90), (20700, 5), (21999, 2), (202020020202, 17186186) ]
    print "Reporting spectrum:", spectrum
    
    room_strength = []
           
    print "Decoding ultrasonic signals"
    for (freq, amp) in spectrum:
        room_num = 0
        # TODO get rid of magic numbers
        if((20000 <= freq) and (freq <= 20600)):
            print "a frequency of", freq, "has been quantized to band 1"
            room_num = 1
        elif(20600 < freq and freq <= 21200):
            print "a frequency of", freq, "has been quantized to band 2"
            room_num = 2
        elif(21200 < freq and freq <= 22000):
            print "a frequency of", freq, "has been quantized to band 3"
            room_num = 3
        else:
            print "Error, frequency", freq, "is out of range"
            room_num = 0
        room_strength.append((freq_room_mapping[room_num], amp))
    
    print "ultrasound has been decoded into the following list:", room_strength
    
    # TODO make this number less arbitrary
    minimum_amplitude_cutoff = 4
    
    ultrasound_rooms = [room for (room, amp) in room_strength if amp > minimum_amplitude_cutoff and room != ""]
    print "Eliminating rooms below amplitude cutoff yields", ultrasound_rooms
    
    u_clause = []
    #neg_u_clause = []
    for room in ultrasound_rooms:
        
        u_clause.append(room_to_constraint_mapping[room])
        #neg_u_clause.append(Not(room_to_constraint_mapping[room]))
    u_clause = Or(u_clause)   
    #s.add(Or(u_clause))

    print "Identifying wifi access points"
    
    
    # I'm thinking here... we can AND the ultrasound clause with every wifi circle
    # but we also have the option to build a long wifi clause as the OR of each of the cirles
    # and then just and the two long clauses together. When I've thought about this in the past,
    # I've always thought of it as the intersection of all the regions, which is the version with all ANDS
    # We can experiment with what the alternative means, but my instinct is that we
    # should stick to the original idea.
    
    # TODO make a wifi signal object with id and strength
    
    print "running query: SELECT access_points FROM table WHERE phone_id = table.phone_id and timestamp = latest "
    # TODO implement "timestamp = latest" in the sql query
    # TODO consider merging all the SQL queries into a single querey, to improve performance
    
    
    # TODO replace hardcoded values with query results.
    wifi_data = [ ("access_point_1", 25), ("access_point_2", 50) ]
    
    #wifi_clauses = ""
    u_clause = [u_clause]
    for (ap,ss)  in wifi_data:
        radius = radius_from_access_strength(ap,ss)
        #(x0, y0) = access_point_to_coord_mapping[ap]
        #print x0
        u_clause.append((x - access_point_to_coord_mapping[ap][0])**2 + (y - access_point_to_coord_mapping[ap][1])**2 <= radius_from_access_strength(ap,ss)**2)
        #s.add((x - access_point_to_coord_mapping[ap][0])**2 + (y - access_point_to_coord_mapping[ap][1])**2 <= radius_from_access_strength(ap,ss)**2 )
        #if ((ap,ss) != wifi_data[-1]):
            #wifi_clauses += " AND "
    u_clause = And(u_clause)
    #print u_clause
    #print "WiFi clauses:" , wifi_clauses
    
    print "Building SMT formula"
    

    #smt_formula = u_clause + wifi_clauses
    #print u_clause
    #print "Sending to SMT solver:", smt_formula
    
    #TODO actually call the SMT solver
    print "Calling SMT solver ..."

    s.add(u_clause)
    print s.check()
    
    #TODO replace hardcoded results with SMT call
    
    print "SMT solver returns" , s.model()

    # ------------------------------------------------------------------
    # Determine a circle which captures all possible value of location
    r = 1
    #print s
    new_x = s.model()[x]
    new_y = s.model()[y]
    
    s.push()
    s.add((x - new_x)**2 + (y - new_y)**2 >= r**2 )
    
    while (s.check() == sat):
        print "SMT solver returns" , s.model(), "r =",r
        r = r * 2
        s.pop()
        s.push()
        s.add((x - new_x)**2 + (y - new_y)**2 >= r**2 )
    
    s.pop()
    range_list = [r/2, r]
    print range_list
    while(range_list[1] - range_list[0] > 0.1):
        s.push()
        s.add((x - new_x)**2 + (y - new_y)**2 >= ((range_list[1] - range_list[0])/2 + range_list[0])**2 )
        if (s.check() == sat):
            print "SMT solver returns" , s.model(), "r =", range_list
            range_list[0] = (float(range_list[1]) - float(range_list[0]))/2 + range_list[0]
        else:
            range_list[1] = (float(range_list[1]) - float(range_list[0]))/2 + range_list[0]
        s.pop()
    print "Outter circle at point [", new_x, ", ", new_y, "] has radius: ", range_list[1]

    # -------------------------------------------------------------------
    # ---------------------Determine inner circle------------------------

    #print u_clause
    s.reset()
    s.add(Not(u_clause))

    r = 1
    #new_x = s.model()[x]
    #new_y = s.model()[y]
    
    s.push()
    s.add((x - new_x)**2 + (y - new_y)**2 <= r**2 )
    
    while (s.check() == unsat):
        #print "SMT solver returns" , s.model(), "r =",r
        r = r * 2
        #print r
        s.pop()
        s.push()
        s.add((x - new_x)**2 + (y - new_y)**2 <= r**2 )
    
    s.pop()
    range_list = [float(r)/2, r]
    while(range_list[1] - range_list[0] > 1):
        s.push()
        s.add((x - new_x)**2 + (y - new_y)**2 <= ((float(range_list[1]) - float(range_list[0]))/2 + range_list[0])**2 )
        if (s.check() == unsat):
            range_list[0] = (float(range_list[1]) - float(range_list[0]))/2 + range_list[0]
        else:
            range_list[1] = (float(range_list[1]) - float(range_list[0]))/2 + range_list[0]
        s.pop()
    print "Inner circle at point [", new_x, ", ", new_y, "] has radius: ", range_list[0]

    # --------------------------------------------------------------------------
    # ---------------------Fill up the whole region with square------------------------
    # --------------------------------with maximum side-------------------------------

    s.reset()
    clause = (x**2 + y**2) <= 4
    s.add(clause)
    square_list = []
    while(s.check() == sat):
        print "a"
        new_x = s.model()[x]
        new_y = s.model()[y]
        print s.model()
        distance = 0.25
        s.reset()
        s.add(Not(clause))
        print s
        s.push()
        s.add(x <= (new_x + distance), x >= (new_x - distance), y <= (new_y + distance), y >= (new_y - distance))
        while(s.check() == unsat):
            s.pop()
            distance = distance * 2
            s.push()
            s.add(x <= (new_x + distance), x >= (new_x - distance), y <= (new_y + distance), y >= (new_y - distance))
        s.pop()
        range_list = [float(distance)/2, distance]
        print range_list
        while(range_list[1] - range_list[0] > 0.1):
            s.push()
            s.add(x <= (new_x + (float(range_list[1]) - float(range_list[0]))/2 + range_list[0]), x >= (new_x - (float(range_list[1]) - float(range_list[0]))/2 + range_list[0]), y <= (new_y + (float(range_list[1]) - float(range_list[0]))/2 + range_list[0]), y >= (new_y - (float(range_list[1]) - float(range_list[0]))/2 + range_list[0]))
            if (s.check() == unsat):
                range_list[0] = (float(range_list[1]) - float(range_list[0]))/2 + range_list[0]
            else:
                range_list[1] = (float(range_list[1]) - float(range_list[0]))/2 + range_list[0]
            s.pop()
        square_list.extend([x <= (new_x + range_list[1]), x >= (new_x - range_list[1]), y <= (new_y + range_list[1]), y >= (new_y - range_list[1])])                
        s.reset()
        s.add(clause)
        s.add(Not(Or(square_list)))
    print square_list
    
    # we could start by looking up this first satisfiable point,
    # or we can resample. # We have a bunch of options here, but for this,
    # let's keep it simple and lookup the first result.
    
    
    # lookup smt_returns in 
    #print "Calling function 'coords_to_room' on (", s.model()[x], ",", s.model()[y], ")"
    
    # This prototype is only going to work with circles and with rectangles
    # I should have a room object and a WiFi range object
    
    location = "kitchen"
    print "localized to:", location


