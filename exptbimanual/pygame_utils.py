import pygame


def scale_image(original_image: pygame.surface, size: tuple[int, int])->pygame.surface:
    return pygame.transform.smoothscale(original_image, size)

