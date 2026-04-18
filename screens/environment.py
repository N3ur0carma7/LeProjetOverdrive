import pygame
import random


class Cloud:
    def __init__(self, image, x, y, speed_x, speed_y=0, alpha=70):
        self.image = image.copy()
        self.image.set_alpha(alpha)
        self.x = float(x)
        self.y = float(y)
        self.speed_x = float(speed_x)
        self.speed_y = float(speed_y)

    def update(self, dt):
        self.x += self.speed_x * dt
        self.y += self.speed_y * dt

    def draw(self, surface, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)

        sw, sh = surface.get_size()

        if screen_x > sw or screen_y > sh:
            return
        if screen_x + self.image.get_width() < 0 or screen_y + self.image.get_height() < 0:
            return

        surface.blit(self.image, (screen_x, screen_y))


class CloudManager:
    def __init__(self, world_min_x, world_max_x, world_min_y, world_max_y):
        self.world_min_x = world_min_x
        self.world_max_x = world_max_x
        self.world_min_y = world_min_y
        self.world_max_y = world_max_y
        self.cloud_images = []
        self.clouds = []

    def load_images(self):
        paths = [
            "assets/environment/cloud_1.png",
            "assets/environment/cloud_2.png",
            "assets/environment/cloud_3.png",
        ]

        self.cloud_images = []
        for path in paths:
            img = pygame.image.load(path).convert_alpha()
            self.cloud_images.append(img)

    def generate_clouds(self, count=40):
        self.clouds = []

        for _ in range(count):
            img = random.choice(self.cloud_images)

            scale = random.uniform(0.8, 1.4)
            w = max(1, int(img.get_width() * scale))
            h = max(1, int(img.get_height() * scale))
            scaled = pygame.transform.scale(img, (w, h))

            x = random.randint(self.world_min_x, self.world_max_x)
            y = random.randint(self.world_min_y, self.world_max_y)
            alpha = random.randint(45, 80)

            speed_x = random.uniform(8, 20)
            speed_y = random.uniform(-2, 2)

            self.clouds.append(Cloud(scaled, x, y, speed_x, speed_y, alpha))

    def update(self, dt):
        for cloud in self.clouds:
            cloud.update(dt)

            if cloud.x > self.world_max_x + 300:
                cloud.x = self.world_min_x - cloud.image.get_width()
                cloud.y = random.randint(self.world_min_y, self.world_max_y)

    def draw(self, surface, camera_x, camera_y):
        for cloud in self.clouds:
            cloud.draw(surface, camera_x, camera_y)