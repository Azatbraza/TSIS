import pygame, sys, json, random
from game import *
from db import *

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

# ---------- SETTINGS ----------
def load_settings():
    try:
        with open("settings.json") as f:
            return json.load(f)
    except:
        return {"snake_color":[0,255,0],"sound":True}

settings = load_settings()
snake_color = tuple(settings["snake_color"])
sound_on = settings["sound"]

# ---------- SOUNDS ----------
def load_sound(path):
    try: return pygame.mixer.Sound(path)
    except: return None

eat_sound = load_sound("assets/eat.wav")
poison_sound = load_sound("assets/poison.wav")
power_sound = load_sound("assets/power.wav")
dead_sound = load_sound("assets/death.wav")

init_db()

def text(t,x,y,c=(255,255,255)):
    screen.blit(font.render(t,True,c),(x,y))


# ---------- MENU ----------
def menu():
    name=""
    while True:
        screen.fill((0,0,0))
        text("MAIN MENU",260,120)
        text("Enter name:",260,180)
        text(name if name else "player",260,220,(0,255,0))
        text("1-Play  2-Leaderboard",180,300)
        text("3-Settings  4-Quit",180,340)
        pygame.display.update()

        for e in pygame.event.get():
            if e.type==pygame.QUIT: return "quit",""

            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_BACKSPACE:
                    name=name[:-1]
                elif e.key in (pygame.K_RETURN, pygame.K_1):
                    return "play", name if name else "player"
                elif e.key==pygame.K_2:
                    return "leaderboard",""
                elif e.key==pygame.K_3:
                    return "settings",""
                elif e.key==pygame.K_4:
                    return "quit",""
                else:
                    if e.unicode.isprintable():
                        name+=e.unicode


# ---------- GAME ----------
def game(username):

    best=get_best(username)

    snake=[(WIDTH//2,HEIGHT//2)]
    dx,dy=CELL,0
    next_dx,next_dy=dx,dy

    food=Food(); food.spawn(snake)
    poison=Poison(); poison.spawn(snake,[food.pos])
    power=None

    score,level=0,1
    eaten=0

    base_delay=160
    last=pygame.time.get_ticks()

    obstacles=[]
    active_power=None
    power_end=0

    while True:
        clock.tick(75)
        now=pygame.time.get_ticks()

        # 🔥 СКОРОСТЬ ОТ POWER
        current_delay = base_delay

        if active_power == "speed":
            current_delay = 80  # быстрее
        elif active_power == "slow":
            current_delay = 240  # медленнее

        # управление
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                return score,level

            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_UP and dy==0: next_dx,next_dy=0,-CELL
                if e.key==pygame.K_DOWN and dy==0: next_dx,next_dy=0,CELL
                if e.key==pygame.K_LEFT and dx==0: next_dx,next_dy=-CELL,0
                if e.key==pygame.K_RIGHT and dx==0: next_dx,next_dy=CELL,0

        # движение
        if now-last>current_delay:
            last=now
            dx,dy=next_dx,next_dy

            new_head=((snake[0][0]+dx)%WIDTH,(snake[0][1]+dy)%HEIGHT)
            head_rect=pygame.Rect(new_head[0],new_head[1],CELL,CELL)

            # 💥 СТОЛКНОВЕНИЕ
            if any(pygame.Rect(x,y,CELL,CELL).colliderect(head_rect) for x,y in snake+obstacles):
                if active_power=="shield":
                    active_power=None  # щит спас
                else:
                    if sound_on and dead_sound: dead_sound.play()
                    return score,level

            snake.insert(0,new_head)

            blocked=obstacles+[poison.pos]

            # исчезновение еды
            if now-food.spawn_time>5000:
                food.spawn(snake,blocked)

            # ЕДА
            if head_rect.colliderect(food.rect):
                score+=food.value
                eaten+=1
                if sound_on and eat_sound: eat_sound.play()
                food.spawn(snake,blocked)

                if eaten%5==0:
                    level+=1
                    base_delay=max(80,base_delay-10)

                    if level>=3:
                        obstacles=generate_obstacles(snake,blocked)

            # ЯД
            elif head_rect.colliderect(poison.rect):
                if sound_on and poison_sound: poison_sound.play()

                if len(snake)>2:
                    snake=snake[:-2]
                else:
                    return score,level

                poison.spawn(snake,blocked)

            # POWER
            elif power and head_rect.colliderect(power.rect):
                active_power=power.type
                power_end=now+5000
                if sound_on and power_sound: power_sound.play()
                power=None

            else:
                snake.pop()

        # таймер power
        if active_power and now>power_end:
            active_power=None

        # спавн power
        if not power and random.random()<0.01:
            power=PowerUp()
            power.spawn(snake,obstacles+[food.pos,poison.pos])

        if power and now-power.spawn_time>8000:
            power=None

        # РИСОВАНИЕ
        screen.fill((0,0,0))

        for s in snake:
            pygame.draw.rect(screen,snake_color,(*s,CELL,CELL))

        for o in obstacles:
            pygame.draw.rect(screen,(100,100,100),(*o,CELL,CELL))

        food.draw(screen)
        poison.draw(screen)
        if power: power.draw(screen)

        text(f"Score:{score}",10,10)
        text(f"Level:{level}",10,40)
        text(f"Best:{best}",10,70)

        if active_power:
            text(f"POWER: {active_power.upper()}",250,10)

        pygame.display.update()


# ---------- GAME OVER ----------
def game_over(score,level):
    while True:
        screen.fill((0,0,0))
        text("GAME OVER",260,250,(255,0,0))
        text(f"{score} lvl{level}",260,300)
        text("R-retry ESC-menu",200,380)
        pygame.display.update()

        for e in pygame.event.get():
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_r: return True
                if e.key==pygame.K_ESCAPE: return False


# ---------- MAIN ----------
while True:

    action,username=menu()

    if action=="quit":
        pygame.quit(); sys.exit()

    if action=="play":
        while True:
            score,level=game(username)
            save_score(username,score,level)
            if not game_over(score,level):
                break