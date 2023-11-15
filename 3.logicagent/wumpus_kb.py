# wumpus_kb.py
# ------------
# Licensing Information:
# Please DO NOT DISTRIBUTE OR PUBLISH solutions to this project.
# You are free to use and extend these projects for EDUCATIONAL PURPOSES ONLY.
# The Hunt The Wumpus AI project was developed at University of Arizona
# by Clay Morrison (clayton@sista.arizona.edu), spring 2013.
# This project extends the python code provided by Peter Norvig as part of
# the Artificial Intelligence: A Modern Approach (AIMA) book example code;
# see http://aima.cs.berkeley.edu/code.html
# In particular, the following files come directly from the AIMA python
# code: ['agents.py', 'logic.py', 'search.py', 'utils.py']
# ('logic.py' has been modified by Clay Morrison in locations with the
# comment 'CTM')
# The file ['minisat.py'] implements a slim system call wrapper to the minisat
# (see http://minisat.se) SAT solver, and is directly based on the satispy
# python project, see https://github.com/netom/satispy .

import utils

#-------------------------------------------------------------------------------
# Wumpus Propositions
#-------------------------------------------------------------------------------

### atemporal variables

proposition_bases_atemporal_location = ['P', 'W', 'S', 'B']

def pit_str(x, y):
    "There is a Pit at <x>,<y>"
    return 'P{0}_{1}'.format(x, y)
def wumpus_str(x, y):
    "There is a Wumpus at <x>,<y>"
    return 'W{0}_{1}'.format(x, y)
def stench_str(x, y):
    "There is a Stench at <x>,<y>"
    return 'S{0}_{1}'.format(x, y)
def breeze_str(x, y):
    "There is a Breeze at <x>,<y>"
    return 'B{0}_{1}'.format(x, y)

### fluents (every proposition who's truth depends on time)

proposition_bases_perceptual_fluents = ['Stench', 'Breeze', 'Glitter', 'Bump', 'Scream']

def percept_stench_str(t):
    "A Stench is perceived at time <t>"
    return 'Stench{0}'.format(t)
def percept_breeze_str(t):
    "A Breeze is perceived at time <t>"
    return 'Breeze{0}'.format(t)
def percept_glitter_str(t):
    "A Glitter is perceived at time <t>"
    return 'Glitter{0}'.format(t)
def percept_bump_str(t):
    "A Bump is perceived at time <t>"
    return 'Bump{0}'.format(t)
def percept_scream_str(t):
    "A Scream is perceived at time <t>"
    return 'Scream{0}'.format(t)

proposition_bases_location_fluents = ['OK', 'L']

def state_OK_str(x, y, t):
    "Location <x>,<y> is OK at time <t>"
    return 'OK{0}_{1}_{2}'.format(x, y, t)
def state_loc_str(x, y, t):
    "At Location <x>,<y> at time <t>"
    return 'L{0}_{1}_{2}'.format(x, y, t)

def loc_proposition_to_tuple(loc_prop):
    """
    Utility to convert location propositions to location (x,y) tuples
    Used by HybridWumpusAgent for internal bookkeeping.
    """
    parts = loc_prop.split('_')
    return (int(parts[0][1:]), int(parts[1]))

proposition_bases_state_fluents = ['HeadingNorth', 'HeadingEast',
                                   'HeadingSouth', 'HeadingWest',
                                   'HaveArrow', 'WumpusAlive']

def state_heading_north_str(t):
    "Heading North at time <t>"
    return 'HeadingNorth{0}'.format(t)
def state_heading_east_str(t):
    "Heading East at time <t>"
    return 'HeadingEast{0}'.format(t)
def state_heading_south_str(t):
    "Heading South at time <t>"
    return 'HeadingSouth{0}'.format(t)
def state_heading_west_str(t):
    "Heading West at time <t>"
    return 'HeadingWest{0}'.format(t)
def state_have_arrow_str(t):
    "Have Arrow at time <t>"
    return 'HaveArrow{0}'.format(t)
def state_wumpus_alive_str(t):
    "Wumpus is Alive at time <t>"
    return 'WumpusAlive{0}'.format(t)

proposition_bases_actions = ['Forward', 'Grab', 'Shoot', 'Climb',
                             'TurnLeft', 'TurnRight', 'Wait']

def action_forward_str(t=None):
    "Action Forward executed at time <t>"
    return ('Forward{0}'.format(t) if t != None else 'Forward')
def action_grab_str(t=None):
    "Action Grab executed at time <t>"
    return ('Grab{0}'.format(t) if t != None else 'Grab')
def action_shoot_str(t=None):
    "Action Shoot executed at time <t>"
    return ('Shoot{0}'.format(t) if t != None else 'Shoot')
def action_climb_str(t=None):
    "Action Climb executed at time <t>"
    return ('Climb{0}'.format(t) if t != None else 'Climb')
def action_turn_left_str(t=None):
    "Action Turn Left executed at time <t>"
    return ('TurnLeft{0}'.format(t) if t != None else 'TurnLeft')
def action_turn_right_str(t=None):
    "Action Turn Right executed at time <t>"
    return ('TurnRight{0}'.format(t) if t != None else 'TurnRight')
def action_wait_str(t=None):
    "Action Wait executed at time <t>"
    return ('Wait{0}'.format(t) if t != None else 'Wait')


def add_time_stamp(prop, t): return '{0}{1}'.format(prop, t)

proposition_bases_all = [proposition_bases_atemporal_location,
                         proposition_bases_perceptual_fluents,
                         proposition_bases_location_fluents,
                         proposition_bases_state_fluents,
                         proposition_bases_actions]


#-------------------------------------------------------------------------------
# Axiom Generator: Current Percept Sentence
#-------------------------------------------------------------------------------

#def make_percept_sentence(t, tvec):
def axiom_generator_percept_sentence(t, tvec):
    """
    Asserts that each percept proposition is True or False at time t.

    t := time
    tvec := a boolean (True/False) vector with entries corresponding to
            percept propositions, in this order:
                (<stench>,<breeze>,<glitter>,<bump>,<scream>)

    Example:
        Input:  [False, True, False, False, True]
        Output: '~Stench0 & Breeze0 & ~Glitter0 & ~Bump0 & Scream0'
    """
    #print('Entered Axiom - axiom_generator_percept_sentence')
    Output = '' #initializing a string varible to construct the axiom string
    
    t_string = str(t)
    
    if(tvec[0]==False):
        Output += '~Stench' + t_string + ' & '
    else:
        Output += 'Stench' + t_string + ' & '
    
    if(tvec[1]==False):
        Output += '~Breeze' + t_string + ' & '
    else:
        Output += 'Breeze' + t_string + ' & '
    
    if(tvec[2]==False):
        Output += '~Glitter' + t_string + ' & '
    else:
        Output += 'Glitter' + t_string + ' & '
    
    if(tvec[3]==False):
        Output += '~Bump' + t_string + ' & '
    else:
        Output += 'Bump' + t_string + ' & '
    
    if(tvec[4]==False):
        Output += '~Scream' + t_string
    else:
        Output += 'Scream' + t_string
    axiom_str = Output
    #print('AXIOM 1 - ',axiom_str)
    return axiom_str


#-------------------------------------------------------------------------------
# Axiom Generators: Initial Axioms
#-------------------------------------------------------------------------------

def axiom_generator_initial_location_assertions(x, y):
    """
    Assert that there is no Pit and no Wumpus in the location

    x,y := the location
    """
    #print('Entered Axiom - axiom_generator_initial_location_assertions')
    no_Pit    = '~P{0}_{1}'.format(x, y)
    no_Wumpus = '~W{0}_{1}'.format(x, y)
    axiom_str = no_Pit + ' & ' + no_Wumpus
    "*** YOUR CODE HERE ***"
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    #print('AXIOM 2:',axiom_str)
    return axiom_str

def axiom_generator_pits_and_breezes(x, y, xmin, xmax, ymin, ymax):
    """
    Assert that Breezes (atemporal) are only found in locations where
    there are one or more Pits in a neighboring location (or the same location!)

    x,y := the location
    xmin, xmax, ymin, ymax := the bounds of the environment; you use these
           variables to 'prune' any neighboring locations that are outside
           of the environment (and therefore are walls, so can't have Pits).
    """
    #print('Entered Axiom - axiom_generator_pits_and_breezes')
    Boundary_On_East = False
    Boundary_On_West = False
    Boundary_On_North = False
    Boundary_On_South = False
    
    if( x+1 > xmax):
        Boundary_On_East = True
    if( x-1 < xmin):
        Boundary_On_West = True
    if( y+1 > ymax):
        Boundary_On_North = True
    if( y-1 < ymin):
        Boundary_On_South = True
    
    Breeze_At_X_Y = 'B{0}_{1}'.format(x,y)
    implies = ' <=> '
    Pit_on_East  = 'P{0}_{1}'.format(x+1,y)
    Pit_on_West  = 'P{0}_{1}'.format(x-1,y)
    Pit_on_North = 'P{0}_{1}'.format(x,y+1)
    Pit_on_South = 'P{0}_{1}'.format(x,y-1)
    Pit_On_X_Y   = 'P{0}_{1}'.format(x,y)
    OR_Operator = ' | '  
    
    Pit_in_surroundings = ''
    if(Boundary_On_East == False):
        Pit_in_surroundings += (Pit_on_East) 
    if(Boundary_On_West == False):
        if(Pit_in_surroundings != ''):
            Pit_in_surroundings += (OR_Operator + Pit_on_West)
        else:
            Pit_in_surroundings += (Pit_on_West)
    if(Boundary_On_North == False):
        if(Pit_in_surroundings != ''):
            Pit_in_surroundings += (OR_Operator + Pit_on_North)
        else:
            Pit_in_surroundings += (Pit_on_North)
    if(Boundary_On_South == False):
        if(Pit_in_surroundings != ''):
            Pit_in_surroundings += (OR_Operator + Pit_on_South)
        else:
            Pit_in_surroundings += (Pit_on_South)
    Pit_in_surroundings += (OR_Operator + Pit_On_X_Y)
    
    #axiom_str = Breeze_At_X_Y + implies + '('+ Pit_in_surroundings + ')' + ' & ' + '('+ Pit_in_surroundings + ')' + implies + Breeze_At_X_Y
    axiom_str = Breeze_At_X_Y + implies + '('+ Pit_in_surroundings + ')'
    "*** YOUR CODE HERE ***"
    #print('AXIOM 3 - ',axiom_str)
    return axiom_str

def generate_pit_and_breeze_axioms(xmin, xmax, ymin, ymax):
    axioms = []
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            axioms.append(axiom_generator_pits_and_breezes(x, y, xmin, xmax, ymin, ymax))
    if utils.all_empty_strings(axioms):
        utils.print_not_implemented('axiom_generator_pits_and_breezes')
    return axioms

def axiom_generator_wumpus_and_stench(x, y, xmin, xmax, ymin, ymax):
    """
    Assert that Stenches (atemporal) are only found in locations where
    there are one or more Wumpi in a neighboring location (or the same location!)

    (Don't try to assert here that there is only one Wumpus;
    we'll handle that separately)

    x,y := the location
    xmin, xmax, ymin, ymax := the bounds of the environment; you use these
           variables to 'prune' any neighboring locations that are outside
           of the environment (and therefore are walls, so can't have Wumpi).
    """
    #print('Entered Axiom - axiom_generator_wumpus_and_stench')
    Boundary_On_East = False
    Boundary_On_West = False
    Boundary_On_North = False
    Boundary_On_South = False
    
    if( x+1 > xmax):
        Boundary_On_East = True
    if( x-1 < xmin):
        Boundary_On_West = True
    if( y+1 > ymax):
        Boundary_On_North = True
    if( y-1 < ymin):
        Boundary_On_South = True
    
    Stench_At_X_Y = 'S{0}_{1}'.format(x,y)
    implies = ' <=> '
    Wumpus_on_East  = wumpus_str(x+1,y) #'W{0}_{1}'.format(x+1,y)
    Wumpus_on_West  = wumpus_str(x-1,y) #'W{0}_{1}'.format(x-1,y)
    Wumpus_on_North = wumpus_str(x,y+1) #'W{0}_{1}'.format(x,y+1)
    Wumpus_on_South = wumpus_str(x,y-1) #'W{0}_{1}'.format(x,y-1)
    Wumpus_On_X_Y   = wumpus_str(x,y) #'W{0}_{1}'.format(x,y)
    OR_Operator = ' | '  
    
    Wumpus_in_surroundings = ''
    if(Boundary_On_East == False):
        Wumpus_in_surroundings += (Wumpus_on_East) 
    if(Boundary_On_West == False):
        if(Wumpus_in_surroundings != ''):
            Wumpus_in_surroundings += (OR_Operator + Wumpus_on_West)
        else:
            Wumpus_in_surroundings += (Wumpus_on_West)
    if(Boundary_On_North == False):
        if(Wumpus_in_surroundings != ''):
            Wumpus_in_surroundings += (OR_Operator + Wumpus_on_North)
        else:
            Wumpus_in_surroundings += (Wumpus_on_North)
    if(Boundary_On_South == False):
        if(Wumpus_in_surroundings != ''):
            Wumpus_in_surroundings += (OR_Operator + Wumpus_on_South)
        else:
            Wumpus_in_surroundings += (Wumpus_on_South)
    Wumpus_in_surroundings += (OR_Operator + Wumpus_On_X_Y)
    axiom_str = Stench_At_X_Y + implies + '('+ Wumpus_in_surroundings + ')'
    "*** YOUR CODE HERE ***"
    #print('AXIOM 4 - ',axiom_str)
    return axiom_str

def generate_wumpus_and_stench_axioms(xmin, xmax, ymin, ymax):
    axioms = []
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            axioms.append(axiom_generator_wumpus_and_stench(x, y, xmin, xmax, ymin, ymax))
    if utils.all_empty_strings(axioms):
        utils.print_not_implemented('axiom_generator_wumpus_and_stench')
    return axioms

def axiom_generator_at_least_one_wumpus(xmin, xmax, ymin, ymax):
    """
    Assert that there is at least one Wumpus.

    xmin, xmax, ymin, ymax := the bounds of the environment.
    """
    # print('Entered Axiom - axiom_generator_at_least_one_wumpus')
    axiom_str = ''
    for i in range(xmin, xmax + 1):
        for j in range(ymin, ymax + 1):
            axiom_str += 'W{0}_{1}'.format(i, j) + ' | '
    axiom_str = axiom_str[:-3]
    
    "*** YOUR CODE HERE ***"
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    # print('AXIOM 5 - ',axiom_str)
    return axiom_str

def axiom_generator_at_most_one_wumpus(xmin, xmax, ymin, ymax):
    """
    Assert that there is at at most one Wumpus.

    xmin, xmax, ymin, ymax := the bounds of the environment.
    """
    # print('Entered Axiom - axiom_generator_at_most_one_wumpus')
    from itertools import combinations
    locations = []
    axiom_str = ''
    for i in range(xmin, xmax+1):
        for j in range(ymin, ymax+1):
            locations.append(wumpus_str(i, j))
    
    pairs = set()
    for pair in combinations(locations, 2):
        pair_string = "(~{} | ~{})".format(pair[0], pair[1])
        pairs.add(pair_string)
    
    for pair in pairs:
        axiom_str += pair + ' & '
    axiom_str = axiom_str[:-3]
    print(axiom_str)
    "*** YOUR CODE HERE ***"
    #print('AXIOM 6 - ',axiom_str)
    return axiom_str

def axiom_generator_only_in_one_location(xi, yi, xmin, xmax, ymin, ymax, t = 0):
    """
    Assert that the Agent can only be in one (the current xi,yi) location at time t.

    xi,yi := the current location.
    xmin, xmax, ymin, ymax := the bounds of the environment.
    t := time; default=0
    """
    #print('Entered Axiom - axiom_generator_only_in_one_location')
    locations = []
    axiom_str = ''
    and_pl = ' & '
    not_pl = '~'
    for i in range (xmin, xmax+1):
        for j in range (ymin, ymax+1):
            if(i != xi or j != yi):
                locations.append('L{0}_{1}_{2}'.format(i,j,t)) 
    axiom_str +=  'L{0}_{1}_{2}'.format(xi,yi,t)
    for locs in locations:
        axiom_str += and_pl + not_pl + locs 

    #print('AXIOM 7 - ',axiom_str)
    "*** YOUR CODE HERE ***"
    return axiom_str

def axiom_generator_only_one_heading(heading = 'north', t = 0):
    """
    Assert that Agent can only head in one direction at a time.

    heading := string indicating heading; default='north';
               will be one of: 'north', 'east', 'south', 'west'
    t := time; default=0
    """
    
    #print('Entered Axiom - axiom_generator_only_one_heading')
    axiom_str = ''
    heading = heading[0].upper() + heading[1:] #to capitalize first char
    directions = ['HeadingNorth','HeadingSouth','HeadingEast','HeadingWest']
    headingDir = 'Heading' + heading + str(t)
    axiom_str += headingDir
    for dir in directions:
        if(dir!= 'Heading' + heading):
            axiom_str += ' & ~' + dir + str(t)
    "*** YOUR CODE HERE ***"
    print('AXIOM 8 - ',axiom_str)
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    return axiom_str

def axiom_generator_have_arrow_and_wumpus_alive(t = 0):
    """
    Assert that Agent has the arrow and the Wumpus is alive at time t.

    t := time; default=0
    """
    HaveArrow_At_T = state_have_arrow_str(t)
    WumpusAlive_At_T = state_wumpus_alive_str(t)
    #print('Entered Axiom - axiom_generator_have_arrow_and_wumpus_alive')
    axiom_str = HaveArrow_At_T + ' & ' + WumpusAlive_At_T
    "*** YOUR CODE HERE ***"
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    #print('AXIOM 9 - ',axiom_str)
    return axiom_str


def initial_wumpus_axioms(xi, yi, width, height, heading='east'):
    """
    Generate all of the initial wumpus axioms
    
    xi,yi = initial location
    width,height = dimensions of world
    heading = str representation of the initial agent heading
    """
    axioms = [axiom_generator_initial_location_assertions(xi, yi)]
    axioms.extend(generate_pit_and_breeze_axioms(1, width, 1, height))
    axioms.extend(generate_wumpus_and_stench_axioms(1, width, 1, height))
    
    axioms.append(axiom_generator_at_least_one_wumpus(1, width, 1, height))
    axioms.append(axiom_generator_at_most_one_wumpus(1, width, 1, height))

    axioms.append(axiom_generator_only_in_one_location(xi, yi, 1, width, 1, height))
    axioms.append(axiom_generator_only_one_heading(heading))

    axioms.append(axiom_generator_have_arrow_and_wumpus_alive())
    
    return axioms


#-------------------------------------------------------------------------------
# Axiom Generators: Temporal Axioms (added at each time step)
#-------------------------------------------------------------------------------

def axiom_generator_location_OK(x, y, t):
    """
    Assert the conditions under which a location is safe for the Agent.
    (Hint: Are Wumpi always dangerous?)

    x,y := location
    t := time
    """
    #print('Entered Axiom - axiom_generator_location_OK')
    Wumpus_present = wumpus_str(x, y)
    Wumpus_Alive = 'WumpusAlive{0}'.format(t)
    Pit_Present = pit_str(x,y)
    location_Safe = 'OK{0}_{1}_{2}'.format(x,y,t)
    implies = ' >> '
    No ='~'
    and_pl = ' & '
    or_PL = ' | '
    
    axiom_str = location_Safe + ' <=> ' + '(' + No + Pit_Present + and_pl + No + '(' +  Wumpus_present + and_pl + Wumpus_Alive +'))' 
    "*** YOUR CODE HERE ***"
    #print('AXIOM 10 - ',axiom_str)
    return axiom_str

def generate_square_OK_axioms(t, xmin, xmax, ymin, ymax):
    axioms = []
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            axioms.append(axiom_generator_location_OK(x, y, t))
    if utils.all_empty_strings(axioms):
        utils.print_not_implemented('axiom_generator_location_OK')
    return list(filter(lambda s: s != '', axioms))


#-------------------------------------------------------------------------------
# Connection between breeze / stench percepts and atemporal location properties

def axiom_generator_breeze_percept_and_location_property(x, y, t):
    """
    Assert that when in a location at time t, then perceiving a breeze
    at that time (a percept) means that the location is breezy (atemporal)

    x,y := location
    t := time
    """
    #print('Entered Axiom - axiom_generator_breeze_percept_and_location_property')
    axiom_str = ''
    Breeze_at_Time_T = percept_breeze_str(t)
    Breeze_at_X_Y    = breeze_str(x,y)
    Location_X_Y_T   = state_loc_str(x,y,t)
    implies = ' >> '
    double_implies = ' <=> ' 
    axiom_str = '('+Location_X_Y_T + implies + '('+ Breeze_at_Time_T + double_implies + Breeze_at_X_Y + '))' 
    
    "*** YOUR CODE HERE ***"
    #print('AXIOM 11 - ',axiom_str)
    return axiom_str

def generate_breeze_percept_and_location_axioms(t, xmin, xmax, ymin, ymax):
    axioms = []
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            axioms.append(axiom_generator_breeze_percept_and_location_property(x, y, t))
    if utils.all_empty_strings(axioms):
        utils.print_not_implemented('axiom_generator_breeze_percept_and_location_property')
    return list(filter(lambda s: s != '', axioms))

def axiom_generator_stench_percept_and_location_property(x, y, t):
    """
    Assert that when in a location at time t, then perceiving a stench
    at that time (a percept) means that the location has a stench (atemporal)

    x,y := location
    t := time
    """
    #print('Entered Axiom - axiom_generator_stench_percept_and_location_property')
    axiom_str = ''
    Stench_at_Time_T = percept_stench_str(t)
    Stench_at_X_Y    = stench_str(x,y)
    Location_X_Y_T   = state_loc_str(x,y,t)
    implies = ' >> '
    double_implies = ' <=> '
    axiom_str = '('+Location_X_Y_T + implies + '('+ Stench_at_Time_T + double_implies + Stench_at_X_Y + '))' 
    
    "*** YOUR CODE HERE ***"
    #print('AXIOM 12 - ',axiom_str)
    return axiom_str

def generate_stench_percept_and_location_axioms(t, xmin, xmax, ymin, ymax):
    axioms = []
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            axioms.append(axiom_generator_stench_percept_and_location_property(x, y, t))
    if utils.all_empty_strings(axioms):
        utils.print_not_implemented('axiom_generator_stench_percept_and_location_property')
    return list(filter(lambda s: s != '', axioms))


#-------------------------------------------------------------------------------
# Transition model: Successor-State Axioms (SSA's)
# Avoid the frame problem(s): don't write axioms about actions, write axioms about
# fluents!  That is, write successor-state axioms as opposed to effect and frame
# axioms
#
# The general successor-state axioms pattern (where F is a fluent):
#   F^{t+1} <=> (Action(s)ThatCause_F^t) | (F^t & ~Action(s)ThatCauseNot_F^t)

# NOTE: this is very expensive in terms of generating many (~170 per axiom) CNF clauses!
def axiom_generator_at_location_ssa(t, x, y, xmin, xmax, ymin, ymax):
    """
    Assert the condidtions at time t under which the agent is in
    a particular location (state_loc_str: L) at time t+1, following
    the successor-state axiom pattern.

    See Section 7. of AIMA.  However...
    NOTE: the book's version of this class of axioms is not complete
          for the version in Project 3.
    
    x,y := location
    t := time
    xmin, xmax, ymin, ymax := the bounds of the environment.
    """
    #print('Entered Axiom - axiom_generator_at_location_ssa')
    axiom_str = ''   
    
    Location_X_Y_at_T = state_loc_str(x,y,t+1)
    implies = ' >> '
    
    Location_T_minus_1_plus_West  = None
    Location_T_minus_1_plus_East  = None
    Location_T_minus_1_plus_South = None
    Location_T_minus_1_plus_North = None
    
    if( x+1 <= xmax):
        Location_T_minus_1_plus_West  = state_loc_str(x+1,y,t)
        axiom_str += '(' + '(' + Location_T_minus_1_plus_West + ' & ' + 'HeadingWest{0}'.format(t) + ' & '+  'Forward{0}'.format(t) + ') >> ' + Location_X_Y_at_T + ')'+  ' & '

    if( x-1 >= xmin):
        Location_T_minus_1_plus_East  = state_loc_str(x-1,y,t)
        axiom_str += '(' +'(' + Location_T_minus_1_plus_East + ' & ' + 'HeadingEast{0}'.format(t) + ' & '+  'Forward{0}'.format(t) + ') >> ' + Location_X_Y_at_T + ')'+' & '
        
    if( y+1 <= ymax):
        Location_T_minus_1_plus_South  = state_loc_str(x,y+1,t)
        axiom_str += '(' +'(' + Location_T_minus_1_plus_South + ' & ' + 'HeadingSouth{0}'.format(t) + ' & '+  'Forward{0}'.format(t) + ') >> ' + Location_X_Y_at_T + ')'+' & '

    if( y-1 >= ymin):
        Location_T_minus_1_plus_North  = state_loc_str(x,y-1,t)
        axiom_str += '(' +'(' + Location_T_minus_1_plus_North + ' & ' + 'HeadingNorth{0}'.format(t) + ' & '+  'Forward{0}'.format(t) + ') >> ' + Location_X_Y_at_T + ')'+' & '
    
    grab_plus_not_Move = '(' + '(' + state_loc_str(x,y,t) + ' & ' + action_grab_str(t) + ' & ' + '~'+ action_forward_str(t) + ')'+  implies + Location_X_Y_at_T + ')'
    shoot_plus_not_Move = '(' + '(' + state_loc_str(x,y,t) + ' & ' + action_shoot_str(t) + ' & ' + '~'+ action_forward_str(t) + ')'+implies + Location_X_Y_at_T + ')'
    same_Loc_TurnLeft = '(' + '(' + state_loc_str(x,y,t) + ' & ' + action_turn_left_str(t) + ' & '+ '~'+ action_forward_str(t) + ')'+implies + Location_X_Y_at_T + ')'
    same_Loc_TurnRight = '(' + '(' + state_loc_str(x,y,t) + ' & ' + action_turn_right_str(t) + ' & '+ '~'+ action_forward_str(t) +')'+ implies + Location_X_Y_at_T + ')'
    same_loc_Wait = '(' + '(' + state_loc_str(x,y,t) + ' & ' + action_wait_str(t) + ' & '+ '~'+ action_forward_str(t) + ')'+implies + Location_X_Y_at_T + ')'
    same_loc_Bump_Tplus1 = '(' + '(' + state_loc_str(x,y,t) + ' & ' + percept_bump_str(t+1) + ' & '+ '~'+ action_forward_str(t) +')'+ implies + Location_X_Y_at_T + ')'
    
    axiom_str += grab_plus_not_Move + ' & ' + shoot_plus_not_Move + ' & ' + same_Loc_TurnLeft + ' & ' + same_Loc_TurnRight + ' & ' + same_loc_Wait + ' & ' + same_loc_Bump_Tplus1 
    
    "*** YOUR CODE HERE ***"
    #print('AXIOM 13 - ',axiom_str)
    return axiom_str

def generate_at_location_ssa(t, x, y, xmin, xmax, ymin, ymax, heading):
    """
    The full at_location SSA converts to a fairly large CNF, which in
    turn causes the KB to grow very fast, slowing overall inference.
    We therefore need to restric generating these axioms as much as possible.
    This fn generates the at_location SSA only for the current location and
    the location the agent is currently facing (in case the agent moves
    forward on the next turn).
    This is sufficient for tracking the current location, which will be the
    single L location that evaluates to True; however, the other locations
    may be False or Unknown.
    """
    axioms = [axiom_generator_at_location_ssa(t, x, y, xmin, xmax, ymin, ymax)]
    if heading == 'west' and x - 1 >= xmin:
        axioms.append(axiom_generator_at_location_ssa(t, x-1, y, xmin, xmax, ymin, ymax))
    if heading == 'east' and x + 1 <= xmax:
        axioms.append(axiom_generator_at_location_ssa(t, x+1, y, xmin, xmax, ymin, ymax))
    if heading == 'south' and y - 1 >= ymin:
        axioms.append(axiom_generator_at_location_ssa(t, x, y-1, xmin, xmax, ymin, ymax))
    if heading == 'north' and y + 1 <= ymax:
        axioms.append(axiom_generator_at_location_ssa(t, x, y+1, xmin, xmax, ymin, ymax))
    if utils.all_empty_strings(axioms):
        utils.print_not_implemented('axiom_generator_at_location_ssa')
    return list(filter(lambda s: s != '', axioms))

#----------------------------------

def axiom_generator_have_arrow_ssa(t):
    """
    Assert the conditions at time t under which the Agent
    has the arrow at time t+1

    t := time
    """
    #print('Entered Axiom - axiom_generator_breeze_percept_and_location_property')
    axiom_str = ''
    Shoot = action_shoot_str(t)
    Has_Arrow = state_have_arrow_str(t)
    Not_PL = '~'
    Has_Arrow_At_T_Plus_1 = state_have_arrow_str(t+1)
    
    
    axiom_str = Has_Arrow_At_T_Plus_1 + ' <=> ' + '('+ Has_Arrow + ' & ' + Not_PL + Shoot + ')' 
    "*** YOUR CODE HERE ***"
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    #print('AXIOM 14 - ',axiom_str)
    return axiom_str

def axiom_generator_wumpus_alive_ssa(t):
    """
    Assert the conditions at time t under which the Wumpus
    is known to be alive at time t+1

    (NOTE: If this axiom is implemented in the standard way, it is expected
    that it will take one time step after the Wumpus dies before the Agent
    can infer that the Wumpus is actually dead.)

    t := time
    """
    #print('Entered Axiom - axiom_generator_wumpus_alive_ssa')
    axiom_str = ''
    Wumpus_Alive = state_wumpus_alive_str(t)
    Wumpus_Alive_T_plus_1 = state_wumpus_alive_str(t+1)
    Scream = percept_scream_str(t+1)
    Not_PL = ' ~'
    
    axiom_str += Wumpus_Alive_T_plus_1 +  ' <=> ' + '(' + Wumpus_Alive + ' &' + Not_PL + Scream + ')' 
    
    "*** YOUR CODE HERE ***"
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    #print('AXIOM 15 - ',axiom_str)
    return axiom_str

#----------------------------------


def axiom_generator_heading_north_ssa(t):
    """
    Assert the conditions at time t under which the
    Agent heading will be North at time t+1

    t := time
    """
    #print('Entered Axiom - axiom_generator_heading_north_ssa')    
    axiom_str = ''
    
    HeadingNorth_at_T_plus_1 = state_heading_north_str(t+1)
    HeadingNorth_at_T = state_heading_north_str(t)
    TurnLeft  = action_turn_left_str(t)
    TurnRight = action_turn_right_str(t)
    Heading_East_at_T = state_heading_east_str(t)
    Heading_West_at_T = state_heading_west_str(t)
    
    axiom_str += HeadingNorth_at_T_plus_1 + ' <=> ' + '(' +'(' + HeadingNorth_at_T + ' & ' + '~' + TurnLeft + ' & ' + '~' + TurnRight + ')'
    axiom_str += ' | ' + '(' + Heading_East_at_T + ' & ' + TurnLeft + ')'
    axiom_str += ' | ' + '(' + Heading_West_at_T + ' & ' + TurnRight + ')' +')'
    "*** YOUR CODE HERE ***"
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    #print('AXIOM 16 - ',axiom_str)
    return axiom_str

def axiom_generator_heading_east_ssa(t):
    """
    Assert the conditions at time t under which the
    Agent heading will be East at time t+1

    t := time
    """
    #print('Entered Axiom - axiom_generator_heading_east_ssa')
    axiom_str = ''
    
    HeadingEast_at_T_plus_1 = state_heading_east_str(t+1)
    HeadingEast_at_T = state_heading_east_str(t)
    TurnLeft  = action_turn_left_str(t)
    TurnRight = action_turn_right_str(t)
    Heading_North_at_T = state_heading_north_str(t)
    Heading_South_at_T = state_heading_south_str(t)
    
    axiom_str += HeadingEast_at_T_plus_1 + ' <=> ' + '(' +'(' + HeadingEast_at_T + ' & ' + '~' + TurnLeft + ' & ' + '~' + TurnRight + ')'
    axiom_str += ' | ' + '(' + Heading_South_at_T + ' & ' + TurnLeft + ')'
    axiom_str += ' | ' + '(' + Heading_North_at_T + ' & ' + TurnRight + ')' +')'
    "*** YOUR CODE HERE ***"
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    #print('AXIOM 17 - ',axiom_str)
    return axiom_str

def axiom_generator_heading_south_ssa(t):
    """
    Assert the conditions at time t under which the
    Agent heading will be South at time t+1

    t := time
    """
    #print('Entered Axiom - axiom_generator_heading_south_ssa')
    axiom_str = ''
    
    HeadingSouth_at_T_plus_1 = state_heading_south_str(t+1)
    HeadingSouth_at_T = state_heading_south_str(t)
    TurnLeft  = action_turn_left_str(t)
    TurnRight = action_turn_right_str(t)
    Heading_East_at_T = state_heading_east_str(t)
    Heading_West_at_T = state_heading_west_str(t)
    
    axiom_str += HeadingSouth_at_T_plus_1 + ' <=> ' + '(' +'(' + HeadingSouth_at_T + ' & ' + '~' + TurnLeft + ' & ' + '~' + TurnRight + ')'
    axiom_str += ' | ' + '(' + Heading_West_at_T + ' & ' + TurnLeft + ')'
    axiom_str += ' | ' + '(' + Heading_East_at_T + ' & ' + TurnRight + ')' +')'
    
    "*** YOUR CODE HERE ***"
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    #print('AXIOM 18 - ',axiom_str)
    return axiom_str

def axiom_generator_heading_west_ssa(t):
    """
    Assert the conditions at time t under which the
    Agent heading will be West at time t+1

    t := time
    """
    #print('Entered Axiom - axiom_generator_heading_west_ssa')
    axiom_str = ''
    
    HeadingWest_at_T_plus_1 = state_heading_west_str(t+1)
    HeadingWest_at_T = state_heading_west_str(t)
    TurnLeft  = action_turn_left_str(t)
    TurnRight = action_turn_right_str(t)
    Heading_North_at_T = state_heading_north_str(t)
    Heading_South_at_T = state_heading_south_str(t)
    
    axiom_str += HeadingWest_at_T_plus_1 + ' <=> ' + '(' +'(' + HeadingWest_at_T + ' & ' + '~' + TurnLeft + ' & ' + '~' + TurnRight + ')'
    axiom_str += ' | ' + '(' + Heading_South_at_T + ' & ' + TurnRight + ')'
    axiom_str += ' | ' + '(' + Heading_North_at_T + ' & ' + TurnLeft + ')' +')'
    
    "*** YOUR CODE HERE ***"
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    #print('AXIOM 19 - ',axiom_str)
    return axiom_str

def generate_heading_ssa(t):
    """
    Generates all of the heading SSAs.
    """
    return [axiom_generator_heading_north_ssa(t),
            axiom_generator_heading_east_ssa(t),
            axiom_generator_heading_south_ssa(t),
            axiom_generator_heading_west_ssa(t)]

def generate_non_location_ssa(t):
    """
    Generate all non-location-based SSAs
    """
    axioms = [] # all_state_loc_ssa(t, xmin, xmax, ymin, ymax)
    axioms.append(axiom_generator_have_arrow_ssa(t))
    axioms.append(axiom_generator_wumpus_alive_ssa(t))
    axioms.extend(generate_heading_ssa(t))
    return list(filter(lambda s: s != '', axioms))

#----------------------------------

def axiom_generator_heading_only_north(t):
    """
    Assert that when heading is North, the agent is
    not heading any other direction.

    t := time
    """
    #print('Entered Axiom - axiom_generator_heading_only_north')
    axiom_str = ''
    HeadingNorth = state_heading_north_str(t)
    HeadingSouth = state_heading_south_str(t)
    HeadingEast = state_heading_east_str(t)
    HeadingWest = state_heading_west_str(t)
    Double_implication = ' <=> '
    Not_PL = '~'
    and_PL = ' & '
    axiom_str += HeadingNorth + Double_implication + '(' + Not_PL + HeadingSouth + and_PL + Not_PL + HeadingEast + and_PL + Not_PL + HeadingWest + ')'
    "*** YOUR CODE HERE ***"
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    #print('AXIOM 20 - ',axiom_str)
    return axiom_str

def axiom_generator_heading_only_east(t):
    """
    Assert that when heading is East, the agent is
    not heading any other direction.

    t := time
    """
    #print('Entered Axiom - axiom_generator_heading_only_east')
    axiom_str = ''
    
    HeadingNorth = state_heading_north_str(t)
    HeadingSouth = state_heading_south_str(t)
    HeadingEast = state_heading_east_str(t)
    HeadingWest = state_heading_west_str(t)
    Double_implication = ' <=> '
    Not_PL = '~'
    and_PL = ' & '
    axiom_str += HeadingEast + Double_implication + '(' + Not_PL + HeadingSouth + and_PL + Not_PL + HeadingNorth + and_PL + Not_PL + HeadingWest + ')'
    
    
    "*** YOUR CODE HERE ***"
    #print('AXIOM 21 - ',axiom_str)
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    return axiom_str

def axiom_generator_heading_only_south(t):
    """
    Assert that when heading is South, the agent is
    not heading any other direction.

    t := time
    """
    # print('Entered Axiom - axiom_generator_heading_only_south')
    axiom_str = ''
    
    HeadingNorth = state_heading_north_str(t)
    HeadingSouth = state_heading_south_str(t)
    HeadingEast = state_heading_east_str(t)
    HeadingWest = state_heading_west_str(t)
    Double_implication = ' <=> '
    Not_PL = '~'
    and_PL = ' & '
    axiom_str += HeadingSouth + Double_implication + '(' + Not_PL + HeadingNorth + and_PL + Not_PL + HeadingEast + and_PL + Not_PL + HeadingWest + ')'
    
    
    "*** YOUR CODE HERE ***"
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    # print('AXIOM 22 - ',axiom_str)
    return axiom_str

def axiom_generator_heading_only_west(t):
    """
    Assert that when heading is West, the agent is
    not heading any other direction.

    t := time
    """
    # print('Entered Axiom - axiom_generator_heading_only_west')
    axiom_str = ''
    HeadingNorth = state_heading_north_str(t)
    HeadingSouth = state_heading_south_str(t)
    HeadingEast = state_heading_east_str(t)
    HeadingWest = state_heading_west_str(t)
    Double_implication = ' <=> '
    Not_PL = '~'
    and_PL = ' & '
    axiom_str += HeadingWest + Double_implication + '(' + Not_PL + HeadingSouth + and_PL + Not_PL + HeadingEast + and_PL + Not_PL + HeadingNorth + ')'
    
    
    "*** YOUR CODE HERE ***"
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    # print('AXIOM 23 - ',axiom_str)
    return axiom_str

def generate_heading_only_one_direction_axioms(t):
    return [axiom_generator_heading_only_north(t),
            axiom_generator_heading_only_east(t),
            axiom_generator_heading_only_south(t),
            axiom_generator_heading_only_west(t)]


def axiom_generator_only_one_action_axioms(t):
    """
    Assert that only one axion can be executed at a time.
    
    t := time
    """
    # print('Entered Axiom - axiom_generator_only_one_action_axioms')
    axiom_str = ''
    "*** YOUR CODE HERE ***"
    import itertools
    
    Grab  = action_grab_str(t)
    Shoot = action_shoot_str(t)
    Climb = action_climb_str(t)
    TurnLeft = action_turn_left_str(t)
    TurnRight = action_turn_right_str(t)
    Forward = action_forward_str(t)
    Wait = action_wait_str(t)
    
    actions = []
    actions.append(Grab)
    actions.append(Shoot)
    actions.append(Climb)
    actions.append(TurnRight)
    actions.append(TurnLeft)
    actions.append(Wait)
    actions.append(Forward)
    
    combinations = list(itertools.combinations(actions, 2)) 
    or_PL = ' | '
    
    Any_One_Action = '(' +  Grab + or_PL + Shoot + or_PL + Climb + or_PL + TurnLeft + or_PL + TurnRight + or_PL + Forward + or_PL + Wait + ')' + ' & '
    axiom_str += Any_One_Action
    for pair in combinations:
        axiom_str += '(~' + pair[0] + ' | ' + '~'+ pair[1] + ') & ' 
    
    axiom_str = axiom_str[:-3]
    
    # Comment or delete the next line once this function has been implemented.
    #utils.print_not_implemented()
    # print('AXIOM 24 - ',axiom_str)
    return axiom_str


def generate_mutually_exclusive_axioms(t):
    """
    Generate all time-based mutually exclusive axioms.
    """
    axioms = []
    
    # must be t+1 to constrain which direction could be heading _next_
    axioms.extend(generate_heading_only_one_direction_axioms(t + 1))

    # actions occur in current time, after percept
    axioms.append(axiom_generator_only_one_action_axioms(t))

    return list(filter(lambda s: s != '', axioms))

#-------------------------------------------------------------------------------
