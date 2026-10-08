import unittest
from unittest.mock import patch
from game.game_engine import GameEngine
import pygame

class TestGameEngine(unittest.TestCase):
    def setUp(self):
        # We need to initialize pygame fonts for GameEngine to create fonts
        pygame.init()
        # Initialize a headless display so surfaces can be created
        pygame.display.set_mode((1, 1), pygame.HIDDEN)
        self.engine = GameEngine(600, 600)

    def tearDown(self):
        pygame.quit()

    def test_wall_collision_triggers_game_over(self):
        self.assertFalse(self.engine.game_over)
        # Move snake right next to left wall, moving left
        self.engine.snake.body[0] = (0, 5)
        self.engine.snake.direction = (-1, 0)
        
        self.engine._frame_counter = 100 # Force update
        self.engine.update()
        
        self.assertTrue(self.engine.game_over)

    def test_self_collision_triggers_game_over(self):
        self.assertFalse(self.engine.game_over)
        # Create a self-collision situation:
        # Head is at (5, 5), moving Right (1, 0).
        # Body wraps around so (6, 5) is occupied.
        self.engine.snake.body = [(5, 5), (5, 6), (6, 6), (6, 5), (7, 5)]
        self.engine.snake.direction = (1, 0) # moving into (6, 5)
        
        self.engine._frame_counter = 100 # Force update
        self.engine.update()
        
        self.assertTrue(self.engine.game_over)

    def test_movement_termination_and_score_preservation(self):
        # Set to game over manually
        self.engine.game_over = True
        self.engine.score = 42
        
        initial_head = self.engine.snake.body[0]
        
        # Call update multiple times
        for _ in range(10):
            self.engine._frame_counter = 100
            self.engine.update()
            
        # Verify snake did not move
        self.assertEqual(self.engine.snake.body[0], initial_head)
        # Verify score is preserved
        self.assertEqual(self.engine.score, 42)

    def test_game_over_rendering(self):
        self.engine.game_over = True
        self.engine.score = 10
        
        screen = pygame.Surface((600, 600))
        # Just ensure rendering doesn't crash and flags are set
        self.engine.render(screen)
        
        # Call render again to test persistent display and single state transition
        self.engine.render(screen)
        self.assertTrue(self.engine._game_over_logged) # Flag should remain True
        
    def test_normal_gameplay_regression(self):
        initial_score = self.engine.score
        # Force a food overlap on NEXT move
        # Head is at (15, 15), moving Right (1, 0). Next head will be (16, 15).
        self.engine.snake.body[0] = (15, 15)
        self.engine.snake.direction = (1, 0)
        self.engine.food.x = 16
        self.engine.food.y = 15
        
        self.engine._frame_counter = 100
        self.engine.update()
        
        # Assert snake grew and score increased
        self.assertTrue(self.engine.snake.grow_pending)
        self.assertEqual(self.engine.score, initial_score + 1)
        self.assertFalse(self.engine.game_over)

    def test_restart_resets_state(self):
        # Set a dirty state
        self.engine.game_over = True
        self.engine.score = 50
        self.engine.snake.body = [(1, 1), (1, 2)]
        self.engine.snake.direction_queue = [(0, -1)]
        self.engine.food.x = 1
        
        # Call restart
        self.engine.restart_game(10)
        
        # Verify fresh state
        self.assertFalse(self.engine.game_over)
        self.assertEqual(self.engine.score, 0)
        self.assertEqual(len(self.engine.snake.body), 3)
        self.assertEqual(self.engine.snake.body[0], (self.engine.grid_width // 2, self.engine.grid_height // 2))
        self.assertEqual(self.engine.snake.direction_queue, [])
        self.assertEqual(self.engine.moves_per_second, 10)
        self.assertEqual(self.engine._frame_counter, 0)

    def test_difficulty_selection_keys(self):
        self.engine.game_over = True
        
        # Test Easy
        self.engine.handle_keydown(pygame.K_1)
        self.assertEqual(self.engine.moves_per_second, 5)
        self.assertFalse(self.engine.game_over)
        
        # Test Medium
        self.engine.game_over = True
        self.engine.handle_keydown(pygame.K_2)
        self.assertEqual(self.engine.moves_per_second, 10)
        self.assertFalse(self.engine.game_over)
        
        # Test Hard
        self.engine.game_over = True
        self.engine.handle_keydown(pygame.K_3)
        self.assertEqual(self.engine.moves_per_second, 15)
        self.assertFalse(self.engine.game_over)

if __name__ == '__main__':
    unittest.main()
