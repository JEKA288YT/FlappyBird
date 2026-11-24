import sys
from random import randint
import numpy as np
import sounddevice as sd
from pygame import *

init()
window_width = 1200
window_height = 700
window = display.set_mode((window_width, window_height))
clock = time.Clock()


current_volume = 0.0
VOICE_THRESHOLD = 0.07

def audio_callback(indata, frames, time_info, status):
    global current_volume
    
    current_volume = np.linalg.norm(indata) / np.sqrt(len(indata))


stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=44100)
stream.start()


score_font = font.SysFont(None, 70)
score = 0
passed_pipes = []

bg_img = transform.scale(image.load('bg.png').convert(), (window_width, window_height))
player_img = transform.scale(image.load('bird.png').convert_alpha(), (80, 80))
pipe_img_raw = image.load('pipe.png').convert_alpha()

player_rect = Rect(80, 200, 80, 80)

def generate_pipes(count, pipe_width=140, gap=280, min_height=50, max_height=370, distance=650):
    pipes = []
    start_x = window_width
    for _ in range(count):
        height = randint(min_height, max_height)
        
        top_rect = Rect(start_x, 0, pipe_width, height)
        top_img = transform.flip(transform.scale(pipe_img_raw, (pipe_width, height)), False, True)
        
        bottom_height = window_height - (height + gap)
        bottom_rect = Rect(start_x, height + gap, pipe_width, bottom_height)
        bottom_img = transform.scale(pipe_img_raw, (pipe_width, bottom_height))
        
        pipes.append((top_rect, top_img))
        pipes.append((bottom_rect, bottom_img))
        start_x += distance
    return pipes

pipes = generate_pipes(150)
pipe_speed = 8
knockback_distance = 0

while True:
    for e in event.get():
        if e.type == QUIT:
            stream.stop()
            stream.close()
            quit()
            sys.exit()

    window.blit(bg_img, (0, 0))
    window.blit(player_img, player_rect)

    for pipe_rect, pipe_img in pipes[:]:
        if knockback_distance > 0:
            pipe_rect.x += 5
        else:
            pipe_rect.x -= pipe_speed

        window.blit(pipe_img, pipe_rect)

        if pipe_rect.y == 0 and pipe_rect.right < player_rect.left and id(pipe_rect) not in passed_pipes:
            score += 1
            passed_pipes.append(id(pipe_rect))

        if pipe_rect.x < -150:
            pipes.remove((pipe_rect, pipe_img))
            
        if player_rect.colliderect(pipe_rect) and knockback_distance <= 0:
            knockback_distance = 150

    if knockback_distance > 0:
        knockback_distance -= 5

    
    if current_volume > VOICE_THRESHOLD:
        if player_rect.top > 0:
            player_rect.y -= 6  
    else:
        if player_rect.bottom < window_height:
            player_rect.y += 5  

    
    bar_width = min(int(current_volume * 1000), 200)
    bar_color = (0, 255, 0) if current_volume > VOICE_THRESHOLD else (200, 200, 200)
    draw.rect(window, bar_color, (30, 30, bar_width, 20))
    draw.rect(window, (255, 255, 255), (30, 30, 200, 20), 2)

    
    score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
    window.blit(score_text, (window_width // 2 - score_text.get_width() // 2, 30))

    display.update()
    clock.tick(60)
