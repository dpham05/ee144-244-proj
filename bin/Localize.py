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

room_to_constraint_mapping = {"kitchen": x >= 5 and x <= 8 and y >= 8 and y <= 10,
                              "bedroom": x >=-8.7 and x <= -2 and y >= -5 and y <= 2.2,
                              "hockey rink": x >=10000 and x <= 20000 and y >= -88888 and y <= -88293}


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
    
    u_clause = None 
    for room in ultrasound_rooms:
        u_clause = u_clause or room_to_constraint_mapping[room]
        # u_clause += "(" + room_to_constraint_mapping[room] + ")"
        #if room != ultrasound_rooms[-1]:
            #u_clause += " OR "
    #u_clause += ")"
    s.add(u_clause)
    #s.check()
        
    #print "ultrasound clause:" , u_clause

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
    
    for (ap,ss)  in wifi_data:
        radius = radius_from_access_strength(ap,ss)
        #(x0, y0) = access_point_to_coord_mapping[ap]
        #print x0
        s.add((x - access_point_to_coord_mapping[ap][0])**2 + (y - access_point_to_coord_mapping[ap][1])**2 <= radius_from_access_strength(ap,ss)**2 )
        #if ((ap,ss) != wifi_data[-1]):
            #wifi_clauses += " AND "
        
    #print "WiFi clauses:" , wifi_clauses
    
    print "Building SMT formula"
    

    #smt_formula = u_clause + wifi_clauses

    #print u_clause
    
    #print "Sending to SMT solver:", smt_formula
    
    #TODO actually call the SMT solver
    print "Calling SMT solver ..."
    
    print s.check()
    
    #TODO replace hardcoded results with SMT call
    
    print "SMT solver returns" , s.model()

    # ------------------------------------------------------------------
    # Determine a circle which captures all possible value of location
    r = 0
    new_x = s.model()[x]
    new_y = s.model()[y]
    while (s.check() == sat):
        r = r + 1
        s.add((x - new_x)**2 + (y - new_y)**2 >= r**2 )
        if s.check() == sat:
            print "SMT solver returns" , s.model(), "r =",r
    # -------------------------------------------------------------------
    
    # we could start by looking up this first satisfiable point,
    # or we can resample. # We have a bunch of options here, but for this,
    # let's keep it simple and lookup the first result.
    
    
    # lookup smt_returns in 
    #print "Calling function 'coords_to_room' on (", s.model()[x], ",", s.model()[y], ")"
    
    # This prototype is only going to work with circles and with rectangles
    # I should have a room object and a WiFi range object
    
    location = "kitchen"
    print "localized to:", location


