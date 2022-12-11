import cProfile
import ctypes
import itertools
import pstats
import math
import time
import winsound
import pickle
from threading import Timer

import numpy as np
import sdl2.ext
import sdl2.sdlgfx
import sdl2
import sdl2.sdlmixer
import sdl2.keyboard

import numba

# Constanten
BREEDTE = 1200
HOOGTE = 750
s_BREEDTE = (int)(1.2 * BREEDTE)
s_HOOGTE = (int)(2 * HOOGTE)
texWidthWall = 512
texHeightWall = 512
texWidthFloor = 992
texHeightFloor = 992

# Dragcoefficient, draaisnelheid, rolsnelheid, scherm_rotatie_limiet, versnelling_v, versnelling_a
var_fighters = [[0.9, 1.6, 50, 30, 5, 0.4],
                [1.2, 1.2, 30, 40, 5, 0.15],
                [0.85, 1.7, 60, 30, 7, 0.5],
                [0.8, 1.8, 70, 30, 6, 0.5],
                [1.1, 1.4, 40, 35, 5, 0.25]]

breedte_tf = 0.7

#
# Globale variabelen
#
d_camera = 0.75

snelheid = 0.0

scherm_hoek = 0

index_fighter = 0

damage_indicator = 0

score = 0

hit = 1

newUsername = " "

magTypen = False

shoot = False
been_shot = 1

# positie van de speler
p_speler = [3 + 1 / math.sqrt(2), 4 - 1 / math.sqrt(2)]

# richting waarin de speler kijkt
r_speler = np.array([1 / math.sqrt(2), 1 / math.sqrt(2)])

# cameravlak
r_cameravlak = np.matmul(r_speler, [[0, -1],
                                    [1, 0]])

# wordt op True gezet als het spel afgesloten moet worden
moet_afsluiten = False

# de "wereldkaart". Dit is een 2d matrix waarin elke cel een type van muur voorstelt
# Een 0 betekent dat op deze plaats in de game wereld geen muren aanwezig zijn
world_map = np.array(
    [[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
     [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 2, 0, 0, 0, 0, 2, 2, 2],
     [2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 0, 0, 2, 2, 2, 2, 0, 0, 2, 2, 0, 0, 0, 2, 0, 0, 2, 2, 0, 2, 2, 2],
     [2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 2, 2, 2, 2, 2, 2, 0, 2, 2, 0, 0, 2, 2, 2],
     [2, 0, 2, 0, 0, 2, 2, 2, 2, 0, 2, 2, 0, 2, 2, 2, 2, 0, 0, 2, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2],
     [2, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 2, 2, 0, 0, 0, 0, 2, 0, 2, 2, 0, 0, 2, 0, 0, 2, 2, 2, 2, 2, 2],
     [2, 0, 2, 2, 0, 0, 2, 0, 2, 0, 2, 0, 0, 0, 0, 2, 0, 2, 2, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 2, 2, 2, 2],
     [2, 0, 2, 2, 0, 2, 2, 2, 0, 0, 2, 0, 2, 0, 0, 0, 2, 2, 2, 0, 0, 2, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 0, 0, 0, 2, 2, 2],
     [2, 0, 2, 0, 0, 2, 2, 0, 0, 2, 0, 0, 2, 2, 2, 0, 2, 0, 2, 0, 0, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2],
     [2, 0, 2, 2, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 2, 0, 2, 0, 2, 2, 0, 0, 0, 0, 0, 2, 0, 2, 2, 2, 2],
     [2, 0, 0, 0, 0, 0, 0, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 2, 0, 2, 0, 2, 2, 0, 0, 2, 0, 0, 0, 2, 2, 2, 2, 2],
     [2, 0, 2, 2, 2, 2, 0, 2, 2, 0, 2, 2, 2, 2, 0, 0, 2, 0, 2, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 2, 0, 0, 2, 2, 2, 2, 2, 2],
     [2, 2, 2, 2, 2, 0, 0, 2, 2, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 2, 2, 2],
     [2, 2, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 2, 2, 2],
     [2, 0, 2, 0, 0, 2, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 2, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 2],
     [2, 0, 2, 0, 0, 0, 0, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 2],
     [2, 2, 0, 0, 0, 2, 0, 2, 0, 2, 2, 0, 0, 0, 0, 0, 2, 2, 2, 0, 2, 2, 0, 0, 2, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
     [2, 2, 0, 0, 0, 2, 0, 0, 0, 2, 2, 2, 2, 0, 2, 0, 2, 2, 2, 0, 2, 2, 0, 0, 2, 0, 0, 2, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2],
     [2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 2, 2, 0, 0, 2, 0, 0, 2, 0, 2, 0, 2, 2, 0, 2, 2, 2, 2],
     [2, 0, 2, 0, 0, 0, 0, 0, 2, 2, 0, 0, 2, 0, 2, 2, 0, 0, 2, 2, 0, 0, 0, 0, 2, 0, 0, 2, 0, 2, 0, 2, 0, 0, 2, 2, 2, 2],
     [2, 0, 2, 0, 2, 2, 2, 0, 2, 2, 0, 0, 2, 0, 2, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 2, 0, 2, 0, 2, 2, 0, 2, 2, 2, 2],
     [2, 0, 2, 0, 2, 2, 2, 0, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2],
     [2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 2, 2, 2, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2],
     [2, 0, 0, 2, 2, 0, 2, 2, 2, 2, 0, 0, 0, 2, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 2, 2, 2, 2, 2],
     [2, 0, 0, 2, 0, 0, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 0, 0, 2, 0, 0, 2, 2, 2, 0, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2],
     [2, 2, 0, 2, 0, 2, 2, 2, 0, 0, 0, 0, 0, 2, 0, 0, 2, 2, 0, 2, 0, 2, 0, 2, 0, 2, 2, 2, 2, 0, 0, 0, 2, 2, 2, 2, 2, 2],
     [2, 2, 0, 0, 0, 2, 0, 0, 0, 2, 2, 2, 0, 2, 0, 0, 0, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 2, 0, 2, 2, 0, 2, 2, 2, 2, 2],
     [2, 2, 2, 0, 2, 2, 0, 0, 0, 2, 2, 2, 2, 0, 2, 2, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 2, 2, 0, 0, 2, 2, 2, 2],
     [2, 0, 2, 0, 2, 0, 0, 2, 0, 2, 2, 2, 0, 0, 0, 0, 2, 2, 2, 2, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 0, 2, 0, 0, 2, 2, 2, 2],
     [2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 2, 2, 0, 0, 2, 2, 2, 2, 0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 2, 2, 0, 0, 2, 0, 2, 2, 2, 2],
     [2, 0, 2, 2, 2, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 2, 2, 2, 0, 2, 0, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2],
     [2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 0, 0, 0, 2, 2, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 2, 0, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 2],
     [2, 2, 2, 2, 0, 0, 0, 2, 2, 2, 0, 0, 2, 2, 2, 0, 2, 2, 0, 2, 0, 2, 0, 2, 2, 2, 0, 0, 0, 0, 0, 2, 0, 2, 2, 2, 2, 2],
     [2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
     [2, 0, 2, 2, 0, 0, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
     [2, 0, 0, 0, 0, 0, 2, 2, 0, 2, 2, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
     [2, 0, 0, 2, 2, 0, 0, 2, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
     [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
     ])

world_size_vertical = len(world_map)
world_size_horizontal = len(world_map[0])

# Vooraf gedefinieerde kleuren
kleuren = [
    sdl2.ext.Color(0, 255, 0),  # groen
    sdl2.ext.Color(255, 0, 0),  # Rood
    sdl2.ext.Color(255, 255, 0),  # Geel
    sdl2.ext.Color(0, 0, 255),  # Blauw
    sdl2.ext.Color(64, 64, 64),  # Donker grijs
    sdl2.ext.Color(128, 128, 128),  # Grijs
    sdl2.ext.Color(192, 192, 192),  # Licht grijs
    sdl2.ext.Color(255, 255, 255),  # Wit
    sdl2.ext.Color(0, 0, 0)  # zwart
]

# fonts
fps_font = sdl2.ext.FontTTF(font='CourierPrime.ttf', size=20, color=kleuren[7])
score_font = sdl2.ext.FontTTF(font='StarJedi.ttf', size=40, color=kleuren[7])
title_font = sdl2.ext.FontTTF(font='StarJedi.ttf', size=80, color=kleuren[7])
enter_font = sdl2.ext.FontTTF(font='StarJedi.ttf', size=30, color=kleuren[7])
failed_font = sdl2.ext.FontTTF(font='StarJedi.ttf', size=120, color=kleuren[1])
menu_font = sdl2.ext.FontTTF(font='StarJedi.ttf', size=60, color=kleuren[7])
fighter_font = sdl2.ext.FontTTF(font='StarJedi.ttf', size=60, color=kleuren[2])
switch_font = sdl2.ext.FontTTF(font='CourierPrime.ttf', size=80, color=kleuren[7])
high_score_font = sdl2.ext.FontTTF(font='arcade.ttf', size=60, color=kleuren[7])

load_fighters = [
    sdl2.ext.load_bmp("fighters/Fighter1.bmp"),
    sdl2.ext.load_bmp("fighters/Fighter2.bmp"),
    sdl2.ext.load_bmp("fighters/Fighter3.bmp"),
    sdl2.ext.load_bmp("fighters/Fighter4.bmp"),
    sdl2.ext.load_bmp("fighters/Fighter5.bmp")
]

load_fighters_fov = [
    sdl2.ext.load_img("fighters/Fighterfov1.png"),
    sdl2.ext.load_img("fighters/Fighterfov2.png"),
    sdl2.ext.load_img("fighters/Fighterfov3.png"),
    sdl2.ext.load_img("fighters/Fighterfov4.png"),
    sdl2.ext.load_img("fighters/Fighterfov5.png")

]

laser_img = sdl2.ext.load_img("sprites/laser.png")
laser_texture = 0

explosion_img = sdl2.ext.load_img("sprites/explosion.png")
explosion_texture = 0

load_tf = [
    sdl2.ext.load_img("sprites/tf1.png"),
    sdl2.ext.load_img("sprites/tf2.png")
]

sprite_pos = np.array([[4.5, 9.5],
                       [1.5, 7.5],
                       [4.5, 4.5],
                       [6.5, 12.5],
                       [1.5, 22.5],
                       [8.5, 20.5],
                       [8.5, 34.5],
                       [11.5, 6.5],
                       [13.5, 13.5],
                       [13.5, 26.5],
                       [17.5, 8.5],
                       [19.5, 33.5],
                       [21.5, 24.5],
                       [23.5, 11.5],
                       [25.5, 2.5],
                       [26.5, 25.5],
                       [30.5, 11.5],
                       [32.5, 30.5],
                       [35.5, 2.5],
                       [35.5, 18.5]
                       ])
sprite_alive = [True for i in sprite_pos]

sprite_init = [False for j in sprite_pos]

richting_bewegen = ["" for k in sprite_pos]

sprite_type = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
               1]  # soort is de index voor de load_tf array


#
# Verwerkt alle input van het toetsenbord en de muis
#
# Argumenten:
# @delta       Tijd in milliseconden sinds de vorige oproep van deze functie
#
def verwerk_input(delta):
    global damage_indicator
    global moet_afsluiten
    global p_speler
    global r_speler
    global r_cameravlak
    global d_camera
    global snelheid
    global scherm_hoek
    global score
    global sprite_pos
    global richting_bewegen
    global sprite_init
    global shoot
    global been_shot
    global hit

    if delta > 1:
        delta = 0
    # Handelt alle input events af die zich voorgedaan hebben sinds de vorige
    # keer dat we de sdl2.ext.get_events() functie hebben opgeroepen
    shoot = False
    events = sdl2.ext.get_events()
    for event in events:
        # Een SDL_QUIT event wordt afgeleverd als de gebruiker de applicatie
        # afsluit door bv op het kruisje te klikken
        if event.type == sdl2.SDL_QUIT:
            moet_afsluiten = True
        # Een SDL_KEYDOWN event wordt afgeleverd wanneer de gebruiker een
        # toets op het toetsenbord indrukt.
        # Let op: als de gebruiker de toets blijft inhouden, dan zien we
        # maar 1 SDL_KEYDOWN en 1 SDL_KEYUP event.
        elif event.type == sdl2.SDL_KEYDOWN:
            key = event.key.keysym.sym
            if key == sdl2.SDLK_c:
                moet_afsluiten = True

            if key == sdl2.SDLK_SPACE:
                laser = sdl2.sdlmixer.Mix_LoadWAV(b'fighters/Laser_sound.wav')
                sdl2.sdlmixer.Mix_PlayChannel(0, laser, 0)
                shoot = True
                been_shot = 0


        # Een SDL_MOUSEWHEEL event wordt afgeleverd wanneer de gebruiker
        # aan het muiswiel draait.
        elif event.type == sdl2.SDL_MOUSEWHEEL:
            d_camera += 0.01 * event.wheel.y
        #            if event.wheel.y > 0:
        #                d_camera -=0.01
        # Wordt afgeleverd als de gebruiker de muis heeft bewogen.
        # Aangezien we relative motion gebruiken zijn alle coordinaten
        # relatief tegenover de laatst gerapporteerde positie van de muis.
        # elif event.type == sdl2.SDL_MOUSEMOTION:
        #     # Aangezien we in onze game maar 1 as hebben waarover de camera
        #     # kan roteren zijn we enkel geinteresseerd in bewegingen over de
        #     # X-as
        #     beweging = -event.motion.xrel
        #     rotatie = [[math.cos(beweging / 360), math.sin(beweging / 360)],
        #                [-1 * math.sin(beweging / 360), math.cos(beweging / 360)]]
        #
        #     r_speler = np.matmul(r_speler, rotatie)
        #     r_cameravlak = np.matmul(r_speler, [[0, -1],
        #                                         [1, 0]])

    # Polling-gebaseerde input. Dit gebruiken we bij voorkeur om bv het ingedrukt
    # houden van toetsen zo accuraat mogelijk te detecteren
    key_states = sdl2.SDL_GetKeyboardState(None)

    if key_states[sdl2.SDL_SCANCODE_UP] or key_states[sdl2.SDL_SCANCODE_W]:
        snelheid += var_fighters[index_fighter][4] * delta

    if key_states[sdl2.SDL_SCANCODE_DOWN] or key_states[sdl2.SDL_SCANCODE_S]:
        snelheid -= var_fighters[index_fighter][5] * delta

    if key_states[sdl2.SDL_SCANCODE_LEFT] or key_states[sdl2.SDL_SCANCODE_A]:
        scherm_hoek -= var_fighters[index_fighter][2] * delta
        rotatie = [[math.cos(var_fighters[index_fighter][1] * delta), math.sin(var_fighters[index_fighter][1] * delta)],
                   [-1 * math.sin(var_fighters[index_fighter][1] * delta),
                    math.cos(var_fighters[index_fighter][1] * delta)]]

        r_speler = np.matmul(r_speler, rotatie)
        r_cameravlak = np.matmul(r_speler, [[0, -1],
                                            [1, 0]])

    if key_states[sdl2.SDL_SCANCODE_RIGHT] or key_states[sdl2.SDL_SCANCODE_D]:
        scherm_hoek += var_fighters[index_fighter][2] * delta
        rotatie = [
            [math.cos(-var_fighters[index_fighter][1] * delta), math.sin(-var_fighters[index_fighter][1] * delta)],
            [-1 * math.sin(-var_fighters[index_fighter][1] * delta), math.cos(-var_fighters[index_fighter][1] * delta)]]

        r_speler = np.matmul(r_speler, rotatie)
        r_cameravlak = np.matmul(r_speler, [[0, -1],
                                            [1, 0]])

    # luchtweerstand
    if (snelheid > 0):
        snelheid -= var_fighters[index_fighter][0] * (1 + damage_indicator / 7) * delta * snelheid ** 2

    else:
        snelheid += var_fighters[index_fighter][0] * delta * snelheid ** 2

    # terug draaien van het scherm
    if not key_states[sdl2.SDL_SCANCODE_A] \
            and not key_states[sdl2.SDL_SCANCODE_D] \
            and not key_states[sdl2.SDL_SCANCODE_LEFT] \
            and not key_states[sdl2.SDL_SCANCODE_RIGHT]:
        if (scherm_hoek > 0):
            scherm_hoek -= 40 * delta
            if (scherm_hoek < 0):
                scherm_hoek = 0
        elif (scherm_hoek < 0):
            scherm_hoek += 40 * delta
            if (scherm_hoek > 0):
                scherm_hoek = 0

    # schermrotatie limiet
    p_speler += snelheid * delta * r_speler
    if scherm_hoek > var_fighters[index_fighter][3]:
        scherm_hoek = var_fighters[index_fighter][3]
    elif scherm_hoek < -var_fighters[index_fighter][3]:
        scherm_hoek = -var_fighters[index_fighter][3]

    # collisions
    if world_map[math.floor(p_speler[0])][math.floor(p_speler[1] - 0.1)] != 0:
        p_speler[1] += 0.101
        damage_indicator += abs(snelheid * r_speler[1])

    if world_map[math.floor(p_speler[0] + 0.1)][math.floor(p_speler[1])] != 0:
        p_speler[0] -= 0.101
        damage_indicator += abs(snelheid * r_speler[0])

    if world_map[math.floor(p_speler[0] - 0.1)][math.floor(p_speler[1])] != 0:
        p_speler[0] += 0.101
        damage_indicator += abs(snelheid * r_speler[0])

    if world_map[math.floor(p_speler[0])][math.floor(p_speler[1] + 0.1)] != 0:
        p_speler[1] -= 0.101
        damage_indicator += abs(snelheid * r_speler[1])

    for x in range(0, len(sprite_pos)):
        if sprite_alive[x] and np.linalg.norm(p_speler - sprite_pos[x]) < 0.5:
            damage_indicator = 5

    # tijd laser
    been_shot += delta
    hit += delta


@numba.jit(nopython=True, cache=True)
def bereken_r_straal(kolom, surface_width, r_speler, r_cameravlak, d_camera):
    r_straal_kolom = d_camera * r_speler + (-1 + ((2 * kolom) / surface_width)) * r_cameravlak
    r_straal = (r_straal_kolom / np.linalg.norm(r_straal_kolom))
    return r_straal


@numba.jit(nopython=True, cache=True)
def delta_bep(r_straal):
    # vermijden divide by 0 error
    if r_straal[0] == 0:
        delta_v = 1e30
    else:
        delta_v = (1 / abs(r_straal[0]))

    if r_straal[1] == 0:
        delta_h = 1e30
    else:
        delta_h = (1 / abs(r_straal[1]))

    return delta_h, delta_v


@numba.jit(nopython=True, cache=True)
def afstand_bep(r_straal, p_speler):
    # d_horizontaal/verticaal in juiste richting bepalen
    (delta_h, delta_v) = delta_bep(r_straal)
    if (r_straal[1] >= 0):
        d_horizontaal = (1 - p_speler[1] + math.floor(p_speler[1])) * delta_h
    else:
        d_horizontaal = (p_speler[1] - math.floor(p_speler[1])) * delta_h

    if (r_straal[0] >= 0):
        d_verticaal = (1 - p_speler[0] + math.floor(p_speler[0])) * delta_v
    else:
        d_verticaal = (p_speler[0] - math.floor(p_speler[0])) * delta_v

    return delta_h, delta_v, d_horizontaal, d_verticaal


@numba.jit(nopython=True, cache=True)
def raycast(r_straal, p_speler, r_speler, texWidthWall, world_map):
    x = 0
    y = 0
    (delta_h, delta_v, d_horizontaal, d_verticaal) = afstand_bep(r_straal, p_speler)

    # zoeken intersection met muur
    while (True):
        # dichtste intersection met grid zoeken
        if (d_horizontaal + y * delta_h <= d_verticaal + x * delta_v):
            i_horizontaal = [0.0, 0.0]
            i_horizontaal[0] = p_speler[0] + (d_horizontaal + y * delta_h) * r_straal[0]
            i_horizontaal[1] = p_speler[1] + (d_horizontaal + y * delta_h) * r_straal[1]
            # round omdat dit in de buurt moet liggen van een gehele coördinaat
            # maar door floating-point error kan dit er ook juist onder liggen
            world_coords_intersection_x = math.floor(i_horizontaal[0])

            if (r_straal[1] >= 0):
                world_coords_intersection_y = round(i_horizontaal[1])
            else:
                world_coords_intersection_y = round(i_horizontaal[1]) - 1

            if (world_coords_intersection_x > world_size_horizontal - 1
                    or world_coords_intersection_y > world_size_vertical - 1
                    or world_coords_intersection_x < 0
                    or world_coords_intersection_y < 0
            ):
                return (0, 0)  # om zichtbaar te maken waar er buiten de wereldgrenzen word gehaan
            else:
                if (world_map[world_coords_intersection_x][world_coords_intersection_y] != 0):
                    textOffset = (i_horizontaal[0] - math.floor(i_horizontaal[0])) * texWidthWall
                    temp = np.array([0.0, 0.0])
                    temp[0] = i_horizontaal[0] - p_speler[0]
                    temp[1] = i_horizontaal[1] - p_speler[1]
                    d_muur = np.linalg.norm(temp) * np.dot(r_speler, r_straal)
                    return (d_muur, textOffset)
            y += 1
        else:
            i_verticaal = [0.0, 0.0]
            i_verticaal[0] = p_speler[0] + (d_verticaal + x * delta_v) * r_straal[0]
            i_verticaal[1] = p_speler[1] + (d_verticaal + x * delta_v) * r_straal[1]
            # round omdat dit in de buurt moet liggen van een gehele coördinaat
            # maar door floating-point error kan dit er ook juist onder liggen
            if (r_straal[0] >= 0):
                world_coords_intersection_x = round(i_verticaal[0])
            else:
                world_coords_intersection_x = round(i_verticaal[0]) - 1

            world_coords_intersection_y = math.floor(i_verticaal[1])

            if (world_coords_intersection_x > world_size_horizontal - 1
                    or world_coords_intersection_y > world_size_vertical - 1
                    or world_coords_intersection_x < 0
                    or world_coords_intersection_y < 0
            ):
                return (0, 0)  # om zichtbaar te maken waar er buiten de wereldgrenzen word gegaan
            else:
                if (world_map[world_coords_intersection_x][world_coords_intersection_y] != 0):
                    textOffset = (i_verticaal[1] - math.floor(i_verticaal[1])) * texWidthWall
                    temp = np.array([0.0, 0])
                    temp[0] = i_verticaal[0] - p_speler[0]
                    temp[1] = i_verticaal[1] - p_speler[1]
                    d_muur = np.linalg.norm(temp) * np.dot(r_speler, r_straal)
                    return (d_muur, textOffset)
            x += 1


def render_kolom(renderer, Height, kolom, d_muur, textOffset, img):
    if d_muur != 0:
        height_line = HOOGTE / d_muur
    else:
        height_line = Height
    renderer.copy(img, (textOffset, 0, 1, texHeightWall),
                  (kolom, Height / 2 - (height_line / 2), 1, height_line))


def render_fps(fps, renderer):
    global score
    message = f'{fps:.2f} fps'
    text = sdl2.ext.renderer.Texture(renderer, fps_font.render_text(message))
    renderer.copy(text, dstrect=(10, 20,
                                 text.size[0], text.size[1]))


def render_score(renderer):
    global score
    message = f'score: {score: .0f}'
    text = sdl2.ext.renderer.Texture(renderer, score_font.render_text(message))
    renderer.copy(text, dstrect=(int((BREEDTE - text.size[0]) / 2), 20, text.size[0], text.size[1]))


def listen_to_btn_actions(renderer, btn_msg, action_button, btn_y, colors, window):
    global moet_afsluiten
    global damage_indicator
    global p_speler
    global r_speler
    global snelheid
    global score
    global newUsername
    global magTypen
    global sprite_alive
    global r_cameravlak

    btn_x = get_x_coordinate_for_action_buttons(window, action_button)
    btn_width = action_button.size[0]
    btn_height = action_button.size[1]
    hover_color = colors[6]
    default_color = colors[4]

    mouse_x, mouse_y = ctypes.c_int(0), ctypes.c_int(0)
    sdl2.SDL_GetMouseState(ctypes.byref(mouse_x), ctypes.byref(mouse_y))
    is_mouse_range_of_button = btn_x + btn_width > mouse_x.value > btn_x and btn_y + btn_height > mouse_y.value > btn_y
    key_states = get_keyboard_state()
    mouse_state = get_mouse_state(mouse_x, mouse_y)

    if is_mouse_range_of_button:

        key_board_or_mouse_pressed = (key_states[sdl2.SDL_SCANCODE_RETURN] or is_left_btn_pressed(mouse_state))

        renderer.draw_rect((btn_x - 10, btn_y - 5, btn_width + 20, btn_height + 10), hover_color)

        if key_board_or_mouse_pressed and btn_msg == get_play_msg():
            chooseFighter(renderer, window)
        elif key_board_or_mouse_pressed and btn_msg == get_try_again_msg():
            damage_indicator = 0
            p_speler = [3 + 1 / math.sqrt(2), 4 - 1 / math.sqrt(2)]
            r_speler = np.array([1 / math.sqrt(2), 1 / math.sqrt(2)])
            r_cameravlak = np.matmul(r_speler, [[0, -1],
                                                [1, 0]])
            snelheid = 0
            score = 0
            sprite_alive = [True for i in sprite_pos]
            chooseFighter(renderer, window)
        elif key_board_or_mouse_pressed and btn_msg == get_enter_name_msg():
            magTypen = True
        elif key_board_or_mouse_pressed and btn_msg == get_back_msg():
            mission_failed(renderer, window)
        elif key_board_or_mouse_pressed and btn_msg == get_highscore_msg():
            show_highscores(renderer, window)
        elif key_board_or_mouse_pressed and btn_msg == get_quit_msg():
            # sdl2.sdlmixer.Mix_HaltChannel(0)
            moet_afsluiten = True
        elif magTypen:
            text_invoegen()

    else:
        renderer.draw_rect((btn_x - 10, btn_y - 5, btn_width + 20, btn_height + 10), default_color)


def text_invoegen():
    global newUsername
    global score

    sdl2.SDL_StartTextInput()
    events = sdl2.ext.get_events()

    for event in events:
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_BACKSPACE:
                if len(newUsername) == 1:
                    newUsername += " "
                else:
                    newUsername = newUsername[:-1]
            if event.key.keysym.sym == sdl2.SDLK_RETURN:
                username = newUsername
                with open("highscores.pkl", "rb") as in_:
                    high_scores = pickle.load(in_)
                high_scores[username] = score
                with open("highscores.pkl", "wb") as out:
                    pickle.dump(high_scores, out)

        elif event.type == sdl2.SDL_TEXTINPUT:
            newUsername += event.text.text.decode("utf-8")


def listen_to_navigation_and_play(renderer, btn_msg, action_button, btn_x, btn_y, colors, window):
    global index_fighter
    btn_width = action_button.size[0]
    btn_height = action_button.size[1]
    hover_color = colors[6]
    default_color = colors[4]

    textfightertextures = [
        "darth maul's scimitar",
        "han solo's millennium falcon",
        "luke skywalker's t-65b x-wing",
        "rz-1 a-wing",
        "btl-a4 y-wing"
    ]

    textfighter_texture = renderer_texture(renderer, fighter_font, textfightertextures[index_fighter])
    background_image = sdl2.ext.load_img("background/background.PNG")
    backgroundimg = sdl2.ext.renderer.Texture(renderer, background_image)

    fightersTextures = [
        sdl2.ext.renderer.Texture(renderer, load_fighters[0]),
        sdl2.ext.renderer.Texture(renderer, load_fighters[1]),
        sdl2.ext.renderer.Texture(renderer, load_fighters[2]),
        sdl2.ext.renderer.Texture(renderer, load_fighters[3]),
        sdl2.ext.renderer.Texture(renderer, load_fighters[4])
    ]

    renderer.copy(fightersTextures[index_fighter],
                  dstrect=(400, 100, fightersTextures[index_fighter].size[0] - 150,
                           fightersTextures[index_fighter].size[1] - 150))
    renderer.copy(textfighter_texture, dstrect=(
        600 - (textfighter_texture.size[0] / 2), 490, textfighter_texture.size[0], textfighter_texture.size[1]))

    mouse_x, mouse_y = ctypes.c_int(0), ctypes.c_int(0)
    sdl2.SDL_GetMouseState(ctypes.byref(mouse_x), ctypes.byref(mouse_y))
    is_mouse_range_of_button = btn_x + btn_width > mouse_x.value > btn_x and btn_y + btn_height > mouse_y.value > btn_y
    key_states = get_keyboard_state()
    mouse_state = get_mouse_state(mouse_x, mouse_y)

    if is_mouse_range_of_button:

        key_board_or_mouse_pressed = (key_states[sdl2.SDL_SCANCODE_RETURN] or is_left_btn_pressed(mouse_state))

        renderer.draw_rect((btn_x - 10, btn_y - 5, btn_width + 20, btn_height + 10), hover_color)
        if key_board_or_mouse_pressed and btn_msg == get_start_game_msg():
            winsound.PlaySound(None, winsound.SND_PURGE)
            for x in fightersTextures:
                sdl2.ext.renderer.Texture.destroy(x)
            sdl2.ext.renderer.Texture.destroy(backgroundimg)
            sdl2.sdlmixer.Mix_HaltChannel(0)

            sdl2.sdlmixer.Mix_PlayChannel(0, sdl2.sdlmixer.Mix_LoadWAV(
                f"start_sounds/start{index_fighter}.wav".encode('ASCII')), 0)

            sdl2.SDL_SetRelativeMouseMode(True)

            game(renderer, window, index_fighter)
            # sdl2.sdlmixer.Mix_FreeChunk(f"start_sounds/start{index_fighter}.wav".encode('ASCII'))
            sdl2.SDL_SetRelativeMouseMode(False)
        elif key_board_or_mouse_pressed and btn_msg == get_left_msg():
            renderer.clear()
            renderer.copy(backgroundimg, dstrect=(0, 0, BREEDTE, HOOGTE))
            index_fighter -= 1
            if index_fighter == -1:
                index_fighter = len(fightersTextures) - 1
            renderer.copy(fightersTextures[index_fighter],
                          dstrect=(
                              400, 100, fightersTextures[index_fighter].size[0] - 150,
                              fightersTextures[index_fighter].size[1] - 150))
            time.sleep(0.2)
        elif key_board_or_mouse_pressed and btn_msg == get_right_msg():
            renderer.clear()
            renderer.copy(backgroundimg, dstrect=(0, 0, BREEDTE, HOOGTE))
            index_fighter += 1
            if index_fighter == len(fightersTextures):
                index_fighter = 0
            renderer.copy(fightersTextures[index_fighter],
                          dstrect=(
                              400, 100, fightersTextures[index_fighter].size[0] - 150,
                              fightersTextures[index_fighter].size[1] - 150))
            time.sleep(0.2)
    else:
        renderer.draw_rect((btn_x - 10, btn_y - 5, btn_width + 20, btn_height + 10), default_color)


def calc_sprite_camera_centre_pos():
    # grootte: aantal sprites x 2 (voor x-y-coords)
    sprites_cam_pos = [[0, 0] for i in range(len(sprite_pos))]  # positie tov de camera-referentie
    sprites_cam_vlak = [0 for i in range(len(sprite_pos))]  # positie op het scherm
    cam_mat_inv = np.linalg.inv([[r_cameravlak[0], r_speler[0]],
                                 [r_cameravlak[1], r_speler[1]]])
    rel_sprite_pos = [[0],
                      [0]]
    for i in range(0, len(sprites_cam_pos)):  # voor elke sprite
        rel_sprite_pos[0][0] = sprite_pos[i][0] - p_speler[0]
        rel_sprite_pos[1][0] = sprite_pos[i][1] - p_speler[1]
        sprites_cam_pos[i] = np.matmul(cam_mat_inv, rel_sprite_pos)
        a = 0
        if sprites_cam_pos[i][1][0] != 0:
            a = sprites_cam_pos[i][0][0] * d_camera / sprites_cam_pos[i][1][0]

        sprites_cam_vlak[i] = a
    return sprites_cam_pos, sprites_cam_vlak


def sprite_renderer(scherm_pos, rel_pos, z_buffer, kolom, renderer, texture, texture_size, sprite_index):
    global score
    global hit

    if 0 < rel_pos[1][0] < z_buffer:
        schaal = 512 / (rel_pos[1][0] * texture_size[0])

        start_pos_texture = int(scherm_pos - (texture_size[0] * (schaal / 2)))
        end_pos_texture = int(scherm_pos + (texture_size[0] * (schaal / 2)))

        # check of de sprite met huidige kolom overlapt
        if start_pos_texture < kolom < end_pos_texture:
            t = Timer(45.0, sprite_respawning, [sprite_index])

            renderer.copy(texture,
                          srcrect=((kolom - start_pos_texture) / schaal, 0, 1, texture_size[1]),
                          dstrect=(kolom, s_HOOGTE / 2 - texture_size[1] * schaal / 2, 1, texture_size[1] * schaal))
            if kolom == s_BREEDTE / 2 and shoot:
                sprite_alive[sprite_index] = False
                score += 1
                hit = 0

            if not sprite_alive[sprite_index]:
                t.start()


def sprite_respawning(sprite_index):
    sprite_alive[sprite_index] = True


def start_menu(renderer, window):
    title_texture = renderer_texture(renderer, title_font, "star wars:")
    subtitle_text = renderer_texture(renderer, title_font, "deathstar race")

    play_texture = renderer_texture(renderer, menu_font, get_play_msg())
    quit_texture = renderer_texture(renderer, menu_font, get_quit_msg())

    background_img = sdl2.ext.load_bmp("pics/background.bmp")
    background = sdl2.ext.renderer.Texture(renderer, background_img)

    y_coordinate_for_play_btn = 300
    y_coordinate_for_quit_btn = 500

    renderer_background(renderer, background, window)
    renderer_titles(renderer, title_texture, 20, window)
    renderer_titles(renderer, subtitle_text, 100, window)

    renderer_action_buttons(renderer, play_texture, y_coordinate_for_play_btn, window)
    renderer_action_buttons(renderer, quit_texture, y_coordinate_for_quit_btn, window)

    sdl2.sdlmixer.Mix_PlayChannel(0, sdl2.sdlmixer.Mix_LoadWAV(b'music/Star_Wars_Intro.wav'), -1)

    while not moet_afsluiten:
        listen_to_btn_actions(renderer, get_play_msg(), play_texture, y_coordinate_for_play_btn, kleuren, window)
        listen_to_btn_actions(renderer, get_quit_msg(), quit_texture, y_coordinate_for_quit_btn, kleuren, window)

        renderer.present()
        verwerk_input(0)


def chooseFighter(renderer, window):
    outer_space = sdl2.ext.load_bmp("pics/outerspace.bmp")
    outerspace = sdl2.ext.renderer.Texture(renderer, outer_space)

    title_texture = renderer_texture(renderer, title_font, "choose your fighter")
    start_game_texture = renderer_texture(renderer, menu_font, get_start_game_msg())
    left_texture = renderer_texture(renderer, switch_font, get_left_msg())
    right_texture = renderer_texture(renderer, switch_font, get_right_msg())

    x_coordinate_left = 200
    x_coordinate_right = 1000
    y_coordinate_left_right = 300
    y_coordinate_for_play_btn = 600

    renderer_background(renderer, outerspace, window)
    renderer_titles(renderer, title_texture, 20, window)

    renderer_action_buttons(renderer, start_game_texture, y_coordinate_for_play_btn, window)
    renderer_left_and_right_buttons(renderer, left_texture, x_coordinate_left, y_coordinate_left_right)
    renderer_left_and_right_buttons(renderer, right_texture, x_coordinate_right, y_coordinate_left_right)

    while not moet_afsluiten:
        listen_to_navigation_and_play(renderer, get_start_game_msg(), start_game_texture,
                                      get_x_coordinate_for_action_buttons(window, start_game_texture),
                                      y_coordinate_for_play_btn,
                                      kleuren,
                                      window)
        listen_to_navigation_and_play(renderer, get_left_msg(), left_texture, x_coordinate_left,
                                      y_coordinate_left_right,
                                      kleuren, window)
        listen_to_navigation_and_play(renderer, get_right_msg(), right_texture, x_coordinate_right,
                                      y_coordinate_left_right,
                                      kleuren, window)
        renderer.present()
        verwerk_input(0)


def showHealthbar(renderer, window):
    global damage_indicator

    damage_texture = renderer_texture(renderer, score_font, "HP: ")

    renderer_off_titles(renderer, damage_texture, 580 - damage_texture.size[0], 670 - 25, window)
    renderer.draw_rect((512, 664, 185, 33), kleuren[0])
    renderer.fill((514, 665, 180 - (damage_indicator * 36), 30), None)
    renderer.fill((514, 665, 180 - (damage_indicator * 36), 30), kleuren[0])

    if damage_indicator >= 5:
        mission_failed(renderer, window)


def showAccessories(renderer, window):
    global snelheid

    speed_texture = renderer_texture(renderer, score_font, "speed:")
    snelheid_texture = renderer_texture(renderer, score_font, str(round(snelheid, 2)))

    renderer_off_titles(renderer, speed_texture, 1000 - speed_texture.size[0], 670 - 25, window)
    renderer_off_titles(renderer, snelheid_texture, 900 + snelheid_texture.size[0], 670 - 25, window)


def game(renderer, window, index):
    global scherm_hoek
    global explosion_texture

    z_buffer = [0 for i in range(0, (int)(1.2 * BREEDTE))]

    # Hide cursor shouldn't be visible in the game
    sdl2.SDL_ShowCursor(0)

    fps_list = []
    fps = 0

    surface = sdl2.SDL_CreateRGBSurface(0, s_BREEDTE, s_HOOGTE, 32, 0, 0, 0, 255)
    s_renderer = sdl2.ext.Renderer(surface)

    wall_img = sdl2.ext.load_bmp("pics/2.bmp")
    wallimg = sdl2.ext.renderer.Texture(s_renderer, wall_img)
    # floor_img = sdl2.ext.load_bmp("pics/floor.bmp")
    # floorimg = sdl2.ext.renderer.Texture(s_renderer, floor_img)
    outer_space = sdl2.ext.load_bmp("pics/outerspace.bmp")
    outerspace = sdl2.ext.renderer.Texture(s_renderer, outer_space)

    fighter_textures_fov = [
        sdl2.ext.renderer.Texture(renderer, load_fighters_fov[0]),
        sdl2.ext.renderer.Texture(renderer, load_fighters_fov[1]),
        sdl2.ext.renderer.Texture(renderer, load_fighters_fov[2]),
        sdl2.ext.renderer.Texture(renderer, load_fighters_fov[3]),
        sdl2.ext.renderer.Texture(renderer, load_fighters_fov[4])
    ]

    tf_textures = [
        sdl2.ext.renderer.Texture(s_renderer, load_tf[0]),
        sdl2.ext.renderer.Texture(s_renderer, load_tf[1])
    ]

    tf_textures_size = [
        i.size for i in tf_textures
    ]

    laser_texture_size = laser_texture.size

    explosion_texture = sdl2.ext.renderer.Texture(renderer, explosion_img)
    explosion_texture_size = explosion_texture.size

    outerspace_size = outerspace.size

    while not moet_afsluiten:
        # Onthoud de huidige tijd
        start_time = time.time()

        # Reset de rendering context
        renderer.clear()
        s_renderer.clear()
        s_renderer.copy(outerspace, (0, 0, outerspace_size[0], outerspace_size[1]),
                        dstrect=(0, 0, s_BREEDTE, s_HOOGTE / 2))
        # Render de huidige frame
        for kolom in range(0, s_BREEDTE):
            r_straal = bereken_r_straal(kolom, s_BREEDTE, r_speler, r_cameravlak, d_camera)
            (d_muur, textOffset) = raycast(r_straal, p_speler, r_speler, texWidthWall, world_map)

            render_kolom(s_renderer, s_HOOGTE, kolom, d_muur, textOffset, wallimg)
            z_buffer[kolom] = d_muur

        # Render sprites
        (rel_pos, scherm_pos) = calc_sprite_camera_centre_pos()
        scherm_pos_pix = [round((scherm_pos[i] + 1) * (s_BREEDTE >> 1)) for i in range(0, len(scherm_pos))]
        for sprite in range(0, len(rel_pos)):
            if sprite_alive[sprite]:
                for kolom in range(0, s_BREEDTE):
                    sprite_renderer(scherm_pos_pix[sprite], rel_pos[sprite], z_buffer[kolom], kolom, s_renderer,
                                    tf_textures[sprite_type[sprite]], tf_textures_size[sprite_type[sprite]], sprite)

        rotated_surface = sdl2.sdlgfx.rotozoomSurface(surface, scherm_hoek, 1, 0)
        texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, rotated_surface)

        # vermijden van null-pointer exceptions
        if texture:
            renderer.copy(texture.contents,
                          srcrect=(
                              rotated_surface.contents.w / 2 - BREEDTE / 2, rotated_surface.contents.h / 2 - HOOGTE / 2,
                              BREEDTE, HOOGTE),
                          dstrect=(0, 0, BREEDTE, HOOGTE),
                          angle=0)
        sdl2.SDL_DestroyTexture(texture)
        sdl2.SDL_FreeSurface(rotated_surface)

        # renderen laser
        if hit < 0.15:
            renderer.copy(explosion_texture,
                          srcrect=(0, 0, explosion_texture_size[0], explosion_texture_size[1]),
                          dstrect=(0, 0, BREEDTE, HOOGTE))

        if been_shot < 0.15:
            renderer.copy(laser_texture,
                          srcrect=(0, 0, laser_texture_size[0], laser_texture_size[1]),
                          dstrect=(
                              (BREEDTE - laser_texture_size[0] / 4) / 2, (HOOGTE - laser_texture_size[1] / 2) / 2,
                              laser_texture_size[0] / 4, laser_texture_size[1]))

        renderer.copy(fighter_textures_fov[index],
                      srcrect=(0, 0, fighter_textures_fov[index].size[0], fighter_textures_fov[index].size[1]),
                      dstrect=(0, 0, BREEDTE, HOOGTE))

        showAccessories(renderer, window)

        key_states = get_keyboard_state()
        if key_states[sdl2.SDL_SCANCODE_ESCAPE]:
            mission_failed(renderer, window)

        end_time = time.time()
        delta = end_time - start_time
        move_sprites(delta)
        showHealthbar(renderer, window)
        verwerk_input(delta)

        # Teken gemiddelde fps van de laatste 20 frames
        fps_list.append(1 / (time.time() - start_time))
        if len(fps_list) == 20:
            fps = np.average(fps_list)
            fps_list = []
        render_fps(fps, renderer)
        render_score(renderer)

        # Verwissel de rendering context met de frame buffer
        renderer.present()

    sdl2.ext.renderer.Renderer.destroy(s_renderer)


def mission_failed(renderer, window):
    global score

    sdl2.SDL_SetRelativeMouseMode(False)
    sdl2.SDL_ShowCursor(1)

    sdl2.sdlmixer.Mix_PlayChannel(0, sdl2.sdlmixer.Mix_LoadWAV(b'defeat/mission_failed.wav'), -1)

    back_ground = sdl2.ext.load_img("defeat/background.jpg")
    background = sdl2.ext.renderer.Texture(renderer, back_ground)

    mission_failed_texture = renderer_texture(renderer, failed_font, "you died")
    enter_your_name_texture = renderer_texture(renderer, enter_font, get_enter_name_msg())
    score_texture = renderer_texture(renderer, score_font, "score: " + str(score))
    show_highscore_texture = renderer_texture(renderer, score_font, get_highscore_msg())
    try_again_texture = renderer_texture(renderer, score_font, get_try_again_msg())
    quit_texture = renderer_texture(renderer, score_font, get_quit_msg())

    y_coordinate_enter_name = 200
    y_coordinate_show_highscore = 350
    y_coordinate_try_again = 480
    y_coordinate_quit = 600

    while not moet_afsluiten:
        renderer.clear()
        renderer_background(renderer, background, window)
        renderer_titles(renderer, mission_failed_texture, 0, window)
        renderer_titles(renderer, try_again_texture, y_coordinate_try_again, window)
        renderer_titles(renderer, quit_texture, y_coordinate_quit, window)
        renderer_titles(renderer, show_highscore_texture, y_coordinate_show_highscore, window)
        renderer_titles(renderer, enter_your_name_texture, y_coordinate_enter_name, window)
        renderer_off_titles(renderer, score_texture, 200, 250, window)

        username_surface = sdl2.ext.renderer.Texture(renderer, enter_font.render_text(newUsername))
        renderer.copy(username_surface, dstrect=((BREEDTE - username_surface.size[0]) / 2, 280,
                                                 username_surface.size[0], username_surface.size[1]))

        listen_to_btn_actions(renderer, get_enter_name_msg(), enter_your_name_texture, y_coordinate_enter_name, kleuren,
                              window)
        listen_to_btn_actions(renderer, get_highscore_msg(), show_highscore_texture, y_coordinate_show_highscore,
                              kleuren, window)
        listen_to_btn_actions(renderer, get_try_again_msg(), try_again_texture, y_coordinate_try_again, kleuren, window)
        listen_to_btn_actions(renderer, get_quit_msg(), quit_texture, y_coordinate_quit, kleuren, window)

        renderer.present()
        verwerk_input(0)


def show_highscores(renderer, window):
    with open("highscores.pkl", "rb") as in_:
        high_scores = pickle.load(in_)
    high_scores = dict(reversed(sorted(high_scores.items(), key=lambda item: item[1])))
    top_ten_high_scores = dict(itertools.islice(high_scores.items(), 10))

    y = 1

    back_ground = sdl2.ext.load_img("defeat/background.jpg")
    background = sdl2.ext.renderer.Texture(renderer, back_ground)

    highscore_texture = renderer_texture(renderer, menu_font, "highscores")
    rank_texture = renderer_texture(renderer, high_score_font, "rank")
    score_texture = renderer_texture(renderer, high_score_font, "score")
    name_texture = renderer_texture(renderer, high_score_font, "name")
    back_texture = renderer_texture(renderer, enter_font, get_back_msg())

    no_high_scores_texture = renderer_texture(renderer, high_score_font, "No highscores yet")

    y_coordinate = 100
    y_coordinate_score = 200
    renderer_background(renderer, background, window)

    renderer_titles(renderer, highscore_texture, 0, window)
    renderer_titles(renderer, back_texture, 700, window)
    renderer_off_titles(renderer, rank_texture, 75 + (rank_texture.size[0] / 2), y_coordinate, window)
    renderer_off_titles(renderer, score_texture, 250 + (score_texture.size[0] / 2), y_coordinate, window)
    renderer_off_titles(renderer, name_texture, 500 + (name_texture.size[0] / 2), y_coordinate, window)
    if len(high_scores) == 0:
        renderer_off_titles(renderer, no_high_scores_texture, 75 + (no_high_scores_texture.size[0] / 2),
                            y_coordinate_score, window)
    else:
        for x in range(1, 11):
            number_rank_texture = renderer_texture(renderer, high_score_font, f"{x}")
            renderer_off_titles(renderer, number_rank_texture, 75 + (number_rank_texture.size[0] / 2),
                                y_coordinate + (x * 50),
                                window)
        for name, score in top_ten_high_scores.items():
            username_texture = renderer_texture(renderer, high_score_font, name)
            points_texture = renderer_texture(renderer, high_score_font, str(score))
            renderer_off_titles(renderer, points_texture, 250 + (points_texture.size[0] / 2),
                                y_coordinate + (y * 50),
                                window)
            renderer_off_titles(renderer, username_texture, 500 + (username_texture.size[0] / 2),
                                y_coordinate + (y * 50),
                                window)
            y += 1

    while not moet_afsluiten:
        listen_to_btn_actions(renderer, get_back_msg(), back_texture, 700, kleuren, window)
        renderer.present()
        verwerk_input(0)


def move_sprites(delta):
    global richting_bewegen
    global p_speler

    index = 0
    aantal_muren = 0

    # beweeg sprite
    for pos in sprite_pos:
        if not sprite_init[index]:
            if world_map[math.floor(pos[0] - 0.6)][math.floor(pos[1])] == 0:
                richting_bewegen[index] = "N"
                aantal_muren += 1
            if world_map[math.floor(pos[0])][math.floor(pos[1] + 0.6)] == 0:
                richting_bewegen[index] = "O"
                aantal_muren += 1
            if world_map[math.floor(pos[0] + 0.6)][math.floor(pos[1])] == 0:
                richting_bewegen[index] = "Z"
                aantal_muren += 1
            if world_map[math.floor(pos[0])][math.floor(pos[1] - 0.6)] == 0:
                richting_bewegen[index] = "W"
                aantal_muren += 1
            sprite_init[index] = True

        if richting_bewegen[index] == "N" and aantal_muren < 3:
            pos[0] -= round(0.3 * delta, 2)
            if world_map[math.floor(pos[0] - 0.5)][math.floor(pos[1])] != 0:
                sprite_init[index] = False

        elif richting_bewegen[index] == "O" and aantal_muren < 3:
            pos[1] += round(0.3 * delta, 2)
            if world_map[math.floor(pos[0])][math.floor(pos[1] + 0.5)] != 0:
                sprite_init[index] = False

        elif richting_bewegen[index] == "Z" and aantal_muren < 3:
            pos[0] += round(0.3 * delta, 2)
            if world_map[math.floor(pos[0] + 0.5)][math.floor(pos[1])] != 0:
                sprite_init[index] = False

        elif richting_bewegen[index] == "W" and aantal_muren < 3:
            pos[1] -= round(0.3 * delta, 2)
            if world_map[math.floor(pos[0])][math.floor(pos[1] - 0.5)] != 0:
                sprite_init[index] = False
        index += 1


def main():
    global laser_texture
    # Initialiseer de SDL2 bibliotheek
    sdl2.ext.init()

    # Maak een venster aan om de game te renderen
    window = sdl2.ext.Window("Star Wars: Deathstar race", size=(BREEDTE, HOOGTE))
    window.show()

    # Show cursor
    sdl2.SDL_ShowCursor(1)

    # Begin met het uitlezen van input van de muis en vraag om relatieve coordinaten

    # Maak een renderer aan zodat we in ons venster kunnen renderen
    renderer = sdl2.ext.Renderer(window)
    laser_texture = sdl2.ext.renderer.Texture(renderer, laser_img)

    sdl2.sdlmixer.Mix_OpenAudio(22050, sdl2.AUDIO_S16SYS, 2, 4096)
    start_menu(renderer, window)

    # deallocate renderers and all acociated textures
    sdl2.ext.renderer.Renderer.destroy(renderer)
    # Sluit SDL2 af
    sdl2.ext.quit()


def get_mouse_state(mouse_x, mouse_y):
    return sdl2.SDL_GetMouseState(mouse_x, mouse_y)


def get_keyboard_state():
    return sdl2.SDL_GetKeyboardState(None)


def is_left_btn_pressed(mouse_state):
    return mouse_state == sdl2.SDL_BUTTON_LMASK


def renderer_background(renderer, background, window):
    renderer.copy(background, dstrect=(0, 0, BREEDTE, HOOGTE))


def renderer_titles(renderer, title_text, y_coordinate, window):
    renderer.copy(title_text, dstrect=(int((window.size[0] - title_text.size[0]) / 2), y_coordinate,
                                       title_text.size[0], title_text.size[1]))


def renderer_off_titles(renderer, title_text, x_coordinate, y_coordinate, window):
    renderer.copy(title_text, dstrect=(x_coordinate - title_text.size[0] / 2, y_coordinate,
                                       title_text.size[0], title_text.size[1]))


def renderer_score(renderer, score_text, y_coordinate, window):
    renderer.copy(score_text, dstrect=(int((BREEDTE - score_text.size[0]) / 2), y_coordinate,
                                       score_text.size[0], score_text.size[1]))


def renderer_action_buttons(renderer, action_button, y_coordinate, window):
    renderer.copy(action_button,
                  dstrect=(get_x_coordinate_for_action_buttons(window, action_button), y_coordinate,
                           action_button.size[0], action_button.size[1]))


def renderer_left_and_right_buttons(renderer, action_button, x_coordinate, y_coordinate):
    renderer.copy(action_button, dstrect=(x_coordinate, y_coordinate, action_button.size[0], action_button.size[1]))


def get_x_coordinate_for_action_buttons(window, action_button):
    return int((window.size[0] - action_button.size[0]) / 2)


def renderer_texture(renderer, font, msg):
    return sdl2.ext.renderer.Texture(renderer, font.render_text(msg))


def get_quit_msg():
    return "quit"


def get_play_msg():
    return "play"


def get_start_game_msg():
    return "start game!"


def get_left_msg():
    return "<"


def get_right_msg():
    return ">"


def get_try_again_msg():
    return "try again"


def get_enter_name_msg():
    return "enter your name"


def get_highscore_msg():
    return "show highscores"


def get_back_msg():
    return "back"


if __name__ == '__main__':
    # profiler = cProfile.Profile()
    # profiler.enable()
    main()
    # profiler.disable()
    # stats = pstats.Stats(profiler)
    # stats.dump_stats("data.prof")
