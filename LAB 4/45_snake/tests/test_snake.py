import unittest
from game.snake import Snake
from game.food import Food

class TestSnake(unittest.TestCase):
    def setUp(self):
        # Create a snake at (5, 5) with cell size 20
        # Body starts at (5, 5), (4, 5), (3, 5) heading RIGHT (1, 0)
        self.snake = Snake(5, 5, 20)
    
    def test_direct_reversals(self):
        # Moving Right, pressing Left
        self.snake.direction = (1, 0)
        self.snake.set_direction(-1, 0)
        self.assertEqual(self.snake.direction_queue, []) # Should be ignored

        # Moving Left, pressing Right
        self.snake.direction = (-1, 0)
        self.snake.set_direction(1, 0)
        self.assertEqual(self.snake.direction_queue, []) # Should be ignored

        # Moving Up, pressing Down
        self.snake.direction = (0, -1)
        self.snake.set_direction(0, 1)
        self.assertEqual(self.snake.direction_queue, []) # Should be ignored

        # Moving Down, pressing Up
        self.snake.direction = (0, 1)
        self.snake.set_direction(0, -1)
        self.assertEqual(self.snake.direction_queue, []) # Should be ignored

    def test_valid_perpendicular_turns(self):
        # Moving Right, pressing Up
        self.snake.direction = (1, 0)
        self.snake.set_direction(0, -1)
        self.assertEqual(self.snake.direction_queue, [(0, -1)])
        
        # Then pressing Left (this should be allowed since last queued is Up)
        self.snake.set_direction(-1, 0)
        self.assertEqual(self.snake.direction_queue, [(0, -1), (-1, 0)])

    def test_rapid_direction_reversal_bypass(self):
        # Moving Right (1, 0)
        # Player presses Up (0, -1), then Left (-1, 0), then Down (0, 1) rapidly
        self.snake.set_direction(0, -1)
        self.snake.set_direction(-1, 0)
        # Should reject down because it's a 180 of Up? No, it's 180 of Left? 
        # Last queued is Left (-1, 0), so pressing Right (1, 0) is blocked.
        self.snake.set_direction(1, 0) # Ignored
        # The queue is full (length 2 limit)
        self.assertEqual(self.snake.direction_queue, [(0, -1), (-1, 0)])
        
        # Test moves
        self.snake.move()
        self.assertEqual(self.snake.direction, (0, -1)) # Moved Up
        self.snake.move()
        self.assertEqual(self.snake.direction, (-1, 0)) # Moved Left
        
    def test_multiple_direction_inputs_before_move(self):
        # Queueing right -> up -> left
        self.snake.set_direction(0, -1) # Up
        self.snake.set_direction(-1, 0) # Left
        self.snake.set_direction(0, 1) # Down (will be ignored because queue size max 2)
        
        self.assertEqual(self.snake.direction_queue, [(0, -1), (-1, 0)])
        
    def test_wall_collisions(self):
        grid_width, grid_height = 10, 10
        
        # Left wall
        self.snake.body[0] = (-1, 5)
        self.assertTrue(self.snake.collides_with_wall(grid_width, grid_height))
        
        # Top wall
        self.snake.body[0] = (5, -1)
        self.assertTrue(self.snake.collides_with_wall(grid_width, grid_height))
        
        # Right wall
        self.snake.body[0] = (10, 5)
        self.assertTrue(self.snake.collides_with_wall(grid_width, grid_height))
        
        # Bottom wall
        self.snake.body[0] = (5, 10)
        self.assertTrue(self.snake.collides_with_wall(grid_width, grid_height))
        
        # Valid position
        self.snake.body[0] = (5, 5)
        self.assertFalse(self.snake.collides_with_wall(grid_width, grid_height))

    def test_self_collision_occupied_segment(self):
        # Head overlaps body
        self.snake.body = [(5, 5), (4, 5), (4, 6), (5, 6), (5, 5)]
        self.assertTrue(self.snake.collides_with_self())

    def test_move_into_vacated_tail(self):
        # Set up a snake chasing its tail
        # Tail is at (6, 5)
        self.snake.body = [(5, 5), (5, 6), (6, 6), (6, 5)] 
        self.snake.direction = (1, 0) # Moving right to (6, 5)
        
        # Tail vacates (6, 5) during move!
        self.snake.move()
        self.assertFalse(self.snake.collides_with_self())
        self.assertEqual(self.snake.body[0], (6, 5)) # Head moved into old tail spot
        
    def test_move_into_tail_when_growing(self):
        # Set up same snake chasing its tail
        self.snake.body = [(5, 5), (5, 6), (6, 6), (6, 5)] 
        self.snake.direction = (1, 0) # Moving right to (6, 5)
        
        self.snake.grow() # set grow_pending = True
        
        # Tail DOES NOT vacate (6, 5) during move because it's growing!
        self.snake.move()
        
        self.assertTrue(self.snake.collides_with_self())
        
    def test_food_collection_and_growth(self):
        initial_length = len(self.snake.body)
        self.snake.grow()
        self.snake.move()
        self.assertEqual(len(self.snake.body), initial_length + 1)
        self.assertFalse(self.snake.grow_pending)

if __name__ == '__main__':
    unittest.main()
