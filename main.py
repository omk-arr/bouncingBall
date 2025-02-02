import pygame
import math
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Physics constants
GRAVITY = 0.5
FRICTION = 0.8
RESTITUTION = 0.7
ROTATION_SPEED = 1.7 # degrees per frame

class Ball:
    def __init__(self, x, y, radius=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.vel_x = 0
        self.vel_y = 0
    
    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)

class Hexagon:
    def __init__(self, center_x, center_y, radius=200):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.rotation = 0  # degrees
        self.points = self.calculate_points()
        
    def calculate_points(self):
        points = []
        for i in range(6):
            angle = math.radians(self.rotation + i * 60)
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            points.append((x, y))
        return points
    
    def rotate(self):
        self.rotation += ROTATION_SPEED
        self.points = self.calculate_points()
        
    def draw(self, screen):
        pygame.draw.polygon(screen, WHITE, self.points, 2)

def get_line_segments(points):
    segments = []
    for i in range(len(points)):
        start = points[i]
        end = points[(i + 1) % len(points)]
        segments.append((start, end))
    return segments

def check_collision(ball, hexagon):
    segments = get_line_segments(hexagon.points)
    
    for start, end in segments:
        # Vector from start to end of wall
        wall_vector = (end[0] - start[0], end[1] - start[1])
        wall_length = math.sqrt(wall_vector[0]**2 + wall_vector[1]**2)
        wall_unit = (wall_vector[0]/wall_length, wall_vector[1]/wall_length)
        
        # Vector from start to ball
        to_ball = (ball.x - start[0], ball.y - start[1])
        
        # Project to_ball onto wall to find closest point
        proj_length = to_ball[0]*wall_unit[0] + to_ball[1]*wall_unit[1]
        proj_length = max(0, min(wall_length, proj_length))
        
        closest_point = (
            start[0] + proj_length * wall_unit[0],
            start[1] + proj_length * wall_unit[1]
        )
        
        # Check distance from closest point to ball
        dist_x = ball.x - closest_point[0]
        dist_y = ball.y - closest_point[1]
        distance = math.sqrt(dist_x**2 + dist_y**2)
        
        if distance < ball.radius:
            # Collision detected, calculate normal vector
            normal = (dist_x/distance, dist_y/distance)
            
            # Calculate relative velocity
            rel_vel_x = ball.vel_x
            rel_vel_y = ball.vel_y
            
            # Calculate velocity along normal
            normal_vel = rel_vel_x*normal[0] + rel_vel_y*normal[1]
            
            # Only bounce if moving toward the wall
            if normal_vel < 0:
                # Calculate bounce response
                ball.vel_x = rel_vel_x - (1 + RESTITUTION) * normal_vel * normal[0]
                ball.vel_y = rel_vel_y - (1 + RESTITUTION) * normal_vel * normal[1]
                
                # Apply friction to parallel component
                ball.vel_x *= FRICTION
                ball.vel_y *= FRICTION
                
                # Move ball out of wall
                ball.x = closest_point[0] + normal[0] * ball.radius
                ball.y = closest_point[1] + normal[1] * ball.radius
                
                return True
    return False

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bouncing Ball in Rotating Hexagon")
    clock = pygame.time.Clock()
    
    ball = Ball(WIDTH//2, HEIGHT//2)
    hexagon = Hexagon(WIDTH//2, HEIGHT//2)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Reset ball position and give it random velocity on click
                ball.x, ball.y = pygame.mouse.get_pos()
                ball.vel_x = np.random.uniform(-10, 10)
                ball.vel_y = np.random.uniform(-10, 10)
        
        # Update
        hexagon.rotate()
        ball.update()
        check_collision(ball, hexagon)
        
        # Draw
        screen.fill(BLACK)
        hexagon.draw(screen)
        ball.draw(screen)
        pygame.display.flip()
        
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()