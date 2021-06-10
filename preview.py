import pygame
import random

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
MAX_X = screen.get_width()
MAX_Y = screen.get_height()
NUMBER_SIZE1 = 100
NUMBER_SIZE2 = 150

# класс, отвечающий за анимацию при запуске игры
class Numbers():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.randint(1, 10)
        self.img_num = random.randint(1, 5)
        # загрузка изображений (цифр)
        self.image_filename = "resources/img/numb" + str(self.img_num) + ".png"
        self.image = pygame.image.load(self.image_filename).convert_alpha()
        # изменение размеров изображений (цифр) по указанным параметрам NUMBER_SIZE1 и NUMBER_SIZE2
        self.image = pygame.transform.scale(self.image, (NUMBER_SIZE1, NUMBER_SIZE2))

    def move_numbers(self):
        # перемещение цифр по вертикали с указанной скоростью self.speed
        self.y = self.y + self.speed
        if self.y > MAX_Y:
            self.y = (0 - NUMBER_SIZE2)
        
    def draw_numbers(self):
        # отрисовка цифр на экране
        screen.blit(self.image, (self.x, self.y))


