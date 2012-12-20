#Person.py

from imageAndMapUtil import *

#This is the person class, which is used by both the player and NPCs. Holds info about the person and has the move and draw functionality
class Person:
	def __init__(self, initTileList, initPos):			#Init with image list (for drawing the charecter) and init to some initial position
		self.position = [0,0]
		self.position[0], self.position[1] = initPos #Assign the position list the values from the initPosition tupel/list
		self.previousPosition = [0,0]
		self.previousPosition[0], self.previousPosition[1] = self.position
		self.tileList = initTileList
		self.monsters = []
		self.inventory = []
		
		self._movingPos = [0,0]			#This variable tells us how far we have to move in each direction. Each time we move a tile, it is advanced toward 0 by 1
		self.ownPixelOffset = [0,0]		#This variable stores the current offset in pixels that we will draw to. It will be multiplied by the number/stage of the subframe drawing to advance
		self._inbetweanMove = False		#Inbetween move is a bool that tells us if we're still moving

		self.faceingDirection = (0,-1)
		self.whichStep = 0


	#getAbleMonster() returns the first able monster we have, or 0 if we don't
	def getAbleMonster(self):
		for monster in self.monsters:
			if monster.stats[0] > 0:
				return(monster)
		return(0)
	#This function tells the character how far to move, starting the move
	def go(self, posTup):
		self._movingPos[0], self._movingPos[1] = posTup	#Assign our movement variables to the input
		self._inbetweanMove = True

	#This function gets the index into the tile list approite for our direction and self.whichStep
	def getFrameIndex(self):
		if self.faceingDirection == (0,-1):
			if self._inbetweanMove:				#Only use the other move frame's for each self.whichStep if we are moving
				if self.whichStep == 1:
					return(2)
				elif self.whichStep == 2:
					return(0)
				elif self.whichStep == 3:
					return(10)
			return(0)							#Must be self.whichStep 0
		elif self.faceingDirection == (0,1):
			if self._inbetweanMove:				#Only use the other move frame's for each self.whichStep if we are moving
				if self.whichStep == 1:
					return(8)
				elif self.whichStep == 2:
					return(5)
				elif self.whichStep == 3:
					return(11)
			return(5)							#Must be self.whichStep 0
		elif self.faceingDirection == (-1,0):
			if self._inbetweanMove:				#Only use the other move frame's for each self.whichStep if we are moving
				if self.whichStep == 1:
					return(3)
				elif self.whichStep == 2:
					return(6)
				elif self.whichStep == 3:
					return(9)
			return(6)							#Must be self.whichStep 0
		elif self.faceingDirection == (1,0):
			if self._inbetweanMove:				#Only use the other move frame's for each self.whichStep if we are moving
				if self.whichStep == 1:
					return(4)
				elif self.whichStep == 2:
					return(1)
				elif self.whichStep == 3:
					return(7)
			return(1)							#Must be self.whichStep 0

		return(0)

	#This function draws the character. It takes in quite a few parameters for drawing, including drawingStage, which is the stage of sub-major-frame drawing that we are doing for smooth movement. 0 is major frame
	def draw(self, surface, mapDict, sectionPos, sectionSize, tileSize, sectionPixelOffset, drawingStage):
	
		if drawingStage == 1:		#If this is the first sub-major-frame stage, set up our movement stuff for the next sub-major frames
			if self._inbetweanMove:	#If we're moving
				self._movingPos[0], incXAmmount = incrementTo0(self._movingPos[0])										#Move our movement ammounts closer to 0 and get what direction we're moving
				self._movingPos[1], incYAmmount = incrementTo0(self._movingPos[1])
				self.faceingDirection = (incXAmmount, incYAmmount)														#The direction we're going is equal to the increment for the next position
				if mapDict[(self.position[0]+incXAmmount) , (self.position[1]+incYAmmount)][1] == 2: 					#If the new position is ground
					self.position[0], self.position[1] = (self.position[0]+incXAmmount) , (self.position[1]+incYAmmount)	#Change the current position accordingly
				else:
					print("Not walkable!")
			
			self.ownPixelOffset = ( ( self.position[0] - self.previousPosition[0])*(tileSize[0]//4)), ((self.position[1] - self.previousPosition[1])*(tileSize[1]//4)  )	#Calculate the offset for the sub-major frames. (will be multiplied by the drawingStage)

		if drawingStage != 0:	#If we're in a sub-major frame

			#If we're on or moving on screen. (we check with the position we're moving to, not the position we're moving from)
			if (self.position[0] >= sectionPos[0]) and (self.position[0] <= (sectionPos[0]+ sectionSize[0])) and (self.position[1] >= sectionPos[1]) and (self.position[1] <= (sectionPos[1]+ sectionSize[1])):
				#Calculate where on the screen we should draw
				blitPos = ( (tileSize[0]*(self.previousPosition[0]-sectionPos[0])) + sectionPixelOffset[0] + (self.ownPixelOffset[0]*drawingStage), (tileSize[1]*(self.previousPosition[1]-sectionPos[1])) + sectionPixelOffset[1] + (self.ownPixelOffset[1]*drawingStage) )
				surface.blit(self.tileList[self.getFrameIndex()], blitPos)

		else: #If this is a major frame, i.e. drawing stage 0

			if self._movingPos[0] == 0 and self._movingPos[1] == 0:	#If that was the last stage of the move, then set our moving status to False
				if self._inbetweanMove == False:						#If we're not moving
					self.whichStep = 0									#Reset the which step counter
				else:
					self.whichStep += 1 								#Go to next step, if over 3 go back to 0
					if self.whichStep > 3:
						self.whichStep = 0
				
				self._inbetweanMove = False								#set moving to false b/c we're done with this go. If a go happens next frame, it will be changed to true before we get back to the whichStep, so it still works


			self.previousPosition[0], self.previousPosition[1] = self.position	#reset our previousPosition to our current position
			#If our position is within the section, found by sectionPos+sectionSize, then we draw ourselves
			if (self.position[0] >= sectionPos[0]) and (self.position[0] <= (sectionPos[0]+ sectionSize[0])) and (self.position[1] >= sectionPos[1]) and (self.position[1] <= (sectionPos[1]+ sectionSize[1])):
				#Calculate where on the screen we should draw
				blitPos = ( (tileSize[0]*(self.position[0]-sectionPos[0])) + sectionPixelOffset[0] + (self.ownPixelOffset[0]*drawingStage), (tileSize[1]*(self.position[1]-sectionPos[1])) + sectionPixelOffset[1] + (self.ownPixelOffset[1]*drawingStage) )
				surface.blit(self.tileList[self.getFrameIndex()], blitPos)
