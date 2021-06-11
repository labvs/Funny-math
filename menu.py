import pygame
import sys
import time
import random
import sqlite3
import os
import game
from preview import Numbers
from input_box import InputBox
from moviepy.editor import VideoFileClip
from moviepy.editor import AudioFileClip 

# инициализация переменных, отвечающих за цвета
gray         = (119, 118, 110)
black        = (0,     0,   0)
white        = (255, 255, 255)
red          = (255,   0,   0)
green        = (0,   200,   0)
blue         = (0,     0, 200)
bright_red   = (255,   0,   0)
bright_green = (0,   255,   0)
bright_blue  = (0,     0, 255)
light_gray   = (200, 200, 200)
light_blue   = (51,  204, 255)
intro_color  = (41,  201, 255)
#инициализация PyGame
pygame.init()

#установка полноэкранного режима
gamedisplays   = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
display_width  = gamedisplays.get_width()
display_height = gamedisplays.get_height()

#внешний вид окна (название, иконка) 
pygame.display.set_caption("Математика")
icon = pygame.image.load('resources/img/calc.ico')
pygame.display.set_icon(icon)
image = pygame.image.load('resources/img/logo.png').convert_alpha()
image = pygame.transform.scale(image, (600, 200))

#создание переменной для отслеживания времени
clock = pygame.time.Clock()

#создание переменных, отвечающих за фоновые изображения
backgroundpic = pygame.image.load("resources/img/full.jpg")
backgroundpic = pygame.transform.scale(backgroundpic, (display_width, display_height))
instruction_background = pygame.image.load("resources/img/blue.jpg")
instruction_background = pygame.transform.scale(instruction_background, (display_width, display_height))

#добавление фоновой музыки при запуске программы
pygame.mixer.music.load(r'resources/music/Music.wav')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.01)

#подключение к базе данных
conn = sqlite3.connect('resources/scores.db')
cur = conn.cursor()

#задание шрифтов
font = pygame.font.SysFont('arial', 32)
largetext = pygame.font.Font('resources/fonts/20421.ttf', 100)
smalltext = pygame.font.Font('resources/fonts/20421.ttf', 55)
mediumtext = pygame.font.Font('resources/fonts/20421.ttf', 80)

#создание таблицы базы данных, если такой не существует
cur.execute("""CREATE TABLE IF NOT EXISTS users(
       `Имя` TEXT NOT NULL,
       `Фамилия` TEXT NOT NULL,
       `Дата` timestamp,
       `Режим` TEXT,
       `Оценка` INT,
       `Счет` INT,
       CONSTRAINT new_pk PRIMARY KEY (Имя, Фамилия, Дата)
       );
    """)
conn.commit()

# инициализация переменных
name_surn = ""
level = "легкий"
max_numbers = 100

# главное меню
def main_menu():
    '''
    Функция отрисовывает главное меню игры
    Выходные данные: отображение пунктов главного меню на экране
    '''
    clock = pygame.time.Clock()
    menu = True
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                check_for_exit(event)
        gamedisplays.blit(backgroundpic, (0, 0))
        # отрисовка текста
        TextSurf, TextRect = text_objects("", largetext)
        TextRect.center = (display_width/2, 150)
        gamedisplays.blit(TextSurf, TextRect)
        # отрисовка кнопок главного меню и присваивание им названия событий
        button("ИГРАТЬ",     display_width / 2 - 200,   display_height/9, 400, display_height/6, blue, bright_blue,  "play")
        button("РЕЙТИНГ",    display_width / 2 - 200,   display_height/3, 400, display_height/6, blue, bright_blue, "score")
        button("УПРАВЛЕНИЕ", display_width / 2 - 200, 5*display_height/9, 400, display_height/6, blue, bright_blue, "intro")
        button("ВЫХОД",      display_width / 2 - 200, 7*display_height/9, 400, display_height/10, blue, bright_blue,  "quit")
        
        pygame.display.update()
        # игра будет работать со скоростью не более 50 кадров в секунду
        clock.tick(50)

def button(msg, x, y, w, h, ic, ac, action=None):
    '''
    Функция отрисовывает кнопки по указанным координатам и проверяет, какая из них была нажата
    Входные данные: msg - название кнопки, x - положение по горизонтали,
    y - положение по вертикали, w - длина кнопки,
    h - ширина, ic и ac - цвета кнопки, action - событие
    Выходные данные: запуск события (функции), за которое отвечает кнопка
    '''
    name = name_surn
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    global level
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(gamedisplays, ac, (x, y, w, h), border_radius = 15)
        if click[0] == 1 and action != None:
            if action == "play":
                setting(name, level)
            if action == "score":
                # отображение рейтинга игроков
                score(1)
            elif action == "quit":
                cur.close()
                pygame.quit()
                sys.exit()
            elif action == "intro":
                instruction()
            elif action == "menu":
                main_menu()
            elif action == "level":
                if(len(name_surn.split()) != 2):
                    setting("Введи свои данные!", level)
                else:
                    levels()
            elif action == "change":
               setting(name_surn, level)
            elif action == "video":
               # запуск видеоклипа
               clip = VideoFileClip('resources/video/Demonstratsia.mp4')
               clip = clip.resize(width = display_width)
               clip.preview()
               pygame.display.set_mode((display_width, display_height))
               pygame.mixer.music.load(r'resources/music/Music.wav')
               pygame.mixer.music.play(-1)
               pygame.mixer.music.set_volume(0.01)
            elif action == "next":
                # отображение рейтинга игроков
               score(3)
            elif action == "search":
               # поиск игрока в таблице рейтинга
               if len(name_surn.split()) != 2:
                    print("Error!")
               else:
                    score(2)
            elif action == "sound":
               # запуск фоновой музыки, если она поставлена на паузу
               pygame.mixer.music.unpause()
            elif action == "sound_stop":
               # поставить фоновую музыку на паузу
               pygame.mixer.music.pause()
            elif action == "lite":
               level = "легкий"
               setting(name_surn, level)
            elif action == "medium":
               level = "средний"
               setting(name_surn, level)
            elif action == "hard":
               level = "сложный"
               setting(name_surn, level)
            elif action == "addition":
               game.start(name_surn, level, 1)
            elif action == "subtraction":
               game.start(name_surn, level, 2)
            elif action == "multiplication":
               game.start(name_surn, level, 3)
            elif action == "division":
               game.start(name_surn, level, 4)
            else:
               game.start(name_surn, level, 5)
    else:
        pygame.draw.rect(gamedisplays, ic, (x, y, w, h), border_radius=15)
    textsurf, textrect = text_objects(msg, smalltext)
    textrect.center = ((x + (w / 2)), (y + (h / 2)))
    gamedisplays.blit(textsurf, textrect)

def text_objects(text, font):
    '''
    Функция передает параметры для отрисовки текста
    Входные данные: text - текст, font - шрифт
    Выходные данные: textsurface – отвечает за отрисовку текста на экране, textsurface.get_rect() - прямоугольник, его размеры соответствуют размерам поверхности textsurface
    '''
    textsurface = font.render(text, True, white)
    return textsurface, textsurface.get_rect()

def levels():
    '''
    Функция отвечает за выбор режима игры
    Выходные данные: отображение доступных режимов на экране
    '''
    levels = True
    while levels:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                check_for_exit(event)
        gamedisplays.blit(backgroundpic, (0, 0))

        # отрисовка текста
        pygame.draw.rect(gamedisplays, blue, (0, 0, display_width, 100))
        TextSurf,TextRect = text_objects("ВЫБЕРИ РЕЖИМ:", largetext)
        TextRect.center = ((display_width / 2),(50))
        gamedisplays.blit(TextSurf,TextRect)

        button("СЛОЖЕНИЕ",  display_width / 2 - 200,   display_height/6, 400, display_height/8, blue, bright_blue, "addition")
        button("ВЫЧИТАНИЕ", display_width / 2 - 200,   display_height/3, 400, display_height/8, blue, bright_blue, "subtraction")
        button("УМНОЖЕНИЕ", display_width / 2 - 200,   display_height/2, 400, display_height/8, blue, bright_blue, "multiplication")
        button("ДЕЛЕНИЕ",   display_width / 2 - 200, 2*display_height/3, 400, display_height/8, blue, bright_blue, "division")
        button("СМЕШАННЫЙ", display_width / 2 - 200, 5*display_height/6, 400, display_height/8, blue, bright_blue, "all")
        button("НАЗАД",display_width*0.75, display_height*0.75, 350, 100, blue, bright_blue, "menu")
        pygame.display.update()
        clock.tick(50)
    
def instruction():
    '''
    Функция отвечает за отображение инструкции
    Выходные данные: отображение текста инструкции на экране
    '''
    instruction = True
    while instruction:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                check_for_exit(event)
                
        gamedisplays.blit(instruction_background, (0, 0))
        pygame.draw.rect(gamedisplays, blue, (0, 0, display_width, 100))
        TextSurf, TextRect = text_objects("УПРАВЛЕНИЕ", largetext)
        TextRect.center = ((display_width / 2), 60)
        gamedisplays.blit(TextSurf, TextRect)
        
        ktextSurf, ktextRect = text_objects("Перед началом игры убедись, что камера подключена!", smalltext)
        ktextRect.center = ((display_width/2), (175))
        gamedisplays.blit(ktextSurf, ktextRect)

        textSurf, textRect = text_objects("Управлять игрой можно с помощью жестов!", smalltext)
        textRect.center = ((display_width / 2), (250))
        gamedisplays.blit(textSurf, textRect)

        sTextSurf, sTextRect = text_objects("МАХНИ", mediumtext)
        sTextRect.center = ((display_width / 2), 325)
        gamedisplays.blit(sTextSurf, sTextRect)
        
        stextSurf, stextRect = text_objects("ВЛЕВО и ВВЕРХ, если правильный ответ в СИНЕМ квадрате.", smalltext)
        stextRect = (0, 375)
        gamedisplays.blit(stextSurf, stextRect)
        
        hTextSurf, hTextRect = text_objects("ВПРАВО и ВВЕРХ - если в ЖЁЛТОМ.", smalltext)
        hTextRect = (0, 475)
        gamedisplays.blit(hTextSurf, hTextRect)
        
        atextSurf, atextRect = text_objects("ВЛЕВО и ВНИЗ - если в ЗЕЛЁНОМ.", smalltext)
        atextRect = (0, 575)
        gamedisplays.blit(atextSurf, atextRect)
        
        rtextSurf, rtextRect = text_objects("ВПРАВО и ВНИЗ - если в КРАСНОМ.", smalltext)
        rtextRect = (0, 675)
        gamedisplays.blit(rtextSurf, rtextRect)
        
        RtextSurf, RtextRect = text_objects("Посмотреть, как играть:", smalltext)
        RtextRect = (0, display_height - 55)
        gamedisplays.blit(RtextSurf, RtextRect)
        
        button(">",display_width/2 - 50, display_height - 60, 100, 55, blue, bright_blue, "video")
        
        button("НАЗАД",display_width*0.75, display_height*0.75, 350, 100, blue, bright_blue, "menu")
        pygame.display.update()
        clock.tick(30)

def mysql(mode, arr):
    '''
    Функция отправляет запрос и получает информацию из базы данных
    Входные данные: mode - режим, arr - список
    Выходные данные: arr - список с результатами, вносятся данные по трем лучшим игрокам для выбранного режима
    '''
    cur.execute("SELECT Имя, Фамилия, SUM(Счет) FROM USERS Where Режим = " + mode + " GROUP BY Имя, Фамилия ORDER BY SUM(Счет) DESC LIMIT 3;")
    records = cur.fetchall()
    for row in records:
            arr.append(str(row[0]) + " " + str(row[1]) + " - " + str(row[2]))
    # если в списке меньше трех игроков, то заполняем пустой строкой
    while(len(arr) < 3):
        arr.append("")
        
def search(name, surname, arr1):
    '''
    Функция ищет данные о всех играх определенного игрока
    Входные данные: name - имя игрока, surname - фамилия игрока, arr1 - список
    Выходные данные: arr1 - список с результатами, в него вносятся данные по всем играм конкретного игрока
    '''
    cur.execute("SELECT Дата, Режим, Оценка, Счет FROM USERS Where Имя =" + "'" + str(name)+ "'" + " AND Фамилия ="+ "'" +str(surname)+ "'" + "ORDER BY Дата DESC")
    records = cur.fetchall()
    for row in records:
            arr1.append(str(row[0]) + " " + str(row[1]) + " " + str(row[2]) + "(" + str(row[3])+ ")")

def text(words, x, y, size):
    '''
    Функция отвечает за отображение текста на экране
    Входные данные: words - слова, x, y - положение текста на экране, size - размер шрифта
    Выходные данные: отображение текста с заданным размером в указанном месте
    '''
    font = pygame.font.Font('resources/fonts/20421.ttf', size)
    text = font.render("{}".format(words), True, 'white')
    return gamedisplays.blit(text, (x, y))

def score(choice):
    '''
    Функция отвечает за отображение рейтинга игрока
    Входные данные: choice - выбранный игроком способ отображения рейтинга
    Выходные данные: отображение на экране рейтинга всех игроков или отображение всех игр введенного пользователя
    '''
    # создание поля для ввода имени и фамилии игрока
    input_box = InputBox(display_width*2/3 + 60, display_height/6 + 100, 250, 52)
    input_boxes = [input_box]
    clock = pygame.time.Clock()
    arr = []
    arr1 = []
    global name_surn
    if(choice == 1):
        name_surn = ""
        mysql("'Сложение'",  arr)
        mysql("'Умножение'", arr)
        mysql("'Вычитание'", arr)
    if(choice == 2):
        search(name_surn.split()[0], name_surn.split()[1], arr1)
    if(choice == 3):
        arr = []
        mysql("'Деление'", arr)
        mysql("'Смешанный'", arr)
    scores = True
    while scores:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                check_for_exit(event)
            for box in input_boxes:
                text = box.handle_event(event)
            textSurf, textRect = text_objects(text, largetext)
            textRect.center = (display_width / 2, (150))

        for box in input_boxes:
            box.update()
            name_surn = box.update()

        gamedisplays.blit(instruction_background, (0, 0))
        pygame.draw.rect(gamedisplays, blue, (display_width*2/3,display_height/8, display_width/3, 325), border_radius = 15) 
        for box in input_boxes:
            box.draw(gamedisplays)

        # отображение текста на заданной поверхности
        textSurf, textRect = text_objects("Мои результаты", smalltext)
        textRect.center = (display_width*5/6, display_height/6)
        gamedisplays.blit(textSurf, textRect)

        textSurf, textRect = text_objects("(имя, фамилия)", smalltext)
        textRect.center = (display_width*5/6, display_height/6 + 50)
        gamedisplays.blit(textSurf, textRect)

        # отрисовка кнопок "ок" и "Сброс"
        button("Ок",display_width*0.75, 350, 100, 55, blue, bright_blue, "search")
        button("Сброс",display_width*0.75 + 150, 350, 150, 55, blue, bright_blue, "score")

        pygame.draw.rect(gamedisplays, blue, (0, 0, display_width, 100))
        TextSurf, TextRect = text_objects("РЕЙТИНГ", largetext)
        TextRect.center = (display_width / 2, 60)
        gamedisplays.blit(TextSurf, TextRect)

        if(choice == 1):
            height = display_height / 5
            stextSurf, stextRect = text_objects("СЛОЖЕНИЕ", smalltext)
            stextRect.center = ((display_width / 2), display_height / 6)
            gamedisplays.blit(stextSurf, stextRect)
            i = 0
            numb = 3
            if len(arr) == 0:
                lines = ""
            else:
                # вывод построчно элементов списка на экран по каждому режиму
                for lines in arr: 
                    ptextSurf, ptextRect = text_objects(lines, smalltext)
                    ptextRect = (0, height)
                    gamedisplays.blit(ptextSurf, ptextRect)
                    height = height + 50
                    i = i + 1
                    if i == numb:
                        operation = "УМНОЖЕНИЕ"
                        height = height + 50
                        stextSurf, stextRect = text_objects(operation, smalltext)
                        stextRect.center = ((display_width / 2), height)
                        gamedisplays.blit(stextSurf, stextRect)
                        height = height + 32
                    elif i == numb*2:
                        operation = "ВЫЧИТАНИЕ"
                        height = height + 50
                        stextSurf, stextRect = text_objects(operation, smalltext)
                        stextRect.center = ((display_width / 2), height)
                        gamedisplays.blit(stextSurf, stextRect)
                        height = height + 32

            # кнопка позволяет перейти на страницу с результатами по режимам "деление" и "смешанный"
            button(">",display_width*0.75, display_height*0.75 - 100, 100, 55, blue, bright_blue, "next")

        if(choice == 2):
            height = display_height / 5
            # отображение на экране фамилии и имени указанного иргока
            stextSurf, stextRect = text_objects(name_surn, smalltext)
            stextRect.center = ((display_width / 3), display_height/6)
            gamedisplays.blit(stextSurf, stextRect)
            if len(arr1) == 0:
                lines = ""
            else:
                # построчное отображение на экране списка всех завершенных игр указанного пользователя
                for lines in arr1: 
                    ptextSurf, ptextRect = text_objects(lines, smalltext)
                    ptextRect = (0, height)
                    gamedisplays.blit(ptextSurf, ptextRect)
                    height = height + 50

        if(choice == 3):
            height = display_height / 5
            stextSurf, stextRect = text_objects("ДЕЛЕНИЕ", smalltext)
            stextRect.center = ((display_width / 2), display_height/6)
            gamedisplays.blit(stextSurf, stextRect)
            i = 0
            numb = 3
            if len(arr) == 0:
                lines = ""
            else:
                for lines in arr:
                    ptextSurf, ptextRect = text_objects(lines, smalltext)
                    ptextRect = (0, height)
                    gamedisplays.blit(ptextSurf, ptextRect)
                    height = height + 50
                    i = i + 1
                    if i == numb:
                        operation = "СМЕШАННЫЙ"
                        height = height + 50
                        stextSurf, stextRect = text_objects(operation, smalltext)
                        stextRect.center = ((display_width / 2), height)
                        gamedisplays.blit(stextSurf, stextRect)
                        height = height + 32
            button("<",display_width*0.75, display_height*0.75 - 100, 100, 55, blue, bright_blue, "score")           
        button("НАЗАД",display_width*0.75, display_height*0.75, 350, 100, blue, bright_blue, "menu")
        pygame.display.update()
        clock.tick(30)

def setting(name, level):
    '''
    Функция отвечает за игровые настройки пользователя: включить/выключить звук, выбрать уровень, ввести свои данные
    Входные данные: name - имя игрока, level - выбранный уровень
    Выходные данные: установка параметров, присвоение переменным значений, отвечающих за настройки игрового процесса
    '''
    clock = pygame.time.Clock()
    # создание поля для ввода имени и фамилии игрока
    input_box1 = InputBox(55, display_height/4 + 100, 250, 52)
    input_boxes = [input_box1]
    main = True
    global name_surn
    while main:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                check_for_exit(event)
            for box in input_boxes:
                box.handle_event(event)

        for box in input_boxes:
            box.update()
            # присвоение переменной данных из поля для ввода
            name_surn = box.update()

        gamedisplays.blit(instruction_background, (0, 0))
        pygame.draw.rect(gamedisplays, blue, (50, display_height/4, display_width/3 - 100, 200), border_radius = 15)
        for box in input_boxes:
            box.draw(gamedisplays)

        text("ИГРОК:", display_width/12, 125, 80)
        text("ЗВУК:", display_width/12 + 40, 2*display_height/3, 80)
        text("УРОВЕНЬ:", display_width/3 + 100, 125 , 80)
        pygame.draw.rect(gamedisplays, blue, (0, 0, display_width, 100))
        
        pygame.draw.line(gamedisplays, blue, (display_width/3, 0), (display_width/3, display_height), 5)
        pygame.draw.line(gamedisplays, blue, (2*display_width/3, 0), (2*display_width/3, display_height), 5)

        TextSurf, TextRect = text_objects("ВВЕДИ ИМЯ И ФАМИЛИЮ:", largetext)
        TextRect.center = (display_width / 2, (50))
        text(name,2*display_width/3 + 15, 200, 45)
        gamedisplays.blit(TextSurf,TextRect)

        text("ТВОИ ИМЯ И", 100, display_height/4, 50)
        text("ФАМИЛИЯ: ", 115, display_height/4 + 50, 50)
        text("уровень: " + level, 2*display_width/3 + 15, 250, 45)

        button("ок", 50, display_height/4 + 225, display_width / 3 - 100, 75, blue, bright_blue, "change")
        # кнопки для влючения/выключения звука
        button("вкл", 75, 2*display_height/3 + 100, 150, 75, blue, bright_blue, "sound")
        button("выкл", display_width/3 - 225, 2*display_height/3+ 100, 150, 75, blue, bright_blue, "sound_stop")
        button("ДАЛЕЕ",display_width*0.75, display_height*0.75 - 125, 350, 100, blue, bright_blue, "level")
        # кнопки для выбора уровня
        button("ЛЕГКИЙ",display_width/3 + 85, display_height/4, display_width/3 - 170, 150, blue, bright_blue, "lite")
        button("СРЕДНИЙ",display_width/3 + 85, display_height/4 + 195, display_width/3 - 170, 150, blue, bright_blue, "medium")
        button("СЛОЖНЫЙ",display_width/3 + 85, display_height/4 + 390, display_width/3 - 170, 150, blue, bright_blue, "hard")
        button("НАЗАД",display_width*0.75, display_height*0.75, 350, 100, blue, bright_blue, "menu")
        pygame.display.update()
        clock.tick(50)

def initilize_numbers(max_numbers, fall):
    '''
    Задание значений переменным, отвечающих за расположение цифр для анимации
    Входные данные: max_numbers - максимальное количество цифр
    Выходные данные: fall - список, содержащий объекты класса Numbers
    '''
    for i in range(0, max_numbers):
        x = random.randint(0, display_width)
        y = random.randint(0, display_height)
        fall.append(Numbers(x, y))

def numbers():
    '''
    Функция отвечает анимацию перед началом игры
    Выходные данные: отображение анимации (движущихся цифр на экране)
    '''
    start_time = time.time()
    end_time = 5
    fall = []
    initilize_numbers(max_numbers, fall)
    numb = True
    while numb == True:
        current_time = int(time.time() - start_time)
        # выключение анимации при истечении указанного времени end_time
        if current_time is end_time:
            numb = False
        gamedisplays.fill(intro_color)
        # задание движения цифрам и их отрисовка
        for i in fall:
            i.move_numbers()
            i.draw_numbers()
        time.sleep(0.025)
        for event in pygame.event.get():
            check_for_exit(event)
            # выключение анимации при нажатии на любую клавишу
            if (event.type == pygame.KEYDOWN):
                numb = False
        pygame.display.flip()

def logo():
    '''
    Функция отвечает за заставку в начале игры
    Выходные данные: отображение логотипа МАГУ
    '''
    start_time = time.time()
    end_time = 2
    logo = True
    while logo == True:
        gamedisplays.fill(intro_color)
        current_time = int(time.time() - start_time)
        # переключение заставки при истечении указанного времени end_time
        if current_time is end_time:
            logo = False
        for event in pygame.event.get():
            check_for_exit(event)
            # переключение заставки при нажатии любой клавиши
            if event.type == pygame.KEYDOWN:
                logo = False
        gamedisplays.fill(intro_color)
        gamedisplays.blit(image, (display_width/2-300, display_height/2-100))
        pygame.display.update()
        clock.tick(30)

def check_for_exit(event):
    # проверка не нажат ли X, закрывающий окно программы
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
