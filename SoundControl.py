
import pygame
from pygame import mixer

GameSound = True
pygame.init()
mixer.init()

# bgm
def play_bgm():
    if GameSound:
        mixer.music.set_volume(0.5)
    else:
        mixer.music.set_volume(0)
    mixer.music.load("Sounds/bgm.wav")
    mixer.music.set_volume(0.3)  # 0~1 之间调整音量
    mixer.music.play(-1)         # -1 表示无限循环

# place a piece
place_sound = mixer.Sound("Sounds/place.mp3")
place_sound.set_volume(0.5)

# win and lose
win_sound = mixer.Sound("Sounds/win.mp3")
lose_sound = mixer.Sound("Sounds/lose.wav")
win_sound.set_volume(0.5)
lose_sound.set_volume(0.5)

all_sounds = [place_sound, win_sound, lose_sound]

def play_win_lose_sound(this_player, winner):
    if winner == this_player:
        win_sound.play()
    elif winner != this_player:
        lose_sound.play()



