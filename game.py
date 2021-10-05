# import cProfile
# import io
# import pstats
import random
import sys

import pygame


# def profile(fnc):
#     """A decorator that uses cProfile to profile a function"""
# 
#     def inner(*args, **kwargs):
#         pr = cProfile.Profile()
#         pr.enable()
#         retval = fnc(*args, **kwargs)
#         pr.disable()
#         s = io.StringIO()
#         sortby = 'cumulative'
#         ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#         ps.print_stats()
#         print(s.getvalue())
#         return retval
# 
#     return inner


global player_pos, heart_pos

# TODO:
#  1) break apart enemy
#  2) graphics: survival/endless, back button
#  X) rotate bushes (randomly or so they blend)

pygame.init()

s = 50
width = 1000
height = 600

button = (int(width / 2 - 100), int(height / 1.5 - 30))
button1 = (int(width / 2 - 100), int(height / 1.5 - 270))
button2 = (int(width / 2 - 100), int(height / 1.5 - 120))
button3 = (int(width / 2 - 100), int(height / 1.5 + 30))

screen = pygame.display.set_mode((width, height))

# loads images
bush = pygame.image.load('bush.jpg')
river = pygame.image.load('river.jpg')
orange_guy = pygame.image.load('orange guy.jpg')
red_guy = pygame.image.load('red guy.jpg')
yellow_guy = pygame.image.load('yellow guy.jpg')
rock = pygame.image.load('rock_wall.jpg')
over = pygame.image.load('combo.jpg')
reset_button = pygame.image.load('reset button.png')
easy_button = pygame.image.load('easy button.png')
normal_button = pygame.image.load('normal button.png')
hard_button = pygame.image.load('hard button.png')
bg = pygame.image.load('unnamed.jpg')
orange_background = pygame.image.load('orange background.png')
green_background = pygame.image.load('green background.png')
blue_background = pygame.image.load('blue background.png')

bush = pygame.transform.scale(bush, (s, s))
river = pygame.transform.scale(river, (s, s))
orange_guy = pygame.transform.scale(orange_guy, (s, s))
red_guy = pygame.transform.scale(red_guy, (s, s))
yellow_guy = pygame.transform.scale(yellow_guy, (s, s))
rock = pygame.transform.scale(rock, (s, s))
over = pygame.transform.scale(over, (s, s))
bg = pygame.transform.scale(bg, (width, height))
orange_background = pygame.transform.scale(orange_background, (width, height))
green_background = pygame.transform.scale(green_background, (width, height))
blue_background = pygame.transform.scale(blue_background, (width, height))

# load data
with open('data.txt', 'r') as data_file_r:
    easy_high_score = int(''.join(filter(str.isdigit, data_file_r.readline())))
    easy_best_combo = int(''.join(filter(str.isdigit, data_file_r.readline())))
    normal_high_score = int(''.join(filter(str.isdigit, data_file_r.readline())))
    normal_best_combo = int(''.join(filter(str.isdigit, data_file_r.readline())))
    hard_high_score = int(''.join(filter(str.isdigit, data_file_r.readline())))
    hard_best_combo = int(''.join(filter(str.isdigit, data_file_r.readline())))
    survival_high_score = int(''.join(filter(str.isdigit, data_file_r.readline())))

easy = [[easy_high_score], [easy_best_combo], 0]
normal = [[normal_high_score], [normal_best_combo], 1]
hard = [[hard_high_score], [hard_best_combo], 2]
survival = [[survival_high_score], [0], 3]

# empty data
last_key = ''
game = True
saved = True
difficulty = None
enemy_amount = None
aggro = None
reseted = False

total_time = 60

# ids
player = 0
heart = 1


def MenuScreen():
    screen.blit(blue_background, (0, 0))

    screen.blit(easy_button, button1)
    if (button1[0] <= pygame.mouse.get_pos()[0] <= button1[0] + 200
            and button1[1] <= pygame.mouse.get_pos()[1] <= button1[1] + 60):
        selected_button = pygame.Surface((200, 60))
        selected_button.set_alpha(25)
        selected_button.fill((0, 0, 0))
        screen.blit(selected_button, button1)
        if pygame.mouse.get_pressed()[0]:
            return easy

    screen.blit(normal_button, button2)
    if (button2[0] <= pygame.mouse.get_pos()[0] <= button2[0] + 200
            and button2[1] <= pygame.mouse.get_pos()[1] <= button2[1] + 60):
        selected_button = pygame.Surface((200, 60))
        selected_button.set_alpha(25)
        selected_button.fill((0, 0, 0))
        screen.blit(selected_button, button2)
        if pygame.mouse.get_pressed()[0]:
            return normal

    screen.blit(hard_button, button3)
    if (button3[0] <= pygame.mouse.get_pos()[0] <= button3[0] + 200
            and button3[1] <= pygame.mouse.get_pos()[1] <= button3[1] + 60):
        selected_button = pygame.Surface((200, 60))
        selected_button.set_alpha(25)
        selected_button.fill((0, 0, 0))
        screen.blit(selected_button, button3)
        if pygame.mouse.get_pressed()[0]:
            return hard
    if pygame.mouse.get_pressed()[0] and difficulty is None:
        return survival


def EnemyMoves(who, identification, restarted, e_a, error=False):
    right_free = True
    left_free = True
    up_free = True
    down_free = True
    right_kill = False
    left_kill = False
    up_kill = False
    down_kill = False
    hidden = False
    if not restarted:
        error = False

    if player_pos in bush_pos and difficulty != survival and difficulty != hard:
        hidden = True
    elif player_pos in bush_pos and (difficulty == hard) and len(e_a) == 2:
        hidden = True
    elif player_pos in bush_pos and (difficulty == survival or difficulty == hard) and random.random() <= aggro:
        hidden = True

    if random.random() >= aggro or len(e_a) == 0 or hidden or error:
        # random enemy movement
        e_a += [random.randrange(4)]

        if e_a[identification - 1] == 0:
            who[0] += s
        elif e_a[identification - 1] == 1:
            who[0] -= s
        elif e_a[identification - 1] == 2:
            who[1] += s
        elif e_a[identification - 1] == 3:
            who[1] -= s

    else:
        # checking surrounding for walls
        if [(who[0] + s), who[1]] in wall_pos or who[0] + s >= width:
            right_free = False
            if player_pos == who:
                right_kill = True
        if [(who[0] - s), who[1]] in wall_pos or who[0] - s <= - s:
            left_free = False
            if player_pos == who and random.random() <= aggro:
                left_kill = True
        if [who[0], (who[1] + s)] in wall_pos or who[1] + s >= height:
            down_free = False
            if player_pos == who and random.random() <= aggro:
                down_kill = True
        if [who[0], (who[1] - s)] in wall_pos or who[1] - s <= - s:
            up_free = False
            if player_pos == who and random.random() <= aggro:
                up_kill = True

        # moving towards player
        if (right_free and player_pos[0] > who[0]) or right_kill:
            who[0] += s
            e_a += [0]
        elif (left_free and player_pos[0] < who[0]) or left_kill:
            who[0] -= s
            e_a += [1]
        elif (down_free and player_pos[1] > who[1]) or down_kill:
            who[1] += s
            e_a += [2]
        elif (up_free and player_pos[1] < who[1]) or up_kill:
            who[1] -= s
            e_a += [3]
        else:
            error = True
            restarted = True
            EnemyMoves(who, identification, restarted, e_a, error)
    return e_a


def Collision(who, identification, e_a, l_k):
    end = None

    # checking surrounding for end of screen
    if who[1] >= height:
        end = 0
    elif who[1] <= - s:
        end = 1
    elif who[0] >= width:
        end = 2
    elif who[0] <= - s:
        end = 3

    if identification == 0 and (who in wall_pos or end is not None):
        # wall and end of screen collision player
        if l_k == 'a' or end == 3:
            who[0] += s
            l_k = 'd'
        elif l_k == 'd' or end == 2:
            who[0] -= s
            l_k = 'a'
        elif l_k == 'w' or end == 1:
            who[1] += s
            l_k = 's'
        elif l_k == 's' or end == 0:
            who[1] -= s
            l_k = 'w'
        else:
            raise SyntaxError
        return True, l_k

    elif identification == 1 and who in wall_pos or identification == 1 and end is not None:
        # wall collision enemy
        if e_a[0] == 0 or end == 2:
            who[0] -= s
            e_a[0] = 1
        elif e_a[0] == 1 or end == 3:
            who[0] += s
            e_a[0] = 0
        elif e_a[0] == 2 or end == 0:
            who[1] -= s
            e_a[0] = 3
        elif e_a[0] == 3 or end == 1:
            who[1] += s
            e_a[0] = 2
        else:
            raise SyntaxError
        return True, l_k
    elif identification >= 2 and (who in wall_pos or end is not None):
        # wall collision enemies
        if e_a[identification - 1] == 0 or end == 2:
            who[0] -= s
            e_a[identification - 1] = 1
        elif e_a[identification - 1] == 1 or end == 3:
            who[0] += s
            e_a[identification - 1] = 0
        elif e_a[identification - 1] == 2 or end == 0:
            who[1] -= s
            e_a[identification - 1] = 3
        elif e_a[identification - 1] == 3 or end == 1:
            who[1] += s
            e_a[identification - 1] = 2
        else:
            raise SyntaxError
        return True, l_k

    if identification == 0 and who in water_pos:
        # water collision player
        if l_k == 'a':
            who[0] -= s
        elif l_k == 'd':
            who[0] += s
        elif l_k == 'w':
            who[1] -= s
        elif l_k == 's':
            who[1] += s
        else:
            raise SyntaxError
        return True, l_k
    elif identification == 1 and who in water_pos:
        # water collision enemy1
        if e_a[0] == 0:
            who[0] += s
        elif e_a[0] == 1:
            who[0] -= s
        elif e_a[0] == 2:
            who[1] += s
        elif e_a[0] == 3:
            who[1] -= s
        else:
            raise SyntaxError
        return True, l_k
    elif identification >= 2 and who in water_pos:
        # water collision enemies
        if e_a[identification - 1] == 0:
            who[0] += s
        elif e_a[identification - 1] == 1:
            who[0] -= s
        elif e_a[identification - 1] == 2:
            who[1] += s
        elif e_a[identification - 1] == 3:
            who[1] -= s
        else:
            raise SyntaxError
        return True, l_k
    return False, l_k


def Images(over_screen, ended):
    # loads everything
    if timed_out:
        screen.blit(green_background, (0, 0))
        over_screen = True
    elif dead:
        screen.blit(orange_background, (0, 0))
        over_screen = True
    else:
        screen.blit(bg, (0, 0))

    if over_screen:
        screen.blit(reset_button, button)
        if (button[0] <= pygame.mouse.get_pos()[0] <= button[0] + 200
                and button[1] <= pygame.mouse.get_pos()[1] <= button[1] + 60):
            selected_button = pygame.Surface((200, 60))
            selected_button.set_alpha(25)
            selected_button.fill((0, 0, 0))
            screen.blit(selected_button, button)
            if pygame.mouse.get_pressed()[0]:
                ended = True

    if not timed_out and not dead:
        if heart_pos == player_pos:
            screen.blit(over, (player_pos[0], player_pos[1]))

        else:
            if heart_pos is not None:
                screen.blit(red_guy, heart_pos)
            screen.blit(yellow_guy, player_pos)
        for n in enemies:
            screen.blit(orange_guy, n)

        for x in range(len(bush_pos)):
            screen.blit(bush, (bush_pos[x][0], bush_pos[x][1]))
        for x in range(len(water_pos)):
            screen.blit(river, (water_pos[x][0], water_pos[x][1]))
        for x in range(len(wall_pos)):
            screen.blit(rock, (wall_pos[x][0], wall_pos[x][1]))
    return over_screen, ended


def Text(animation1=0, animation2=0, animation3=0, animation4=0, animation5=0):
    global white, white2, white3, white4

    if difficulty != survival:
        if timed_out or dead or score < high_score[0] or score == 0:
            font = pygame.font.SysFont('None', 35)
        else:
            font = pygame.font.SysFont('None', 35 - round(animation1))
            if animation1 < 15:
                animation1 += 0.75

        text1 = 'score: ' + str(score)
        label = font.render(text1, 1, white)
        screen.blit(label, (width - 990, height - 590))

        if timed_out or dead or score < high_score[0] or score == 0:
            font = pygame.font.SysFont('None', 20)
            white2 = white
        else:
            if white2 == (230, 230, 255):
                white2 = yellow
            font = pygame.font.SysFont('None', 20 + round(animation2))
            if animation2 < 15:
                animation2 += 0.75

        text2 = 'high score: ' + str(high_score[0])
        label = font.render(text2, 1, white2)
        screen.blit(label, (width - 990, height - 570))

        font = pygame.font.SysFont('None', 35)

        if not timed_out and not dead:
            text3 = 'time: ' + str(int(total_time - time / 1000))
        elif dead:
            text3 = 'time: ' + str(int(total_time - time_dead / 1000))
        else:
            if round(animation4) % 2 == 1 and timed_out:
                text3 = 'time: ' + str(int(0))
            else:
                text3 = ''
        label = font.render(text3, 1, white)
        screen.blit(label, (width - 200, height - 590))

        if not timed_out and not dead and (combo < best_combo[0] or best_combo[0] == 0):
            if animation3 > 0:
                animation3 -= 0.75
            font = pygame.font.SysFont('None', 35 - round(animation3))
        else:
            font = pygame.font.SysFont('None', 35 - round(animation3))
            if animation3 < 15:
                animation3 += 0.75

        text4 = 'combo: ' + str(combo)
        label = font.render(text4, 1, white)
        screen.blit(label, (width - 600, height - 590))

        if not timed_out and not dead and (combo < best_combo[0] or best_combo[0] == 0):
            if animation4 > 0:
                animation4 -= 1
            font = pygame.font.SysFont('None', 15 + round(animation4))
            white3 = white
        else:
            if white3 == (230, 230, 255):
                white3 = yellow
            font = pygame.font.SysFont('None', 15 + round(animation4))
            if animation4 < 15:
                animation4 += 0.75

        text5 = 'best total combo: ' + str(best_combo[0])
        label = font.render(text5, 1, white3)
        screen.blit(label, (width - 600, height - 550))

        if not timed_out and not dead and (combo < best_game_combo or best_game_combo == 0):
            if animation5 > 0:
                animation5 -= 1
            font = pygame.font.SysFont('None', 20 + round(animation5))
            white4 = white
        else:
            if white4 == (230, 230, 255):
                white4 = yellow
            font = pygame.font.SysFont('None', 20 + round(animation5))
            if animation5 < 15:
                animation5 += 0.75

        text6 = 'best combo: ' + str(best_game_combo)
        label = font.render(text6, 1, white4)
        screen.blit(label, (width - 600, height - 570))

    else:
        if dead or moves < high_score[0] or moves == 0:
            font = pygame.font.SysFont('None', 35)
        else:
            font = pygame.font.SysFont('None', 35 - round(animation1))
            if animation1 < 15:
                animation1 += 0.75

        text1 = 'moves: ' + str(moves)
        label = font.render(text1, 1, white2)
        screen.blit(label, (width - 990, height - 590))

        if timed_out or dead or moves < high_score[0] or moves == 0:
            font = pygame.font.SysFont('None', 20)
            if high_score[0] != 666:
                white = (230, 230, 255)
        else:
            if white == (230, 230, 255):
                white = yellow
            font = pygame.font.SysFont('None', 20 + round(animation2))
            if animation2 < 15:
                animation2 += 0.75

        text2 = 'most moves: ' + str(high_score[0])
        label = font.render(text2, 1, white)
        screen.blit(label, (width - 990, height - 570))


def SaveData():
    with open('data.txt', 'w') as data_file_w:
        data_file_w.write(f'easy_high_score = {easy[0][0]}\neasy_best_combo = {easy[1][0]}'
                          f'\nnormal_high_score = {normal[0][0]}\nnormal_best_combo = {normal[1][0]}'
                          f'\nhard_high_score = {hard[0][0]}\nhard_best_combo = {hard[1][0]}'
                          f'\nsurvival_high_score = {survival[0][0]}')
    return True


# @profile
def SpawnEnemies():
    global player_pos, heart_pos, bush_pos, wall_pos, water_pos, enemies, in_use
    # spawns everything

    if (200 / s) % 2 == 1:
        player_pos = [int((width - s) / 2), height - 2 * s]
        in_use[str(player_pos)] = 'player'
    elif (200 / s) % 2 == 0:
        player_pos = [int(width / 2), height - 2 * s]
        in_use[str(player_pos)] = 'player'
    else:
        player_pos = [0, 0]
        in_use[str(player_pos)] = 'player'

    for x in range(random.randrange(int(20000 / s ** 2 + 1))):
        space = [int(random.randint(0, int((width - s) / s)) * s), int(random.randint(0, int((height - s) / s)) * s)]
        if str(space) not in in_use:
            bush_pos.append(space)
            in_use[str(space)] = 'bush'

    bush_pos = list(map(list, set(map(tuple, bush_pos))))

    for x in range(random.randrange(int(30000 / s ** 2 + 1))):
        space = [int(random.randint(0, int((width - s) / s)) * s), int(random.randint(0, int((height - s) / s)) * s)]
        if str(space) not in in_use:
            wall_pos.append(space)
            in_use[str(space)] = 'wall'

    wall_pos = list(map(list, set(map(tuple, wall_pos))))

    for x in range(random.randrange(int(30000 / s ** 2 + 1))):
        space = [int(random.randint(0, int((width - s) / s)) * s), int(random.randint(0, int((height - s) / s)) * s)]
        if str(space) not in in_use:
            water_pos.append(space)
            in_use[str(space)] = 'water'

    water_pos = list(map(list, set(map(tuple, water_pos))))

    for e in range(enemy_amount):
        while True:
            space = [int(random.randint(0, int((width - s) / s)) * s),
                     int(random.randint(0, int((height - s) / s)) * s)]
            if str(space) not in in_use:
                enemies.append(space)
                in_use[str(space)] = 'enemies'
                break

    if difficulty == survival:
        heart_pos = None

    else:
        while True:
            heart_pos = [int(random.randint(0, int((width - s) / s)) * s),
                         int(random.randint(0, int((height - s) / s)) * s)]
            if str(heart_pos) not in in_use:
                in_use[str(heart_pos)] = 'heart'
                break


while game:
    for event in pygame.event.get():
        # X quits program
        if event.type == pygame.QUIT:
            sys.exit()

    if difficulty is None:
        difficulty = MenuScreen()

        pygame.display.update()
        continue

    high_score = difficulty[0]
    best_combo = difficulty[1]

    if difficulty == easy:
        aggro = 0.05
    elif difficulty == normal:
        aggro = 0.4
    elif difficulty == hard:
        aggro = 0.5
    elif difficulty == survival:
        aggro = 0

    if difficulty == hard:
        enemy_amount = 2
    else:
        enemy_amount = 1

    wall_pos = []
    bush_pos = []
    water_pos = []
    enemies = []
    enemy_action = []
    in_use = {}

    SpawnEnemies()

    time = 0
    clock = None

    white = (230, 230, 255)
    white2 = white
    white3 = white
    white4 = white
    yellow = (255, 255, 200)
    orange = (250, 155, 0)
    green = (50, 150, 75)
    red = (230, 50, 50)
    red2 = (255, 100, 50)

    ran = False
    collided = False
    moved = False
    moves = 0

    timed_out = False
    time_dead = 0
    dead = False
    game_over_screen = False

    score = 0
    combo = 0
    best_game_combo = 0

    game_over = False
    while not game_over:
        for event in pygame.event.get():
            # X quits program
            if event.type == pygame.QUIT:
                sys.exit()

            # detecting keys
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_d or event.key == pygame.K_RIGHT) and not dead and not timed_out:
                    player_pos[0] += s
                    last_key = 'd'
                    ran = True
                    break
                if (event.key == pygame.K_a or event.key == pygame.K_LEFT) and not dead and not timed_out:
                    player_pos[0] -= s
                    last_key = 'a'
                    ran = True
                    break
                if (event.key == pygame.K_w or event.key == pygame.K_UP) and not dead and not timed_out:
                    player_pos[1] -= s
                    last_key = 'w'
                    ran = True
                    break
                if (event.key == pygame.K_s or event.key == pygame.K_DOWN) and not dead and not timed_out:
                    player_pos[1] += s
                    last_key = 's'
                    ran = True
                    break
                if (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN) and (dead or timed_out):
                    game_over = True
                if (event.key == pygame.K_ESCAPE) and (dead or timed_out):
                    game_over = True
                    difficulty = None

        # measures time
        if moves == 1:
            clock = pygame.time.Clock()
            moved = True
        if moved:
            time += clock.tick(30)

        if ran:
            # collisions
            collided, last_key = Collision(player_pos, player, enemy_action, last_key)
            while collided:
                collided, last_key = Collision(player_pos, player, enemy_action, last_key)

            moves += 1
            enemy_action = []

            if heart_pos is not None:
                enemy_action = EnemyMoves(heart_pos, heart, reseted, enemy_action)
                collided, last_key = Collision(heart_pos, heart, enemy_action, last_key)
                while collided:
                    collided, last_key = Collision(heart_pos, heart, enemy_action, last_key)
            else:
                enemy_action += [None]

            for e, m in zip(enemies, range(len(enemies))):
                enemy_action = EnemyMoves(e, m + 2, reseted, enemy_action)
                if difficulty == survival:
                    aggro += 0.1
            for e, m in zip(enemies, range(len(enemies))):
                collided, last_key = Collision(e, m + 2, enemy_action, last_key)
                while collided:
                    collided, last_key = Collision(e, m + 2, enemy_action, last_key)

            if difficulty == survival:
                aggro = 0

            # spawns enemies and spawns and despawns bushes
            if difficulty == survival:
                if moves % 20 == 0 and enemy_amount < 12:
                    repeat = 0
                    while True:
                        space = [int(random.randint(0, int((width - s) / s)) * s),
                                 int(random.randint(0, int((height - s) / s)) * s)]
                        if str(space) not in in_use:
                            enemies.append(space)
                            in_use[str(space)] = 'enemies'
                            enemy_amount += 1
                            break
                        repeat += 1
                        if repeat == 50:
                            break

                if random.random() <= 0.11 and len(bush_pos) != 0:
                    bush_pos.remove(random.choice(bush_pos))

                if random.random() <= 0.1 and len(bush_pos) <= 16:
                    repeat = 0
                    while True:
                        space = [int(random.randint(0, int((width - s) / s)) * s),
                                 int(random.randint(0, int((height - s) / s)) * s)]
                        if str(space) not in in_use:
                            bush_pos.append(space)
                            in_use[str(space)] = 'bush'
                            break
                        repeat += 1
                        if repeat == 50:
                            break

            # checks if you died
            if player_pos in enemies:
                dead = True
                white = red
                white2 = red
                white3 = red
                white4 = red

            if difficulty == survival and moves == 666:
                white2 = red
            else:
                white2 = (230, 230, 255)
            if difficulty == survival and high_score[0] == 666:
                white = red

            # points
            if heart_pos == player_pos:
                combo += 1
                score += 1
            else:
                combo = 0
            if score > high_score[0] and difficulty != survival:
                high_score[0] += score - high_score[0]
                saved = False
            elif moves > high_score[0] and difficulty == survival:
                high_score[0] += moves - high_score[0]
                saved = False
            if combo > best_game_combo:
                best_game_combo = combo
            if combo > best_combo[0]:
                saved = False
                best_combo[0] += combo - best_combo[0]

            ran = False

        # time out
        if time / 1000 >= total_time and not dead and difficulty != survival:
            timed_out = True
            white = red2
            white2 = red2
            white3 = red2
            white4 = red2

        game_over_screen, game_over = Images(game_over_screen, game_over)
        Text()

        if not saved and (timed_out or dead):
            saved = SaveData()

        pygame.display.update()
