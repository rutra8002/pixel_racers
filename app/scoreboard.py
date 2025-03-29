import pygame

class Scoreboard:
    def __init__(self, display, column_names, tuple_list, font_size=18, line_height=50, padding=12, max_height=300):
        self.display = display
        self.screen = self.display.game.screen
        self.column_names = column_names
        self.tuple_list = tuple_list
        self.font = pygame.font.Font("fonts/joystix monospace.otf", font_size)
        self.line_height = line_height
        self.padding = padding
        self.max_height = max_height
        self.scroll_offset = 0
        self.colors = {
            "background": (20, 20, 20),
            "text": (255, 255, 255),
            "border": (26, 26, 26),
            "header_hover": (200, 200, 200)
        }
        self.column_widths = self.calculate_column_widths()
        self.sort_list(1, True)

        self.display.objects.append(self)

    def delete(self):
        self.display.objects.remove(self)
        del self

    def calculate_column_widths(self):
        num_columns = len(self.column_names)
        max_widths = [0] * num_columns
        for tup in [self.column_names] + self.tuple_list:
            for i in range(num_columns):
                text = str(tup[i])
                text_surface = self.font.render(text, True, self.colors["text"])
                max_widths[i] = max(max_widths[i], text_surface.get_width())

        for i, width in enumerate(max_widths):
            width += 35
            max_widths[i] = width
        return max_widths


    def format(self, t):
        full_time = t
        milliseconds = int((full_time % 1) * 1000)
        total_seconds = int(full_time)
        minutes, seconds = divmod(total_seconds, 60)

        if total_seconds < 60:
            formatted_time = f"{total_seconds}:{milliseconds:03d}"
        else:
            formatted_time = f"{minutes}:{seconds:02d}:{milliseconds:03d}"
        return formatted_time



    def events(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * self.line_height
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.scroll_offset -= self.line_height
            elif event.key == pygame.K_DOWN:
                self.scroll_offset += self.line_height
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            if self.is_in_header(mouse_x, mouse_y):
                clicked_column = self.get_clicked_column(mouse_x)
                if clicked_column is not None:
                    self.sort_list(clicked_column, True)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mouse_x, mouse_y = event.pos
            if self.is_in_header(mouse_x, mouse_y):
                clicked_column = self.get_clicked_column(mouse_x)
                if clicked_column is not None:
                    self.sort_list(clicked_column, False)

        self.scroll_offset = max(0, min(self.scroll_offset, self.total_height() - self.max_height + self.line_height))

    def total_height(self):
        return len(self.tuple_list) * self.line_height

    def is_in_header(self, x, y):
        header_y = (self.screen.get_height() - self.max_height) // 2
        return header_y <= y < header_y + self.line_height

    def get_clicked_column(self, x):
        xpos = (self.screen.get_width() - sum(self.column_widths) - 2 * self.padding * len(self.column_widths)) // 2
        for i, width in enumerate(self.column_widths):
            if x >= xpos and x <= xpos + width:
                return i
            xpos += width + 2 * self.padding
        return None

    def render(self):
        screen_width, screen_height = self.screen.get_size()
        menu_width = sum(self.column_widths) + 2 * self.padding * len(self.column_widths)

        x = (screen_width - menu_width) // 2
        y = (screen_height - self.max_height) // 2

        header_y = y
        xpos = x
        for i in range(len(self.column_names)):
            column_name = str(self.column_names[i])
            if column_name == str(self.column_names[self.sortby[0]]):
                if self.sortby[1] == True:
                    text_surface = self.font.render(f"{column_name} <", True, self.colors["text"])
                else:
                    text_surface = self.font.render(f"{column_name} >", True, self.colors["text"])
            else:
                text_surface = self.font.render(column_name, True, self.colors["text"])
            text_rect = text_surface.get_rect()
            column_width = self.column_widths[i]

            if self.is_in_header(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                pygame.draw.rect(
                    self.screen,
                    self.colors["header_hover"],
                    (xpos, header_y, column_width + 2 * self.padding, text_rect.height + 2 * self.padding),
                )

            pygame.draw.rect(
                self.screen,
                self.colors["background"],
                (xpos, header_y, column_width + 2 * self.padding, text_rect.height + 2 * self.padding),
            )
            pygame.draw.rect(
                self.screen,
                self.colors["border"],
                (xpos, header_y, column_width + 2 * self.padding, text_rect.height + 2 * self.padding),
                1,
            )
            self.screen.blit(
                text_surface,
                (xpos + self.padding, header_y + self.padding)
            )

            xpos += column_width + 2 * self.padding

        content_y = y + self.line_height

        clip_rect = pygame.Rect(x, content_y, menu_width, self.max_height - self.line_height)
        self.screen.set_clip(clip_rect)

        y = content_y - self.scroll_offset
        for idx, tup in enumerate(self.tuple_list):
            xpos = x
            for i in range(len(tup)):
                if i == 0:
                    text = str(tup[i])
                else:
                    text = str(self.format(tup[i]))
                if i == 0:
                    text_surface = self.font.render(f"{idx + 1}. {text}", True, self.colors["text"])
                else:
                    text_surface = self.font.render(text, True, self.colors["text"])
                text_rect = text_surface.get_rect()
                column_width = self.column_widths[i]

                pygame.draw.rect(
                    self.screen,
                    self.colors["background"],
                    (xpos, y, column_width + 2 * self.padding, text_rect.height + 2 * self.padding),
                )
                pygame.draw.rect(
                    self.screen,
                    self.colors["border"],
                    (xpos, y, column_width + 2 * self.padding, text_rect.height + 2 * self.padding),
                    1,
                )
                self.screen.blit(
                    text_surface,
                    (xpos + self.padding, y + self.padding)
                )

                xpos += column_width + 2 * self.padding

            y += self.line_height

        self.screen.set_clip(None)

    def sort_list(self, M, left_clicked):
        self.tuple_list = self.quick_sort(self.tuple_list, M)
        if left_clicked == False and M!=0:
            self.tuple_list.reverse()
        elif left_clicked  and M == 0:
            self.tuple_list.reverse()

        self.sortby = [M, left_clicked]
    def quick_sort(self, lst, key=0):
        if len(lst) <= 1:
            return lst

        pivot = lst[0]
        left = []
        right = []
        equal = []

        for item in lst:
            if item[key] < pivot[key]:
                left.append(item)
            elif item[key] > pivot[key]:
                right.append(item)
            else:
                equal.append(item)

        sorted_left = self.quick_sort(left, key)
        sorted_right = self.quick_sort(right, key)

        return sorted_left + equal + sorted_right