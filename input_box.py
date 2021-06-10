import pygame
import sys

pygame.init()

INACTIVE = pygame.Color('gray')
ACTIVE = pygame.Color('black')
FONT = pygame.font.SysFont('arial', 32)
name = ""

# класс, отвечающий за поле ввода текста
class InputBox:

    def __init__(self, x, y, w, h, text=''):
        # поле ввода текста с началом в точке x, y, длиной w и высотой h
        self.rect = pygame.Rect(x, y, w, h)
        self.color = INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # если пользователь нажимает внутри поля ввода
            if self.rect.collidepoint(event.pos):
                # переключение активной переменной
                self.active = not self.active
            else:
                self.active = False
            # изменение текущего цветп поля ввода
            self.color = ACTIVE if self.active else INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                # удаление буквы при нажатии на клавишу BACKSPACE
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

                global name
                name = self.text
                self.txt_surface = FONT.render(self.text, True, self.color)
            

    def update(self):
        # изменение размера поля, если текст слишком длинный
        width = max(400, self.txt_surface.get_width()+10)
        self.rect.w = width
        return name 

    def draw(self, screen):
        # отображение текста в поле ввода
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)
        
