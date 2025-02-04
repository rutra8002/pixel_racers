import pygame

class StackedSprite:
    def __init__(self, image, num_of_sprites, sprite_size, scale_factor):
        self.image = image
        self.num_of_sprites = num_of_sprites
        self.sprite_size = sprite_size
        self.scale_factor = scale_factor
        self.sprites = self.load_sprites()
        self.sprites.reverse()
        self.rect = self.sprites[0].get_rect()
        self.masks = [pygame.mask.from_surface(sprite) for sprite in self.sprites]


    def load_sprites(self):
        sprites = []
        sprite_width, sprite_height = self.sprite_size
        for i in range(self.num_of_sprites):
            sprite = self.image.subsurface((0, i * sprite_height, sprite_width, sprite_height))
            scaled_sprite = pygame.transform.scale(sprite, (sprite_width * self.scale_factor, sprite_height * self.scale_factor))
            sprites.append(scaled_sprite)
        return sprites

    def render(self, screen, position, rotation):
        x, y = position
        for i, sprite in enumerate(self.sprites):
            rotated_sprite = pygame.transform.rotate(sprite, rotation-90)
            sprite_rect = rotated_sprite.get_rect(center=(x, y))
            screen.blit(rotated_sprite, (sprite_rect[0], sprite_rect[1] - i * self.scale_factor))