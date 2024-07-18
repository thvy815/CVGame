import pygame
import sys
import cv2
from cvzone.HandTrackingModule import HandDetector
import random
from pygame import mixer
import time

width = 1366
height = 768

# opencv code
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Hand Detector
detector = HandDetector(maxHands=1, detectionCon=0.8)

# Initialize the pygame
pygame.init()

# background sounds
mixer.music.load('music/background.mp3')
mixer.music.play(loops=-1)

closedHand_sound = mixer.Sound('music/slap.mp3')
catching_sound = mixer.Sound('music/catching_sound.wav')

# Define the screen
screen = pygame.display.set_mode((width, height))

# Timer
clock = pygame.time.Clock()
currentTime = 1

# Title and Icon
pygame.display.set_caption("Catch Ball")
icon = pygame.image.load('images/ball_32_1.png').convert_alpha()
pygame.display.set_icon(icon)
backgroundImg = pygame.image.load('images/TennisBack.png').convert()

# Player
playerPosition = [370, 480]
playerMovement = [0, 0]
x = (width/2 - 64) 
y = (height/2 - 64) 
openHandImg = pygame.image.load('images/openHand.png').convert_alpha()
openHandImg = pygame.transform.scale(openHandImg, (128, 128))
openHand_rect = openHandImg.get_rect(topleft=(x, y))

closedHandImg = pygame.image.load('images/closedHand.png').convert_alpha()
closedHandImg = pygame.transform.scale(closedHandImg, (128, 128))
closedHand_rect = closedHandImg.get_rect(topleft=(x, y))

# Insects
InsectImg = []
InsectX = []
InsectY = []
insect_rect = []
insectMoveX = []
insectMoveY = []
numberOfInsects = 10
for i in range(numberOfInsects):
    InsectX.append(random.randint(0, 1366))
    InsectY.append(random.randint(0, 768))
    InsectImg.append(pygame.image.load('images/ball_32_1.png').convert_alpha())
    #InsectImg.append(pygame.transform.scale(InsectImg, (32, 32)))
    insect_rect.append(InsectImg[i].get_rect(topleft=(InsectX[i], InsectY[i])))
    insectMoveX.append(10)
    insectMoveY.append(8)

## Game Texts
font = pygame.font.Font('freesansbold.ttf', 32)

 # Score Text
score_value = 0
def show_score():
    score = font.render("Score : " + str(score_value), True, (0, 0, 0))
    screen.blit(score, (100, 50))

 # Time Text
countdown_time = 60
def show_timer():
    timer = font.render("Time: " + str(int(currentTime)), True, (0, 0, 0))
    screen.blit(timer, (1120, 50))
    
 # Menu
menu_options = ['Start Game', 'Quit']
menu_state = 'main_menu'
game_state = 'not_started'

indexes_for_closed_fingers = [8, 12, 16, 20]
########## Game Loop ##########
catch_insect_with_openHand = False
fingers = [0, 0, 0, 0]
while True:
    # Game code
    screen.blit(backgroundImg, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if menu_state == 'main_menu':
                 # Start Game
                if event.pos[0] > width/2 - 100 and event.pos[0] < width/2 + 100 and event.pos[1] > height/2 - 50 and event.pos[1] < height/2:
                    menu_state = 'game'
                    game_state = 'started'
                    start_time = time.time()
                    score_value = 0
                 # Quit
                elif event.pos[0] > width/2 - 100 and event.pos[0] < width/2 + 100 and event.pos[1] > height/2 and event.pos[1] < height/2 + 50:
                    cap.release()
                    cv2.destroyAllWindows()
                    pygame.quit()
                    sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and game_state == 'finished':
                menu_state = 'main_menu'
                game_state = 'not_started'
    
    # showing menu
    if menu_state == 'main_menu':
        title = font.render('CATCH BALL', True, (0, 0, 0))
        screen.blit(title, (width/2 - title.get_width()/2, height/2 - 100))
        for i, option in enumerate(menu_options):
            text = font.render(option, True, (0, 0, 0))
            screen.blit(text, (width/2 - title.get_width()/2, height/2 - 25 + i * 50))    
    elif menu_state == 'game':
        if game_state == 'started':  

            # showing texts
            show_score()
            currentTime = countdown_time - (time.time() - start_time)
            if currentTime <= 0: 
                game_state = 'finished'
            else:
                show_timer()

                # opencv code
                success, frame = cap.read()

                # Mediapipe code for hand detection and Landmarks
                hands, frame = detector.findHands(frame)

                # Landmarks value - (x,y,z) * 21
                if hands:
                    #Get the first hand detected
                    lmList = hands[0]
                    positionOfTheHand = lmList['lmList']
                    openHand_rect.left = width - (positionOfTheHand[9][0] - 200) * 1.5
                    openHand_rect.top = (positionOfTheHand[9][1] - 200) * 1.5
                    closedHand_rect.left = width - (positionOfTheHand[9][0] - 200) * 1.5
                    closedHand_rect.top = (positionOfTheHand[9][1] - 200) * 1.5

                    ## open or closed hand
                    hand_is_closed = 0 #for playing the sound once when hand is closed
                    for index in range(0, 4):
                        if positionOfTheHand[indexes_for_closed_fingers[index]][1] > positionOfTheHand[indexes_for_closed_fingers[index] - 2][1]:
                            fingers[index] = 1
                        else:
                            fingers[index] = 0
                        if fingers[0]*fingers[1]*fingers[2]*fingers[3]:
                            # playing close hand sound
                            if hand_is_closed and catch_insect_with_openHand == False:
                                closedHand_sound.play()
                            hand_is_closed = 0
                            screen.blit(closedHandImg, closedHand_rect)
                            # detect catching
                            for iteration in range(numberOfInsects):
                                if openHand_rect.colliderect(insect_rect[iteration]) and catch_insect_with_openHand:
                                    score_value += 1
                                    catching_sound.play()
                                    catch_insect_with_openHand = False
                                    insect_rect[iteration] = InsectImg[iteration].get_rect(topleft=(random.randint(0, 1366), random.randint(0, 768)))

                            catch_insect_with_openHand = False
                        else:
                            screen.blit(openHandImg, openHand_rect)
                            hand_is_closed = 1
                            for iterate in range(numberOfInsects):
                                if openHand_rect.colliderect(insect_rect[iterate]):
                                    catch_insect_with_openHand = True
        elif game_state == 'finished':
            timeOver_font = pygame.font.Font('freesansbold.ttf', 100)
            timeOver = timeOver_font.render("Time Over!", True, (255, 0, 0))
            screen.blit(timeOver, (width/2 - 300, height/2 - 30))
            show_score()
            pygame.display.flip()
            
    # Opencv Screen
    #frame = cv2.resize(frame, (0, 0), None, 0.3, 0.3)
    # It's something optional If you don't want to see your hand, omit this line of code
    #cv2.imshow("webcam", frame)

    # Game screen
    ## placing Insects

    ## moving Insects
    for i in range(numberOfInsects):
            # moving X
        insect_rect[i].right += insectMoveX[i] 
        if insect_rect[i].right <= 16:
            insectMoveX[i] += 10 
        elif insect_rect[i].right >= width:
            insectMoveX[i] -= 10 

            # moving Y
        insect_rect[i].top += insectMoveY[i] 
        if insect_rect[i].top <= 0:
            insectMoveY[i] += 8 
        elif insect_rect[i].top >= height-32:
            insectMoveY[i] -= 8 
        screen.blit(InsectImg[i], insect_rect[i])

    # display update
    pygame.display.update()
    clock.tick(60)
    