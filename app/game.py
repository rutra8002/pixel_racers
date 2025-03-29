import json
import platform
import pygame, sys, threading, code, os, sqlite3
from app import config, sounds, cheats
from app.database import DatabaseManager
from customObjects import custom_text, custom_images, custom_button
import particle_system
import ctypes
import inspect

if platform.system() == "Windows":
    ctypes.windll.user32.SetProcessDPIAware()
class Game:
    def __init__(self):
        pygame.init()

        self.sound_manager = sounds.SoundManager()
        self.sound_manager.load_music('sounds/music/Neon Rush.wav')
        self.sound_manager.load_music('sounds/music/Chasing Snowflakes.wav')
        self.sound_manager.load_sound('Credits', 'sounds/music/credits.ogg')
        self.sound_manager.load_sound('Boom','sounds/TireBoom.wav')
        self.sound_manager.load_sound('bounce', 'sounds/bounce.wav')
        self.sound_manager.load_sound('Powerup', 'sounds/Powerup_sound.wav')
        self.sound_manager.load_sound('Heal', 'sounds/Heal.wav')
        self.sound_manager.load_sound('Strength', 'sounds/Strength.wav')
        self.sound_manager.load_sound('Pitstop', 'sounds/Pitstop.wav')
        self.sound_manager.load_sound('Banana', 'sounds/goofy-slip.wav')
        self.sound_manager.load_sound('coin', 'sounds/Coin.wav')
        self.sound_manager.load_sound('kaching', 'sounds/ka-ching.wav')
        self.sound_manager.set_music_volume(0.2)

        config.set_config()

        self.db_manager = DatabaseManager()
        self.player_name = self.db_manager.get_last_player_name()

        self.map_dir = 'maps'
        self.update_settings()

        self.player_model = 1

        self.objects_in_memory = 0
        self.clock = pygame.time.Clock()
        self.font = None

        self.run = True

        self.delta_time = 0
        self.calibration = 60

        self.objects = []
        self.currentLeaderboard = None

        self.menu_particle_system = particle_system.ParticleSystem()

        self.hotbar_dimentions = (self.width, self.height/6)


        from app import display

        self.template_display = display.basic_display(self)
        self.upgrade_worlds()

        self.displays = {'template_display': self.template_display, 'game_display': display.game_display, 'level_selector': display.level_selector(self), 'map_display': display.map_display(self), 'main_menu_display': display.main_menu_display(self), 'settings_display': display.settings_display(self), 'pause_display': display.pause_display(self), 'map_maker_menu': display.map_maker_menu(self), 'change_vehicle': display.change_vehicle(self), 'credits': display.credits(self), 'leaderboard': display.leaderboard(self), 'change_player_name': display.change_player_name(self), 'new_leaderboard': display.new_leaderboard(self)}
        self.current_display = self.displays['main_menu_display']

        self.displays['level_selector'].load_maps()

        self.pointing_at = []


        self.debug = False
        self.debug_items = [custom_text.Custom_text(self, 12, 15, f'Current version: {self.version}', text_color='white', font=self.font, font_height=30,  center=False),
                            custom_text.Custom_text(self, 12, 45, f'Resolution: {self.width}x{self.height}', font=self.font, font_height=30, text_color='white', center=False),
                            custom_text.Custom_text(self, 12, 75, f'FPS cap: {self.fps}', font=self.font, font_height=30,  text_color='white', center=False),
                            custom_text.Custom_text(self, 12, 105, f'FPS: {self.clock.get_fps()}', font=self.font, font_height=30,  text_color='white', center=False),
                            custom_text.Custom_text(self, 12, 135, f'Objects in memory: {self.current_display.objects_in_memory}', font=self.font, font_height=30,  text_color='white', center=False),
                            custom_text.Custom_text(self, 12, 165, f'Current display: {type(self.current_display)}', font=self.font, font_height=30,  text_color='white', center=False)]

        for debug_item in self.debug_items:
            debug_item.hidden = True

        self.cheats = cheats.Cheats(self)
        self.custom_locals = {
            'self': self,
            'pygame': pygame,
            'config': config,
            'display': display,
            'custom_text': custom_text,
            'custom_images': custom_images,
            'custom_button': custom_button,
            'cheats': self.cheats
        }

        for name, method in inspect.getmembers(self.cheats, inspect.ismethod):
            if not name.startswith('__'):
                self.custom_locals[name] = method

        self.console_cursor_pos = 0

        self.console_active = False
        self.console_input = ""
        self.console_history = []
        # db_path = 'scores.sqlite'
        # if not os.path.exists(db_path):
        #     conn = sqlite3.connect(db_path)
        #     cursor = conn.cursor()
        #     cursor.execute('''
        #         CREATE TABLE scores (
        #             id INTEGER PRIMARY KEY AUTOINCREMENT,
        #             name TEXT NOT NULL,
        #             level TEXT NOT NULL,
        #             full_time REAL NOT NULL,
        #             fastest_lap REAL NOT NULL,
        #             score INTEGER NOT NULL
        #         )
        #     ''')
        #     conn.commit()
        #     conn.close()

        try:
            self.console_font = pygame.font.Font('fonts/JetBrainsMonoNLNerdFontMono-Regular.ttf', 20)
        except FileNotFoundError:
            print("Warning: JetBrainsMonoNLNerdFontMono-Regular font not found, using default font")
            self.console_font = pygame.font.Font(None, 24)

        self.console_history_index = 0

        # self.db = sqlite3.connect('scores.sqlite')
        # self.cursor = self.db.cursor()


    #     console_thread = threading.Thread(target=self.start_console, args=(custom_locals,))
    #     console_thread.start()
    #
    # def start_console(self, locals):
    #     console = code.InteractiveConsole(locals=locals)
    #     console.interact()

    def music(self):
        if isinstance(self.current_display, self.displays["game_display"]) and not self.sound_manager.is_playing_music():
            self.sound_manager.play_music(loops=-1)
        elif not isinstance(self.current_display, self.displays["game_display"]):
            self.sound_manager.pause_music()

    def fade(self, fade_in=True, duration=0.3):
        fade_surface = pygame.Surface((self.width, self.height))
        fade_surface.fill((0, 0, 0))
        alpha = 0 if fade_in else 255
        increment = 255 / duration

        while (fade_in and alpha < 255) or (not fade_in and alpha > 0):
            fade_surface.set_alpha(alpha)
            self.render()
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            self.delta_time = self.clock.tick(self.fps) / 1000.0
            alpha += increment * self.delta_time if fade_in else -increment * self.delta_time

    def change_display(self, new_display):
        self.fade(fade_in=True)
        try:
            self.current_display = self.displays[new_display]
        except Exception as e:
            print(e)
        self.fade(fade_in=False)

    def mainloop(self):
        while self.run:
            self.music()
            self.current_display.mainloop()
            self.render()
            self.update()
            self.events()
            self.clock.tick(self.fps)
        pygame.quit()
        sys.exit()


    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSLASH and self.enable_debug:
                    self.debug = not self.debug
                    for di in self.debug_items:
                        di.hidden = not di.hidden

                elif event.key == pygame.K_BACKQUOTE and self.enable_debug:
                    self.console_active = not self.console_active
                    self.console_history_index = 0

            # console
            if self.console_active:
                self.console_stuff(event)
            else:
                self.current_display.events(event)

    def console_stuff(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                try:
                    result = eval(self.console_input, self.custom_locals, {})
                    # Store result without formatting to preserve multiline structure
                    self.console_history.append({"input": self.console_input, "output": result})
                    self.console_input = ""
                    self.console_cursor_pos = 0
                    self.console_history_index = 0
                except Exception as e:
                    self.console_history.append({"input": self.console_input, "output": f"Error: {str(e)}"})
                    self.console_input = ""
                    self.console_cursor_pos = 0
                    self.console_history_index = 0
            elif event.key == pygame.K_BACKSPACE:
                if self.console_cursor_pos > 0:
                    # Delete character before cursor
                    self.console_input = self.console_input[:self.console_cursor_pos - 1] + self.console_input[
                                                                                            self.console_cursor_pos:]
                    self.console_cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                # Delete character at cursor
                if self.console_cursor_pos < len(self.console_input):
                    self.console_input = self.console_input[:self.console_cursor_pos] + self.console_input[
                                                                                        self.console_cursor_pos + 1:]
            elif event.key == pygame.K_LEFT:
                # Move cursor left
                self.console_cursor_pos = max(0, self.console_cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                # Move cursor right
                self.console_cursor_pos = min(len(self.console_input), self.console_cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                # Move cursor to start
                self.console_cursor_pos = 0
            elif event.key == pygame.K_END:
                # Move cursor to end
                self.console_cursor_pos = len(self.console_input)
            elif event.key == pygame.K_UP:
                if self.console_history:
                    self.console_history_index = min(self.console_history_index + 1, len(self.console_history))
                    self.console_input = self.console_history[-self.console_history_index]["input"]
                    self.console_cursor_pos = len(self.console_input)
            elif event.key == pygame.K_DOWN:
                if self.console_history:
                    self.console_history_index = max(self.console_history_index - 1, 0)
                    if self.console_history_index > 0:
                        self.console_input = self.console_history[-self.console_history_index]["input"]
                    else:
                        self.console_input = ""
                    self.console_cursor_pos = len(self.console_input)
            # Check for ` and ignore it
            elif event.key != pygame.K_BACKQUOTE:
                if event.unicode:
                    # Insert character at cursor position
                    self.console_input = self.console_input[
                                         :self.console_cursor_pos] + event.unicode + self.console_input[
                                                                                     self.console_cursor_pos:]
                    self.console_cursor_pos += 1

    def render(self):
        self.screen.fill('black')
        self.current_display.render()

        for object in self.objects:
            object.render()

        # console
        if self.console_active:
            console_height = self.height // 2
            console_surface = pygame.Surface((self.width, console_height), pygame.SRCALPHA)
            console_surface.fill((0, 0, 0, 180))
            self.screen.blit(console_surface, (0, self.height - console_height))

            line_height = 20
            max_history_lines = (console_height - 30) // line_height

            # Draw input prompt at the bottom
            y = self.height - 30
            input_text = "> " + self.console_input[:self.console_cursor_pos] + "█" + self.console_input[
                                                                                     self.console_cursor_pos:]
            input_surf = self.console_font.render(input_text, True, (0, 255, 0))
            self.screen.blit(input_surf, (10, y))

            # Prepare visible history in correct order
            y -= line_height
            history_content = []
            lines_used = 0

            # Process from newest to oldest, limited by available space
            for entry in reversed(self.console_history):
                # Check if we've reached the maximum lines
                if lines_used >= max_history_lines:
                    break

                # Calculate how many lines this entry will use (command + output)
                entry_lines = 1  # Command line
                output = entry['output']
                output_lines_count = len(output.strip().split('\n')) if isinstance(output, str) else 1

                # Skip this entry if it won't fit completely
                if lines_used + entry_lines + output_lines_count > max_history_lines:
                    continue

                # Process output first (so oldest content appears at the top)
                if isinstance(output, str):
                    output_lines = output.strip().split('\n')
                    for line in reversed(output_lines):
                        history_content.insert(0, (line, (180, 255, 180)))
                        lines_used += 1
                else:
                    history_content.insert(0, (f"Result: {output}", (180, 255, 180)))
                    lines_used += 1

                # Add command (insert at beginning to maintain correct order)
                command_line = (f"> {entry['input']}", (0, 255, 0))
                history_content.insert(0, command_line)
                lines_used += 1

            # Display history from bottom up
            # Show most recent entries (at the end of history_content)
            display_count = min(max_history_lines, len(history_content))
            for i in range(display_count):
                idx = len(history_content) - 1 - i
                if idx >= 0:
                    text, color = history_content[idx]
                    text_surf = self.console_font.render(text, True, color)
                    self.screen.blit(text_surf, (10, y))
                    y -= line_height


    def update(self):
        if self.clock.get_time() / 1000.0 > 0.1:
            self.delta_time = 0.1
        else:
            self.delta_time = self.clock.get_time() / 1000.0
        if self.debug:

            self.debug_items[3].update_text(f'FPS: {self.clock.get_fps()}')
            self.debug_items[4].update_text(f'Objects in memory: {self.current_display.objects_in_memory}')
            self.debug_items[5].update_text(f'Current display: {type(self.current_display)}')

        pygame.display.flip()

    def update_settings(self):
        self.cfg = config.read_config()

        self.version = self.cfg['version']
        self.width = int(self.cfg['width'])
        self.height = int(self.cfg['height'])
        self.fps = float(self.cfg['fps'])
        self.title = self.cfg['title']
        self.fullscreen = int(self.cfg['full-screen'])
        self.enable_debug = int(self.cfg['enable_debug'])

        self.screen = pygame.display.set_mode((self.width, self.height))
        if self.fullscreen:
            pygame.display.toggle_fullscreen()
        pygame.display.set_caption(f"{self.title} (v {self.version})")

        if not os.path.exists(self.map_dir):
            os.makedirs(self.map_dir)
    def get_level_names(self):
        return [file[:-5] for file in os.listdir(self.map_dir) if file.endswith('.json')]

    def upgrade_worlds(self):
        directories = self.get_level_names()

        for file in directories:
            with open(f'{self.map_dir}/{file}.json', 'r') as f:
                josn_obj = json.load(f)

                f.close()

                if 'version' not in josn_obj.keys() or ('version' in josn_obj.keys() and josn_obj['version'] != self.version):
                    temp_map = dict(self.template_display.map_data)
                    temp_map.update(josn_obj)
                    temp_map['version'] = self.version
                    if 'player_position' in josn_obj.keys():
                        if isinstance(josn_obj['player_position'], list):
                            temp_map['player'][0] = josn_obj['player_position']


                    with open(f'{self.map_dir}/{file}.json', 'w') as f:
                        json.dump(temp_map, f)
                        f.close()

    def update_player_model(self):
        names = self.get_level_names()
        for name in names:
            self.displays[name].update_player_model(self.player_model)
