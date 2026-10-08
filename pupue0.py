import sys
import cv2
import numpy as np
import pygame

# Ініціалізація Pygame
pygame.init()

# Ініціалізація камери через OpenCV
cap = cv2.VideoCapture(0)
success, frame = cap.read()
if not success:
    print("Помилка: Не вдалося отримати доступ до вебкамери!")
    sys.exit()

h, w, _ = frame.shape

screen = pygame.display.set_mode((w, h))
pygame.display.set_caption("Virtual Paint (Draw: D, Eraser: E, Clear: C)")

canvas = pygame.Surface((w, h), pygame.SRCALPHA)

# Налаштування кольорів та пензля
brush_color = (255, 0, 128, 255)  # Рожевий колір (RGBA)
brush_thickness = 8
eraser_thickness = 50              # Ластик робимо товстішим, щоб зручно стирати
prev_x, prev_y = None, None

current_mode = 'draw'

lower_color = np.array([35, 50, 50])
upper_color = np.array([85, 255, 255])


clock = pygame.time.Clock()
print("Програма успішно запущена!")
print("Керування:\n[D] - Малювати\n[E] - Стирати (Ластик)\n[C] - Очистити все\n[ESC] - Вихід")

while True:
    # Обробка натискань клавіш
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_d:  
                current_mode = 'draw'
                print("Режим: Малювання")
            elif event.key == pygame.K_e:  
                current_mode = 'erase'
                print("Режим: Ластик (Стирання)")
            elif event.key == pygame.K_c:  
                canvas.fill((0, 0, 0, 0))   
                print("Полотно очищено!")

    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    track_x, track_y = None, None

    if contours:
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 500:
            M = cv2.moments(c)
            if M["m00"] != 0:
                track_x = int(M["m10"] / M["m00"])
                track_y = int(M["m01"] / M["m00"])

    if track_x is not None and track_y is not None:
        if prev_x is not None and prev_y is not None:
            if current_mode == 'draw':
                pygame.draw.line(canvas, brush_color, (prev_x, prev_y), (track_x, track_y), brush_thickness)
            elif current_mode == 'erase':
                pygame.draw.line(canvas, (0, 0, 0, 0), (prev_x, prev_y), (track_x, track_y), eraser_thickness)
        prev_x, prev_y = track_x, track_y
    else:
        prev_x, prev_y = None, None

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = np.rot90(frame_rgb)
    frame_rgb = np.flipud(frame_rgb)
    camera_surface = pygame.surfarray.make_surface(frame_rgb)

    screen.blit(camera_surface, (0, 0))  # Камера
    screen.blit(canvas, (0, 0))          # Малюнок / Гумка
    
    if track_x is not None and track_y is not None:
        if current_mode == 'draw':
            pygame.draw.circle(screen, (0, 255, 0), (track_x, track_y), 6)  # Зелена точка для малювання
        elif current_mode == 'erase':
            pygame.draw.circle(screen, (255, 255, 255), (track_x, track_y), eraser_thickness // 2, 2)

    pygame.display.update()
    clock.tick(60)
