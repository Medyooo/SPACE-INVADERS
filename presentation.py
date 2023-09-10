
# SPACE INVADERS
# FLORIAN HOUPIER
# MOHAMMED LARBI EI BAIDI
# L2 INFORMATIQUE GROUPE 3

# IMPORTS
try:
    import tkinter as tk
    import tkinter.messagebox as tkMessageBox
except:
    import Tkinter as tk
    import tkMessageBox

# ADDED IMPORTS:
from PIL import Image, ImageTk
#from playsound import playsound
#import pyglet, os
#pyglet.font.add_file('ARCADECLASSIC.ttf')
#pyglet.font.add_file('Arial.ttf')
import os
import time
import random
import json


# INITIALIZATION:
class Constantes():
    # Main window dimensions
    HEIGHT_WINDOW = 600
    WIDTH_WINDOW = 800
    # Game window dimensions
    HEIGHT_GAME_WINDOW = 472
    WIDTH_GAME_WINDOW = 720
    # Starting position of player
    POS_PLAYER_START_X = WIDTH_GAME_WINDOW/2
    POS_PLAYER_START_Y = HEIGHT_GAME_WINDOW-80
    # Defender size
    HEIGHT_DEFENDER = 60
    WIDTH_DEFENDER = 60
    # Alien size
    HEIGHT_ALIEN = 30
    WIDTH_ALIEN = 30
    # Score:
    SCORE = 0
    HIGHEST_SCORE = 0
    # Game Over State:
    GameOverState = 0

# Alien class to create alien object
class Alien(object):

    def __init__(self):
        self.id = None
        self.alive = True

    # Creating alien on the canvas
    def install_in(self, canvas, x, y, image):
        self.x = x
        self.y = y
        self.canvas = canvas
        self.image = image
        # Getting image and resizing
        image_alien = Image.open(self.image)
        resized_image = image_alien.resize((Constantes.WIDTH_ALIEN, Constantes.HEIGHT_ALIEN))
        self.img = ImageTk.PhotoImage(resized_image)
        # Install alien image on canvas
        self.id = self.canvas.create_image(x+Constantes.WIDTH_ALIEN/2, y+Constantes.HEIGHT_ALIEN/2, image=self.img)

    # Moving alien image on the canvas
    def move_in(self, canvas, dx, dy):
        self.canvas = canvas
        self.dx = dx
        self.dy = dy
        self.canvas.move(self.id, self.dx, self.dy)

    # Managing case Alien object is touched by bullet
    def touched_by(self, canvas, projectile):
        self.canvas = canvas
        self.projectile = projectile
        # Getting bbox coordinates of Alien and Bullet
        coord_alien_bbox = self.canvas.bbox(self.id)
        coord_projectile_bbox = self.canvas.bbox(self.projectile)
        # To know if bullet touched Alien
        if (coord_projectile_bbox[2]<coord_alien_bbox[2]):
            if (coord_alien_bbox[1]<=coord_projectile_bbox[1]<=coord_alien_bbox[3]):
                # if Alien is touched, then delete Alien, delete Projectile, update score
                self.canvas.delete(self.id)
                self.alive = False
                self.canvas.delete(self.projectile)
                Constantes.SCORE = Constantes.SCORE + 100
                del self

# Fleet class to create a fleet of Alien objects
class Fleet(object):

    def __init__(self):
        # Alien matrix
        self.alien_lines = 5
        self.alien_columns = 10
        self.fleet_size = self.alien_lines * self.alien_columns
        self.aliens_fleet = []
        self.nb_alien_types = 4

        self.direction = "right" # default starting direction
        self.y_alien = 0

    def install_in(self, canvas):
        self.canvas = canvas
        # Starting position of Alien matrix
        self.x = 0
        self.y = 50
        # Position of Aliens matrix
        self.aliens_matrix_left_side = 0
        self.aliens_matrix_right_side = self.x + Constantes.WIDTH_ALIEN*self.alien_columns
        self.aliens_matrix_bottom = self.y + Constantes.HEIGHT_ALIEN*self.alien_lines
        # Creating fleet of Alien objects
        for i in range(0, self.fleet_size):
            self.aliens_fleet.append(Alien())
        # Getting Aliens images on canvas
        nb_aliens_created = 0
        alien_type = random.randint(1, self.nb_alien_types)
        for alien in self.aliens_fleet:
            if nb_aliens_created == self.alien_columns:
                # To go next line, go down of an Alien image size
                self.y = self.y + Constantes.HEIGHT_ALIEN
                self.x = 0
                nb_aliens_created = 0
                # May be another alien type by random
                alien_type = random.randint(1, self.nb_alien_types)
            # Get a random image of alien type each line
            img_name = 'alien'+str(alien_type)+'.png'


            alien.install_in(self.canvas, self.x, self.y, img_name)
            self.x = self.x + Constantes.WIDTH_ALIEN
            nb_aliens_created = nb_aliens_created+1

    # Moving all the Fleet matrice at once
    def move_in(self, canvas):
        self.canvas = canvas
        self.canvas_width = int(canvas.cget("width"))
        # Saving direction
        previous_direction = self.direction
        for alien in self.aliens_fleet:
            if self.aliens_matrix_right_side>self.canvas_width:
                # if the right side of the matrix touch the side of the screen, going left
                self.direction = "left"
            if self.aliens_matrix_left_side<0:
                # if the left side of the matrix touch the side of the screen, going right
                self.direction = "right"
            if self.direction=="left":
                alien.move_in(self.canvas, -20, self.y_alien)
            if self.direction=="right":
                alien.move_in(self.canvas, 20, self.y_alien)
        # Compare previous direction and after direction
        # If direction changed, moving all Aliens down
        if previous_direction!=self.direction:
            self.y_alien = 20
            self.aliens_matrix_bottom = self.aliens_matrix_bottom + 20
        if previous_direction==self.direction:
            self.y_alien = 0
        # Update the position of the matrix
        if self.direction=="left":
            self.aliens_matrix_left_side = self.aliens_matrix_left_side-20
            self.aliens_matrix_right_side = self.aliens_matrix_right_side-20
        if self.direction=="right":
            self.aliens_matrix_left_side = self.aliens_matrix_left_side+20
            self.aliens_matrix_right_side = self.aliens_matrix_right_side+20

    # Checking if Alien object in Fleet is touched by bullet
    def manage_touched_aliens_by(self, canvas, defender):
        self.canvas = canvas
        self.defender = defender
        for alien in self.aliens_fleet:
            if alien.alive == True:
                alien.touched_by(self.canvas, self.defender)
                if self.canvas.bbox(self.defender) == None:
                    # In case the Bullet object have been destroyed, stop the loop
                    break
            # If Alien object is destroyed, updating the aliens_fleet list
            if alien.alive == False:
                self.aliens_fleet.remove(alien)

# Class to create and manage the Bullet shooted
class Bullet(object):

    def __init__(self,shooter):
        self.radius = 5
        self.color = "red"
        self.speed = 4
        self.id = None
        self.shooter = shooter

    def install_in(self, canvas):
        self.canvas = canvas
        defender_coords = self.canvas.coords(self.shooter.id)
        x0 = defender_coords[0]-self.radius
        y0 = defender_coords[1]-self.radius
        x1 = defender_coords[0]+self.radius
        y1 = defender_coords[1]+self.radius
        self.id = self.canvas.create_oval(x0,y0,x1,y1, fill=self.color)

    def move_in(self, canvas):
        self.canvas = canvas
        self.canvas.move(self.id, 0, -self.speed)

# Class to create and manage the Defender object
class Defender(object):

    def __init__(self):
        self.width = Constantes.WIDTH_DEFENDER
        self.height = Constantes.HEIGHT_DEFENDER
        image_defender = Image.open('ship.png')
        resized_image_defender = image_defender.resize((self.width, self.height))
        self.image = ImageTk.PhotoImage(resized_image_defender)
        self.move_delta = 20
        self.id = None
        self.max_fired_bullets = 8
        self.fired_bullets = []

    # Create Defender image on canvas
    def install_in(self, canvas):
        self.canvas = canvas
        self.id = self.canvas.create_image(Constantes.POS_PLAYER_START_X, Constantes.POS_PLAYER_START_Y, image=self.image)

    # Moving Defender image on canvas
    def move_in(self, canvas, dx):
        self.canvas = canvas
        self.dx = dx
        self.canvas_width = int(canvas.cget("width"))
        self.canvas.move(self.id, self.dx*self.move_delta, 0)

    # Action to shoot: create Bullet object
    def fire(self, canvas):
        self.canvas = canvas
        # Checking if number of Bullets shooted don't go out of limit
        if len(self.fired_bullets) < self.max_fired_bullets+1:
            self.fired_bullets.append(Bullet(self))

# Class to manage the frame of the running game
class Game(object):

    def __init__(self, frame, root):
        self.root = root
        self.frame = frame
        self.alien = Alien()
        self.defender = Defender()
        self.canvas_width = Constantes.WIDTH_GAME_WINDOW
        self.canvas_height = Constantes.HEIGHT_GAME_WINDOW
        self.fleet = Fleet()
        self.canvas = tk.Canvas(self.frame, width=self.canvas_width, height=self.canvas_height, bg='black')
        self.canvas.pack(side="top", fill="both")
        # Install background
        image_bg = Image.open('level_bg.png')
        resized_bg = image_bg.resize((self.canvas_width, self.canvas_height))
        self.bg_image = ImageTk.PhotoImage(resized_bg)
        self.bg_level = self.canvas.create_image( 0, 0, image = self.bg_image, anchor = "nw")
        # Install defender and fleet
        self.fleet.install_in(self.canvas)
        self.defender.install_in(self.canvas)
        # Getting the score on screen
        self.player_score = self.canvas.create_text(120, 30, text = 'SCORE     '+str(Constantes.SCORE), fill = 'white', font = ('Arial', 10))
        self.best_score = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW-150, 30, text = 'HI-SCORE     '+str(Constantes.HIGHEST_SCORE), fill = 'white', font = ('Arial', 10))
        # Start moving objects
        self.start_animation()
        # When event any key pressed, then activate keypress
        self.frame.focus_set()
        self.frame.bind("<Key>", self.keypress)

    def start_animation(self):
        self.canvas.after(10, self.animation)

    # Moving Alien Fleet and Game Over checking
    def animation(self):
        self.fleet.move_in(self.canvas)
        self.canvas.after(300, self.animation)
        # Game Over by Wining: no Alien() object left
        if len(self.fleet.aliens_fleet) == 0:
            self.get_win()
        # Game Over by Loosing: Alien Fleet touched the top X coordinate of Defender
        if self.fleet.aliens_matrix_bottom >= Constantes.POS_PLAYER_START_Y:
            self.get_loose()

    # Creating and moving Bullets managing
    def move_bullets(self):
        for each_bullets in self.defender.fired_bullets:
            # If Bullet object haven't been created before, then create
            if each_bullets.id == None:
                each_bullets.install_in(self.canvas)
                #playsound('./shoot1.wav')
            each_bullets.move_in(self.canvas)
            # What happens to Bullet depends of its position
            coord_tir = self.canvas.coords(each_bullets.id)
            if (len(coord_tir)>0) and (coord_tir[3]>0):
                # Here the Bullet is still in the Game Window
                # Check if the Bullet touched an Alien
                self.fleet.manage_touched_aliens_by(self.canvas, each_bullets.id)
                # Update Player Score in live
                self.canvas.itemconfigure(self.player_score, text="SCORE     "+str(Constantes.SCORE))
            else:
                # If Bullet go out of game Window, then delete and remove from Bullet list fired_bullets
                self.canvas.delete(each_bullets)
                self.defender.fired_bullets.remove(each_bullets)
        # Repeat
        self.canvas.after(80, self.move_bullets)

    # Actions when pressing keys
    def keypress(self, event):
        if event.keysym == 'Left':
            self.x = -1
            self.defender.move_in(self.canvas, -1)
        elif event.keysym == 'Right':
            self.x = +1
            self.defender.move_in(self.canvas, 1)
        elif event.keysym == 'space':
            # Then shooting
            self.defender.fire(self.canvas)
            self.move_bullets()

    # Functions in case of Game Over, Win or Loose
    def get_win(self):
        # Going to Game Over Frame:
        Constantes.GameOverState = 1
        self.root.get_screen(GameOver, self)

    def get_loose(self):
        Constantes.GameOverState = 2
        self.root.get_screen(GameOver, self)

# Class to manage the Title Screen frame
class TitleScreen(object):
    def __init__(self, frame, root):
        self.root = root
        self.frame = frame
        self.canvas_width = Constantes.WIDTH_GAME_WINDOW
        self.canvas_height = Constantes.HEIGHT_GAME_WINDOW
        self.canvas = tk.Canvas(self.frame, width=self.canvas_width, height=self.canvas_height, bg='black')
        self.canvas.pack(side='top', fill="both")
        # Function to display the elements of Title Screen
        self.set_elements()
        self.start_animation_title()
        self.start_animation_press_start()
        # When event any key pressed, then activate keypress
        self.frame.focus_set()
        self.frame.bind("<Key>", self.keypress)

    def keypress(self, event):
        if event.keysym == 'Left':
            print('gauche')
        elif event.keysym == 'Right':
            print('droite')
        elif event.keysym == 'space':
            # Going to Game frame
            self.root.get_screen(Game, self)

    def set_elements(self):
        # Install background
        image_bg = Image.open('bg_title_1.png')
        resized_bg = image_bg.resize((self.canvas_width, self.canvas_height))
        self.bg_image = ImageTk.PhotoImage(resized_bg)
        self.bg_level = self.canvas.create_image( 0, 0, image = self.bg_image, anchor = "nw")

    def appear_title(self):
        image_title = Image.open('game_title.png')
        resized_title = image_title.resize((560, 170))
        self.img_title = ImageTk.PhotoImage(resized_title)
        self.game_title = self.canvas.create_image(Constantes.WIDTH_GAME_WINDOW/2, 180, image = self.img_title)

    def start_animation_title(self):
        self.canvas.after(2000, self.appear_title)
        # Create scores then
        self.canvas.after(3000, self.appear_scores)

    def disappear_press_start(self):
        self.canvas.delete(self.press_space)
        self.canvas.after(1000, self.appear_press_start)

    def appear_press_start(self):
        self.press_space = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW/2, 400, text = 'PRESS SPACE', fill = 'white', font = ('Arial', 10))
        self.canvas.after(1000, self.disappear_press_start)

    def start_animation_press_start(self):
        self.canvas.after(3000, self.appear_press_start)


    def appear_scores(self):
        # Display player score
        self.player_score = self.canvas.create_text(120, 30, text = 'SCORE     '+str(Constantes.SCORE), fill = 'white', font = ('Arial', 10))
        # Opening the scores file:
        with open('scores.json') as file:
            data_scores = json.load(file)
        # Converting scores from file to a sorted list with int score type
        all_scores = dict()
        for each_data_score in data_scores["scores"]:
            all_scores[each_data_score] = int(data_scores["scores"][each_data_score])
        # Get a list with the 5 best players by score
        sorted_scores = sorted(all_scores, key=all_scores.get, reverse=True)[:5]
        # Display the 5 best players and scores
        i = 60
        for each_of_top5 in sorted_scores:
            self.player_name_top = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW/2 - 100, 220+i, text = (each_of_top5), fill = 'grey', font = ('Arial',10))
            self.player_score_top = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW/2 + 100, 220+i, text = str(all_scores[each_of_top5]), fill = 'grey', font = ('Arial',10))
            i = i+20
        # Get the best player and update Hi-Score
        best_player = sorted_scores[0]
        Constantes.HIGHEST_SCORE = (all_scores[best_player])
        # Display the best player in corner right of the screen
        self.best_score = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW-150, 30, text = 'HI-SCORE     '+str(Constantes.HIGHEST_SCORE), fill = 'white', font = ('Arial', 8))
        # Display Press Space to continue

class SegaLogo(object):
    def __init__(self, frame, root):
        self.root = root
        self.frame = frame
        self.canvas_width = Constantes.WIDTH_GAME_WINDOW
        self.canvas_height = Constantes.HEIGHT_GAME_WINDOW
        self.canvas = tk.Canvas(self.frame, width=self.canvas_width, height=self.canvas_height, bg='black')
        self.canvas.pack(side='top', fill="both")
        self.start_animation_logo()

    def appear_title(self):
        image_title = Image.open('logo_sega.png')
        resized_title = image_title.resize((225, 97))
        self.img_title = ImageTk.PhotoImage(resized_title)
        self.game_title = self.canvas.create_image(Constantes.WIDTH_GAME_WINDOW/2, Constantes.HEIGHT_GAME_WINDOW/2, image = self.img_title)
        self.canvas.after(2000, self.goto_title_screen)

    def start_animation_logo(self):
        self.canvas.after(2000, self.appear_title)

    def goto_title_screen(self):
        self.root.get_screen(TitleScreen, self)

class GameOver(object):
    def __init__(self, frame, root):
        self.root = root
        self.frame = frame
        self.canvas_width = Constantes.WIDTH_GAME_WINDOW
        self.canvas_height = Constantes.HEIGHT_GAME_WINDOW
        self.canvas = tk.Canvas(self.frame, width=self.canvas_width, height=self.canvas_height, bg='black')
        self.canvas.pack(side='top', fill="both")
        self.start_animation_game_over()
        # Letters
        self.list_letters = ['A','A','A']
        # Get position of selected letter:
        self.selected = 0
        # When event any key pressed, then activate keypress
        self.frame.focus_set()
        self.frame.bind("<Key>", self.keypress)

    # Actions when pressing keys
    def keypress(self, event):

        if event.keysym == 'Left':
            # Going to next letter: moving arrow and selected letter
            if self.selected == 0:
                self.selected = 2
                # Moving arrows in same time
                self.canvas.move(self.arrow1, 100, 0)
                self.canvas.move(self.arrow2, 100, 0)
            else:
                self.selected = self.selected-1
                # Moving arrows in same time
                self.canvas.move(self.arrow1, -50, 0)
                self.canvas.move(self.arrow2, -50, 0)
            print("GAUCHE")

        elif event.keysym == 'Right':
            # Going to next letter: moving arrow and selected letter
            if self.selected == 2:
                self.selected = 0
                # Moving arrows in same time
                self.canvas.move(self.arrow1, -100, 0)
                self.canvas.move(self.arrow2, -100, 0)
            else:
                self.selected = self.selected+1
                # Moving arrows in same time
                self.canvas.move(self.arrow1, 50, 0)
                self.canvas.move(self.arrow2, 50, 0)

        elif event.keysym == 'Down':
            # When Down key pressed, letters go next in alphabet
            self.list_letters[self.selected] = chr(ord(self.list_letters[self.selected]) + 1)
            self.canvas.itemconfigure(self.list_of_letters_widgets[self.selected], text=self.list_letters[self.selected])

        elif event.keysym == 'Up':
            # When Up key pressed, letters go previous in alphabet
            self.list_letters[self.selected] = chr(ord(self.list_letters[self.selected]) -1)
            self.canvas.itemconfigure(self.list_of_letters_widgets[self.selected], text=self.list_letters[self.selected])

        elif event.keysym == 'space':
            print("CONFIRM")
            # If space pressed, score and name are saved and go back to Title Screen
            player_name_chosen = self.list_letters[0]+self.list_letters[1]+self.list_letters[2]
            #new_score_to_add = {player_name_chosen:str(Constantes.SCORE)}
            with open('scores.json','r',encoding='utf-8') as file:
                file_data = json.load(file)
            with open('scores.json','w',encoding='utf-8') as file2:
                #file_data2 = json.load(file2)
                dic_scores = file_data["scores"]
                dic_scores[player_name_chosen] = str(Constantes.SCORE)
                new_dic_scores = {}
                new_dic_scores["scores"] = dic_scores
                json.dump(new_dic_scores, file2, indent = 4)
            # We set back the score to zero
            Constantes.SCORE = 0
            # Go back to Title Screen
            self.canvas.after(2000, self.goto_title_screen)

    def appear_infos(self):
        # Display Game Over
        self.game_over_title = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW/2, 120, text = 'GAME OVER', fill = 'grey', font = ('Arial',15))
        # Display if Win or Loose
        if Constantes.GameOverState == 1:
            # Case of Win
            self.game_over_state = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW/2, 140, text = 'VICTORY', fill = 'grey', font = ('Arial',12))
        if Constantes.GameOverState == 2:
            # Case of Loose
            self.game_over_state = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW/2, 140, text = 'DEFEAT', fill = 'grey', font = ('Arial',15))
        # Display player score:
        self.player_score = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW/2, 180, text = 'SCORE     '+str(Constantes.SCORE), fill = 'white', font = ('Arial', 10))
        # Enter Player Name:
        self.enter_player_name = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW/2, 200, text = 'ENTRY PLAYER NAME', fill = 'white', font = ('Arial', 10))
        # 3 Letters to choose as Player name:
        self.letter1 = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW/2-50, 300, text = 'A', fill = 'white', font = ('Arial', 14))
        self.letter2 = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW/2, 300, text = 'A', fill = 'white', font = ('Arial', 14))
        self.letter3 = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW/2+50, 300, text = 'A', fill = 'white', font = ('Arial', 14))
        # The arrows are on first letter by default:
        self.arrow1 = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW/2-50, 240, text = '↑', fill = 'white', font = ('Arial', 10))
        self.arrow2 = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW/2-50, 360, text = '↓', fill = 'white', font = ('Arial', 10))
        # List of items
        self.list_of_letters_widgets = [self.letter1, self.letter2, self.letter3]
        # Press Space to confirm
        self.press_space_to_confirm = self.canvas.create_text(Constantes.WIDTH_GAME_WINDOW/2, 440, text = 'Press Space to Confirm', fill = 'white', font = ('Arial', 10))

    def start_animation_game_over(self):
        self.canvas.after(2000, self.appear_infos)

    def goto_title_screen(self):
        self.root.get_screen(TitleScreen, self)



# Main class to run the game
class SpaceInvaders(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Space Invaders")
        self.frame = tk.Frame(self.root)
        self.frame.pack(side="top", fill="both")
        # Starting with Title Screen first
        self.get_screen_start(SegaLogo)

    # Install the first screen
    def get_screen_start(self, frame_class):
        self.frame_class = frame_class
        self.current_class = self.frame_class(self.frame, self)
        self.current_class.frame.tkraise()

    # Install the next screen
    def get_screen(self, frame_class, frame_to_destroy):
        self.frame_class = frame_class
        self.frame_to_destroy = frame_to_destroy
        # Destroy the canvas of the current frame
        self.current_class.canvas.destroy()
        # Then create the next canvas
        self.current_class = self.frame_class(self.frame, self)
        self.current_class.frame.tkraise()

    # Activate the mainloop
    def play(self):
        self.root.mainloop()

# Launch the game process
print("LAUCH")
SpaceInvaders().play()
