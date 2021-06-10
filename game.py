# -*- coding: utf-8 -*-
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import cv2
from random import randint
import random
import time
import sqlite3
import datetime
import menu
import os
import sys

frame_width  = 1280
frame_height = 700

red     = (0,     0, 255, 150)
yellow  = (0,   255, 255, 150)
black   = (0,     0,   0, 200)
green   = (0,   255,   0, 150)
white   = (255, 255, 255, 150)
blue    = (255,   0,   0, 150)
radius  = 15

crop   = frame_width // 8

def camera(cap):
    """
    Проверка наличия подключенной к компьютеру камеры
    Если камера не подключена, то осуществляется возврат в главное меню
    """
    if(cap.isOpened() == False):
       cap = cv2.VideoCapture(1)
       if (cap.isOpened() == False):
           menu.setting("Камера не найдена!", "")


def movement(diff):
      """
      Обнаружение движения
      Входные данные: область изображения
      Выходные данные: возвращает 1, если в заданной области обнаружено движение
      """
      # перевод кадров в черно-белую градацию
      gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
      # фильтрация лишних контуров
      blur = cv2.GaussianBlur(gray, (3, 3), -1)
      # метод для выделения края объекта белым цветом
      _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
      # расширение выделенной на предыдущем этапе области
      dilated = cv2.dilate(thresh, None, iterations = 3)
      # нахождение массива контурных точек
      сontours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

      for contour in сontours:
        # проверка меньше ли площадь выделенного объекта 3500 px
        if cv2.contourArea(contour) < 3500:
            continue
        return 1


def start(name_student, level, x):
    """
    Настройка положения игрока
    Запуск игры осуществляется после принятия игроком (name_student) правильного положения (расположение лица между двумя линиями)
    """
    fontpath = "resources/fonts/20421.ttf"
    font = ImageFont.truetype(fontpath, 30)

    cap = cv2.VideoCapture(0)
    camera(cap)

    # установка размера окна
    cap.set(3,  frame_width)
    cap.set(4, frame_height)

    # загрузка файлов Хаара для распознавания лица и глаз
    face_cascade = cv2.CascadeClassifier('resources/haarcascade_frontalface_default.xml')
    eye_cascade  = cv2.CascadeClassifier('resources/haarcascade_eye.xml')

    height = frame_height//6
    count  = 0

    while cap.isOpened():
          ret, frame = cap.read()
          frame = cv2.flip(frame, 1)
          name_frame = "start"

          img_pil    = Image.fromarray(frame)
          draw       = ImageDraw.Draw(img_pil, "RGBA")

          # отрисовка прямоугольников
          draw.rounded_rectangle((0,                 0, frame_width//3 - 20,   frame_height//3), radius = radius, fill = red,    outline = black)
          draw.rounded_rectangle((0,   frame_height//3, frame_width//3 - 20, 2*frame_height//3), radius = radius, fill = yellow, outline = black)
          draw.rounded_rectangle((0, 2*frame_height//3, frame_width//3 - 20,      frame_height), radius = radius, fill = green,  outline = black)

          draw.text((0, frame_height//3 + 40),
                    "Устройтесь так,\nчтобы лицо находилось\nмежду двумя линиями!\nОпустите руки вниз.",
                    font = ImageFont.truetype("resources/fonts/20421.ttf", 30), fill = black)
          draw.text((0, 0),
                    "В игре будут появляться\nвопросы, на которые нужно\nответить, махнув рукой! \n\nМахать рукой надо \nв области с разноцветным\nквадратом, где указан \nверный ответ!",
                    font = font, fill = black)
          draw.text((0, 2 * frame_height // 3 + 40),
                    "Чтобы начать игру, нужно\nморгнуть несколько раз,\nпока красный мяч\nне попадет в цель!\nПропустить: 'Пробел'",
                    font=font, fill=black)

          draw.ellipse((5*frame_width//6 - 45, height - 45, 5*frame_width//6 + 45, height + 45), fill = red, outline = black, width = 5)
          draw.ellipse((5 * frame_width // 6 - 45, frame_height//6 + 455, 5 * frame_width // 6 + 45, frame_height//6 + 545), outline = black, width = 5)
          frame = np.array(img_pil)

          # перевод изображения в черно-белый формат
          gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

          # определение областей, где есть лица
          faces = face_cascade.detectMultiScale(
          gray,
          scaleFactor  =  1.1,
          minNeighbors =  25,
          minSize      = (20, 20)
          )

          # поиск лица, если лицо нашлось, то рисуем вокруг него прямоугольник
          for (x1, y1, w1, h1) in faces:
                  cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), 2)
                  roi_gray  =  gray[y1:(y1 + h1), x1:(x1 + w1)]
                  roi_color = frame[y1:(y1 + h1), x1:(x1 + w1)]

                  # проверка попадания лица в указанную область между двумя линиями
                  if((x1 > frame_width//3) and ((x1 + w1) < 2*frame_width//3)):
                      # линии зеленого цвета, если лицо попало в указанную область
                      cv2.line(frame, (frame_width//3,   0),  (frame_width//3, frame_height* 2), (0, 255, 0), 3)
                      cv2.line(frame, (2*frame_width//3, 0), (2*frame_width//3, frame_height*2), (0, 255, 0), 3)
                      area = 1
                  else:
                      # линии желтого цвета, если лицо не попало в указанную область
                      cv2.line(frame, (frame_width//3,   0), (  frame_width//3, frame_height * 2), (0, 255, 255), 3)
                      cv2.line(frame, (2*frame_width//3, 0), (2*frame_width//3, frame_height * 2), (0, 255, 255), 3)
                      area = 0

                  # поиск глаз в области с лицом
                  eyes = eye_cascade.detectMultiScale(
                      roi_gray,
                      scaleFactor   = 1.1,
                      minNeighbors  = 25,
                      minSize       = (5, 5),
                  )
                  # выделение области с глазами прямоугольниками
                  for (ex, ey, ew, eh) in eyes:
                      cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

                  # подсчет количества морганий
                  if (not list(eyes) and area == 1):
                      height = height + 100  
                      count = count + 1

          cv2.namedWindow(name_frame, cv2.WND_PROP_FULLSCREEN)
          cv2.setWindowProperty(name_frame, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
          cv2.imshow(name_frame, frame)

          # запуск игры при моргании более, чем 6 раз
          if (count >= 6):
                  cap.release()
                  cv2.destroyWindow(name_frame)
                  game(name_student, level, x)

          # запуск игры при нажатии на клавишу 'Пробел'
          if(cv2.waitKey(1) & 0xFF == ord(' ')):
                  cap.release()
                  cv2.destroyWindow(name_frame)
                  game(name_student, level, x)

    cap.release() 
    cv2.destroyAllWindows()


def result(score, answ):
    """
     Перевод полученных баллов в оценку
     Входные данные: score - баллы, answ - количество вопросов
     Выходные данные: estimation - оценка от 2 до 5
    """
    percent = (score / answ) * 100
    if(percent < 50):
        estimation = 2
    elif(percent >= 50 and percent < 70):
        estimation = 3
    elif(percent >= 70 and percent < 90):
        estimation = 4
    else:
        estimation = 5
    return estimation

def correct_answer(first, second, mode):
    """
     Осуществляет различные арифметические действия в зависимости от заданного режима
     Входные данные: first - первое число, second - второе число, mode - режим
     Выходные данные: true - вычисленный ответ, operation - знак операции (для вывода на экран)
    """
    if(mode == 1):
        operation = '+'
        true = first + second

    elif(mode == 2):
        operation = '-'
        if (first < second):
                buf = first
                first = second
                second = buf
        true = first - second
    elif(mode == 3):
        operation = '*'
        true = first * second

    elif(mode == 4):
        operation = '/'
        second = randint(1, 101)
        first = randint(0, 101)
        while (first % second != 0 or first < second):
             second = randint(1, 101)
             first = randint(0, 101)
             true = first // second
    return true, operation, first, second

def title(x):
    """
     Определение режима
     Входные данные: x - режим в числовом формате
     Выходные данные: name - название режима в текстовом формате
    """
    if  (x == 1):
        name = 'Сложение'
    elif(x == 2):
        name = 'Вычитание'
    elif(x == 3):
        name = 'Умножение'
    elif(x == 4):
        name = 'Деление'
    if  (x == 5):
        name = 'Смешанный'
    return name


def game(name_student, level, x):
    """
     Отвечает за игровой процесс
     Входные данные: name_student - имя и фамилия игрока, level - уровень, x - режим
     Выходные данные: отображение и смена на экране вопросов, ответов, внесение результатов в базу данных
    """
    cap = cv2.VideoCapture(0)
    camera(cap)
    if(level   == "легкий"):
        questions = 10
    elif(level == "средний"):
        questions = 15    
    elif(level == "сложный"):
        questions = 30

    # установка размера окна
    cap.set(3,frame_width)
    cap.set(4,frame_height)

    name_frame = title(x)

    # подключение к базе данных
    conn = sqlite3.connect('resources/scores.db')
    cur = conn.cursor()

    # создание таблицы, если такой не существует
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

    i = 1
    score = 0
    answ  = 0
    fontpath        = "resources/fonts/20421.ttf"
    fontpath_numb   = "resources/fonts/17575.ttf"
    font = ImageFont.truetype(fontpath, 115)
    font_numbers = ImageFont.truetype(fontpath_numb, 125)

    # isOpened() выводит статус видеопотока
    while cap.isOpened():
            
      ret, frame1 = cap.read()
      ret, frame2 = cap.read()

      # поворот изображения
      frame1 = cv2.flip(frame1, 1)
      frame2 = cv2.flip(frame2, 1)

      img_pil   = Image.fromarray(frame1)
      img_fin   = Image.fromarray(frame1)
      img_answ  = Image.fromarray(frame1)
      draw      = ImageDraw.Draw(img_pil,  "RGBA")
      finish    = ImageDraw.Draw(img_fin,  "RGBA")
      answers   = ImageDraw.Draw(img_answ, "RGBA")

      draw.text((frame_width//3, 50), "Очки: " + str(score) + "/" + str(questions), font = font, fill = black)
      frame1 = np.array(img_pil)

      # вырезание квадратов
      up_left_1 = frame1[0:crop, 0:crop]
      up_left_2 = frame2[0:crop, 0:crop]

      down_left_1 = frame1[frame_height - crop:frame_height, 0:crop]
      down_left_2 = frame2[frame_height - crop:frame_height, 0:crop]

      up_right_1 = frame1[0:crop, frame_width - crop:frame_width]
      up_right_2 = frame2[0:crop, frame_width - crop:frame_width]

      down_right_1 = frame1[frame_height - crop:frame_height, frame_width - crop:frame_width]
      down_right_2 = frame2[frame_height - crop:frame_height, frame_width - crop:frame_width]

      # нахождение разницы двух кадров, которая проявляется при изменении одного из них, с этого момента программа реагирует на любое движение
      diff_1 = cv2.absdiff(   up_left_1,    up_left_2)
      diff_2 = cv2.absdiff( down_left_1,  down_left_2)
      diff_3 = cv2.absdiff(  up_right_1,   up_right_2)
      diff_4 = cv2.absdiff(down_right_1, down_right_2)

      if(i != 0):
          first  = randint(0, 9)
          second = randint(0, 9)
          rect   = randint(1, 4)

          if (x == 5):
              new_x = randint(1, 4)
              true, operation, first, second =  correct_answer(first, second, new_x)
          else:
              true, operation, first, second =  correct_answer(first, second, x)

          variants = random.sample(list(range(0, int(true))) + list(range(int(true) + 1, 100)), 4)
          variants[rect - 1] = true
          i = 0
          time.sleep(0.5)

      # отрисовка прямоугольников
      draw.rounded_rectangle((0, frame_height - crop, crop, frame_height),  radius = radius, fill = green,  outline = black, width = 2)
      draw.rounded_rectangle((0, 0, crop, crop),                            radius = radius, fill = blue,   outline = black, width = 2)
      draw.rounded_rectangle((frame_width - crop, 0, frame_width, crop),    radius = radius, fill = yellow, outline = black, width = 2)
      draw.rounded_rectangle((frame_width - crop, frame_height - crop, frame_width, frame_height), radius = radius, fill = red, outline = black, width = 2)

      # отображение вопроса на экране
      draw.rounded_rectangle((0, frame_height//3, frame_width//3, 2*frame_height//3), radius = radius, fill = white, outline = black, width = 2)
      draw.text((10, frame_height // 2 - 50), (str(first) + operation + str(second) + "=?"), font = font, fill=black)

      # отображение вариантов ответа на экране
      draw.text((crop // 8, 35), str(variants[0]), font = font_numbers, fill = black)
      draw.text((crop // 8, 5 * frame_height // 6 - 10), str(variants[1]), font = font_numbers, fill = black)
      draw.text((frame_width - crop * 7 // 8, 35), str(variants[2]), font = font_numbers, fill = black)
      draw.text((frame_width - crop * 7 // 8, 5 * frame_height // 6 - 10), str(variants[3]), font = font_numbers, fill = black)
      frame1 = np.array(img_pil)

      # проверка, если выбрано более одного ответа, то вывод сообщения "Ответ не засчитан!"
      if(((    movement(diff_1) == 1) and (movement(diff_2) == 1))
           or((movement(diff_1) == 1) and (movement(diff_3) == 1))
           or((movement(diff_1) == 1) and (movement(diff_4) == 1))
           or((movement(diff_2) == 1) and (movement(diff_3) == 1))
           or((movement(diff_2) == 1) and (movement(diff_4) == 1))
           or((movement(diff_3) == 1) and (movement(diff_4) == 1))):
           answers.text((frame_width//6, frame_height//2),  "Ответ не засчитан!", font = font, fill = red)
           frame1 = np.array(img_answ)

      # проверка, совпадает ли область, в которой произошло движение, с областью, содержащей правильный ответ
      elif((  movement(diff_1) == 1 and rect == 1)
           or(movement(diff_2) == 1 and rect == 2)
           or(movement(diff_3) == 1 and rect == 3)
           or(movement(diff_4) == 1 and rect == 4)):
        answers.text((frame_width//3, frame_height//2),  "Верно:)", font = font, fill = green)
        frame1 = np.array(img_answ)
        score += 1
        answ  += 1
        time.sleep(0.5)
        i = 1

      # вывод на экран сообщения "Неверно", если движение обнаружено в области с неправильным ответом
      elif((movement(diff_1) == 1) or(movement(diff_2) == 1) or (movement(diff_3) == 1) or (movement(diff_4) == 1)):
           answers.text((frame_width//3, frame_height//2),  "Неверно:(", font = font, fill = red)
           frame1 = np.array(img_answ)
           answ += 1
           time.sleep(0.5)
           i = 1

      if(answ >= questions):
          del draw
          cv2.destroyWindow("game")
          estimation = result(score, answ)

          # внесение результатов в базу данных
          lst = name_student.split()
          users = (lst[0], lst[1], datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), name_frame, estimation, score)
          cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?,?);", users)
          conn.commit()

          # отображение результатов на экране
          finish.text((0, frame_height // 3), name_student + "!" + "\nТвой результат: " + str(score) + "\nОценка: " + str(estimation), font=font, fill= green)
          finish.text((0, frame_height - 40), "Нажми на любую клавишу, чтобы вернуться в главное меню!", font = ImageFont.truetype(fontpath, 30),  fill= green)
          frame1 = np.array(img_fin)

          cv2.namedWindow("finish", cv2.WND_PROP_FULLSCREEN)
          cv2.setWindowProperty("finish", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
          cv2.imshow("finish", frame1)

          # открытие главного меню при нажатии на любую клавишу
          if cv2.waitKey(0):
                  cap.release()
                  cv2.destroyAllWindows()
                  menu.setting(name_student, level)

      cv2.namedWindow("game", cv2.WND_PROP_FULLSCREEN)
      cv2.setWindowProperty("game",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
      cv2.imshow("game", frame1)

      if cv2.waitKey(1) & 0xFF == ord('q'):
          break

    cap.release()
    cv2.destroyAllWindows()
