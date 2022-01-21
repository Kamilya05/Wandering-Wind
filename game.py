import os
import sys
import pygame


pygame.init()
size = width, height = 700, 500
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Wandering Wind')
clock = pygame.time.Clock()
FPS = 10
levels = 3

# все используемые в игре звуки
mixer = pygame.mixer
mixer.init()
open_chest_sound = mixer.Sound('data/sounds/chest.mp3')
open_chest_sound.set_volume(0.07)
open_door_sound = mixer.Sound('data/sounds/door.mp3')
open_door_sound.set_volume(0.2)
get_coin_sound = mixer.Sound('data/sounds/coin.mp3')
get_heart_sound = mixer.Sound('data/sounds/heart.mp3')
fire_sound = mixer.Sound('data/sounds/fire.mp3')
fire_sound.set_volume(0.05)
bg_music = mixer.Sound('data/sounds/bg.mp3')
bg_music.set_volume(0.05)
after_level_music = mixer.Sound('data/sounds/after_game.mp3')
after_level_music.set_volume(0.08)


def terminate():
    with open('save.txt', 'w') as file: # сохранение лучшего результата
        file.write(f'best_score={best_score}')
    pygame.quit()
    sys.exit()


def cursor():
    # смена дизайна курсора
    if pygame.mouse.get_focused():
        pygame.mouse.set_visible(False)
        screen.blit(pygame.transform.scale(cursor_image, (25, 25)), pygame.mouse.get_pos())


def load_image(name, colorkey=None):
    # загрузка изображения
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    im = pygame.image.load(fullname)
    if colorkey is not None:
        im = im.convert()
        if colorkey == -1:
            colorkey = im.get_at((0, 0))
        im.set_colorkey(colorkey)
    else:
        im = im.convert_alpha()
    return im


def load_several_images(name, n, form='.png'):
    # удобная загрузка изображений для спрайтов с анимацией (сердце, огонь)
    images = []
    for i in range(1, n + 1):
        images.append(load_image(name + str(i) + form))
    return images


def load_level(filename):
    filename = "data/levels/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y, exit_coords, guard, guard_activation_coords = None, None, None, None, None, []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('ground', x, y)
            elif level[y][x] == '=':
                guard_activation_coords.append((x, y))
                level_map[y] = level_map[y].replace('=', '#', 1)
                Tile('ground', x, y)
            elif level[y][x] == '-':
                Tile('bottom', x, y)
            elif level[y][x] == '_':
                Tile('wall', x, y)
            elif level[y][x] == 'l':
                Tile('wall_left', x, y)
            elif level[y][x] == 'L':
                Tile('bottom', x, y)
                Tile('wall_left', x, y)
            elif level[y][x] == 'r':
                Tile('wall_right', x, y)
            elif level[y][x] == 'R':
                Tile('bottom', x, y)
                Tile('wall_right', x, y)
            elif level[y][x] == 'b':
                Tile('ground', x, y)
                Tile('box', x, y)
            elif level[y][x] == 'd':
                Tile('wall', x, y)
                Tile('door2', x, y)
            elif level[y][x] == 'D':
                Tile('wall', x, y)
                Tile('door3', x, y)
                exit_coords = x, y + 1
            elif level[y][x] == 'h':
                Tile('ground', x, y)
                Heart(heart_images, x, y)
                level_map[y] = level_map[y].replace('h', '#', 1)
            elif level[y][x] == 'f':
                Tile('ground', x, y)
                Fire(fire_images, x, y)
            elif level[y][x] == '$':
                Tile('ground', x, y)
                Coin(coin_image, x, y)
                level_map[y] = level_map[y].replace('$', '#', 1)
            elif level[y][x] == 'c':
                Tile('ground', x, y)
                Chest(load_image(f'chest{lvl}.png'), x, y)
                level_map[y] = level_map[y].replace('c', '#', 1)
            elif level[y][x] == '@':
                Tile('ground', x, y)
                new_player = Player(x, y, 8, 1)
                level_map[y] = level_map[y].replace('@', '#', 1)
            elif level[y][x] == 'g':
                Tile('ground', x, y)
                guard = Guard(x, y, 8, 1)
                level_map[y] = level_map[y].replace('g', '#', 1)
    # вернем игрока, а также размер карты в клетках, координаты выхода,
    # стражника и координаты клеток, на которых он замечает главного персонажа
    return new_player, x, y, exit_coords, guard, guard_activation_coords


def draw_text(text, pos_x, pos_y, size_font, color):
    # функция для демнстрации текста
    font = pygame.font.Font(None, size_font)
    for line in text:
        text = font.render(line, True, color)
        rect = text.get_rect()
        rect.x = pos_x
        rect.top = pos_y
        pos_y += rect.height
        screen.blit(text, rect)


def move(player):
    # передвижения персонажа при нажатии определённых клавиш
    x, y = player.pos
    if key_up:
        if y > 0 and level_map[y - 1][x] in '#f':
            player.move(x, y - 1)
    if key_down:
        if y < level_y - 1 and level_map[y + 1][x] in '#f':
            player.move(x, y + 1)
    if key_left:
        player.side = False
        if x > 0 and level_map[y][x - 1] in '#f':
            player.move(x - 1, y)
    if key_right:
        player.side = True
        if x < level_x - 1 and level_map[y][x + 1] in '#f':
            player.move(x + 1, y)


def rules():
    # показ правил игры
    text = ["                                      ПРАВИЛА", '',
            "~  Вам нужно выбраться из лабиринта", '',
            "~  Чтобы перейти на следующий уровень, откройте дверь",
            "   ключом, который находится в сундуке", '',
            "~  Остерегайтесь огня и стражника", '',
            "~  Собранные монетки принесут дополнительные очки", '',
            "~  В начале игры у персонажа есть 3 жизни на прохождение",
            "   всех уровней", '',
            "~  Наберите как можно больше очков!"]
    fon = pygame.transform.scale(fon_image, (width, height))
    while True:
        screen.blit(fon, (0, 0))
        draw_text(text, 70, 35, 30, pygame.Color('grey'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 3 < x < 190 and 417 < y < 475:
                    return
        # кнопка подсвечивается при наведении
        x, y = pygame.mouse.get_pos()
        if 3 < x < 190 and 417 < y < 475:
            screen.blit(buttons_images[2], (3, 417))
        cursor()
        pygame.display.flip()


def win():
    # функция вызывается после прохождения всех уровней
    fon = pygame.transform.scale(win_image, (width, height))
    after_level_music.play()
    while True:
        screen.blit(fon, (0, 0))
        draw_text([str(best_score)], 390, 330, 35, 'grey')
        draw_text([str(score)], 390, 360, 50, 'pink')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 233 < x < 468 and 399 < y < 465:
                    after_level_music.stop()
                    return
        # кнопка подсвечивается при наведении
        x, y = pygame.mouse.get_pos()
        if 233 < x < 468 and 399 < y < 465:
            screen.blit(buttons_images[3], (233, 399))
        cursor()
        pygame.display.flip()


def game_over():
    # функция вызывается, если закончились жизни
    fon = pygame.transform.scale(losing_image, (width, height))
    after_level_music.play()
    while True:
        screen.blit(fon, (0, 0))
        draw_text([str(score)], 450, 175, 70, 'grey')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 155 < x < 516 and 362 < y < 475:
                    after_level_music.stop()
                    return
        # кнопка подсвечивается при наведении
        x, y = pygame.mouse.get_pos()
        if 155 < x < 516 and 362 < y < 475:
            screen.blit(buttons_images[4], (155, 362))
        cursor()
        pygame.display.flip()


def menu():
    global lvl, lives, score, best_score
    fon = pygame.transform.scale(begin_image, (width, height))
    bg_music.play()
    while True:
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 216 < x < 485 and 154 < y < 231:
                    # начало прохождения уровней
                    lvl = 0
                    lives = 3
                    score = 0
                    bg_music.stop()
                    while lvl != levels:
                        lvl += 1
                        open_door_sound.play()
                        if new_level():
                            score += 1000
                            if lvl == 3:
                                if score > best_score:
                                    best_score = score
                                win()
                                bg_music.play()
                        else:
                            if score > best_score:
                                best_score = score
                            game_over()
                            bg_music.play()
                            lvl = levels
                elif 215 < x < 484 and 254 < y < 331:
                    rules()
        # кнопки подсвечивается при наведении
        x, y = pygame.mouse.get_pos()
        if 216 < x < 485 and 154 < y < 231:
            screen.blit(buttons_images[0], (216, 154))
        elif 215 < x < 484 and 254 < y < 331:
            screen.blit(buttons_images[1], (215, 254))
        cursor()
        pygame.display.flip()


def new_level():
    # общая функция для всех уровней. Возвращает True при прохождении, False при проигрыше
    global all_sprites, up_group, player_group, level_map, player, level_x, level_y, guard, \
        guard_activation_coords, exit_coords, key_up, key_down, key_left, key_right
    all_sprites = pygame.sprite.Group()
    up_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    level_map = load_level(f'lvl_{lvl}.txt')  # загрузка карты
    player, level_x, level_y, exit_coords, guard, guard_activation_coords = generate_level(level_map)

    visual_heart = load_image('heart1.png')
    visual_key = pygame.transform.scale(load_image('key.png', -1), (35, 35))

    key_up = key_down = key_left = key_right = False
    keys = 0
    sound = True
    flag = False
    camera = Camera()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and flag:
                    return True
                if event.key == pygame.K_UP:
                    key_up = True
                if event.key == pygame.K_DOWN:
                    key_down = True
                if event.key == pygame.K_LEFT:
                    key_left = True
                if event.key == pygame.K_RIGHT:
                    key_right = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    key_up = False
                if event.key == pygame.K_DOWN:
                    key_down = False
                if event.key == pygame.K_LEFT:
                    key_left = False
                if event.key == pygame.K_RIGHT:
                    key_right = False
        move(player)

        if guard_activation_coords:  # если в уровень добавлен стражник, то на карте есть специальные
            if player.pos in guard_activation_coords:  # места для активации стражника
                guard.activation = True
            if guard.activation:  # если стражник не активен, то он стоит на месте,
                guard.move()  # а не гонится за персонажем

        camera.update(player)  # камера следит за персонажем
        for sprite in all_sprites:
            camera.apply(sprite)
        all_sprites.update()

        screen.fill('black')
        all_sprites.draw(screen)
        player_group.draw(screen)
        up_group.draw(screen)
        if lives == 0:  # если жизни кончились, то игрок проиграл
            return False
        if player.key and not keys:  # если игрок открыл сундук, то у него появляется ключ
            keys += 1

        # очки, жизни и количество ключей выводится сверху слева
        draw_text([f'SCORE: {score}', '',  f'lives:      x {lives}', f'keys:      x {keys}'],
                      player.rect.x - 310, player.rect.y - 210, 25, 'white')
        screen.blit(visual_heart, (67, 48))
        screen.blit(visual_key, (56, 58))

        if player.key and player.pos == exit_coords:  # если у игрока есть ключ и он находится на выходе
            Tile('door1', exit_coords[0], exit_coords[1] - 1)  # дверь открывается
            draw_text(['                  Нажмите "Enter",', 'чтобы перейти на следующий уровень'],
                      player.rect.x - 130, player.rect.y - 130, 25, 'pink')
            if sound:
                open_door_sound.play()
                sound = False
            flag = True
        else:
            if flag:
                open_door_sound.play()
                sound = True
            Tile('door3', exit_coords[0], exit_coords[1] - 1)
            flag = False

        pygame.display.flip()
        clock.tick(FPS)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None
        self.x, self.y = 0, 0

    def update(self):
        pass

    def get_event(self, event):
        pass


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.x, self.y = pos_x * tile_width, pos_y * tile_height


class Heart(Sprite):
    # класс сердца/жизней с анимацией
    def __init__(self, sheet, pos_x, pos_y):
        super().__init__((all_sprites, up_group))
        self.x, self.y = pos_x * tile_width + 17, pos_y * tile_height + 12
        self.frames = []
        self.frames = sheet
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.rect = self.rect.move(self.x, self.y)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

        if pygame.sprite.collide_mask(self, player):
            # при соприкосновении с героем сердце исчезает и +1 жизнь, +очки
            self.kill()
            get_heart_sound.play()
            global lives, score
            lives += 1
            score += 133


class Coin(Sprite):
    # класс монеток с анимацией
    def __init__(self, sheet, pos_x, pos_y):
        super().__init__((all_sprites, up_group))
        self.x, self.y = pos_x * tile_width + 17, pos_y * tile_height + 12
        self.frames = self.cut_sheet(sheet, 8, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.rect = self.rect.move(self.x, self.y)
        self.mask = pygame.mask.from_surface(self.image)

    def cut_sheet(self, sheet, columns, rows):
        # нарезка одного изображения на равные части
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        frames = []
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
        return frames

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if pygame.sprite.collide_mask(self, player):
            # при соприкосновении с героем монетка исчезает и +очки
            self.kill()
            get_coin_sound.play()
            global score
            score += 55


class Fire(Sprite):
    # класс огня с анимацией
    def __init__(self, sheet, pos_x, pos_y):
        super().__init__((all_sprites, up_group))
        self.x, self.y = pos_x * tile_width, pos_y * tile_height - 17
        self.pos = pos_x, pos_y
        self.frames = []
        self.frames = sheet
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.rect = self.rect.move(self.x, self.y)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

        # при соприкосновении с героем огонь исчезает и -1 жизнь
        if pygame.sprite.collide_mask(self, player):
            fire_sound.play()
            self.kill()
            x, y = self.pos
            level_map[y] = level_map[y][:x] + '#' + level_map[y][x + 1:]
            global lives
            lives -= 1


class Chest(Sprite):
    # класс сундука с анимацией
    def __init__(self, sheet, pos_x, pos_y):
        super().__init__((all_sprites, up_group))
        self.mod = False
        self.sheet = sheet
        self.x, self.y = pos_x * tile_width, pos_y * tile_height
        self.frames = self.cut_sheet(self.sheet, 5, 2)
        self.frames2 = self.cut_sheet(self.sheet, 5, 2, (1, 2))
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.rect = self.rect.move(self.x, self.y)
        self.mask = pygame.mask.from_surface(self.image)

    def cut_sheet(self, sheet, columns, rows, r=(0, 1)):
        # нарезка одного изображения на равные части
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        size = self.rect.width - 7, self.rect.height
        frames = []
        for j in range(*r):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(frame_location, size)))
        return frames

    def update(self):
        if not self.mod or self.cur_frame != 4:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.flip(self.frames[self.cur_frame], True, False)

            # при соприкосновении с героем сундук открывается и у героя появляется ключ
            if pygame.sprite.collide_mask(self, player) and not self.mod:
                self.mod = True
                player.key = True
                self.frames = self.frames2
                self.cur_frame = 0
                self.image = self.frames[self.cur_frame]
                open_chest_sound.play()
                global score
                score += 200


class Player(Sprite):
    # класс персонажа с двумя видами анимации
    def __init__(self, pos_x, pos_y, columns, rows):
        super().__init__((player_group, all_sprites))
        x, y = pos_x * tile_width, pos_y * tile_height - 20
        self.views = {'stand': self.cut_sheet(player_images['stand'], columns, rows),
                      'run': self.cut_sheet(player_images['run'], columns, rows)
                      }
        self.cur_view = 'stand'  # текущий вид анимации
        self.side = True  # персонаж повернут вправо
        self.frames = self.views[self.cur_view]
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect().move(x, y)
        self.pos = pos_x, pos_y
        self.x, self.y = x, y

        self.key = False  # наличие ключа

    def cut_sheet(self, sheet, columns, rows):
        # нарезка одного изображения на равные части
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        size = self.rect.size[0] - 174, self.rect.size[1]
        frames = []
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i + 87, self.rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(frame_location, size)))
        return frames

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)

        # смена вида анимации
        if (key_up or key_down or key_left or key_right) and self.cur_view != 'run':
            self.cur_frame = 0
            self.cur_view = 'run'
        elif not (key_up or key_down or key_left or key_right) and self.cur_view != 'stand':
            self.cur_frame = 0
            self.cur_view = 'stand'

        self.frames = self.views[self.cur_view]
        if self.side:  # повороты персонажа
            self.image = self.frames[self.cur_frame]
        else:
            self.image = pygame.transform.flip(self.frames[self.cur_frame], True, False)

    def move(self, x, y):
        # перемещения героя
        self.pos = x, y
        xx, yy = tile_width * x, tile_height * y - 20
        self.x, self.y = xx, yy
        self.rect = self.image.get_rect().move(xx, yy)


class Guard(Sprite):
    # класс стражника с двумя видами анимации
    def __init__(self, pos_x, pos_y, columns, rows):
        super().__init__((player_group, all_sprites))
        x, y = pos_x * tile_width - 10, pos_y * tile_height - 130
        self.views = {'stand': self.cut_sheet(guard_image['stand'], columns, rows),
                      'run': self.cut_sheet(guard_image['run'], columns, rows)}
        self.cur_view = 'stand'  # текущий вид анимации
        self.side = False  # персонаж повернут влево
        self.frames = self.views[self.cur_view]
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect().move(x, y)
        self.pos = pos_x, pos_y
        self.x, self.y = x, y
        self.timer = 3
        self.next_pos = self.next_xy = self.pos
        self.activation = False

    def cut_sheet(self, sheet, columns, rows):
        # нарезка одного изображения на равные части
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        size = self.rect.size[0] - 174, self.rect.size[1]
        frames = []
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i + 87, self.rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(frame_location, size)))
        return frames

    def update(self):
        # смена вида анимации
        if self.activation and self.cur_view == 'stand':
            self.cur_view = 'run'
            self.cur_frame = 0

        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.frames = self.views[self.cur_view]

        if self.side:  # поворот стражника
            self.image = self.frames[self.cur_frame]
        else:
            self.image = pygame.transform.flip(self.frames[self.cur_frame], True, False)
        if pygame.sprite.collide_mask(self, player):
            global lives
            lives = 0

    def find_path_step(self, start, target):
        # поиск кратчайшего пути к персонажу
        inf = 1000
        x, y = start
        distance = [[inf] * level_x for _ in range(level_y)]
        distance[y][x] = 0
        prev = [[None] * level_x for _ in range(level_y)]
        queue = [(x, y)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in (-1, 0), (1, 0), (0, -1), (0, 1):
                next_x, next_y = x + dx, y + dy
                if 0 < next_x < level_x and 0 < next_y < level_y and \
                        '#' in level_map[next_y][next_x] and distance[next_y][next_x] == inf:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
        x, y = target
        if distance[y][x] == inf or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y

    def move(self):
        # перемещения стражника, он движется в 3 раза медленнее игрока
        self.timer += 1
        if self.timer >= 3:
            self.timer = 0
            self.pos = self.next_pos
            self.x, self.y = self.pos[0] * tile_width - 10, self.pos[1] * tile_height - 130
            x, y = guard.find_path_step(self.pos, player.pos)
            if self.pos[0] > x:
                self.side = False
            elif self.pos[0] < x:
                self.side = True
            self.next_pos = x, y
            self.next_xy = x * tile_width - 10, y * tile_height - 130

        step = 16
        if self.x < self.next_xy[0]:
            self.x += step
        elif self.x > self.next_xy[0]:
            self.x -= step
        elif self.y < self.next_xy[1]:
            self.y += step
        elif self.y > self.next_xy[1]:
            self.y -= step


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x = obj.x + self.dx
        obj.rect.y = obj.y + self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.y + target.rect.h // 2 - height // 2)


tile_width = tile_height = 50

# загрузка всех используемых изображений для уровней
tile_images = {
    'ground': load_image('tile_#.png'),
    'bottom': load_image('tile_-.png'),
    'wall': load_image('tile__.png'),
    'wall_left': load_image('tile_l.png'),
    'wall_right': load_image('tile_r.png'),
    'box': load_image('tile_box.png'),
    'door1': load_image('tile_door1.png'),
    'door2': load_image('tile_door2.png'),
    'door3': load_image('tile_door3.png')
}
heart_images = load_several_images('heart', 8)
coin_image = load_image('coin.png')
fire_images = load_several_images('fire', 12)
player_images = {'stand': load_image('pers_8.png'),
                 'run': load_image('pers_run_8.png')}
guard_image = {'stand': load_image('guard.png'),
               'run': load_image('guard_run.png')}

# загрузка всех используемых изображений для заставок
begin_image = load_image('menu.png')
fon_image = load_image('fon.png')
win_image = load_image('congratulation.png')
losing_image = load_image('game_over.png')
buttons_images = load_several_images('btn', 5)
cursor_image = load_image('cursor.png')

# получение лучшего результата из файла
with open('save.txt') as file:
    best_score = int(file.read().split('=')[1])

# запуск игры
menu()
