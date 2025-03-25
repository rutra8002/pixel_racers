import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music = None
        self.paused = False

    def load_sound(self, name, filepath):
        self.sounds[name] = pygame.mixer.Sound(filepath)

    def is_playing_music(self):
        return pygame.mixer.music.get_busy()

    def play_sound(self, name, loops=0):
        if name in self.sounds:
            self.sounds[name].play(loops=loops)
        else:
            print(f"Sound '{name}' not found!")

    def stop_sound(self, name):
        if name in self.sounds:
            self.sounds[name].stop()
        else:
            print(f"Sound '{name}' not found!")

    def load_music(self, filepath):
        self.music = filepath
    def unload_music(self):
        self.music = None
        pygame.mixer.music.unload()

    def play_music(self, loops=-1):
        if self.music:
            if self.paused:
                self.unpause_music()
            else:
                pygame.mixer.music.load(self.music)
                pygame.mixer.music.play(loops=loops)
        else:
            print("No music loaded!")

    def pause_music(self):
        pygame.mixer.music.pause()
        self.paused = True

    def unpause_music(self):
        pygame.mixer.music.unpause()
        self.paused = False

    def set_music_volume(self, volume):
        pygame.mixer.music.set_volume(volume)

    def set_sound_volume(self, name, volume):
        if name in self.sounds:
            self.sounds[name].set_volume(volume)
        else:
            print(f"Sound '{name}' not found!")