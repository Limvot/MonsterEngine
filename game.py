from imageAndMapUtil import *
from person import *
#from monster import *

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

	personTileStart = (0,0)
	personTileEnd = (3,4)
	bigGrid = (6,6)
	personTileBegin = personTileEnd[0]*bigGrid[0], personTileEnd[1]*bigGrid[1]
	personTileEnd = personTileEnd[0]*(bigGrid[0]+1), personTileEnd[1]*(bigGrid[1]+1)

	#Make our player character. Use the list of images loaded from parseGridImages(name, tileStart, tileEnd, beginTile, endTile, step, colorkey, border)
	playerCharacter = Person(parseGridImage("data/npcoverworldsDP.png", (0,0), (32,32), personTileBegin, personTileEnd, 1, -1, 1), (10,100))	#create our player character
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
			playerCharacter.draw(screen, mapDict, previousSectionPos, sectionSize, tileSize, (pixelOffset[0]*i, pixelOffset[1]*i), i)
			for npc in NPCList:
				npc.draw(screen, mapDict, previousSectionPos, sectionSize, tileSize, (pixelOffset[0]*i, pixelOffset[1]*i), i)

			pygame.display.flip()
	
			#print("SectionPos", sectionPos, "previousSectionPos", previousSectionPos, "PixelOffset!", (pixelOffset[0]*i, pixelOffset[1]*i))
			pygame.time.wait(frameDelay)
	
		#Then the new position
		previousSectionPos = ( sectionPos[0], sectionPos[1] )	#Reset previousSectionPosition to the current sectionPos
		
		screen.blit(gray, (0,0) ) #Background
		screen.blit(drawMap(mapDict, tileList, tileSize, sectionSize, sectionPos), (0,0))	#Draw the new map

		playerCharacter.draw(screen, mapDict, sectionPos, sectionSize, tileSize, (0,0), 0)					#Draw the person with the new position
		for npc in NPCList:
			npc.draw(screen, mapDict, sectionPos, sectionSize, tileSize, (0,0), 0)

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

def battle(trainer1, trainer2):
	#Battle state stuff
	weWon = True

	#Get our first non-fainted pokemon
	ourMonster = trainer1.getAbleMonster()
	opponentMonster = trainer2.getAbleMonster()
	while opponentMonster not == 0:
		fight(ourMonster, opponentMonster)
		if ourMonster.battleStats[0] <= 1:
			ourMonster = trainer1.getAbleMonster()
			if ourMonster == 0:
				weWon = False
		#Whether we win or lose that fight, update our opponent monster. If the current monster can still fight, it will return it.
		opponentMonster = trainer2.getAbleMonster()

		
	for monster in trainer1.monsters:
		monster.updateLevel()
	return(weWon)

#Returns 1 if we win, -1 if we lose
def fight(ourMonster, opponentMonster):
	ourMonster.setupBattleStats()
	opponentMonster.setupBattleStats()

	while opponentMonster.battleStats[0] > 0:
		if ourMonster.battleStats <= 0:
			ourMonster.afterBattleStats()
			opponentMonster.afterBattleStats()
			return(-1)
		if ourMonster.battleStats[5] >= opponentMonster.battleStats[5]:
			whichAttack = int(getInput()[1])
			opponentMonster.battleStats[0] -= calcAttack(ourMonster, ourMonster.attacks[whichAttack], opponentMonster)
		else:
			ourMonster.battleStats[0] -= calcAttack(opponentMonster, random.choice(opponentMonster.attacks), ourMonster)

	ourMonster.addExperience(opponentMonster)
	ourMonster.afterBattleStats()
	opponentMonster.afterBattleStats()
	return(1)



goMenu() #Run our menu to start