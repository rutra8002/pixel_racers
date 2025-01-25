import pygame

class saveselector:
    def __init__(self, display):
        self.display = display
        self.game = self.display.game
        self.screen_width = self.game.width
        self.screen_height = self.game.height
        self.button_width = int(self.screen_width * 0.63)
        self.button_height = int(self.screen_height * 0.13)
        self.container_width = int(self.screen_width * 0.75)
        self.container_height = int(self.screen_height * (2 / 3))
        self.scrollspeed = 30
        self.num_of_buttons = 3
        self.spacing = 20

        self.screen = self.game.screen

        self.container_rect = pygame.Rect((self.screen_width - self.container_width) // 2,
                                          (self.screen_height - self.container_height) // 2, self.container_width,
                                          self.container_height)

        self.game.objects.append(self)

    def render(self):
        if self.game.screen_mode.state == 'presets' and self.game.screen_mode.action == 'presets':
            for i, button in enumerate(self.presets_buttons):
                self.target_positions[i] = (self.screen_height - self.container_height) // 2 + i * (
                        self.button_height + self.spacing) + self.spacing
                if button.is_visible(self.container_rect):
                    if i + self.scroll_offset < len(self.presets):

                        button.text = self.presets[i + self.scroll_offset]

                    button.render()
    def generate_presets_buttons(self):

        self.presets = [file[:-5] for file in os.listdir(self.preset_dir) if file.endswith('.json')]


        self.scrolling_needed = len(self.presets) > self.num_of_buttons
        print(self.scrolling_needed)
        self.scroll_offset = 0

        self.presets_buttons = []
        for i in range(self.num_of_buttons):
            if i < len(self.presets):
                button1 = (self.Button_v2(self.game, self.presets[i], self.presets_date_title_thingy[i],
                                          (self.screen_width - self.button_width) // 2,
                                          (self.screen_height - self.container_height - 150) // 2 + i * (
                                                  self.button_height + self.spacing) + self.spacing,
                                          self.button_width, self.button_height, self.game.selected_buttons))
                self.presets_buttons.append(button1)

        self.target_positions = [button.rect.y for button in self.presets_buttons]


