#! /usr/bin/python

#Craig LaCrone
#CSS 390 - Scripting
#Assignment 4 - FSM Generator

import sys
import fileinput

# function prints all code up until
# the machine code
def printBeginningCode(l):
	for line in l:
		print line
	print "#include <iostream>"
	print "using namespace std;"


# function prints all code after
# the machine code
def printEndingCode(l):
	for line in l:
		print line
	

# function takes the machine code, and creates
# a dictionary of all event strings, and their
# enumerated value
def createEventDict(l):
	event_dict = {}
	for line in l:
		if line.startswith('%event'):
			event_dict[line.split(' ')[1]] = (line.split(' ')[1] + "_EVENT")
	return event_dict


# function takes the machine code, and creates
# a dictionary of all important information
# structure of states_dict:
# states_dict keys are each state
# values for a state is a tuple including a list of state code, 
# and a dictionary of events
# the keys for the event dictionary are events, and the values
# are tuples with the next state, and a list of event code
# structure below:
# states_dict[state] = ( [stateCode], event_dict[event] = ( nextState, [eventCode] ) )
def processMachineCode(l):
	states_dict = {}
	curState = None
	curEvent = None
	nextState = None
	event = False
	for line in l:
		if line.startswith('%state'):	#get the state
			event = False
			curState = line.split(' ')[1] + "_STATE"
			states_dict[curState] = ([], {})	#add state with value of tuple(list, dict)
		elif line.startswith('%machine') or line.startswith('%end_machine'):	#skip these lines
			pass
		elif not curState == None:	#state exists
			if line.startswith('%event'):	#keep the events
				event = True
				curEvent = line.split(' ')[1] + "_EVENT"
				nextState = line.split(' ')[2] + "_STATE"
				states_dict[curState][1][curEvent] = (nextState, [])
			elif not event: #state code
				states_dict[curState][0].append(line)
			elif event: #event code
				states_dict[curState][1][curEvent][1].append(line)
			if not nextState in states_dict.keys() and not nextState == None:	#add states that may only exist as next state
				states_dict[nextState] = ([], {})
	return states_dict


# function takes the states_dict, and creates
# the enumerate states function based on the state
# keys
def printEnumStates(d):
	print "enum State {"
	for state in sorted(d.keys()):	#states in state dictionary
		print "\t" + state + ","
	print "};"


# function takes the events_dict, and creates
# the enumerate events function based on the event
# keys
def printEnumEvents(d):
	print
	print "enum Event {"
	event_list = sorted(d.values())	#events in event dictionary
	event_list.insert(0, "INVALID_EVENT")
	for event in event_list:
		print "\t" + event + ","
	print "};"


# function takes the events_dict, and creates
# the string_to_event function based on the event
# strings and enums
def printStringToEvent(d):
	output = "event_string"	#string
	print
	print "Event GetNextEvent();"
	print
	print "Event string_to_event(string " + output + "){"

	for string, enum in sorted(d.items()):	#string 'END', enum 'END_EVENT'
		print "\tif (" + output + " == \"" + string + "\"){"
		print "\t\treturn " + enum + ";"
		print "\t}"
	print "\treturn INVALID_EVENT;"
	print "}"


# function takes the states_dict, string name of the 
# FSM and prints the large switch statement
# lots of formatting
def printMachineCode(d, name):
	initState = "initial_state"	#string
	print
	print
	print "int " + name + "(State " + initState + ") {"
	print 
	print 
	print "\t State state = " + initState + ";"
	print "\t Event event;"
	print "\t while (true) {"
	print "\t\tswitch(state) {"

	for state in sorted(d.keys()):	#for each existing state
		print "\t\t case " + state + ":"
		for stateCode in d[state][0]:	#print any state code
			print "\t\t\t" + stateCode
		print "\t\t\tevent = GetNextEvent();"
		print "\t\t\tswitch(event) {"

		for event in sorted(d[state][1].keys()):	#for each event belonging to the current state
			print "\t\t\tcase " + event + ":"
			for eventCode in d[state][1][event][1]:	#print any event code
				print "\t\t\t\t" + eventCode
			print "\t\t\t\tstate = " + d[state][1][event][0] + ";" #print next state
			print "\t\t\t\tbreak;"

		print "\t\t\tdefault:"
		print '\t\t\t\tcerr << "invalid event in state ' + state.replace("_STATE", "") + ': " << event << endl;'
		print "\t\t\t\treturn -1;"
		print "\t\t\t}" 
		print "\t\t\tbreak;"

	print "\t\tdefault:"
	print '\t\t\tcerr << "INVALID STATE " << state << endl;'
	print "\t\t\treturn -1;"
	print "\t\t}"
	print "\t}"
	print "}"


# this code reads file input, and creates 3 lists,
# beginning code list holds all lines until it reaches 
# '%machine', machine list holds all code from '%machine'
# until it reaches '%end_machine', and endcode list holds
# all code after '%end_machine'. This setup makes it easy to print
# anything at anytime
def readInputAndRunCoverter():
	machine_list = []	#list holding all machine code
	beginningcode_list = []	#list holding all code until FSM
	endcode_list = []	#list holding all code after FSM
	started = False
	ended = False

	for line in fileinput.input():
		if line.startswith('%machine'):	#FSM code begins
			started = True
			machine_list.append(line.strip("\n"))
			machineName = line.strip("\n").split(' ')[1]	#get machine name
		elif line.startswith('%end_machine'):	#FSM code ends
			machine_list.append(line.strip("\n"))
			started = False
			ended = True
		elif started: #keeps all machine code
			machine_list.append(line.strip("\n"))
		elif ended and not started:	#FSM code ends, keep in separate list
			endcode_list.append(line.strip("\n"))
		else:	#FSM code not begun, keep in separate list
			beginningcode_list.append(line.strip("\n"))


	#function prints code up till FSM
	printBeginningCode(beginningcode_list)

	#function creates a dictionary of all event strings and enums from FSM
	events_dict = createEventDict(machine_list)

	#function creates a dictionary of all machine code
	states_dict = processMachineCode(machine_list)

	#function prints enum states function code
	printEnumStates(states_dict)

	#function prints enum events function code
	printEnumEvents(events_dict)

	#function prints string to event function code
	printStringToEvent(events_dict)

	#function prints machine code switch statement
	printMachineCode(states_dict, machineName)

	#function prints code after FSM
	printEndingCode(endcode_list)



if __name__ == "__main__":
	readInputAndRunCoverter()