import os, sys
import math
import pickle
import pygame
from pygame.locals import *


if not pygame.font: print("Fonts will be disabled")
if not pygame.mixer: print("Sound will be disabled")


def load_image(name, colorkey=None):
	#fullname = os.path.join('data', name)
	fullname = name

	try:
		image = pygame.image.load(fullname)
	except (pygame.error):
		print("Cannot load image:", name)
		print ("Full path was:", fullname)
		raise (SystemExit)

	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		print(str(colorkey))
		image.set_colorkey(colorkey, RLEACCEL)

	return(image, image.get_rect())

def imageHash(image1, size):
	totalBrightness = 0
	imagePixelArray = pygame.PixelArray(image1)
	for yPos in range(size[1]):
		for xPos in range(size[0]):
			totalBrightness += imagePixelArray[xPos][yPos] + imagePixelArray[xPos][yPos]//(xPos+1) + imagePixelArray[xPos][yPos]//(yPos+1)


	totalBrightness += imagePixelArray[0][0]
	totalBrightness += imagePixelArray[size[0]-1][0] * 2
	totalBrightness += imagePixelArray[0][size[1]-1] * 3
	totalBrightness += imagePixelArray[size[0]-1][size[1]-1] * 4

	return(totalBrightness)

#getInput waits a certain ammount of time (-1 for indefinite) for one character input, and returns it
def getInput(pauseTime=0, waitTime=5):
	if pauseTime < 0:
		while True:	#Wait forever
			for event in pygame.event.get():
				if event.type == QUIT:
					return("QUIT")
				elif event.type == KEYDOWN:
					return(pygame.key.name(event.key))
		pygame.time.wait(waitTime)

	if pauseTime == 0:
		for event in pygame.event.get():
			if event.type == QUIT:
				return("QUIT")
			elif event.type == KEYDOWN:
				return(pygame.key.name(event.key))
		return None #No input

	beginningTicks = pygame.time.get_ticks()					#Get time now
	while beginningTicks + pauseTime > pygame.time.get_ticks():	#While ending time is greater than current time
		for event in pygame.event.get():
			if event.type == QUIT:
				return("QUIT")
			elif event.type == KEYDOWN:
				return(pygame.key.name(event.key))
		pygame.time.wait(waitTime)

	return None	#No input



#takes in a file path and top corner and bottom corner x,y start and end nums, and a step,
#returns a list of images
def parseImage(filePath, topCorner, bottomCorner, start, end, step):
	tileList = []
	tileSize = (bottomCorner[0] - topCorner[0], bottomCorner[1] - topCorner[1])

	mapFull, mapFullRect = load_image(filePath, -1)
	mapSize = mapFull.get_size()
	numTiles = (mapSize[0]//bottomCorner[0], mapSize[1]//bottomCorner[1])

	if end == -1:
		end = numTiles[0] * numTiles[1]

	mapFullPixArray = pygame.PixelArray(mapFull)

	number = start
	while number < end:

		yPos = number//(numTiles[0])

		xPos = number%(numTiles[0])

		xPixBeg = (xPos * bottomCorner[0]) + topCorner[0]
		xPixEnd = ((xPos+1) * bottomCorner[0])
		yPixBeg = (yPos * bottomCorner[1]) + topCorner[1]
		yPixEnd = ((yPos+1) * bottomCorner[1])

		newTile = pygame.Surface(tileSize)

		pygame.surfarray.blit_array(newTile, mapFullPixArray[xPixBeg:xPixEnd,yPixBeg:yPixEnd])
		tileList.append(newTile)

		number += step

	return(tileList)

#takes in a file path and top corner and bottom corner x,y start and end TUPELS, and a step, and an optional colorkey,
#returns a list of images
def parseGridImage(filePath, topCorner, bottomCorner, start, end, step, colorKey=-1, border=0):
	tileList = []
	tileSize = (bottomCorner[0] - topCorner[0], bottomCorner[1] - topCorner[1])

	mapFull, mapFullRect = load_image(filePath, -1)
	mapSize = mapFull.get_size()
	numTiles = (mapSize[0]//bottomCorner[0], mapSize[1]//bottomCorner[1])

	if end == -1:
		end = numTiles[0] * numTiles[1]

	mapFullPixArray = pygame.PixelArray(mapFull)

	for yPos in range(start[1], end[1]):
		for xPos in range(start[0], end[0]):
			xPixBeg = (xPos * bottomCorner[0]) + topCorner[0]
			xPixEnd = ((xPos+1) * bottomCorner[0])
			yPixBeg = (yPos * bottomCorner[1]) + topCorner[1]
			yPixEnd = ((yPos+1) * bottomCorner[1])
	
			newTile = pygame.Surface(tileSize)

			pygame.surfarray.blit_array(newTile, mapFullPixArray[xPixBeg:xPixEnd,yPixBeg:yPixEnd])
			if colorKey == -1:
				colorKey = newTile.get_at((0,0))
			
			if border != 0:
				newTileArray = pygame.PixelArray(newTile)
				newTileArray[:,0:border] = colorKey
				newTileArray[:,-border:] = colorKey
				newTileArray[0:border,:] = colorKey
				newTileArray[-border:,:] = colorKey
				newTile = newTileArray.make_surface()
			newTile.set_colorkey(colorKey)
			tileList.append(newTile)

	return(tileList)

def parseMap(filePath, topCorner, bottomCorner, start, end, step):

	imgHashedDict = {}

	tileList = []
	mapList = []
	tileDict = {}
	numProcessedTiles = 0
	map = []		#list of tupels, x,y,tileNum
	tileSize = (bottomCorner[0] - topCorner[0], bottomCorner[1] - topCorner[1])

	mapFull, mapFullRect = load_image(filePath, (165,235,255))
	mapSize = mapFull.get_size()
	numTiles = (mapSize[0]//bottomCorner[0], mapSize[1]//bottomCorner[1])

	mapFullPixArray = pygame.PixelArray(mapFull)
	print(numTiles)
	number = start
	while number < end:
		print(str(number))
		yPos = number//(numTiles[0])
		xPos = number%(numTiles[0])
		print ( (xPos, yPos))
		xPixBeg = (xPos * bottomCorner[0]) + topCorner[0]
		xPixEnd = ((xPos+1) * bottomCorner[0]) #- 1
		yPixBeg = (yPos * bottomCorner[1]) + topCorner[1]
		yPixEnd = ((yPos+1) * bottomCorner[1]) #- 1

		newTile = pygame.Surface(tileSize)

		pygame.surfarray.blit_array(newTile, mapFullPixArray[xPixBeg:xPixEnd,yPixBeg:yPixEnd])

		retImgID = imgHashedDict.get(imageHash(newTile, tileSize), None)
		if retImgID == None:
			newTilePosition = len(tileList)
			mapList.append( (xPos, yPos, newTilePosition) )	#Note that we use the lenght before the append, which is the index after
			tileList.append(newTile)
			imgHashedDict[imageHash(newTile, tileSize)] = newTilePosition
			print("Did not find identical")
		else:
			mapList.append( (xPos, yPos, retImgID) )
			print("Found identical!")
			screen.blit(newTile, (0,0))
			pygame.display.flip()

		number += step

	return( (mapList, tileList) )

def saveTileList(tileList, savePath, topCorner, bottomCorner):
	
	tileSize = (bottomCorner[0] - topCorner[0], bottomCorner[1] - topCorner[1])

	newTileGridSize = int(math.ceil(math.sqrt(len(tileList))))
	print(str(newTileGridSize))
	newTileGrid = pygame.Surface( (newTileGridSize*tileSize[0], newTileGridSize*tileSize[1]) )
	gridPos = [0,0]

	for tile in tileList:
		newTileGrid.blit(tile, (gridPos[0]*tileSize[0], gridPos[1]*tileSize[1]) )
		
		if gridPos[0] < (newTileGridSize-1): #If we're not at the end of the row
			gridPos[0] += 1					#advance position
		else:								#If we are at then end of the row
			gridPos[0] = 0					#Reset x to 0
			gridPos[1] += 1 				#add 1 to y

	pygame.image.save(newTileGrid, savePath)

#return a list of images scaled accordingly
def scaleImageList(tileList, newDimensions):
	newTileList = []
	for tile in tileList:
		newTileList.append(pygame.transform.scale(tile, newDimensions))
	return newTileList

def scaleImageList2x(tileList):
	newTileList = []
	for tile in tileList:
		newTileList.append(pygame.transform.scale2x(tile))
	return newTileList

#Takes in filename of tile map and of the pickled map,
#returns a map dictionary and a list of tile images
def loadMap(mapImageName, mapPickleName, tileSize):
	mapTiles = parseImage(mapImageName, (0,0), tileSize, 0, -1, 1)
	mapList = pickle.load( open(mapPickleName, "rb") )
	mapDict = {}
	for mapTup in mapList:
		mapDict[(mapTup[0], mapTup[1])] = mapTup[2]
	return( (mapDict, mapTiles) )
	
def drawMap(mapDict, mapTiles, tileSize, sectionSize, sectionLocation):
	mapSection = pygame.Surface((tileSize[0]*sectionSize[0], tileSize[1]*sectionSize[1]))

	for yPos in range(sectionLocation[1], sectionLocation[1]+sectionSize[1]):
		for xPos in range(sectionLocation[0], sectionLocation[0]+sectionSize[0]):
			mapSection.blit(mapTiles[mapDict.get( (xPos, yPos), 0 )], (tileSize[0]*(xPos-sectionLocation[0]), tileSize[1]*(yPos-sectionLocation[1]) ))
	
	return(mapSection)

'''
pygame.init()
screen = pygame.display.set_mode( (1000,1000) )
pygame.display.set_caption("Convert that map!")
pygame.mouse.set_visible(1)
'''
'''
screen = pygame.display.set_mode( (1000,1000) )
pygame.display.set_caption("Convert that map!")
pygame.mouse.set_visible(1)


totalMap, totalRec = load_image("data/Pokemon-FL-Kanto.png")
totalMapArray = pygame.PixelArray(totalMap)
totalMapArray[::16,:] = (0,0,0)
totalMapArray[:,::16] = (0,0,0)
totalMapEdited = totalMapArray.make_surface()

screenPos = [0,0]
multiplier = 1
stop = False
while stop == False:
	screen.blit(totalMapEdited, screenPos)
	pygame.display.flip()
	userInput = getInput()
	if userInput == "LEFT":
		screenPos[0] -= 16*multiplier
	elif userInput == "RIGHT":
		screenPos[0] += 16*multiplier
	elif userInput == "UP":
		screenPos[1] -= 16*multiplier
	elif userInput == "DOWN":
		screenPos[1] += 16*multiplier
	elif userInput == "x":
		multiplier -= 1
	elif userInput == "z":
		multiplier += 1
	elif userInput == "QUIT" or userInput == "ESCAPE":
		stop = True
'''

'''
kantoList = parseImage("data/kantopokemon.png", (5,5), (69,69), 0, 302, 1)
johtoList = parseImage("data/johtopokemon.PNG", (5,5), (69,69), 0, 198, 1)
hoennList = parseImage("data/hoennpokemon.PNG", (5,5), (69,69), 0, 266, 1)
print(len(kantoList))
print(len(johtoList))
print(len(hoennList))
tileList = kantoList + johtoList + hoennList
saveTileList(tileList, "data/pokemon/pokemon.bmp", (5,5), (69,69))
#saveTileList(kantoList, "data/pokemon/kantoPokemon.bmp", (5,5), (69,69))
#saveTileList(johtoList, "data/pokemon/johtoPokemon.bmp", (5,5), (69,69))
#saveTileList(hoennList, "data/pokemon/hoennPokemon.bmp", (5,5), (69,69))
'''
'''
kantoMapList, kantoTileList = parseMap("data/kanto_fixed.png", (0,0), (16,16), 0, 163200, 1)
saveTileList(kantoTileList, "data/maps/kanto/kanto.bmp", (0,0), (16,16))
print(kantoMapList[:100])
pickle.dump(kantoMapList, open("data/maps/kanto/kantoMap.pickle", "wb") )
'''
'''
johtoMapList, johtoTileList = parseMap("data/Pokemon-GSC-Johto.png", (0,0), (16,16), 0, 126900, 1)
saveTileList(johtoTileList, "data/maps/johto/johto.bmp", (0,0), (16,16))
print(johtoMapList[:100])
pickle.dump(johtoMapList, open("data/maps/johto/johtoMap.pickle", "wb") )
'''
'''
hoennMapList, hoennTileList = parseMap("data/Pokemon-RS-Hoenn.png", (0,0), (16,16), 0, 304000, 1)
saveTileList(hoennTileList, "data/maps/hoenn/hoenn.bmp", (0,0), (16,16))
print(hoennMapList[:100])
pickle.dump(hoennMapList, open("data/maps/hoenn/hoennMap.pickle", "wb") )
'''
'''
drawMap("data/maps/hoenn/hoenn.bmp", "data/maps/hoenn/hoennMap.pickle", (16,16) )
drawMap("data/maps/johto/johto.bmp", "data/maps/johto/johtoMap.pickle", (16,16) )
drawMap("data/maps/kanto/kanto.bmp", "data/maps/kanto/kantoMap.pickle", (16,16) )
'''