from mapEdit import *

#init the pygame stuff
pygame.init()

pygame.key.set_repeat(1,0)
clock = pygame.time.Clock()


loadTileSize = (16,16)
tileSize = (loadTileSize[0]*2,loadTileSize[1]*2)	#Maps are stored at half res, have to be scaled up

frameDelay = 20

#We have a big screen
screenSizeMultipler = 2
screenSize = (480*screenSizeMultipler,288*screenSizeMultipler)
sectionSize = ( (screenSize[0]//tileSize[0]+1), (screenSize[1]//tileSize[1]+1) )	#Adjust the tile section size to the screen size, so that it covers the entire screen
screen = pygame.display.set_mode( screenSize )
gray = pygame.Surface(screenSize)													#This grey is our background which shouldn't really ever show through
gray.fill( (185,200,254) )
pygame.display.set_caption("Pokeon Universal!")


#This function takes in a number and advances it one toward zero, returning the new number and the number it subtracted to get it there 10 -> (9, 1), -10 -> (-9,-1)
def incrementTo0(number):
	if number == 0:
		return (0,0)
	elif number > 0:
		return (number-1, 1)
	else:
		return(number+1, -1)

#This is the person class, which is used by both the player and NPCs. Holds info about the person and has the move and draw functionality
class Person:
	def __init__(self, initTileList, initPos):			#Init with image list (for drawing the charecter) and init to some initial position
		self.position = [0,0]
		self.position[0], self.position[1] = initPos #Assign the position list the values from the initPosition tupel/list
		self.previousPosition = [0,0]
		self.previousPosition[0], self.previousPosition[1] = self.position
		self.tileList = initTileList
		self.pokemon = []
		self.invatory = []
		
		self._movingPos = [0,0]			#This variable tells us how far we have to move in each direction. Each time we move a tile, it is advanced toward 0 by 1
		self.ownPixelOffset = [0,0]		#This variable stores the current offset in pixels that we will draw to. It will be multiplied by the number/stage of the subframe drawing to advance
		self._inbetweanMove = False		#Inbetween move is a bool that tells us if we're still moving

		self.faceingDirection = (0,-1)

	#This function tells the character how far to move, starting the move
	def go(self, posTup):
		self._movingPos[0], self._movingPos[1] = posTup	#Assign our movement variables to the input
		self._inbetweanMove = True

	#This function gets the index into the tile list approite for our direction and drawingStage
	def getFrameIndex(self, drawingStage):
		if self.faceingDirection == (0,-1):
			if self._inbetweanMove:				#Only use the other move frame's for each drawingStage if we are moving
				if drawingStage == 1:
					return(2)
				elif drawingStage == 2:
					return(0)
				elif drawingStage == 3:
					return(10)
			return(0)							#Must be drawingStage 0
		elif self.faceingDirection == (0,1):
			if self._inbetweanMove:				#Only use the other move frame's for each drawingStage if we are moving
				if drawingStage == 1:
					return(8)
				elif drawingStage == 2:
					return(5)
				elif drawingStage == 3:
					return(11)
			return(5)							#Must be drawingStage 0
		elif self.faceingDirection == (-1,0):
			if self._inbetweanMove:				#Only use the other move frame's for each drawingStage if we are moving
				if drawingStage == 1:
					return(3)
				elif drawingStage == 2:
					return(6)
				elif drawingStage == 3:
					return(9)
			return(6)							#Must be drawingStage 0
		elif self.faceingDirection == (1,0):
			if self._inbetweanMove:				#Only use the other move frame's for each drawingStage if we are moving
				if drawingStage == 1:
					return(4)
				elif drawingStage == 2:
					return(1)
				elif drawingStage == 3:
					return(7)
			return(1)							#Must be drawingStage 0

		return(0)

	#This function draws the character. It takes in quite a few parameters for drawing, including drawingStage, which is the stage of sub-major-frame drawing that we are doing for smooth movement. 0 is major frame
	def draw(self, surface, sectionPos, sectionSize, tileSize, sectionPixelOffset, drawingStage):
	
		if drawingStage == 1:		#If this is the first sub-major-frame stage, set up our movement stuff for the next sub-major frames
			if self._inbetweanMove:	#If we're moving
				self._movingPos[0], incXAmmount = incrementTo0(self._movingPos[0])										#Move our movement ammounts closer to 0 and get what direction we're moving
				self._movingPos[1], incYAmmount = incrementTo0(self._movingPos[1])
				self.faceingDirection = (incXAmmount, incYAmmount)														#The direction we're going is equal to the increment for the next position
				self.position[0], self.position[1] = (self.position[0]+incXAmmount) , (self.position[1]+incYAmmount)	#Change the current position accordingly
			
			self.ownPixelOffset = ( ( self.position[0] - self.previousPosition[0])*(tileSize[0]//4)), ((self.position[1] - self.previousPosition[1])*(tileSize[1]//4)  )	#Calculate the offset for the sub-major frames. (will be multiplied by the drawingStage)

		if drawingStage != 0:	#If we're in a sub-major frame

			#If we're on or moving on screen. (we check with the position we're moving to, not the position we're moving from)
			if (self.position[0] >= sectionPos[0]) and (self.position[0] <= (sectionPos[0]+ sectionSize[0])) and (self.position[1] >= sectionPos[1]) and (self.position[1] <= (sectionPos[1]+ sectionSize[1])):
				#Calculate where on the screen we should draw
				blitPos = ( (tileSize[0]*(self.previousPosition[0]-sectionPos[0])) + sectionPixelOffset[0] + (self.ownPixelOffset[0]*drawingStage), (tileSize[1]*(self.previousPosition[1]-sectionPos[1])) + sectionPixelOffset[1] + (self.ownPixelOffset[1]*drawingStage) )
				surface.blit(self.tileList[self.getFrameIndex(drawingStage)], blitPos)

		else: #If this is a major frame, i.e. drawing stage 0

			if self._movingPos[0] == 0 and self._movingPos[1] == 0:	#If that was the last stage of the move, then set our moving status to False
				self._inbetweanMove = False		
			self.previousPosition[0], self.previousPosition[1] = self.position	#reset our previousPosition to our current position
			#If our position is within the section, found by sectionPos+sectionSize, then we draw ourselves
			if (self.position[0] >= sectionPos[0]) and (self.position[0] <= (sectionPos[0]+ sectionSize[0])) and (self.position[1] >= sectionPos[1]) and (self.position[1] <= (sectionPos[1]+ sectionSize[1])):
				#Calculate where on the screen we should draw
				blitPos = ( (tileSize[0]*(self.position[0]-sectionPos[0])) + sectionPixelOffset[0] + (self.ownPixelOffset[0]*drawingStage), (tileSize[1]*(self.position[1]-sectionPos[1])) + sectionPixelOffset[1] + (self.ownPixelOffset[1]*drawingStage) )
				surface.blit(self.tileList[self.getFrameIndex(drawingStage)], blitPos)
			
		

def goMenu():
	screen.blit(gray, (0,0))		#Draw our gray background
	if pygame.font:					#Only if fonts are enabled
		font = pygame.font.Font(None, 68)										#Font size
		text = font.render("Welcome to Pokeon Universal!", 1, (10, 10, 10))		#Font message
		textpos = text.get_rect(centerx=screen.get_width()//2)					#Center of screen
		screen.blit(text, textpos)												#Draw

		font = pygame.font.Font(None, 48)										#Font size

		text = font.render("Play (H)oenn!", 1, (10, 10, 10))					#Each of these are the same, but drawn to the first 1/3 of the screen
		textpos = text.get_rect(centerx=screen.get_width()//3)
		screen.blit(text, (textpos[0], textpos[1]+100))

		text = font.render("Play (J)ohto!", 1, (10, 10, 10))
		textpos = text.get_rect(centerx=screen.get_width()//3)
		screen.blit(text, (textpos[0], textpos[1]+200) )

		text = font.render("Play (K)anto!", 1, (10, 10, 10))
		textpos = text.get_rect(centerx=screen.get_width()//3)
		screen.blit(text, (textpos[0], textpos[1]+300))

		text = font.render("or (Q)uit!", 1, (10, 10, 10))
		textpos = text.get_rect(centerx=screen.get_width()//3)
		screen.blit(text, (textpos[0], textpos[1]+400))


	pygame.display.flip()			#Flip our display

	while True:						#Load the appropriate map
		userInput = getInput()
		if userInput == "h":
			goOverworld("h")
			break

		if userInput == "j":
			goOverworld("j")
			break

		if userInput == "k":
			goOverworld("k")
			break

		if userInput == "quit" or userInput == "escape" or userInput == "q":
			break
			


def goOverworld(world):
	if world == "h":		#Load the appropriate map
		mapDict, tileList = loadMap("data/maps/hoenn/hoenn.bmp", "data/maps/hoenn/hoennMap.pickle", loadTileSize)
	if world == "k":
		mapDict, tileList = loadMap("data/maps/kanto/kanto.bmp", "data/maps/kanto/kantoMap.pickle", loadTileSize)
	if world == "j":
		mapDict, tileList = loadMap("data/maps/johto/johto.bmp", "data/maps/johto/johtoMap.pickle", loadTileSize)
	
	tileList = scaleImageList2x(tileList)	#Scale up the map's tile list because it is stored at half-rez. The function we use does some simple interpoliation.

	sectionPos = (0,0)			#init some variables
	previousSectionPos = [0,0]
	screenPos = [0,0]
	multiplier = 1

	playerCharacter = Person(parseGridImage("data/npcoverworldsDP.png", (0,0), (32,32), (12,20), (15,24), 1), (10,10))	#create our player character
	NPCList = [Person(parseGridImage("data/npcoverworldsDP.png", (0,0), (32,32), (0,0), (3,4), 1), (10,10))]	#create a random person

	NPCList[0].go( (20,20) )

	stop = False
	while stop == False:		#Go until we quit

		#Find our screen position from the player position
		sectionPos = (playerCharacter.position[0] - (sectionSize[0]//2 - 1), playerCharacter.position[1] - (sectionSize[1]//2 - 1))
	
		#first draw the old position (sligtly bigger) offset
		oldMap = drawMap(mapDict, tileList, tileSize, (sectionSize[0]+2, sectionSize[1]+2) , (previousSectionPos[0]-1, previousSectionPos[1]-1) ) 	#Note we draw 2 bigger, but move the orgin up and to the left, so one tile buffer on every side
		pixelOffset = ( -( sectionPos[0] - previousSectionPos[0])*(tileSize[0]//4)), -((sectionPos[1] - previousSectionPos[1])*(tileSize[1]//4) ) 	#Calculate the offset
		
		#now we draw four times, advancing the interpoliated sub-frame posistion each time
		for i in range(1,4):
			screen.blit(gray, (0,0) )
			screen.blit(oldMap, (pixelOffset[0]*i-tileSize[0], pixelOffset[1]*i-tileSize[1]) ) #The -tileSize are to take into account the extra border area drawn above
			
			#Note we use previousSectionPos, because we've updated sectionPos, but are still using the old map to draw, so since we pass in the map's pixelOffset, we also pass in the old map position
			playerCharacter.draw(screen, previousSectionPos, sectionSize, tileSize, (pixelOffset[0]*i, pixelOffset[1]*i), i)
			for npc in NPCList:
				npc.draw(screen, previousSectionPos, sectionSize, tileSize, (pixelOffset[0]*i, pixelOffset[1]*i), i)

			pygame.display.flip()
	
			#print("SectionPos", sectionPos, "previousSectionPos", previousSectionPos, "PixelOffset!", (pixelOffset[0]*i, pixelOffset[1]*i))
			pygame.time.wait(frameDelay)
	
		#Then the new position
		previousSectionPos = ( sectionPos[0], sectionPos[1] )	#Reset previousSectionPosition to the current sectionPos
		
		screen.blit(gray, (0,0) ) #Background
		screen.blit(drawMap(mapDict, tileList, tileSize, sectionSize, sectionPos), (0,0))	#Draw the new map

		playerCharacter.draw(screen, sectionPos, sectionSize, tileSize, (0,0), 0)					#Draw the person with the new position
		for npc in NPCList:
			npc.draw(screen, sectionPos, sectionSize, tileSize, (0,0), 0)

		pygame.display.flip()
		pygame.time.wait(frameDelay-5)
	

		userInput = getInput(15,5)				#Get user input and update variables accordingly
												#We look for input for 15 milliseconds, returing to processor for 5 every time we look
		if userInput != None:

			if userInput == "left":
				playerCharacter.go( (-1,0) )
			elif userInput == "right":
				playerCharacter.go( (1,0) )
			elif userInput == "up":
				playerCharacter.go( (0,-1) )
			elif userInput == "down":
				playerCharacter.go( (0,1) )

			elif userInput == "x":
				multiplier -= 1
			elif userInput == "z":
				multiplier += 1
			elif userInput == "x":
				multiplier -= 1


			elif userInput == "quit" or userInput == "escape":
				stop = True


goMenu() #Run our menu to start