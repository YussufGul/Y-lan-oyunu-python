import pygame
import random
import sys
import os
import time

pygame.init()

# Ekran boyutları ve ayarlar
screen_width, screen_height = 600, 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Yılan Oyunu')

# Renkler
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)  # Yeşil renk

# Diğer değişkenler
cell_size = 20
game_over = False
paused = False
snake_pos = [(100, 100)]
snake_dir = (cell_size, 0)
snake_speed = 10
food_pos = (random.randint(0, (screen_width // cell_size) - 1) * cell_size,
            random.randint(0, (screen_height // cell_size) - 1) * cell_size)
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont('Arial', 28, bold=True)
tiny_font = pygame.font.SysFont('Arial', 20)
score = 0
high_score = 0
last_food_time = time.time()  # Son yemin ne zaman doğduğunu tutar
is_food_black = False  # Yem rengi kontrolü
food_black_start_time = 0  # Siyah yem süresini takip etmek için
obstacle_pos = None  # Engel pozisyonu
obstacle_speed = 5   # Engel düşme hızı
obstacle_timer = 0   # Engel için zamanlayıcı
obstacle_interval = 10 * 1000  # Engel her 10 saniyede bir düşer (milisaniye cinsinden)


def draw_snake():
    head = snake_pos[0]
    pygame.draw.circle(screen, BLACK, (head[0] + cell_size // 2, head[1] + cell_size // 2), cell_size // 2)
    eye_radius = 2
    eye_offset_x = 4
    eye_offset_y = -4
    mouth_offset_y = 2
    pygame.draw.circle(screen, WHITE, (head[0] + cell_size // 2 - eye_offset_x, head[1] + cell_size // 2 + eye_offset_y), eye_radius)
    pygame.draw.circle(screen, WHITE, (head[0] + cell_size // 2 + eye_offset_x, head[1] + cell_size // 2 + eye_offset_y), eye_radius)
    pygame.draw.arc(screen, WHITE, (head[0] + cell_size // 4, head[1] + cell_size // 2, cell_size // 2, cell_size // 4), 0, 3.14, 1)
    for segment in snake_pos[1:]:
        pygame.draw.rect(screen, BLACK, pygame.Rect(segment[0], segment[1], cell_size, cell_size))

def load_high_score():
    global high_score
    if os.path.exists('high_score.txt'):
        with open('high_score.txt', 'r') as file:
            high_score = int(file.read())

def save_high_score():
    global high_score
    with open('high_score.txt', 'w') as file:
        file.write(str(high_score))

def draw_grid():
    for x in range(0, screen_width, cell_size):
        pygame.draw.line(screen, GRAY, (x, 0), (x, screen_height))
    for y in range(0, screen_height, cell_size):
        pygame.draw.line(screen, GRAY, (0, y), (screen_width, y))

def draw_food():
    """Yemi çizer, rengini kontrol eder"""
    color = BLACK if is_food_black else RED
    pygame.draw.rect(screen, color, pygame.Rect(food_pos[0], food_pos[1], cell_size, cell_size))

def draw_score():
    score_text = tiny_font.render(f'Puan: {score}', True, BLACK)
    high_score_text = tiny_font.render(f'En Yüksek Puan: {high_score}', True, BLACK)
    screen.blit(score_text, (screen_width - 130, 10))
    screen.blit(high_score_text, (screen_width - 160, 40))
def spawn_obstacle():
    """Yukarıdan düşen engelin başlangıç pozisyonunu ayarlar"""
    global obstacle_pos
    obstacle_pos = (random.randint(0, (screen_width // cell_size) - 1) * cell_size, 0)

def draw_obstacle():
    """Engeli ekrana çizer"""
    if obstacle_pos:
        pygame.draw.rect(screen, GREEN, pygame.Rect(obstacle_pos[0], obstacle_pos[1], cell_size, cell_size))

def move_obstacle():
    """Engeli aşağı doğru hareket ettirir"""
    global obstacle_pos
    if obstacle_pos:
        obstacle_pos = (obstacle_pos[0], obstacle_pos[1] + obstacle_speed)
        # Engel ekrandan çıkarsa tekrar yukarıdan başlat
        if obstacle_pos[1] > screen_height:
            obstacle_pos = None  # Engel kaybolur, bir sonraki 10 saniyede tekrar başlatılır

def check_obstacle_collision():
    """Yılanın kafasının engele çarpmasını kontrol eder"""
    global score
    if obstacle_pos and snake_pos[0][0] == obstacle_pos[0] and snake_pos[0][1] == obstacle_pos[1]:
        score -= 10
        obstacle_pos = None  # Çarpışma sonrası engel kaybolur
        if score <= 0:  # Skor sıfır olduğunda oyun biter
            score = 0
            global game_over
            game_over = True

# Başlangıç zamanı
obstacle_timer = pygame.time.get_ticks()    

def game_over_screen():
    screen.fill(WHITE)
    text = font.render('Yandın!', True, RED)
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 3))
    score_text = font.render(f'Puan: {score}', True, BLACK)
    screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, screen_height // 2))
    button_text = small_font.render('Tekrar Oyna', True, BLACK)
    button_rect = button_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
    pygame.draw.rect(screen, GRAY, button_rect.inflate(20, 10))
    screen.blit(button_text, button_rect)
    pygame.display.update()
    return button_rect

def reset_game():
    global snake_pos, snake_dir, food_pos, game_over, score, snake_speed, is_food_black, food_black_start_time, last_food_time
    snake_pos = [(100, 100)]
    snake_dir = (cell_size, 0)
    food_pos = (random.randint(0, (screen_width // cell_size) - 1) * cell_size,
                random.randint(0, (screen_height // cell_size) - 1) * cell_size)
    score = 0
    snake_speed = 10
    is_food_black = False
    food_black_start_time = 0
    last_food_time = time.time()  # Yemin doğma zamanını sıfırlıyoruz
    game_over = False

def spawn_black_food():
    global is_food_black, food_black_start_time, last_food_time
    """Siyah yem rastgele her 10 saniyede bir doğar"""
    if time.time() - last_food_time > 10:  # 10 saniyede bir siyah yem doğar
        is_food_black = True
        food_black_start_time = time.time()  # Siyah yemin doğuş zamanını tutar
        last_food_time = time.time()  # Son yem doğma zamanını günceller

def check_black_food_timeout():
    """Siyah yemin süresi dolarsa, yemi normal hale getir"""
    global is_food_black
    if is_food_black and time.time() - food_black_start_time > 5:  # 5 saniye
        is_food_black = False
        
def handle_food_collision(new_head):
    """
    Yem yendiğinde gerekli işlemleri yapar:
    - Normal yem: Skor +10, yılan büyür.
    - Siyah yem: Skor -10, yılan küçülür, 0 ise oyun biter.
    """
    global food_pos, score, game_over, is_food_black, snake_pos

    if new_head == food_pos:
        if is_food_black:  # Siyah yem yenirse
            score -= 10
            if score <= 0:  # Skor 0 veya altına düşerse oyun biter
                score = 0
                game_over = True
            else:
                if len(snake_pos) > 1:  # Yılan küçülür (tek segmentten büyükse)
                    snake_pos.pop()
        else:  # Normal yem yenirse
            score += 10
            snake_pos.append(snake_pos[-1])  # Yılan büyür

        # Yeni yem konumu oluştur
        food_pos = (random.randint(0, (screen_width // cell_size) - 1) * cell_size,
                    random.randint(0, (screen_height // cell_size) - 1) * cell_size)
        spawn_black_food()  # Rastgele siyah yem doğabilir        

# Yüksek puanı yükle
# --- Yüksek Skoru Yükle ---
load_high_score()

running = True
paused = False
game_over = False

while running:
    # Oyun bitti ekranı
    if game_over:
        button_rect = game_over_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score()
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_high_score()
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                reset_game()
    
    # Oyun devam ediyor
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score()
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_high_score()
                    running = False
                elif event.key == pygame.K_SPACE:  # Oyunu duraklat/başlat
                    paused = not paused
                elif not paused:  # Duraklama durumunda yön değişikliği engellenir
                    if event.key == pygame.K_UP and snake_dir != (0, cell_size):
                        snake_dir = (0, -cell_size)
                    elif event.key == pygame.K_DOWN and snake_dir != (0, -cell_size):
                        snake_dir = (0, cell_size)
                    elif event.key == pygame.K_LEFT and snake_dir != (cell_size, 0):
                        snake_dir = (-cell_size, 0)
                    elif event.key == pygame.K_RIGHT and snake_dir != (-cell_size, 0):
                        snake_dir = (cell_size, 0)

        # Oyun duraklatıldıysa diğer işlemleri atla
        if paused:
            continue

        # --- Yılanın Hareketi ---
        new_head = (snake_pos[0][0] + snake_dir[0], snake_pos[0][1] + snake_dir[1])
        new_head = (new_head[0] % screen_width, new_head[1] % screen_height)  # Ekran sınırlarını aşma

        # Kendine çarpma kontrolü
        if new_head in snake_pos:
            game_over = True
            continue

        # Yem kontrolü
        if new_head == food_pos:
            if is_food_black:  # Siyah yem yenirse
                score -= 10
                if score <= 0:
                    score = 0
                    game_over = True
                elif len(snake_pos) > 1:  # Yılan küçülür
                    snake_pos.pop()
            else:  # Normal yem yenirse
                score += 10
                snake_pos.append(snake_pos[-1])  # Yılan büyür
            food_pos = (
                random.randint(0, (screen_width // cell_size) - 1) * cell_size,
                random.randint(0, (screen_height // cell_size) - 1) * cell_size
            )
            spawn_black_food()

        # Engel kontrolü (skor 100'den büyükse)
        if score > 100 and obstacle_pos:
            move_obstacle()
            if check_obstacle_collision(new_head):
                game_over = True
                continue

        # Yılanı hareket ettir
        snake_pos = [new_head] + snake_pos[:-1]

        # Siyah yem süresi kontrolü
        check_black_food_timeout()

        # Yüksek skor kontrolü
        if score > high_score:
            high_score = score

        # --- Ekranı Güncelle ---
        screen.fill(WHITE)
        draw_grid()
        draw_snake()
        draw_food()
        if score > 100:
            draw_obstacle()
        draw_score()
        pygame.display.update()
        clock.tick(snake_speed)

# Oyunu kapat
pygame.quit()
sys.exit()