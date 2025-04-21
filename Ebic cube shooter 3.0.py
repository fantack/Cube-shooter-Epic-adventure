import pygame
import random
import math
import os
from enum import Enum

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Epic Adventure")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)
LIGHT_GREEN = (100, 255, 100)
DARK_GREEN = (0, 100, 0)
DARK_RED = (150, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)  # Light gray for sniper bullets
DARK_BROWN = (101, 67, 33)  # Dark brown for shooter's jacket
BROWN = (139, 69, 19)  # Brown color for horns
PINK = (255, 105, 180)  # Pink color for hearts
ORANGE = (255, 165, 0)  # Orange for explosions

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Game states
class GameState(Enum):
    HOME = 0
    PLAYING = 1
    GAME_OVER = 2
    VICTORY = 3
    PAUSED = 4  # New paused state

# Character types
class CharacterType(Enum):
    SQUARE = 0
    KNIGHT = 1
    ROBOT = 2
    WIZARD = 3
    SNIPER = 4
    SAMURAI = 5
    SHOOTER = 6  # New character type

# Character class
class Character:
    def __init__(self, character_type):
        self.type = character_type
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.size = 30
        self.speed = 5
        self.projectiles = []
        self.last_shot = 0
        self.cooldown = 0
        self.awakening_cooldown = 15000  # Default cooldown
        self.last_awakening = -self.awakening_cooldown  # Allow immediate use at start
        self.frozen_enemies = []  # For samurai awakening
        self.freeze_end_time = 0  # For samurai awakening
        self.speed_boost_end_time = 0  # For robot speed boost
        self.slowed_enemies = []  # For shooter awakening
        
        # Character-specific attributes
        if self.type == CharacterType.SQUARE:
            self.health = 1
            self.cooldown = 125  # 0.25 seconds
            self.color = BLUE
            self.speed = 5
            self.awakening_cooldown = 20000  # 20 seconds
        elif self.type == CharacterType.KNIGHT:
            self.health = 2
            self.cooldown = 500  # 0.5 seconds for sword attack
            self.color = (150, 75, 0)  # Brown for knight
            self.speed = 6
            self.awakening_cooldown = 15000  # 15 seconds
        elif self.type == CharacterType.ROBOT:
            self.health = 1
            self.cooldown = 100  # 0.1 seconds for laser
            self.color = (100, 100, 100)  # Gray for robot
            self.speed = 4
            self.awakening_cooldown = 25000  # 25 seconds
            self.normal_speed = 4  # Store normal speed for speed boost
        elif self.type == CharacterType.WIZARD:
            self.health = 2
            self.cooldown = 400  # 0.4 seconds
            self.color = (0, 100, 100)  # Teal for wizard
            self.speed = 5
            self.awakening_cooldown = 10000  # 10 seconds
        elif self.type == CharacterType.SNIPER:
            self.health = 1
            self.cooldown = 400  # 0.4 seconds for sniper shots
            self.color = LIGHT_GREEN
            self.speed = 4  # Same as robot
            self.awakening_cooldown = 25000  # Changed to 25 seconds
        elif self.type == CharacterType.SAMURAI:
            self.health = 3
            self.cooldown = 200  # 0.15 seconds
            self.color = RED
            self.speed = 4
            self.awakening_cooldown = 20000  # 15 seconds
        elif self.type == CharacterType.SHOOTER:
            self.health = 2
            self.cooldown = 400  # 0.3 seconds for triple shots
            self.color = LIGHT_GRAY
            self.speed = 4
            self.awakening_cooldown = 20000  # 20 seconds

    def draw(self):
        if self.type == CharacterType.SQUARE:
            pygame.draw.rect(screen, self.color, (self.x - self.size // 2, self.y - self.size // 2, self.size, self.size))
        elif self.type == CharacterType.KNIGHT:
            # Square knight with grid pattern
            pygame.draw.rect(screen, self.color, (self.x - self.size // 2, self.y - self.size // 2, self.size, self.size))
            # Grid pattern
            for i in range(3):
                pygame.draw.line(screen, BLACK, 
                                 (self.x - self.size // 2, self.y - self.size // 2 + i * self.size // 3), 
                                 (self.x + self.size // 2, self.y - self.size // 2 + i * self.size // 3), 1)
                pygame.draw.line(screen, BLACK, 
                                 (self.x - self.size // 2 + i * self.size // 3, self.y - self.size // 2), 
                                 (self.x - self.size // 2 + i * self.size // 3, self.y + self.size // 2), 1)
        elif self.type == CharacterType.ROBOT:
            # Hexagonal robot
            points = []
            for i in range(6):
                angle = 2 * math.pi * i / 6
                points.append((
                    self.x + int(self.size / 2 * math.cos(angle)),
                    self.y + int(self.size / 2 * math.sin(angle))
                ))
            pygame.draw.polygon(screen, self.color, points)
            # Robot eyes
            pygame.draw.circle(screen, RED, (self.x - self.size // 4, self.y - self.size // 6), self.size // 8)
            pygame.draw.circle(screen, RED, (self.x + self.size // 4, self.y - self.size // 6), self.size // 8)
            
            # Show speed boost effect if active
            current_time = pygame.time.get_ticks()
            if current_time < self.speed_boost_end_time:
                # Draw speed boost effect (yellow glow)
                boost_surface = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
                for i in range(3):
                    alpha = 100 - i * 30
                    pygame.draw.polygon(boost_surface, (255, 255, 0, alpha), points)
                screen.blit(boost_surface, (self.x - self.size, self.y - self.size))
                
        elif self.type == CharacterType.WIZARD:
            # Circular wizard
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.size // 2)
            # Wizard hat (green triangle with rounded tip)
            hat_points = [
                (self.x, self.y - self.size - self.size // 3),  # Top point
                (self.x - self.size // 2, self.y - self.size // 2),  # Bottom left
                (self.x + self.size // 2, self.y - self.size // 2)   # Bottom right
            ]
            pygame.draw.polygon(screen, GREEN, hat_points)
            # Rounded tip for hat
            pygame.draw.circle(screen, GREEN, (self.x, self.y - self.size - self.size // 3), self.size // 8)
        elif self.type == CharacterType.SNIPER:
            # Light green square with dark green suspenders
            pygame.draw.rect(screen, LIGHT_GREEN, (self.x - self.size // 2, self.y - self.size // 2, self.size, self.size))
            # Dark green suspenders (vertical straps)
            pygame.draw.line(screen, DARK_GREEN, 
                            (self.x - self.size // 4, self.y - self.size // 2), 
                            (self.x - self.size // 4, self.y + self.size // 2), 4)
            pygame.draw.line(screen, DARK_GREEN, 
                            (self.x + self.size // 4, self.y - self.size // 2), 
                            (self.x + self.size // 4, self.y + self.size // 2), 4)
            # Horizontal connector
            pygame.draw.line(screen, DARK_GREEN, 
                            (self.x - self.size // 4, self.y), 
                            (self.x + self.size // 4, self.y), 3)
        elif self.type == CharacterType.SAMURAI:
            # Red octagon with dark red armor
            points = []
            for i in range(8):
                angle = 2 * math.pi * i / 8
                points.append((
                    self.x + int(self.size / 2 * math.cos(angle)),
                    self.y + int(self.size / 2 * math.sin(angle))
                ))
            pygame.draw.polygon(screen, RED, points)
            
            # Dark red armor - create a smaller octagon inside
            armor_points = []
            for i in range(8):
                angle = 2 * math.pi * i / 8
                armor_points.append((
                    self.x + int(self.size / 3 * math.cos(angle)),
                    self.y + int(self.size / 3 * math.sin(angle))
                ))
            pygame.draw.polygon(screen, DARK_RED, armor_points)
        elif self.type == CharacterType.SHOOTER:
            # Light gray pentagon with dark brown jacket
            points = []
            for i in range(5):
                angle = 2 * math.pi * i / 5 - math.pi/2  # Start from top point
                points.append((
                    self.x + int(self.size / 2 * math.cos(angle)),
                    self.y + int(self.size / 2 * math.sin(angle))
                ))
            pygame.draw.polygon(screen, LIGHT_GRAY, points)
            
            # Dark brown jacket (drawing a smaller pentagon inside)
            jacket_points = []
            for i in range(5):
                angle = 2 * math.pi * i / 5 - math.pi/2
                # Make jacket a bit larger on top to look like a jacket
                radius = self.size / 3 if i == 0 else self.size / 4
                jacket_points.append((
                    self.x + int(radius * math.cos(angle)),
                    self.y + int(radius * math.sin(angle))
                ))
            pygame.draw.polygon(screen, DARK_BROWN, jacket_points)
            
            # Add collar detail
            collar_left = (self.x - self.size // 6, self.y - self.size // 6)
            collar_right = (self.x + self.size // 6, self.y - self.size // 6)
            collar_top = (self.x, self.y - self.size // 3)
            pygame.draw.line(screen, LIGHT_GRAY, collar_left, collar_top, 2)
            pygame.draw.line(screen, LIGHT_GRAY, collar_right, collar_top, 2)
            
    def move(self, keys):
        # Check if robot has speed boost
        current_time = pygame.time.get_ticks()
        if self.type == CharacterType.ROBOT and current_time < self.speed_boost_end_time:
            current_speed = self.speed  # Already doubled in awakening method
        else:
            # Reset robot speed if boost ended
            if self.type == CharacterType.ROBOT and self.speed != self.normal_speed and current_time >= self.speed_boost_end_time:
                self.speed = self.normal_speed
            current_speed = self.speed
            
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= current_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += current_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= current_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += current_speed
            
        # Border constraints
        self.x = max(self.size // 2, min(WIDTH - self.size // 2, self.x))
        self.y = max(self.size // 2, min(HEIGHT - self.size // 2, self.y))

    def shoot(self, target_x, target_y):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.cooldown:
            self.last_shot = current_time
            
            # Calculate direction
            dx = target_x - self.x
            dy = target_y - self.y
            distance = max(1, (dx**2 + dy**2)**0.5)  # Avoid division by zero
            dx /= distance
            dy /= distance
            angle = math.atan2(dy, dx)
            
            # Different projectile behaviors per character
            if self.type == CharacterType.SQUARE:
                self.projectiles.append({
                    'x': self.x, 'y': self.y,
                    'dx': dx * 8, 'dy': dy * 8,
                    'size': 10, 'color': GREEN,
                    'damage': 1, 'type': 'bullet',
                    'angle': 0, 'lifetime': 0
                })
            elif self.type == CharacterType.KNIGHT:
                # Sword attack - rectangle sword attack in direction of mouse
                angle = math.atan2(dy, dx)
                sword_length = 60 * 1.3  # 30% longer
                sword_width = 15
                
                # Calculate sword position (extending from character toward mouse)
                sword_center_x = self.x + (self.size // 2 + sword_length // 2) * dx
                sword_center_y = self.y + (self.size // 2 + sword_length // 2) * dy
                
                self.projectiles.append({
                    'x': sword_center_x, 'y': sword_center_y,
                    'dx': dx, 'dy': dy,
                    'size': sword_width,
                    'length': sword_length,
                    'color': GRAY,  # Gray color for sword
                    'damage': 2,
                    'type': 'sword',
                    'angle': angle, 'lifetime': 200
                })
            elif self.type == CharacterType.ROBOT:
                self.projectiles.append({
                    'x': self.x, 'y': self.y,
                    'dx': dx * 12, 'dy': dy * 12,
                    'size': 7, 'color': RED,
                    'damage': 1, 'type': 'laser',
                    'angle': 0, 'lifetime': 0
                })
            elif self.type == CharacterType.WIZARD:
                self.projectiles.append({
                    'x': self.x, 'y': self.y,
                    'dx': dx * 6, 'dy': dy * 6,
                    'size': 15, 'color': LIGHT_GREEN,
                    'damage': 2, 'type': 'magic',
                    'angle': 0, 'lifetime': 0
                })
            elif self.type == CharacterType.SNIPER:
                # Updated sniper to shoot rectangular gray bullets
                bullet_length = 16
                bullet_width = 6
                
                self.projectiles.append({
                    'x': self.x, 'y': self.y,
                    'dx': dx * 15, 'dy': dy * 15,  # Fast bullets
                    'size': bullet_width,
                    'length': bullet_length,
                    'color': LIGHT_GRAY,
                    'damage': 3, 'type': 'sniper_bullet',
                    'angle': angle, 'lifetime': 0
                })
            elif self.type == CharacterType.SAMURAI:
                # Updated Samurai to attack in mouse direction
                slice_width = 160  # 160 degree arc
                
                # Calculate attack position based on mouse direction
                attack_dist = 60  # Distance in front of player
                attack_x = self.x + dx * attack_dist
                attack_y = self.y + dy * attack_dist
                
                self.projectiles.append({
                    'x': attack_x, 'y': attack_y,
                    'dx': 0, 'dy': 0,  # Doesn't move
                    'size': 60, 'color': RED,
                    'damage': 1, 'type': 'samurai_slice',
                    'angle': angle, 'lifetime': 90,
                    'width': slice_width,
                    'penetrate': True
                })
            elif self.type == CharacterType.SHOOTER:
                # Shooter: Triple shot in slightly different directions
                base_speed = 9
                spread_angle = 15  # degrees
                
                # Central bullet - straight ahead
                self.projectiles.append({
                    'x': self.x, 'y': self.y,
                    'dx': dx * base_speed, 'dy': dy * base_speed,
                    'size': 8, 'color': YELLOW,
                    'damage': 1, 'type': 'bullet',
                    'angle': angle, 'lifetime': 0
                })
                
                # Left bullet - angled slightly left
                left_angle = angle - math.radians(spread_angle)
                left_dx = math.cos(left_angle)
                left_dy = math.sin(left_angle)
                self.projectiles.append({
                    'x': self.x, 'y': self.y,
                    'dx': left_dx * base_speed, 'dy': left_dy * base_speed,
                    'size': 8, 'color': YELLOW,
                    'damage': 1, 'type': 'bullet',
                    'angle': left_angle, 'lifetime': 0
                })
                
                # Right bullet - angled slightly right
                right_angle = angle + math.radians(spread_angle)
                right_dx = math.cos(right_angle)
                right_dy = math.sin(right_angle)
                self.projectiles.append({
                    'x': self.x, 'y': self.y,
                    'dx': right_dx * base_speed, 'dy': right_dy * base_speed,
                    'size': 8, 'color': YELLOW,
                    'damage': 1, 'type': 'bullet',
                    'angle': right_angle, 'lifetime': 0
                })

    def awakening(self, target_x, target_y):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_awakening > self.awakening_cooldown:
            self.last_awakening = current_time
            
            # Calculate direction toward target
            dx = target_x - self.x
            dy = target_y - self.y
            distance = max(1, (dx**2 + dy**2)**0.5)
            dx /= distance
            dy /= distance
            angle = math.atan2(dy, dx)
            
            # Different awakening abilities per character
            if self.type == CharacterType.SQUARE:
                # Blue Square: 25 bullets in a circle, each dealing 1 damage
                for i in range(25):
                    bullet_angle = 2 * math.pi * i / 25
                    bullet_dx = math.cos(bullet_angle)
                    bullet_dy = math.sin(bullet_angle)
                    self.projectiles.append({
                        'x': self.x, 'y': self.y,
                        'dx': bullet_dx * 8, 'dy': bullet_dy * 8,
                        'size': 10, 'color': BLUE,
                        'damage': 1, 'type': 'bullet',
                        'angle': 0, 'lifetime': 0
                    })
            
            elif self.type == CharacterType.KNIGHT:
                # Updated Knight awakening:
                # - Now mouse-targeted (uses target_x, target_y)
                # - 2x larger range (900 instead of 450)
                # - Passes through enemies (penetrate: True)
                self.projectiles.append({
                    'x': self.x, 'y': self.y,
                    'dx': dx * 10, 'dy': dy * 10,
                    'size': 20, 'color': BLUE,
                    'damage': 5, 'type': 'knight_arc_wave',
                    'angle': angle, 'lifetime': 500,
                    'width': 120,  # Arc width
                    'range': 900,  # 2x larger range (450 * 2)
                    'stage': 0,    # Current animation stage
                    'penetrate': True  # Passes through enemies
                })
            
            elif self.type == CharacterType.ROBOT:
                # Robot: Long red beam that passes through enemies, deals 5 damage
                self.projectiles.append({
                    'x': self.x, 'y': self.y,
                    'dx': dx * 15, 'dy': dy * 15,
                    'size': 15, 'color': RED,
                    'damage': 5, 'type': 'beam',
                    'angle': angle,
                    'lifetime': 2000,
                    'length': 300,
                    'width': 20,
                    'penetrate': True
                })
                
                # Apply speed boost
                self.speed = self.normal_speed * 2  # Double speed
                self.speed_boost_end_time = current_time + 5000  # 5 second boost
            
            elif self.type == CharacterType.WIZARD:
                # Wizard: 2x larger range, passes through enemies
                self.projectiles.append({
                    'x': self.x, 'y': self.y,
                    'dx': dx * 4, 'dy': dy * 4,
                    'size': 60,  # 2x larger (30 * 2)
                    'color': GREEN,
                    'damage': 3, 'type': 'magic_orb',
                    'angle': 0, 'lifetime': 2000,
                    'penetrate': True
                })
            
            elif self.type == CharacterType.SNIPER:
                # NEW Sniper awakening: Bouncing blue ball that bounces for 5 seconds
                # Choose initial direction (toward cursor)
                self.projectiles.append({
                    'x': self.x, 'y': self.y,
                    'dx': dx * 20, 'dy': dy * 20,  # Slow moving ball (for bouncing)
                    'size': 100, 'color': BLUE,
                    'damage': 3,  # 3 damage as requested
                    'type': 'bouncing_ball',
                    'angle': angle, 
                    'lifetime': 6000,  # 6 seconds lifetime
                    'bounces': 0,  # Track number of bounces for effects
                    'penetrate': True  # Can hit multiple enemies
                })
                
            elif self.type == CharacterType.SAMURAI:
                # Samurai: Freeze all enemies for 5 seconds
                self.freeze_end_time = current_time + 5000  # 5 seconds from now
                
                # Create a wave effect that travels across the screen
                wave_points = 12
                for i in range(wave_points):
                    wave_angle = 2 * math.pi * i / wave_points
                    self.projectiles.append({
                        'x': self.x, 'y': self.y,
                        'dx': math.cos(wave_angle) * 15,
                        'dy': math.sin(wave_angle) * 15,
                        'size': 25, 'color': (255, 100, 100, 150),
                        'damage': 0, 'type': 'freeze_wave',
                        'angle': wave_angle, 'lifetime': 800,
                    })
                    
            elif self.type == CharacterType.SHOOTER:
                # Shooter's awakening: 360-degree wave that slows enemies and does damage
                self.slowed_enemies = []  # Reset list of slowed enemies
                
                # Create a 360-degree wave
                wave_points = 36  # More points for smoother circle
                for i in range(wave_points):
                    wave_angle = 2 * math.pi * i / wave_points
                    self.projectiles.append({
                        'x': self.x, 'y': self.y,
                        'dx': math.cos(wave_angle) * 10,  # Fast moving wave
                        'dy': math.sin(wave_angle) * 10,
                        'size': 30, 'color': (255, 200, 0, 180),  # Golden color
                        'damage': 1, 'type': 'slow_wave',  # Does 1 damage and slows
                        'angle': wave_angle, 'lifetime': 1000,
                        'slow_duration': 3000,  # 3 seconds slow effect
                        'slow_factor': 0.5,  # Slows to half speed
                    })

    def update_projectiles(self):
        current_time = pygame.time.get_ticks()
        new_projectiles = []
        for p in self.projectiles:
            # For normal projectiles and some awakening projectiles
            if p['type'] in ['bullet', 'laser', 'magic', 'arc_segment', 'magic_orb', 'freeze_wave', 'slow_wave']:
                p['x'] += p['dx']
                p['y'] += p['dy']
                
                # Check lifetime for timed projectiles
                if 'lifetime' in p and p['lifetime'] > 0:
                    p['lifetime'] -= 16  # Decrease lifetime
                    if p['lifetime'] <= 0:
                        continue  # Skip adding this projectile to new list
                
                # Remove if out of bounds, unless it's a beam that's still active
                if 0 <= p['x'] <= WIDTH and 0 <= p['y'] <= HEIGHT:
                    new_projectiles.append(p)
            
            # For bouncing ball (sniper awakening)
            elif p['type'] == 'bouncing_ball':
                # Update position
                p['x'] += p['dx']
                p['y'] += p['dy']
                
                # Check for collisions with walls and bounce
                hit_wall = False
                
                # Left/right walls
                if p['x'] - p['size'] < 0:
                    p['x'] = p['size']  # Place at wall
                    p['dx'] = -p['dx']  # Reverse x direction
                    hit_wall = True
                elif p['x'] + p['size'] > WIDTH:
                    p['x'] = WIDTH - p['size']  # Place at wall
                    p['dx'] = -p['dx']  # Reverse x direction
                    hit_wall = True
                    
                # Top/bottom walls
                if p['y'] - p['size'] < 0:
                    p['y'] = p['size']  # Place at wall
                    p['dy'] = -p['dy']  # Reverse y direction
                    hit_wall = True
                elif p['y'] + p['size'] > HEIGHT:
                    p['y'] = HEIGHT - p['size']  # Place at wall
                    p['dy'] = -p['dy']  # Reverse y direction
                    hit_wall = True
                
                if hit_wall:
                    p['bounces'] += 1
                    # Create bounce effect
                    self.projectiles.append({
                        'x': p['x'], 'y': p['y'],
                        'dx': 0, 'dy': 0,
                        'size': p['size'] * 1.5,
                        'color': (100, 150, 255, 150),  # Light blue with transparency
                        'damage': 0, 'type': 'bounce_effect',
                        'angle': 0, 'lifetime': 200  # Short lifetime for visual effect
                    })
                
                # Update lifetime
                p['lifetime'] -= 16
                if p['lifetime'] > 0:
                    new_projectiles.append(p)
            
            # For bounce effect (visual only)
            elif p['type'] == 'bounce_effect':
                p['lifetime'] -= 16
                if p['lifetime'] > 0:
                    new_projectiles.append(p)
                
            # For sword and sniper projectiles
            elif p['type'] in ['sword', 'sniper_bullet']:
                if p['type'] == 'sniper_bullet':
                    p['x'] += p['dx']
                    p['y'] += p['dy']
                    
                    # Remove if out of bounds
                    if not (0 <= p['x'] <= WIDTH and 0 <= p['y'] <= HEIGHT):
                        continue
                
                if 'lifetime' in p and p['lifetime'] > 0:
                    p['lifetime'] -= 16  # Decrease lifetime
                    if p['lifetime'] <= 0:
                        continue
                
                new_projectiles.append(p)
            
            # For beam projectiles (robot awakening)
            elif p['type'] == 'beam':
                p['lifetime'] -= 16  # Decrease lifetime
                if p['lifetime'] > 0:
                    new_projectiles.append(p)
                    
            # For knight's arc wave
            elif p['type'] == 'knight_arc_wave':
                p['lifetime'] -= 16  # Decrease lifetime
                if p['lifetime'] > 0:
                    # Move the wave outward
                    p['stage'] += 1
                    new_projectiles.append(p)
                    
            # For samurai slice
            elif p['type'] == 'samurai_slice':
                p['lifetime'] -= 16  # Decrease lifetime
                if p['lifetime'] > 0:
                    new_projectiles.append(p)
        
        self.projectiles = new_projectiles
    
    def create_explosion(self, x, y, radius, damage):
        # Create explosion visual effect with specified radius (12% of screen)
        self.projectiles.append({
            'x': x, 'y': y,
            'dx': 0, 'dy': 0,
            'size': radius, 'color': ORANGE,  # Orange color for explosion
            'damage': damage, 'type': 'explosion',
            'angle': 0, 'lifetime': 300,  # Short lifetime for explosion visual
            'radius': radius,
            'frame': 0,  # Animation frame
            'max_frames': 10  # Total animation frames
        })

    def draw_projectiles(self):
        for p in self.projectiles:
            if p['type'] in ['bullet', 'magic', 'arc_segment']:
                pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), p['size'])
            
            elif p['type'] == 'magic_orb':  # Wizard's awakening projectile
                pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), p['size'])
                # Add a glowing effect
                glow_size = p['size'] + 10
                glow_surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*p['color'], 128), (glow_size, glow_size), glow_size)
                screen.blit(glow_surface, (int(p['x'])-glow_size, int(p['y'])-glow_size), special_flags=pygame.BLEND_ADD)
            
            elif p['type'] == 'bouncing_ball':  # Sniper's awakening
                # Draw blue bouncing ball with glow effect
                pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), p['size'])
                
                # Add pulsing glow effect
                pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.3 + 0.7  # Value between 0.7 and 1.3
                glow_size = int(p['size'] * 1.5 * pulse)
                glow_surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                
                # Multiple layers of glow
                for i in range(3):
                    alpha = int(100 * (1 - i/3))
                    color = (100, 150, 255, alpha)  # Light blue glow
                    pygame.draw.circle(glow_surface, color, (glow_size, glow_size), glow_size - i*5)
                
                screen.blit(glow_surface, (int(p['x'] - glow_size), int(p['y'] - glow_size)), special_flags=pygame.BLEND_ADD)
                
                # Add energy trail
                trail_length = min(5, p['bounces'] + 1)  # Longer trail after more bounces
                for i in range(trail_length):
                    trail_x = int(p['x'] - p['dx'] * (i+1) * 2)
                    trail_y = int(p['y'] - p['dy'] * (i+1) * 2)
                    trail_size = p['size'] * (1 - i/trail_length * 0.8)
                    alpha = int(200 * (1 - i/trail_length))
                    
                    trail_surface = pygame.Surface((int(trail_size*2), int(trail_size*2)), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surface, (*p['color'], alpha), 
                                      (int(trail_size), int(trail_size)), int(trail_size))
                    screen.blit(trail_surface, (trail_x - int(trail_size), trail_y - int(trail_size)))
                    
            elif p['type'] == 'bounce_effect':
                # Draw bounce effect (expanding circle)
                alpha = int(255 * p['lifetime'] / 200)  # Fade out
                size = p['size'] * (1 - p['lifetime'] / 200 * 0.5)  # Expand slightly
                
                bounce_surface = pygame.Surface((int(size*2), int(size*2)), pygame.SRCALPHA)
                pygame.draw.circle(bounce_surface, (*p['color'][:3], alpha), 
                                  (int(size), int(size)), int(size))
                screen.blit(bounce_surface, (int(p['x'] - size), int(p['y'] - size)))
            
            elif p['type'] == 'laser':
                pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), p['size'])
            
            elif p['type'] == 'sniper_bullet':
                # Draw rectangular bullet for sniper
                bullet_surface = pygame.Surface((p['length'], p['size']), pygame.SRCALPHA)
                pygame.draw.rect(bullet_surface, p['color'], (0, 0, p['length'], p['size']))
                
                # Rotate to match direction
                rotated_bullet = pygame.transform.rotate(bullet_surface, -math.degrees(p['angle']))
                bullet_rect = rotated_bullet.get_rect(center=(int(p['x']), int(p['y'])))
                
                # Draw the bullet
                screen.blit(rotated_bullet, bullet_rect)
            
            elif p['type'] == 'sword':
                # Draw rectangular sword in the direction of the mouse
                angle = p['angle']
                
                # Create a surface for the sword
                sword_surface = pygame.Surface((p['length'], p['size']), pygame.SRCALPHA)
                pygame.draw.rect(sword_surface, p['color'], (0, 0, p['length'], p['size']))
                
                # Rotate the surface
                rotated_sword = pygame.transform.rotate(sword_surface, -math.degrees(angle))
                
                # Get the rect for positioning
                sword_rect = rotated_sword.get_rect(center=(p['x'], p['y']))
                
                # Draw the sword
                screen.blit(rotated_sword, sword_rect)
            
            elif p['type'] == 'beam':
                # Draw the robot's awakening beam
                start_x, start_y = int(p['x']), int(p['y'])
                end_x = int(p['x'] + math.cos(p['angle']) * p['length'])
                end_y = int(p['y'] + math.sin(p['angle']) * p['length'])
                
                # Draw the main beam line
                pygame.draw.line(screen, p['color'], (start_x, start_y), (end_x, end_y), p['width'])
                
                # Add a glowing effect around the beam
                for i in range(3):
                    alpha = 150 - i * 50
                    width = p['width'] + i * 4
                    color = (*p['color'], alpha)
                    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    pygame.draw.line(s, color, (start_x, start_y), (end_x, end_y), width)
                    screen.blit(s, (0, 0), special_flags=pygame.BLEND_ADD)
            
            elif p['type'] == 'knight_arc_wave':
                # Draw the Knight's arc wave - now directional using p['angle']
                angle = p['angle']
                arc_radius = min(p['range'], p['stage'] * 10)  # Grows outward
                arc_width = p['width']
                
                # Create semi-transparent surface for the arc
                arc_surface = pygame.Surface((arc_radius*2, arc_radius*2), pygame.SRCALPHA)
                
                # Draw arc (semi-circle facing mouse direction)
                start_angle = math.degrees(angle) - arc_width/2
                end_angle = math.degrees(angle) + arc_width/2
                
                # Draw multiple arcs for a thicker appearance
                for thickness in range(0, 20, 5):
                    arc_color = (*p['color'], 150 - thickness * 5)  # Fade out for thicker parts
                    pygame.draw.arc(arc_surface, arc_color, 
                                   (thickness, thickness, 
                                    (arc_radius-thickness)*2, (arc_radius-thickness)*2), 
                                   math.radians(start_angle), math.radians(end_angle), 10)
                
                # Calculate position to draw the arc surface
                arc_pos = (int(self.x - arc_radius), int(self.y - arc_radius))
                
                # Rotate the arc surface to face in the right direction
                rotated_arc = pygame.transform.rotate(arc_surface, -90)
                rotated_rect = rotated_arc.get_rect(center=(self.x, self.y))
                
                # Draw the arc
                screen.blit(rotated_arc, rotated_rect)
                
            elif p['type'] == 'explosion':
                # Advanced explosion animation
                frame = p['frame']
                max_frames = p['max_frames']
                progress = frame / max_frames
                radius = p['radius'] * (1 - progress * 0.2)  # Slightly shrinks over time
                
                # Create a surface for the explosion
                explosion_size = int(radius * 2)
                explosion_surface = pygame.Surface((explosion_size, explosion_size), pygame.SRCALPHA)
                
                # Draw expanding rings
                for i in range(3):
                    ring_radius = radius * (0.6 + 0.2 * i) * (1 - progress * 0.3)
                    alpha = max(0, int(255 * (1 - progress) * (1 - i * 0.3)))
                    
                    # Gradient colors from yellow to orange to red
                    if i == 0:
                        color = (255, 255, 0, alpha)  # Yellow
                    elif i == 1:
                        color = (255, 165, 0, alpha)  # Orange
                    else:
                        color = (255, 0, 0, alpha)  # Red
                        
                    pygame.draw.circle(explosion_surface, color, 
                                     (explosion_size//2, explosion_size//2), 
                                     int(ring_radius))
                
                # Draw random bright spots (embers)
                for _ in range(15):
                    ember_angle = random.random() * math.pi * 2
                    ember_distance = random.random() * radius * 0.8
                    ember_x = explosion_size//2 + math.cos(ember_angle) * ember_distance
                    ember_y = explosion_size//2 + math.sin(ember_angle) * ember_distance
                    
                    ember_size = random.randint(2, 6)
                    ember_alpha = max(0, int(200 * (1 - progress)))
                    pygame.draw.circle(explosion_surface, (255, 255, 200, ember_alpha),
                                     (int(ember_x), int(ember_y)), ember_size)
                
                # Draw smoke particles at later frames
                if progress > 0.5:
                    smoke_amount = int((progress - 0.5) * 20)
                    for _ in range(smoke_amount):
                        smoke_angle = random.random() * math.pi * 2
                        smoke_distance = random.random() * radius * (0.6 + progress * 0.4)
                        smoke_x = explosion_size//2 + math.cos(smoke_angle) * smoke_distance
                        smoke_y = explosion_size//2 + math.sin(smoke_angle) * smoke_distance
                        
                        smoke_size = random.randint(4, 8)
                        smoke_alpha = max(0, int(100 * (1 - (progress - 0.5) * 2)))
                        smoke_color = (80, 80, 80, smoke_alpha)
                        pygame.draw.circle(explosion_surface, smoke_color,
                                        (int(smoke_x), int(smoke_y)), smoke_size)
                
                # Draw the explosion
                screen.blit(explosion_surface, 
                           (int(p['x'] - explosion_size//2), 
                            int(p['y'] - explosion_size//2)))
                
                # Update animation frame
                p['frame'] += 1
            
            elif p['type'] == 'samurai_slice':
                # Draw a circular slice around the samurai
                slice_surface = pygame.Surface((p['size']*2, p['size']*2), pygame.SRCALPHA)
                
                # Calculate the slice area
                angle = p['angle']
                slice_width = p['width']
                
                # Draw the slice
                start_angle = angle - math.radians(slice_width / 2)
                end_angle = angle + math.radians(slice_width / 2)
                
                # Draw multiple arcs for a nicer appearance
                fade = p['lifetime'] / 150  # 1.0 to 0.0 during lifetime
                for i in range(4):  # One more layer for better effect
                    size = p['size'] - i * 5
                    alpha = int(200 * fade)
                    color = (255, 0, 0, alpha)  # Red with alpha
                    
                    pygame.draw.arc(slice_surface, color, 
                                  (5, 5, size*2-10, size*2-10), 
                                  start_angle, end_angle, 5)  # Thicker line
                
                # Position the slice centered on attack point
                screen.blit(slice_surface, (p['x'] - p['size'], p['y'] - p['size']))
                
                # Add a red trail effect
                trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                trail_points = []
                trail_width = p['width'] * math.pi / 180 * p['size']  # Convert degrees to radians for arc length
                
                for i in range(5):
                    trail_alpha = int(150 * fade * (1 - i/5))
                    trail_angle = angle
                    
                    # Calculate arc points
                    for j in range(int(slice_width)):
                        point_angle = trail_angle - math.radians(slice_width/2) + math.radians(j)
                        point_x = p['x'] + math.cos(point_angle) * (p['size'] - i*5)
                        point_y = p['y'] + math.sin(point_angle) * (p['size'] - i*5)
                        
                        if len(trail_points) < 2:
                            trail_points.append((point_x, point_y))
                        else:
                            trail_points[1] = (point_x, point_y)
                            pygame.draw.line(trail_surface, (255, 0, 0, trail_alpha), 
                                          trail_points[0], trail_points[1], 2)
                            trail_points[0] = trail_points[1]
                
                screen.blit(trail_surface, (0, 0))
            
            elif p['type'] == 'freeze_wave':
                # Draw a circular wave expanding outward
                radius = 15
                alpha = int(200 * (p['lifetime'] / 800))  # Fade as it expands
                
                # Create a surface for the wave
                wave_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(wave_surface, (*p['color'][:3], alpha), (radius, radius), radius)
                
                # Draw the wave
                screen.blit(wave_surface, (int(p['x'] - radius), int(p['y'] - radius)))
                
            elif p['type'] == 'slow_wave':
                # Draw the shooter's slow wave (golden expanding wave)
                radius = 20
                progress = p['lifetime'] / 1000  # 1.0 to 0.0
                alpha = int(180 * progress)  # Fade out over time
                
                # Create a surface for the wave particle
                wave_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(wave_surface, (*p['color'][:3], alpha), (radius, radius), radius)
                
                # Add golden glow effect
                glow_radius = radius * 1.5
                glow_surface = pygame.Surface((int(glow_radius*2), int(glow_radius*2)), pygame.SRCALPHA)
                glow_color = (255, 215, 0, int(alpha * 0.6))  # More transparent version of gold
                pygame.draw.circle(glow_surface, glow_color, 
                                  (int(glow_radius), int(glow_radius)), int(glow_radius))
                
                # Position and draw
                screen.blit(glow_surface, (int(p['x'] - glow_radius), int(p['y'] - glow_radius)))
                screen.blit(wave_surface, (int(p['x'] - radius), int(p['y'] - radius)))

    # Draw awakening cooldown indicator
    def draw_awakening_cooldown(self):
        current_time = pygame.time.get_ticks()
        cooldown_remaining = max(0, self.awakening_cooldown - (current_time - self.last_awakening))
        
        # Position in the bottom right corner
        indicator_width = 150
        indicator_height = 20
        x = WIDTH - indicator_width - 20
        y = HEIGHT - indicator_height - 20
        
        # Draw background
        pygame.draw.rect(screen, GRAY, (x, y, indicator_width, indicator_height))
        
        # Calculate fill width based on cooldown
        fill_width = indicator_width * (1 - cooldown_remaining / self.awakening_cooldown)
        
        # Draw fill
        if cooldown_remaining > 0:
            pygame.draw.rect(screen, YELLOW, (x, y, fill_width, indicator_height))
        else:
            pygame.draw.rect(screen, YELLOW, (x, y, indicator_width, indicator_height))
            
        # Draw border
        pygame.draw.rect(screen, BLACK, (x, y, indicator_width, indicator_height), 2)
        
        # Draw text
        font = pygame.font.SysFont('Arial', 14)
        if cooldown_remaining > 0:
            text = font.render(f"Awakening: {cooldown_remaining/1000:.1f}s", True, BLACK)
        else:
            text = font.render("Awakening: READY", True, BLACK)
        
        text_rect = text.get_rect(center=(x + indicator_width/2, y + indicator_height/2))
        screen.blit(text, text_rect)


# Enemy class
class Enemy:
    def __init__(self, enemy_type='normal', boss_level=1):
        self.type = enemy_type
        self.boss_level = boss_level
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-50, -10)
        self.speed = random.uniform(1.5, 2.5)
        self.projectiles = []
        self.last_shot = 0
        self.frozen = False
        self.frozen_until = 0
        self.slowed = False
        self.slowed_until = 0
        self.slow_factor = 1.0  # No slowdown by default
        
        if enemy_type == 'normal':  # Red enemies
            self.size = 25
            self.color = RED
            self.health = 1
            self.damage = 1
        elif enemy_type == 'purple':
            self.size = 25
            self.color = PURPLE
            self.health = 2
            self.damage = 1
        elif enemy_type == 'green':  # New green enemies
            self.size = int(25 * 1.3)  # 1.3x larger
            self.color = DARK_GREEN
            self.health = 3
            self.damage = 1
            self.speed *= 0.7  # 1.2x slower
        elif enemy_type == 'boss':
            if boss_level == 1:  # First boss
                self.size = 60
                self.color = RED
                self.health = 20
                self.max_health = 20
                self.damage = 1
            elif boss_level == 2:  # Second boss
                self.size = 65
                self.color = GRAY
                self.health = 30
                self.max_health = 30
                self.damage = 1
            elif boss_level == 3:  # General boss
                self.size = 80
                self.color = DARK_RED
                self.health = 50
                self.max_health = 50
                self.damage = 1
            elif boss_level == 4:  # Final boss (after General)
                self.size = 90
                self.color = (100, 0, 100)  # Purple-red
                self.health = 100
                self.max_health = 100
                self.damage = 2
                self.cooldown = 1500  # 1.5 seconds between shots
            
            # Boss spawns in the middle top
            self.x = WIDTH // 2
            self.y = -self.size
            self.speed = 1

    def draw(self):
        # If frozen, draw with a blue tint
        color = self.color
        if self.frozen:
            # Create a blue-tinted version of the original color
            r, g, b = self.color
            color = (max(0, r - 100), max(0, g - 50), min(255, b + 150))
        elif self.slowed:
            # Create a yellow-tinted version for slowed enemies
            r, g, b = self.color
            color = (min(255, r + 50), min(255, g + 50), max(0, b - 50))
        
        pygame.draw.rect(screen, color, (self.x - self.size // 2, self.y - self.size // 2, self.size, self.size))
        
        # Draw horns for normal and purple enemies
        if self.type in ['normal', 'purple']:
            pygame.draw.polygon(screen, BROWN, [
                (self.x - self.size // 4, self.y - self.size // 2),
                (self.x - self.size // 4, self.y - self.size),
                (self.x, self.y - self.size // 2)
            ])
            pygame.draw.polygon(screen, BROWN, [
                (self.x + self.size // 4, self.y - self.size // 2),
                (self.x + self.size // 4, self.y - self.size),
                (self.x, self.y - self.size // 2)
            ])
            
            # Draw eyes
            pygame.draw.circle(screen, BLACK, (self.x - self.size // 4, self.y), 5)
            pygame.draw.circle(screen, BLACK, (self.x + self.size // 4, self.y), 5)
        
        # Draw spikes for green enemies
        elif self.type == 'green':
            # Top spikes
            for i in range(3):
                offset = (i - 1) * self.size // 3
                pygame.draw.polygon(screen, color, [
                    (self.x + offset, self.y - self.size // 2),
                    (self.x + offset, self.y - self.size),
                    (self.x + offset + self.size // 9, self.y - self.size // 2)
                ])
            
            # Eyes (angrier looking)
            pygame.draw.polygon(screen, RED, [
                (self.x - self.size // 3, self.y - self.size // 8),
                (self.x - self.size // 6, self.y - self.size // 8),
                (self.x - self.size // 4, self.y + self.size // 8)
            ])
            pygame.draw.polygon(screen, RED, [
                (self.x + self.size // 3, self.y - self.size // 8),
                (self.x + self.size // 6, self.y - self.size // 8),
                (self.x + self.size // 4, self.y + self.size // 8)
            ])
        
        # Boss-specific details
        if self.type == 'boss':
            if self.boss_level == 1:
                # Large purple eyes
                pygame.draw.circle(screen, PURPLE, (self.x - self.size // 3, self.y - self.size // 6), 10)
                pygame.draw.circle(screen, PURPLE, (self.x + self.size // 3, self.y - self.size // 6), 10)
                # Black center in eyes
                pygame.draw.circle(screen, BLACK, (self.x - self.size // 3, self.y - self.size // 6), 5)
                pygame.draw.circle(screen, BLACK, (self.x + self.size // 3, self.y - self.size // 6), 5)
                # Smile
                pygame.draw.arc(screen, DARK_RED, 
                                (self.x - self.size // 3, self.y, self.size * 2 // 3, self.size // 3), 
                                0, math.pi, 3)
            elif self.boss_level == 2:
                # Large purple eyes for gray boss
                pygame.draw.circle(screen, PURPLE, (self.x - self.size // 3, self.y - self.size // 6), 12)
                pygame.draw.circle(screen, PURPLE, (self.x + self.size // 3, self.y - self.size // 6), 12)
                # Black center in eyes
                pygame.draw.circle(screen, BLACK, (self.x - self.size // 3, self.y - self.size // 6), 6)
                pygame.draw.circle(screen, BLACK, (self.x + self.size // 3, self.y - self.size // 6), 6)
                # Smile
                pygame.draw.arc(screen, DARK_RED, 
                                (self.x - self.size // 3, self.y, self.size * 2 // 3, self.size // 3), 
                                0, math.pi, 4)
            elif self.boss_level == 3:  # General boss
                # Decorative elements for General
                # Crown
                crown_points = [
                    (self.x - self.size // 2, self.y - self.size // 2),
                    (self.x - self.size // 2, self.y - self.size // 2 - 15),
                    (self.x - self.size // 4, self.y - self.size // 2 - 5),
                    (self.x, self.y - self.size // 2 - 20),
                    (self.x + self.size // 4, self.y - self.size // 2 - 5),
                    (self.x + self.size // 2, self.y - self.size // 2 - 15),
                    (self.x + self.size // 2, self.y - self.size // 2)
                ]
                pygame.draw.polygon(screen, YELLOW, crown_points)
                
                # Eyes
                pygame.draw.circle(screen, RED, (self.x - self.size // 3, self.y - self.size // 6), 12)
                pygame.draw.circle(screen, RED, (self.x + self.size // 3, self.y - self.size // 6), 12)
                # Black center in eyes
                pygame.draw.circle(screen, BLACK, (self.x - self.size // 3, self.y - self.size // 6), 6)
                pygame.draw.circle(screen, BLACK, (self.x + self.size // 3, self.y - self.size // 6), 6)
                
                # Angry mouth
                pygame.draw.arc(screen, BLACK, 
                               (self.x - self.size // 3, self.y + self.size // 6, self.size * 2 // 3, self.size // 3), 
                               math.pi, 2 * math.pi, 4)
            
            elif self.boss_level == 4:  # Final boss
                # Bigger, more intimidating design
                # Crown with jewels
                crown_points = [
                    (self.x - self.size // 2, self.y - self.size // 2),
                    (self.x - self.size // 2, self.y - self.size // 2 - 20),
                    (self.x - self.size // 3, self.y - self.size // 2 - 10),
                    (self.x - self.size // 6, self.y - self.size // 2 - 25),
                    (self.x, self.y - self.size // 2 - 15),
                    (self.x + self.size // 6, self.y - self.size // 2 - 25),
                    (self.x + self.size // 3, self.y - self.size // 2 - 10),
                    (self.x + self.size // 2, self.y - self.size // 2 - 20),
                    (self.x + self.size // 2, self.y - self.size // 2)
                ]
                pygame.draw.polygon(screen, (255, 215, 0), crown_points)  # Gold color
                
                # Jewels in crown
                pygame.draw.circle(screen, RED, (self.x - self.size // 3, self.y - self.size // 2 - 15), 5)
                pygame.draw.circle(screen, BLUE, (self.x, self.y - self.size // 2 - 15), 5)
                pygame.draw.circle(screen, GREEN, (self.x + self.size // 3, self.y - self.size // 2 - 15), 5)
                
                # Glowing eyes
                for i in range(3):
                    alpha = 200 - i * 60
                    radius = 12 + i * 3
                    s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (255, 0, 0, alpha), (radius, radius), radius)
                    screen.blit(s, (int(self.x - self.size // 3 - radius), int(self.y - self.size // 6 - radius)))
                    screen.blit(s, (int(self.x + self.size // 3 - radius), int(self.y - self.size // 6 - radius)))
                
                # Evil grin
                pygame.draw.arc(screen, WHITE, 
                               (self.x - self.size // 3, self.y + self.size // 6, self.size * 2 // 3, self.size // 3), 
                               0, math.pi, 4)
                
                # Draw projectiles
                self.draw_projectiles()
            
            # Draw boss health bar
            self.draw_health_bar()
            
        # Draw ice crystals if frozen
        if self.frozen:
            # Draw small ice crystals around the enemy
            for i in range(5):
                angle = random.random() * math.pi * 2
                distance = self.size * 0.6
                crystal_x = self.x + math.cos(angle) * distance
                crystal_y = self.y + math.sin(angle) * distance
                crystal_size = random.randint(3, 6)
                
                # Draw a small blue crystal
                pygame.draw.polygon(screen, (100, 150, 255), [
                    (crystal_x, crystal_y - crystal_size),
                    (crystal_x + crystal_size, crystal_y),
                    (crystal_x, crystal_y + crystal_size),
                    (crystal_x - crystal_size, crystal_y)
                ])
        
        # Draw slow effect if slowed
        elif self.slowed:
            # Draw yellow sparkles around the enemy to indicate slowdown
            for i in range(3):
                angle = (pygame.time.get_ticks() / 200 + i * 2.1) % (2 * math.pi)  # Rotating sparkles
                distance = self.size * 0.7
                sparkle_x = self.x + math.cos(angle) * distance
                sparkle_y = self.y + math.sin(angle) * distance
                sparkle_size = random.randint(2, 4)
                
                # Draw a small yellow sparkle
                pygame.draw.circle(screen, (255, 255, 0), (int(sparkle_x), int(sparkle_y)), sparkle_size)

    def draw_projectiles(self):
        for p in self.projectiles:
            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), p['size'])
            
            # Add glow effect for final boss projectiles
            if self.boss_level == 4:
                glow_size = p['size'] + 10
                glow_surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                for i in range(3):
                    alpha = 150 - i * 40
                    radius = glow_size - i * 3
                    pygame.draw.circle(glow_surface, (*p['color'], alpha), (glow_size, glow_size), radius)
                
                screen.blit(glow_surface, (int(p['x'] - glow_size), int(p['y'] - glow_size)), special_flags=pygame.BLEND_ADD)

    def update_projectiles(self):
        new_projectiles = []
        for p in self.projectiles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            
            # Remove if out of bounds
            if 0 <= p['x'] <= WIDTH and 0 <= p['y'] <= HEIGHT:
                new_projectiles.append(p)
        
        self.projectiles = new_projectiles

    def shoot(self, target_x, target_y):
        # Don't shoot if frozen
        if self.frozen:
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.cooldown:
            self.last_shot = current_time
            
            # Calculate direction toward target
            dx = target_x - self.x
            dy = target_y - self.y
            distance = max(1, (dx**2 + dy**2)**0.5)
            dx /= distance
            dy /= distance
            
            # Create projectile
            if self.boss_level == 4:  # Final boss shoots bigger projectiles
                self.projectiles.append({
                    'x': self.x, 'y': self.y,
                    'dx': dx * 5, 'dy': dy * 5,
                    'size': 20, 'color': (255, 0, 100),
                    'damage': self.damage
                })
            else:
                self.projectiles.append({
                    'x': self.x, 'y': self.y,
                    'dx': dx * 4, 'dy': dy * 4,
                    'size': 10, 'color': self.color,
                    'damage': self.damage
                })

    def draw_health_bar(self):
        if self.type == 'boss':
            # Health bar dimensions
            bar_width = self.size * 1.5
            bar_height = 10
            
            # Position above the boss
            x = self.x - bar_width / 2
            y = self.y - self.size / 2 - 20
            
            # Draw background (empty health)
            pygame.draw.rect(screen, GRAY, (x, y, bar_width, bar_height))
            
            # Draw filled health
            health_percentage = self.health / self.max_health
            filled_width = bar_width * health_percentage
            
            # Color changes based on health percentage
            if health_percentage > 0.6:
                color = GREEN
            elif health_percentage > 0.3:
                color = YELLOW
            else:
                color = RED
                
            pygame.draw.rect(screen, color, (x, y, filled_width, bar_height))
            
            # Draw border
            pygame.draw.rect(screen, BLACK, (x, y, bar_width, bar_height), 2)
            
            # Draw health text
            font = pygame.font.SysFont('Arial', 14)
            health_text = font.render(f"{self.health}/{self.max_health}", True, WHITE)
            text_rect = health_text.get_rect(center=(self.x, y - 10))
            screen.blit(health_text, text_rect)

    def move(self, player_x, player_y, modifier=1.0):
        # Don't move if frozen
        current_time = pygame.time.get_ticks()
        if self.frozen and current_time < self.frozen_until:
            return
        elif self.frozen:
            self.frozen = False  # Unfreeze if time is up
        
        # Check slow status
        if self.slowed and current_time < self.slowed_until:
            # Apply slow factor
            current_modifier = modifier * self.slow_factor
        elif self.slowed:
            self.slowed = False  # Remove slow effect if time is up
            self.slow_factor = 1.0  # Reset slow factor
            current_modifier = modifier
        else:
            current_modifier = modifier
        
        # Move towards player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = max(1, (dx**2 + dy**2)**0.5)  # Avoid division by zero
        dx /= distance
        dy /= distance
        
        # Apply speed and modifier
        self.x += dx * self.speed * current_modifier
        self.y += dy * self.speed * current_modifier
    
    def freeze(self, duration):
        self.frozen = True
        self.frozen_until = pygame.time.get_ticks() + duration
    
    def slow(self, duration, factor):
        self.slowed = True
        self.slowed_until = pygame.time.get_ticks() + duration
        self.slow_factor = factor  # Factor < 1.0 means slower
    
    def is_hit_by_projectile(self, projectile):
        # For projectiles that can pass through enemies
        penetrates = projectile.get('penetrate', False)
        
        if projectile['type'] == 'sword':
            # For sword, check distance from sword center
            dx = self.x - projectile['x']
            dy = self.y - projectile['y']
            distance = (dx**2 + dy**2)**0.5
            
            # Increase effective hitbox for sword's length
            sword_reach = projectile['length'] // 2 + self.size // 2
            return distance < sword_reach
        
        elif projectile['type'] == 'knight_arc_wave':
            # For knight's arc wave, check if enemy is in the arc area
            # Calculate distance from player (wave origin)
            dx = self.x - projectile['x']
            dy = self.y - projectile['y']
            distance = (dx**2 + dy**2)**0.5
            
            # Calculate angle between wave direction and enemy
            wave_angle = projectile['angle']
            enemy_angle = math.atan2(dy, dx)
            
            # Normalize angle difference
            angle_diff = abs((enemy_angle - wave_angle + math.pi) % (2 * math.pi) - math.pi)
            
            # Check if enemy is within wave's arc width and range
            arc_radius = min(projectile['range'], projectile['stage'] * 10)
            arc_width_rad = math.radians(projectile['width'] / 2)
            
            return distance <= arc_radius and angle_diff <= arc_width_rad
        
        elif projectile['type'] == 'beam':
            # For robot's awakening beam, check if enemy is in the beam's path
            start_x, start_y = projectile['x'], projectile['y']
            beam_angle = projectile['angle']
            beam_length = projectile['length']
            
            # Calculate end point of beam
            end_x = start_x + math.cos(beam_angle) * beam_length
            end_y = start_y + math.sin(beam_angle) * beam_length
            
            # Calculate closest point on line segment to enemy center
            line_vec_x = end_x - start_x
            line_vec_y = end_y - start_y
            line_len = (line_vec_x**2 + line_vec_y**2)**0.5
            
            if line_len == 0:  # If beam has zero length
                return False
                
            # Normalize line vector
            line_vec_x /= line_len
            line_vec_y /= line_len
            
            # Calculate vector from start point to enemy
            enemy_vec_x = self.x - start_x
            enemy_vec_y = self.y - start_y
            
            # Project enemy vector onto line vector (dot product)
            projection = enemy_vec_x * line_vec_x + enemy_vec_y * line_vec_y
            
            # Clamp projection to line segment
            projection = max(0, min(line_len, projection))
            
            # Calculate closest point on line
            closest_x = start_x + projection * line_vec_x
            closest_y = start_y + projection * line_vec_y
            
            # Calculate distance from closest point to enemy center
            dx = self.x - closest_x
            dy = self.y - closest_y
            distance = (dx**2 + dy**2)**0.5
            
            # Check if enemy is within beam width
            beam_width = projectile['width'] + self.size // 2
            return distance < beam_width
            
        elif projectile['type'] == 'explosion':
            # Check if enemy is within explosion radius
            dx = self.x - projectile['x']
            dy = self.y - projectile['y']
            distance = (dx**2 + dy**2)**0.5
            return distance < (projectile['radius'] + self.size // 2)
            
        elif projectile['type'] == 'samurai_slice':
            # For samurai's slice, check if enemy is in range and within the slice angle
            dx = self.x - projectile['x']
            dy = self.y - projectile['y']
            distance = (dx**2 + dy**2)**0.5
            
            if distance > projectile['size'] + self.size // 2:
                return False
                
            # Check if enemy is within the slice angle
            enemy_angle = math.atan2(dy, dx)
            slice_angle = projectile['angle']
            
            # Calculate angle difference
            angle_diff = abs((enemy_angle - slice_angle + math.pi) % (2 * math.pi) - math.pi)
            
            # Check if within slice width
            return angle_diff <= math.radians(projectile['width'] / 2)
            
        elif projectile['type'] == 'sniper_bullet':
            # For sniper's rectangular bullet
            dx = self.x - projectile['x']
            dy = self.y - projectile['y']
            distance = (dx**2 + dy**2)**0.5
            
            # Use a slightly larger hitbox for rectangular bullet
            bullet_reach = max(projectile['length'], projectile['size']) / 2 + self.size / 2
            return distance < bullet_reach
        
        elif projectile['type'] == 'bouncing_ball':
            # For sniper's bouncing ball awakening
            dx = self.x - projectile['x']
            dy = self.y - projectile['y']
            distance = (dx**2 + dy**2)**0.5
            
            hit = distance < (self.size // 2 + projectile['size'])
            return hit
            
        elif projectile['type'] == 'slow_wave':
            # For shooter's awakening slow wave
            dx = self.x - projectile['x']
            dy = self.y - projectile['y']
            distance = (dx**2 + dy**2)**0.5
            
            # If hit by slow wave, apply slow effect
            if distance < (self.size // 2 + projectile['size'] * 1.5):
                self.slow(projectile['slow_duration'], projectile['slow_factor'])
                return True
            return False
            
        else:
            # For bullet/laser/magic projectiles
            dx = self.x - projectile['x']
            dy = self.y - projectile['y']
            distance = (dx**2 + dy**2)**0.5
            hit = distance < (self.size // 2 + projectile['size'])
            return hit

# Heart drop class
class Heart:
    def __init__(self, x, y, is_boss_heart=False):
        self.x = x
        self.y = y
        # Make boss hearts larger
        self.size = 40 if is_boss_heart else 20
        self.color = PINK
        self.is_boss_heart = is_boss_heart
    
    def draw(self):
        # Draw a heart shape
        pygame.draw.circle(screen, self.color, (self.x - self.size // 4, self.y - self.size // 4), self.size // 2)
        pygame.draw.circle(screen, self.color, (self.x + self.size // 4, self.y - self.size // 4), self.size // 2)
        points = [
            (self.x - self.size // 2, self.y - self.size // 5),
            (self.x + self.size // 2, self.y - self.size // 5),
            (self.x, self.y + self.size // 2)
        ]
        pygame.draw.polygon(screen, self.color, points)
        
        # Add glow effect for boss hearts
        if self.is_boss_heart:
            glow_size = self.size + 10
            glow_surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
            
            # Draw the glow as a soft circle
            for i in range(3):
                alpha = 100 - i * 30
                size = glow_size - i * 3
                pygame.draw.circle(glow_surface, (*self.color, alpha), (glow_size, glow_size), size)
            
            screen.blit(glow_surface, (self.x - glow_size, self.y - glow_size), special_flags=pygame.BLEND_ADD)
    
    def is_collected(self, player_x, player_y, player_size):
        dx = self.x - player_x
        dy = self.y - player_y
        distance = (dx**2 + dy**2)**0.5
        return distance < (player_size // 2 + self.size // 2)

# Game class
class Game:
    def __init__(self):
        self.state = GameState.HOME
        self.selected_character = CharacterType.SQUARE
        self.player = None
        self.enemies = []
        self.hearts = []
        self.score = 0
        self.high_score = 0
        self.game_start_time = 0
        self.last_enemy_spawn = 0
        self.last_score_update = 0
        
        # Boss and game progression tracking
        self.general_defeated = False
        self.general_defeat_time = 0
        self.final_boss_spawned = False
        self.final_boss_defeated = False
        
        # Load high score if exists
        self.load_high_score()
    
    def load_high_score(self):
        try:
            if os.path.exists("highscore.txt"):
                with open("highscore.txt", "r") as f:
                    self.high_score = int(f.read())
        except:
            self.high_score = 0
    
    def save_high_score(self):
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass
    
    def start_game(self):
        self.player = Character(self.selected_character)
        self.enemies = []
        self.hearts = []
        self.score = 0
        self.game_start_time = pygame.time.get_ticks()
        self.last_enemy_spawn = pygame.time.get_ticks()
        self.last_score_update = pygame.time.get_ticks()
        self.general_defeated = False
        self.general_defeat_time = 0
        self.final_boss_spawned = False
        self.final_boss_defeated = False
        self.state = GameState.PLAYING
    
    def draw_home_screen(self):
        # Background
        screen.fill(BLACK)
        
        # Title
        font = pygame.font.SysFont('Arial', 50)
        title = font.render("Epic Adventure", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        
        # Character selection
        font = pygame.font.SysFont('Arial', 30)
        text = font.render("Select Your Character:", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 150))
        
        # Character display
        character_x = WIDTH // 2
        character_y = 250
        character_size = 50
        
        # Draw selected character
        if self.selected_character == CharacterType.SQUARE:
            pygame.draw.rect(screen, BLUE, 
                             (character_x - character_size // 2, 
                              character_y - character_size // 2, 
                              character_size, character_size))
            character_name = "Blue Square"
            character_desc = "Fast attack rate, 1 health"
            character_awakening = "Awakening: 25 bullets in a circle"
        elif self.selected_character == CharacterType.KNIGHT:
            pygame.draw.rect(screen, (150, 75, 0), 
                             (character_x - character_size // 2, 
                              character_y - character_size // 2, 
                              character_size, character_size))
            # Grid pattern
            for i in range(3):
                pygame.draw.line(screen, BLACK, 
                                 (character_x - character_size // 2, character_y - character_size // 2 + i * character_size // 3), 
                                 (character_x + character_size // 2, character_y - character_size // 2 + i * character_size // 3), 2)
                pygame.draw.line(screen, BLACK, 
                                 (character_x - character_size // 2 + i * character_size // 3, character_y - character_size // 2), 
                                 (character_x - character_size // 2 + i * character_size // 3, character_y + character_size // 2), 2)
            character_name = "Square Knight"
            character_desc = "Melee attack (2 damage), 2 health"
            character_awakening = "Directed arc wave (5 damage)"
        elif self.selected_character == CharacterType.ROBOT:
            # Hexagonal robot
            points = []
            for i in range(6):
                angle = 2 * math.pi * i / 6
                points.append((
                    character_x + int(character_size / 2 * math.cos(angle)),
                    character_y + int(character_size / 2 * math.sin(angle))
                ))
            pygame.draw.polygon(screen, (100, 100, 100), points)
            # Robot eyes
            pygame.draw.circle(screen, RED, (character_x - character_size // 4, character_y - character_size // 6), character_size // 8)
            pygame.draw.circle(screen, RED, (character_x + character_size // 4, character_y - character_size // 6), character_size // 8)
            character_name = "Hexagon Robot"
            character_desc = "Rapid fire laser, 1 health"
            character_awakening = "Beam + speed boost (5 damage)"
        elif self.selected_character == CharacterType.WIZARD:
            # Circular wizard
            pygame.draw.circle(screen, (0, 100, 100), (character_x, character_y), character_size // 2)
            # Wizard hat
            hat_points = [
                (character_x, character_y - character_size - character_size // 3),
                (character_x - character_size // 2, character_y - character_size // 2),
                (character_x + character_size // 2, character_y - character_size // 2)
            ]
            pygame.draw.polygon(screen, GREEN, hat_points)
            # Rounded tip for hat
            pygame.draw.circle(screen, GREEN, (character_x, character_y - character_size - character_size // 3), character_size // 8)
            character_name = "Circle Wizard"
            character_desc = "Powerful magic (2 damage), 2 health"
            character_awakening = "Large orb (3 damage, piercing)"
        elif self.selected_character == CharacterType.SNIPER:
            # Light green square with dark green suspenders
            pygame.draw.rect(screen, LIGHT_GREEN, (character_x - character_size // 2, character_y - character_size // 2, character_size, character_size))
            # Dark green suspenders (vertical straps)
            pygame.draw.line(screen, DARK_GREEN, 
                            (character_x - character_size // 4, character_y - character_size // 2), 
                            (character_x - character_size // 4, character_y + character_size // 2), 4)
            pygame.draw.line(screen, DARK_GREEN, 
                            (character_x + character_size // 4, character_y - character_size // 2), 
                            (character_x + character_size // 4, character_y + character_size // 2), 4)
            # Horizontal connector
            pygame.draw.line(screen, DARK_GREEN, 
                            (character_x - character_size // 4, character_y), 
                            (character_x + character_size // 4, character_y), 3)
            character_name = "Sniper"
            character_desc = "High damage (3), 1 health"
            character_awakening = "Bouncing blue ball (2 damage)"
        elif self.selected_character == CharacterType.SAMURAI:
            # Red octagon with dark red armor
            points = []
            for i in range(8):
                angle = 2 * math.pi * i / 8
                points.append((
                    character_x + int(character_size / 2 * math.cos(angle)),
                    character_y + int(character_size / 2 * math.sin(angle))
                ))
            pygame.draw.polygon(screen, RED, points)
            
            # Dark red armor - create a smaller octagon inside
            armor_points = []
            for i in range(8):
                angle = 2 * math.pi * i / 8
                armor_points.append((
                    character_x + int(character_size / 3 * math.cos(angle)),
                    character_y + int(character_size / 3 * math.sin(angle))
                ))
            pygame.draw.polygon(screen, DARK_RED, armor_points)
            character_name = "Samurai"
            character_desc = "Circular attack, 3 health"
            character_awakening = "Freeze enemies (5 seconds)"
        elif self.selected_character == CharacterType.SHOOTER:
            # Light gray pentagon with dark brown jacket
            points = []
            for i in range(5):
                angle = 2 * math.pi * i / 5 - math.pi/2  # Start from top point
                points.append((
                    character_x + int(character_size / 2 * math.cos(angle)),
                    character_y + int(character_size / 2 * math.sin(angle))
                ))
            pygame.draw.polygon(screen, LIGHT_GRAY, points)
            
            # Dark brown jacket (drawing a smaller pentagon inside)
            jacket_points = []
            for i in range(5):
                angle = 2 * math.pi * i / 5 - math.pi/2
                radius = character_size / 3 if i == 0 else character_size / 4
                jacket_points.append((
                    character_x + int(radius * math.cos(angle)),
                    character_y + int(radius * math.sin(angle))
                ))
            pygame.draw.polygon(screen, DARK_BROWN, jacket_points)
            
            character_name = "Shooter"
            character_desc = "Triple shot (1 damage each), 2 health"
            character_awakening = "Slowing wave (1 damage)"
            
        # Navigation arrows
        arrow_width = 30
        arrow_height = 20
        # Left arrow
        pygame.draw.polygon(screen, WHITE, [
            (character_x - 80, character_y),
            (character_x - 80 + arrow_width, character_y - arrow_height // 2),
            (character_x - 80 + arrow_width, character_y + arrow_height // 2)
        ])
        # Right arrow
        pygame.draw.polygon(screen, WHITE, [
            (character_x + 80, character_y),
            (character_x + 80 - arrow_width, character_y - arrow_height // 2),
            (character_x + 80 - arrow_width, character_y + arrow_height // 2)
        ])
        
        # Character name and description
        name_text = font.render(character_name, True, WHITE)
        screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, 320))
        
        desc_font = pygame.font.SysFont('Arial', 24)
        desc_text = desc_font.render(character_desc, True, WHITE)
        screen.blit(desc_text, (WIDTH // 2 - desc_text.get_width() // 2, 360))
        
        # Awakening description
        awakening_text = desc_font.render(character_awakening, True, WHITE)
        screen.blit(awakening_text, (WIDTH // 2 - awakening_text.get_width() // 2, 390))
        
        # Controls info
        controls_text = desc_font.render("Right-click to use awakening ability", True, WHITE)
        screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, 420))
        
        # Play button
        pygame.draw.rect(screen, YELLOW, (WIDTH // 2 - 75, 450, 150, 50))
        play_text = font.render("Play", True, BLACK)
        screen.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2, 460))
        
        # High score display
        high_score_font = pygame.font.SysFont('Arial', 24)
        high_score_text = high_score_font.render(f"High Score: {self.high_score}", True, WHITE)
        screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, 520))

    def draw_victory_screen(self):
        # Background
        screen.fill(BLACK)
        
        # Victory message
        font = pygame.font.SysFont('Arial', 50)
        title = font.render("Congratulations!", True, RED)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
        
        # Subtext
        subtitle_font = pygame.font.SysFont('Arial', 36)
        subtitle = subtitle_font.render("You completed the game!", True, WHITE)
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 220))
        
        # Score display
        score_font = pygame.font.SysFont('Arial', 30)
        score_text = score_font.render(f"Final Score: {self.score}", True, YELLOW)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 300))
        
        high_score_text = score_font.render(f"High Score: {self.high_score}", True, GREEN)
        screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, 340))
        
        # Return to main menu button
        pygame.draw.rect(screen, BLUE, (WIDTH // 2 - 100, 450, 200, 60))
        menu_font = pygame.font.SysFont('Arial', 28)
        menu_text = menu_font.render("Main Menu", True, WHITE)
        screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, 465))
    
    def draw_pause_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
        screen.blit(overlay, (0, 0))
        
        # Pause text
        font = pygame.font.SysFont('Arial', 50)
        title = font.render("PAUSED", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
        
        # Instructions
        inst_font = pygame.font.SysFont('Arial', 24)
        inst_text = inst_font.render("Press ESC to resume or M for main menu", True, WHITE)
        screen.blit(inst_text, (WIDTH // 2 - inst_text.get_width() // 2, 280))
        
        # Current score
        score_font = pygame.font.SysFont('Arial', 28)
        score_text = score_font.render(f"Score: {self.score}", True, YELLOW)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 350))
    
    def handle_home_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Check if arrows clicked
            character_x = WIDTH // 2
            character_y = 250
            
            # Left arrow clicked
            if (character_x - 80 - 30 < mouse_x < character_x - 80 + 30 and 
                character_y - 20 < mouse_y < character_y + 20):
                current_value = self.selected_character.value
                current_value = (current_value - 1) % 7  # Updated for 7 character types
                self.selected_character = CharacterType(current_value)
            
            # Right arrow clicked
            elif (character_x + 80 - 30 < mouse_x < character_x + 80 + 30 and 
                  character_y - 20 < mouse_y < character_y + 20):
                current_value = self.selected_character.value
                current_value = (current_value + 1) % 7  # Updated for 7 character types
                self.selected_character = CharacterType(current_value)
            
            # Play button clicked
            elif WIDTH // 2 - 75 < mouse_x < WIDTH // 2 + 75 and 450 < mouse_y < 500:
                self.start_game()
    
    def handle_victory_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Check if menu button clicked
            if WIDTH // 2 - 100 < mouse_x < WIDTH // 2 + 100 and 450 < mouse_y < 510:
                self.state = GameState.HOME
    
    def handle_pause_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.PLAYING
            elif event.key == pygame.K_m:
                self.state = GameState.HOME
    
    def draw_game_screen(self):
        # Background
        screen.fill(BLACK)
        
        # Draw player
        self.player.draw()
        self.player.draw_projectiles()
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw()
        
        # Draw hearts
        for heart in self.hearts:
            heart.draw()
        
        # Draw score and health
        font = pygame.font.SysFont('Arial', 24)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        health_text = font.render(f"Health: {self.player.health}", True, WHITE)
        screen.blit(health_text, (20, 50))
        
        # Draw awakening cooldown indicator
        self.player.draw_awakening_cooldown()
        
        # Draw pause button in top right corner
        pause_button_width = 80
        pause_button_height = 30
        pause_x = WIDTH - pause_button_width - 20
        pause_y = 20
        
        # Draw button background
        pygame.draw.rect(screen, GRAY, (pause_x, pause_y, pause_button_width, pause_button_height))
        pygame.draw.rect(screen, BLACK, (pause_x, pause_y, pause_button_width, pause_button_height), 2)
        
        # Draw button text
        pause_font = pygame.font.SysFont('Arial', 20)
        pause_text = pause_font.render("PAUSE", True, BLACK)
        text_rect = pause_text.get_rect(center=(pause_x + pause_button_width//2, pause_y + pause_button_height//2))
        screen.blit(pause_text, text_rect)
    
    def handle_game_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Check if pause button was clicked
            pause_button_width = 80
            pause_button_height = 30
            pause_x = WIDTH - pause_button_width - 20
            pause_y = 20
            
            if pause_x <= mouse_x <= pause_x + pause_button_width and pause_y <= mouse_y <= pause_y + pause_button_height:
                self.state = GameState.PAUSED
                return
            
            # Left mouse button for normal attack
            if event.button == 1:  
                self.player.shoot(mouse_x, mouse_y)
            # Right mouse button for awakening ability
            elif event.button == 3:  
                self.player.awakening(mouse_x, mouse_y)
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.PAUSED
    
    def update_game(self):
        current_time = pygame.time.get_ticks()
        game_elapsed = current_time - self.game_start_time
        
        # Move player
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        
        # Update projectiles
        self.player.update_projectiles()
        
        # Update enemy projectiles (for final boss)
        for enemy in self.enemies:
            if hasattr(enemy, 'projectiles') and enemy.projectiles:
                enemy.update_projectiles()
                
                # Check if enemy projectiles hit player
                for projectile in enemy.projectiles[:]:
                    dx = self.player.x - projectile['x']
                    dy = self.player.y - projectile['y']
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance < (self.player.size // 2 + projectile['size']):
                        self.player.health -= projectile['damage']
                        enemy.projectiles.remove(projectile)
                        
                        if self.player.health <= 0:
                            self.end_game()
                            return
            
            # Have the final boss shoot at the player
            if enemy.type == 'boss' and enemy.boss_level == 4:
                enemy.shoot(self.player.x, self.player.y)
                
            # Check if enemies should be frozen (for samurai awakening)
            if self.player.type == CharacterType.SAMURAI and current_time < self.player.freeze_end_time:
                enemy.freeze(5000)  # Freeze for 5 seconds
        
        # Different enemy spawning logic based on game state
        if self.general_defeated:
            time_since_general = current_time - self.general_defeat_time
            
            # Spawn final boss after 150 seconds
            if time_since_general >= 150000 and not self.final_boss_spawned:
                self.final_boss_spawned = True
                self.enemies.append(Enemy('boss', 4))  # Add final boss
            
            # Otherwise spawn enemies in waves based on time since general defeat
            elif current_time - self.last_enemy_spawn >= 3000:  # Every 3 seconds
                self.last_enemy_spawn = current_time
                
                # Spawn green monsters with adjusted speed based on time
                green_faster = time_since_general >= 40000  # 40 seconds after general
                
                # Determine spawn counts based on time since general defeat
                if time_since_general >= 80000:  # 80+ seconds
                    red_count = random.randint(8, 10)
                    purple_count = random.randint(6, 7)
                    green_count = random.randint(3, 4)
                elif time_since_general >= 40000:  # 40-80 seconds
                    red_count = random.randint(7, 8)
                    purple_count = random.randint(4, 5)
                    green_count = random.randint(2, 3)
                else:  # 0-40 seconds
                    red_count = 6
                    purple_count = random.randint(3, 4)
                    green_count = random.randint(2, 3)
                
                # Spawn red enemies
                for _ in range(red_count):
                    self.enemies.append(Enemy('normal'))
                
                # Spawn purple enemies
                for _ in range(purple_count):
                    self.enemies.append(Enemy('purple'))
                
                # Spawn green enemies
                for _ in range(green_count):
                    enemy = Enemy('green')
                    if green_faster:
                        enemy.speed *= 1.5  # Make 1.2x faster (offsetting the initial 0.8x)
                    self.enemies.append(enemy)
        
        else:
            # Standard game progression (before general boss)
            # Calculate when to spawn the General boss
            if game_elapsed >= 320000:
                # Spawn General boss if not present
                general_present = False
                for enemy in self.enemies:
                    if enemy.type == 'boss' and enemy.boss_level == 3:
                        general_present = True
                        break
                
                if not general_present:
                    self.enemies.append(Enemy('boss', 3))  # Add General boss
            
            # For regular enemies
            if current_time - self.last_enemy_spawn >= 3000:  # Every 3 seconds
                self.last_enemy_spawn = current_time
                
                # Spawn standard enemies
                spawn_count = self.get_spawn_count(game_elapsed)
                
                for _ in range(spawn_count):
                    enemy_type = 'normal'
                    if game_elapsed >= 150000 and random.random() < 0.3:
                        enemy_type = 'purple'
                    
                    self.enemies.append(Enemy(enemy_type))
        
        # Update score every half second
        if current_time - self.last_score_update >= 500:
            self.score += 1
            self.last_score_update = current_time
        
        # Move enemies and check for collisions
        speed_modifier = self.get_speed_modifier(game_elapsed)
        
        for enemy in self.enemies[:]:
            # Move enemies
            if hasattr(enemy, 'is_projectile') and enemy.is_projectile:
                # For boss projectiles, move in straight line
                enemy.x += enemy.dx
                enemy.y += enemy.dy
                
                # Remove if out of bounds
                if not (0 <= enemy.x <= WIDTH and 0 <= enemy.y <= HEIGHT):
                    self.enemies.remove(enemy)
                    continue
            else:
                # Normal movement towards player
                enemy.move(self.player.x, self.player.y, speed_modifier)
            
            # Check if enemy hits player
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            distance = (dx**2 + dy**2)**0.5
            
            if distance < (self.player.size // 2 + enemy.size // 2):
                self.player.health -= enemy.damage
                self.enemies.remove(enemy)
                
                if self.player.health <= 0:
                    self.end_game()
                    return
                continue
            
            # Check if enemy is hit by player projectiles
            enemy_hit = False
            for projectile in self.player.projectiles[:]:
                if enemy.is_hit_by_projectile(projectile):
                    enemy.health -= projectile['damage']
                    
                    # For bouncing ball, don't remove since it bounces
                    if projectile['type'] == 'bouncing_ball':
                        continue
                    
                    # For slow wave, just check if it hit (don't remove)
                    if projectile['type'] == 'slow_wave':
                        continue
                    
                    # For explosion projectiles, don't remove them on hit
                    if projectile['type'] == 'explosion':
                        continue
                    
                    # Remove projectile only if it doesn't penetrate
                    if not projectile.get('penetrate', False) and projectile['type'] not in ['sword', 'beam', 'knight_arc_wave']:
                        self.player.projectiles.remove(projectile)
                    
                    enemy_hit = True
                    if enemy.health <= 0:
                        # Handle enemy defeat
                        if enemy.type == 'boss':
                            # Track which boss was defeated
                            if enemy.boss_level == 3:  # General boss
                                self.general_defeated = True
                                self.general_defeat_time = current_time
                                # Spawn heart
                                self.hearts.append(Heart(enemy.x, enemy.y, is_boss_heart=False))
                                # Add score
                                self.score += 100
                            elif enemy.boss_level == 4:  # Final boss
                                self.final_boss_defeated = True
                                self.score += 1000  # Big bonus for final boss
                                self.end_game(won=True)
                                return
                        else:
                            # Add score for regular enemy
                            self.score += 10
                        
                        self.enemies.remove(enemy)
                        break
                    
                    # Only process one hit per enemy per frame (except for penetrating projectiles and explosions)
                    if enemy_hit and not projectile.get('penetrate', False) and projectile['type'] not in ['explosion', 'slow_wave']:
                        break
        
        # Check heart collections
        for heart in self.hearts[:]:
            if heart.is_collected(self.player.x, self.player.y, self.player.size):
                # Boss hearts give more health
                health_bonus = 2 if heart.is_boss_heart else 1
                self.player.health += health_bonus
                self.hearts.remove(heart)
    
    def get_spawn_count(self, game_elapsed):
        # Return number of enemies to spawn based on game time
        if game_elapsed < 30000:  # first 30 seconds
            return random.randint(2, 3)
        elif game_elapsed < 60000:  # 30-60 seconds
            return random.randint(2, 4)
        elif game_elapsed < 120000:  # 60-120 seconds
            return random.randint(2, 4)
        else:  # after 120 seconds
            return random.randint(3, 5)
    
    def get_speed_modifier(self, game_elapsed):
        # Return speed multiplier based on game time
        base_modifier = 1.0
        
        # Speed increases after certain time thresholds
        if game_elapsed >= 120000:  # after 120 seconds
            base_modifier *= 1.2
            
        # Speed increases after defeating general
        if self.general_defeated:
            time_since_general = pygame.time.get_ticks() - self.general_defeat_time
            if time_since_general >= 40000:  # 40 seconds after general
                base_modifier *= 1.2
        
        return base_modifier
    
    def end_game(self, won=False):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        
        if won:
            self.state = GameState.VICTORY
        else:
            self.state = GameState.HOME
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.state == GameState.HOME:
                    self.handle_home_events(event)
                elif self.state == GameState.PLAYING:
                    self.handle_game_events(event)
                elif self.state == GameState.VICTORY:
                    self.handle_victory_events(event)
                elif self.state == GameState.PAUSED:
                    self.handle_pause_events(event)
            
            # Update game state
            if self.state == GameState.HOME:
                self.draw_home_screen()
            elif self.state == GameState.PLAYING:
                self.update_game()
                self.draw_game_screen()
            elif self.state == GameState.VICTORY:
                self.draw_victory_screen()
            elif self.state == GameState.PAUSED:
                self.draw_pause_screen()
            
            # Update display
            pygame.display.flip()
            clock.tick(FPS)
        
        pygame.quit()

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()
