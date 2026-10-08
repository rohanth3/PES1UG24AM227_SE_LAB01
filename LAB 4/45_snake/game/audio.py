import pygame
import io
import wave
import struct
import math

class Audio:
    def __init__(self):
        self.initialized = False
        self.eat_sound = None
        self.game_over_sound = None

        try:
            # Initialize mixer if not already initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.initialized = True
            
            # Generate sounds
            self.eat_sound = self._generate_tone(frequency=880, duration=0.1)
            self.game_over_sound = self._generate_tone(frequency=220, duration=0.5, sweep=True)
        except Exception as e:
            print(f"Warning: Audio initialization failed. {e}")

    def _generate_tone(self, frequency, duration, volume=0.5, sample_rate=44100, sweep=False):
        """Generates a simple tone in-memory and returns a pygame.mixer.Sound."""
        try:
            num_samples = int(sample_rate * duration)
            f = io.BytesIO()
            w = wave.open(f, 'w')
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sample_rate)
            
            data = []
            for t in range(num_samples):
                if sweep:
                    # Pitch bend downwards
                    current_freq = frequency - (frequency / 2) * (t / num_samples)
                else:
                    current_freq = frequency
                    
                sample = volume * math.sin(2 * math.pi * current_freq * t / sample_rate)
                data.append(int(32767 * sample))
                
            w.writeframes(struct.pack('<' + 'h' * num_samples, *data))
            w.close()
            
            f.seek(0)
            return pygame.mixer.Sound(f)
        except Exception as e:
            print(f"Warning: Failed to generate sound. {e}")
            return None

    def play_eat(self):
        if self.initialized and self.eat_sound:
            try:
                self.eat_sound.play()
            except Exception:
                pass

    def play_game_over(self):
        if self.initialized and self.game_over_sound:
            try:
                self.game_over_sound.play()
            except Exception:
                pass
