import random
import json

def generate(rows, cols, state=0):
	if state == 1 or state == 2:
		nodeMatrix = [[(state - 1) for x in range(cols)] for y in range(rows)]
	else:
		nodeMatrix = [[random.getrandbits(1) for x in range(cols)] for y in range(rows)]
	
	return nodeMatrix

def createDictionary(rows, cols, data):
	config = {'rows':rows, 'cols':cols, 'data':data}
	return config

def outputJSON(data, filename):
	with open('nodeInfo.config', 'w') as file:
		json.dump(data, file)

def readConfig(filename):
	with open(filename) as file:
		config = json.load(file)
	return config
	
rows = 8
cols = 6

filename = 'nodeInfo.config'

nodeMatrix = generate(rows, cols)
nodeDict = createDictionary(rows, cols, nodeMatrix)
outputJSON(nodeDict, filename)
config = readConfig(filename)

dat = config['data']
nodeArray = [item for sublist in dat for item in sublist]
print(nodeArray)