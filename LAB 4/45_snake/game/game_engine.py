import pygame
from .snake import Snake
from .food import Food

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cell_size = 20
        self.grid_width = width // self.cell_size
        self.grid_height = height // self.cell_size

        self.snake = Snake(self.grid_width // 2, self.grid_height // 2, self.cell_size)
        self.food = Food(self.grid_width, self.grid_height, self.cell_size)

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont("Arial", 50)

        self.moves_per_second = 8
        self._frame_counter = 0

        self.game_over = False
        self._game_over_logged = False

    def handle_keydown(self, key):
        if self.game_over:
            if key == pygame.K_1:
                self.restart_game(moves_per_second=5)  # Easy
            elif key == pygame.K_2:
                self.restart_game(moves_per_second=10) # Medium
            elif key == pygame.K_3:
                self.restart_game(moves_per_second=15) # Hard
            elif key == pygame.K_q:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        # Direction changes are applied immediately on key press.
        if key in (pygame.K_UP, pygame.K_w):
            self.snake.set_direction(0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.snake.set_direction(0, 1)
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.snake.set_direction(-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.snake.set_direction(1, 0)

    def restart_game(self, moves_per_second):
        self.moves_per_second = moves_per_second
        self.snake = Snake(self.grid_width // 2, self.grid_height // 2, self.cell_size)
        self.food = Food(self.grid_width, self.grid_height, self.cell_size)
        self.score = 0
        self._frame_counter = 0
        self.game_over = False
        self._game_over_logged = False

    def handle_input(self):
        # Reserved for continuously-held-key input (not used for a
        # grid-based snake, but kept here to mirror the engine's shape).
        pass

    def update(self):
        if self.game_over:
            return

        self._frame_counter += 1
        frames_per_move = max(1, 60 // self.moves_per_second)
        if self._frame_counter < frames_per_move:
            return
        self._frame_counter = 0

        self.snake.move()

        if self.snake.collides_with_wall(self.grid_width, self.grid_height):
            self.game_over = True
            return

        if self.snake.collides_with_self():
            self.game_over = True
            return

        if self.snake.head_rect().colliderect(self.food.rect()):
            self.snake.grow()
            self.score += 1
            self.food.respawn(self.snake.body)

    def render(self, screen):
        # Draw food
        pygame.draw.rect(screen, RED, self.food.rect())

        # Draw snake
        for rect in self.snake.segment_rects():
            pygame.draw.rect(screen, GREEN, rect)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            # Draw GAME OVER screen
            game_over_text = self.game_over_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 40))
            screen.blit(game_over_text, text_rect)
            
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            score_rect = final_score_text.get_rect(center=(self.width // 2, self.height // 2 + 10))
            screen.blit(final_score_text, score_rect)
            
            prompt_font = pygame.font.SysFont("Arial", 20)
            instructions_text = prompt_font.render("Press 1: Easy | 2: Medium | 3: Hard | Q: Quit", True, WHITE)
            instructions_rect = instructions_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
            screen.blit(instructions_text, instructions_rect)
            
            if not self._game_over_logged:
                print("Game over! Final score:", self.score)
                self._game_over_logged = True
