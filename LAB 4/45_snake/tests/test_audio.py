import unittest
from unittest.mock import patch
from game.audio import Audio

class TestAudio(unittest.TestCase):
    def test_audio_initialization(self):
        audio = Audio()
        # It shouldn't crash.
        # Check if it initialized gracefully
        self.assertTrue(hasattr(audio, 'initialized'))

    def test_audio_play_methods_dont_crash(self):
        audio = Audio()
        # Calling play methods shouldn't raise exceptions even in headless/test environments
        audio.play_eat()
        audio.play_game_over()

if __name__ == '__main__':
    unittest.main()
