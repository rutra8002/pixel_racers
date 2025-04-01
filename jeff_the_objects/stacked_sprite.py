import random

import pygame

class StackedSprite:
    def __init__(self, display, image, num_of_sprites, sprite_size, scale_factor, rotation=0, rotate=True, collision=True, isenemy=None):
        self.display = display
        self.image = image.copy()
        self.isenemy = isenemy
        self.num_of_sprites = num_of_sprites
        self.sprite_size = sprite_size
        self.scale_factor = scale_factor
        self.sprites = self.load_sprites()
        self.sprites.reverse()
        self.rect = self.sprites[0].get_rect()
        self.collision = collision
        self.masks = [pygame.mask.from_surface(sprite) for sprite in self.sprites]
        self.largest_mask_index = self.get_largest_mask_index()
        self.mask = self.masks[self.largest_mask_index]
        if not self.collision:
            self.mask.clear()
        self.rotation_cache = {}
        self.update_mask_rotation(rotation)
        self.rotation = rotation
        self.rotate = rotate


    def load_sprites(self):
        sprites = []
        sprite_width, sprite_height = self.sprite_size
        for i in range(self.num_of_sprites):
            sprite = self.image.subsurface((0, i * sprite_height, sprite_width, sprite_height))
            scaled_sprite = pygame.transform.scale(sprite, (sprite_width * self.scale_factor, sprite_height * self.scale_factor))
            sprites.append(scaled_sprite)
        return sprites

    def render(self, screen, position):
        x, y = position
        for i, sprite in enumerate(self.sprites):
            if self.rotate:
                rotated_sprite = self.get_rotated_sprite(sprite, self.rotation - 90)
                sprite_rect = rotated_sprite.get_rect(center=(x, y))
                screen.blit(rotated_sprite, (sprite_rect[0], sprite_rect[1] - i * self.scale_factor))
            else:
                sprite_rect = sprite.get_rect(center=(x, y))
                screen.blit(sprite, (sprite_rect[0], sprite_rect[1] - i * self.scale_factor))
        if self.display.game.debug:
            # render self.mask
            mask_surface = self.mask.to_surface()
            mask_surface.set_colorkey((0, 0, 0))
            mask_rect = mask_surface.get_rect(center=(x, y))
            screen.blit(mask_surface, (mask_rect[0], mask_rect[1]))

    def update_mask_rotation(self, rotation):
        for i, sprite in enumerate(self.sprites):
            rotated_sprite = self.get_rotated_sprite(sprite, rotation - 90)
            self.masks[i] = pygame.mask.from_surface(rotated_sprite)
        self.mask = self.masks[self.largest_mask_index]
        self.rect = self.mask.get_rect()
        self.rotation = rotation
        if not self.collision:
            self.mask.clear()
        return self.mask

    def get_rotated_sprite(self, sprite, rotation):
        if (sprite, rotation) not in self.rotation_cache:
            self.rotation_cache[(sprite, rotation)] = pygame.transform.rotate(sprite, rotation)
        return self.rotation_cache[(sprite, rotation)]

    def get_largest_mask_index(self):
        return max(range(len(self.masks)), key=lambda i: self.masks[i].count())