#! /usr/bin/python

#Craig LaCrone
#CSS 390 - Scripting
#Assignment 4 - FSM Generator

import sys
import fileinput

def remove_duplicates(l):
	return list(set(l))

def sort_list(l):
	l.sort()

machine_list = []
beginningcode_list = []
endcode_list = []
started = False
ended = False
for line in fileinput.input():
	if line.startswith('%machine'):
		started = True
		machine_list.append(line.strip("\n"))
		machineName = line.strip("\n").split(' ')[1]
	elif line.startswith('%end_machine'):
		machine_list.append(line.strip("\n"))
		started = False
		ended = True
	elif started: #and not line.startswith('%end_machine')
		machine_list.append(line.strip("\n"))
	elif ended and not started:
		endcode_list.append(line.strip("\n"))
	else:
		beginningcode_list.append(line.strip("\n"))


#print "Starting code"
for line in beginningcode_list:
	print line

print "using namespace std;"
#beginningcode_list has the code until the machine starts
#machine_list has the whole machine in it
#state_list has possible states (alphabetically ordered)
#event_list has possible events (alphabetically ordered)
#endcode_list has the code after the machine ends

#print "machine name = " + machineName

#separating states and events
state_list = []
event_list = []
event_dict = {}
for line in machine_list:
	if line.startswith('%state'):
		state_list.append(line.split(' ')[1] + "_STATE")
	elif line.startswith('%event'):
		event_list.append(line.split(' ')[1] + "_EVENT")
		event_dict[line.split(' ')[1]] = (line.split(' ')[1] + "_EVENT")
		state_list.append(line.split(' ')[2] + "_STATE")

#print "event_dict" 
#print event_dict

#Remove Duplicates / sort
state_list = remove_duplicates(state_list)
event_list = remove_duplicates(event_list)
sort_list(state_list)
sort_list(event_list)

#add invalid event
event_list.insert(0, "INVALID_EVENT")


#print state_list
#print event_list


#print enumerate states function
print "enum State {"
for state in state_list:
	print "\t" + state + ","
print "};"


#print enumerate events function
print
print "enum Event {"
for event in event_list:
	print "\t" + event + ","
print "};"

print
print "Event GetNextEvent();"

print


event_string_output = "event_string"
print "Event string_to_event(string " + event_string_output + "){"
for string, enum in sorted(event_dict.items()):
	print "\tif (" + event_string_output + " == \"" + string + "\"){"
	print "\t\treturn " + enum + ";"
	print "\t}"

print "\treturn " + event_list[0] + ";"
print "}"





#print "Machine starting"
#for line in machine_list:
#	print line

states_dict = {}
state_code = []
firstState = False
for line in machine_list:
	if line.startswith('%state'):
		#if firstState:
			#states_dict[curState] = state_code
			#del state_code[:]
		curState = line.split(' ')[1] + "_STATE"
		firstState = True
		states_dict[curState] = []
	elif line.startswith('%machine') or line.startswith('%end_machine'):
		pass
	elif firstState:		
		states_dict[curState].append(line)


for k in state_list:
	if not k in states_dict.keys():
		states_dict[k] = []

print
print
stateVar = "initial_state"
print "int " + machineName + "(State " + stateVar + ") {"
print
print
print "\tState state = " + stateVar + ";"
print "\tEvent event;"
print "\twhile (true) {"
print "\t\tswitch(state) {"
for state, code in sorted(states_dict.items()):
	print "\t\t case " + state + ":"
	stateCode = True
	for i in code:
		if i.startswith('%event'):
			stateCode = False
		elif stateCode:
			print "\t\t\t" + i
	print "\t\t\tevent = GetNextEvent();"
	print "\t\t\tswitch(event) {"
	eventStart = False
	for j in range(0, len(code)):
		if code[j].startswith('%event'):
			event = code[j].split(' ')[1]
			nextState = code[j].split(' ')[2] + "_STATE"
			print "\t\t\tcase " + event + "_EVENT:"
			eventStart = True
			if ((j+1) < len(code)) and code[j+1].startswith('%event'):
				print "\t\t\t  state = " + nextState + ";"
				print "\t\t\t  break;"
		elif not eventStart:
			pass
		else:
			#if not code[j].strip() == '':
			print "\t\t\t" + code[j]
			if ((j+1) < len(code)) and code[j+1].startswith('%event'):
				print "\t\t\t  state = " + nextState + ";"
				print "\t\t\t  break;"
			elif ((j+1) < len(code)) and not code[j+1].strip():
				print "\t\t\t  state = " + nextState + ";"
				print "\t\t\t  break;"
			elif code[j].strip() == '':
				print "\t\t\t  state = " + nextState + ";"
				print "\t\t\t  break;"


	print "\t\t\tdefault:\n\t\t\t\tcerr << \"invalid event in state " + state.split('_')[0] + ": \" << event << endl;\n\t\t\t\treturn -1;\n\t\t\t}\n\t\t\tbreak;"
print "\t\tdefault:\n\t\t\tcerr << \"INVALID STATE \" << state << endl;\n\t\t\treturn -1;\n\t\t}\n\t}\n}"


#print "End program"
for line in endcode_list:
	print line


	
#print "dictionary = "
#print states_dict

#iterate through the machine, each state becomes a dictionary, #where the key is the event, and its value is the next state

#list of dictionaries to iterate through
#dictionary of states, where the value is another dictionary of the events and etc.


