import pygame
import random

pygame.init()

# Sound Effects
lane_change_sound = pygame.mixer.Sound('assets/line.mp3')
collision_sound = pygame.mixer.Sound('assets/game_over.mp3')
pygame.mixer.music.load('assets/music.mp3')
pygame.mixer.music.play(-1)

# Screen Setup
width, height = 500, 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Car Game')

# Colors
gray, green, red, white, yellow = (100, 100, 100), (76, 208, 56), (200, 0, 0), (255, 255, 255), (255, 232, 0)

# Track Class
class Track:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.left_lane = 150
        self.center_lane = 250
        self.right_lane = 350
        self.road = pygame.Rect(100, 0, 300, height)
        self.edge_left = pygame.Rect(95, 0, 10, height)
        self.edge_right = pygame.Rect(395, 0, 10, height)
        self.marker_y = 0

    def draw(self):
        screen.fill(green)
        pygame.draw.rect(screen, gray, self.road)
        pygame.draw.rect(screen, yellow, self.edge_left)
        pygame.draw.rect(screen, yellow, self.edge_right)
        for y in range(-50, self.height, 100):
            pygame.draw.rect(screen, white, (self.left_lane + 45, y + self.marker_y, 10, 50))
            pygame.draw.rect(screen, white, (self.center_lane + 45, y + self.marker_y, 10, 50))

    def update_markers(self, speed):
        self.marker_y += speed * 2
        if self.marker_y >= 100:
            self.marker_y = 0

# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/car.png')
        self.rect = self.image.get_rect(center=(x, y))

    def move_left(self):
        if self.rect.centerx > 150:
            self.rect.x -= 100  # Adjusted movement distance
            lane_change_sound.play()

    def move_right(self):
        if self.rect.centerx < 350:
            self.rect.x += 100  # Adjusted movement distance
            lane_change_sound.play()

# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, speed):
        self.rect.y += speed
        if self.rect.top > height:
            self.kill()

# Initialize Track, Player, and Enemies
track = Track(width, height)
player = Player(250, 400)
player_group = pygame.sprite.GroupSingle(player)
enemy_group = pygame.sprite.Group()
score, speed, running, gameover = 0, 2, True, False

# Font Setup
font = pygame.font.Font(None, 36)

# Main Game Loop
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and not gameover:
                player.move_left()
            elif event.key == pygame.K_RIGHT and not gameover:
                player.move_right()
            elif event.key == pygame.K_r and gameover:  # Restart game if 'R' is pressed
                score, speed, gameover = 0, 2, False  # Reset score and speed
                enemy_group.empty()  # Clear enemies for a new game
                player.rect.center = (250, 400)  # Reset player position

    if not gameover:
        track.update_markers(speed)
        track.draw()
        player_group.draw(screen)
        enemy_group.draw(screen)

        # Add enemies randomly
        if len(enemy_group) < 2:
            lane = random.choice([track.left_lane, track.center_lane, track.right_lane])
            enemy = Enemy(lane, -50, random.choice(['assets/pickup_truck.png', 'assets/taxi.png']))
            enemy_group.add(enemy)

        # Update enemies and check for score increment
        for enemy in enemy_group:
            enemy.update(speed)
            if enemy.rect.top > height:  # If enemy goes off screen
                score += 1  # Increment score when avoiding an enemy
                enemy.kill()  # Remove the enemy after it goes off screen

        # Increase enemy speed based on score
        speed = 2 + (score // 5)  # Increase speed as score increases

        # Check collisions
        if pygame.sprite.spritecollideany(player, enemy_group):
            collision_sound.play()
            gameover = True

    # Draw everything
    track.draw()
    player_group.draw(screen)
    enemy_group.draw(screen)

    # Render and display the score
    score_text = font.render(f'Score: {score}', True, white)
    screen.blit(score_text, (20, 20))

    # Handle game over screen
    if gameover:
        gameover_text = font.render('Game Over! Press R to Restart', True, red)
        screen.blit(gameover_text, (width // 2 - gameover_text.get_width() // 2, height // 2))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
