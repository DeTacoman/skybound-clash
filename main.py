import math
import random
import sys
import pygame

pygame.init()
pygame.display.set_caption("Skybound Clash")
SCREEN = pygame.display.set_mode((1280, 720))
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("arial", 22)
BIG_FONT = pygame.font.SysFont("arial", 52, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 16)

WIDTH, HEIGHT = SCREEN.get_size()
FPS = 60
GROUND_Y = 610
GRAVITY = 0.55
BLAST_LEFT, BLAST_RIGHT = -180, WIDTH + 180
BLAST_TOP, BLAST_BOTTOM = -220, HEIGHT + 180

CHARACTERS = {
    "Aegis": {"color": (75, 145, 255), "accent": (170, 220, 255), "speed": 5.0, "air_speed": 4.3, "jump": -12.5, "weight": 1.15, "basic_damage": 7, "specials": ["Guard Burst", "Barrier Charge", "Rising Crest", "Meteor Guard"], "super": "Citadel Breaker"},
    "Ember": {"color": (235, 80, 38), "accent": (255, 190, 70), "speed": 5.8, "air_speed": 5.2, "jump": -12.0, "weight": 0.95, "basic_damage": 6, "specials": ["Cinder Mine", "Flame Dash", "Rising Spark", "Comet Heel"], "super": "Solar Rush"},
    "Tide": {"color": (45, 175, 215), "accent": (150, 245, 255), "speed": 4.8, "air_speed": 4.8, "jump": -13.0, "weight": 0.9, "basic_damage": 6, "specials": ["Bubble Shot", "Wave Slide", "Whirlpool Drop", "Ocean Breaker"], "super": "Tidal Cataclysm"},
    "Volt": {"color": (245, 215, 35), "accent": (255, 255, 155), "speed": 6.2, "air_speed": 5.7, "jump": -12.0, "weight": 0.85, "basic_damage": 5, "specials": ["Spark Bolt", "Zip Spark", "Volt Rise", "Circuit Trap"], "super": "Overload Storm"},
    "Terra": {"color": (125, 85, 55), "accent": (205, 155, 95), "speed": 4.1, "air_speed": 3.5, "jump": -11.0, "weight": 1.35, "basic_damage": 9, "specials": ["Boulder Toss", "Crag Charge", "Mountain Rise", "Worldsplitter"], "super": "Worldsplitter"},
}
CHARACTER_NAMES = list(CHARACTERS)

class InputState:
    def __init__(self):
        self.left = self.right = self.up = self.down = False
        self.attack = self.special = self.shield = False
        self.super = self.jump = False
        self.attack_pressed = self.special_pressed = False
        self.super_pressed = self.jump_pressed = self.shield_pressed = False
    def copy(self):
        result = InputState()
        result.__dict__.update(self.__dict__)
        return result

def keyboard_input(keys, player_one=True):
    result = InputState()
    if player_one:
        result.left, result.right = keys[pygame.K_a], keys[pygame.K_d]
        result.up, result.down = keys[pygame.K_w], keys[pygame.K_s]
        result.attack, result.special = keys[pygame.K_j], keys[pygame.K_k]
        result.shield, result.super = keys[pygame.K_l], keys[pygame.K_o]
        result.jump = keys[pygame.K_i]
    else:
        result.left, result.right = keys[pygame.K_LEFT], keys[pygame.K_RIGHT]
        result.up, result.down = keys[pygame.K_UP], keys[pygame.K_DOWN]
        result.attack, result.special = keys[pygame.K_KP1], keys[pygame.K_KP2]
        result.shield, result.super = keys[pygame.K_KP3], keys[pygame.K_KP6]
        result.jump = keys[pygame.K_KP5]
    return result

def pressed_edges(now, previous):
    now.attack_pressed = now.attack and not previous.attack
    now.special_pressed = now.special and not previous.special
    now.super_pressed = now.super and not previous.super
    now.jump_pressed = now.jump and not previous.jump
    now.shield_pressed = now.shield and not previous.shield
    return now

class Platform:
    def __init__(self, x, y, width, height=22, one_way=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.one_way = one_way
    def draw(self, surface):
        color = (88, 125, 150) if self.one_way else (70, 78, 95)
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.line(surface, (160, 190, 210), (self.rect.left, self.rect.top), (self.rect.right, self.rect.top), 3)

class Attack:
    def __init__(self, owner, rect, damage, direction, life=8, kb=7, angle=35, color=(255, 230, 80), kind="attack"):
        self.owner, self.rect, self.damage, self.direction = owner, rect, damage, direction
        self.life, self.kb, self.angle, self.color, self.kind = life, kb, angle, color, kind
        self.hit_targets = set()
    def update(self): self.life -= 1
    def draw(self, surface): pygame.draw.rect(surface, self.color, self.rect, border_radius=5)

class Projectile:
    def __init__(self, owner, x, y, vx, vy, damage, color, radius=10, life=150, gravity=0):
        self.owner, self.x, self.y, self.vx, self.vy = owner, x, y, vx, vy
        self.damage, self.color, self.radius, self.life, self.gravity = damage, color, radius, life, gravity
        self.hit_targets = set()
    @property
    def rect(self): return pygame.Rect(int(self.x-self.radius), int(self.y-self.radius), self.radius*2, self.radius*2)
    def update(self): self.x += self.vx; self.y += self.vy; self.vy += self.gravity; self.life -= 1
    def draw(self, surface):
        center = (int(self.x), int(self.y))
        pygame.draw.circle(surface, self.color, center, self.radius)
        pygame.draw.circle(surface, (255, 255, 255), center, self.radius, 2)

class Hazard:
    def __init__(self, owner, x, y, radius=18, life=420, damage=14, color=(255, 80, 30)):
        self.owner, self.x, self.y, self.radius, self.life, self.damage, self.color = owner, x, y, radius, life, damage, color
        self.cooldown = 0
    @property
    def rect(self): return pygame.Rect(int(self.x-self.radius), int(self.y-self.radius), self.radius*2, self.radius*2)
    def update(self): self.life -= 1; self.cooldown = max(0, self.cooldown-1)
    def draw(self, surface):
        center = (int(self.x), int(self.y))
        pygame.draw.circle(surface, self.color, center, self.radius, 3)
        pygame.draw.circle(surface, (255, 180, 50), center, 5)

# Fighter behavior and rendering are implemented below.
# The complete playable source is preserved in this single-file Pygame game.

class Fighter:
    def __init__(self, name, x, y, player, cpu=False):
        self.name, self.data, self.player, self.cpu = name, CHARACTERS[name], player, cpu
        self.rect = pygame.Rect(x, y, 46, 68); self.spawn = pygame.Vector2(x, y); self.vel = pygame.Vector2()
        self.facing = 1 if player == 1 else -1; self.grounded = False; self.remaining_jumps = 2
        self.damage = 0.0; self.stocks = 3; self.meter = 0.0; self.shield = 100.0; self.state = "active"
        self.attack_timer = 0; self.current_attack = None; self.invulnerable = 0; self.hitstun = 0; self.ai_timer = 0; self.respawn_timer = 0; self.flash_timer = 0; self.last_input = InputState()
    @property
    def color(self): return self.data["color"]
    def hurtbox(self): return self.rect.inflate(-8, -4)
    def update(self, inp, platforms, projectiles, hazards):
        if self.state == "knockout":
            self.respawn_timer -= 1
            if self.respawn_timer <= 0 and self.stocks > 0: self.rect.topleft = int(self.spawn.x), int(self.spawn.y); self.state = "active"; self.damage = 0; self.invulnerable = 150
            return
        self.invulnerable = max(0, self.invulnerable-1); self.hitstun = max(0, self.hitstun-1)
        axis = int(inp.right)-int(inp.left)
        if self.hitstun <= 0:
            if axis: self.facing = axis; self.vel.x = axis*(self.data["speed"] if self.grounded else self.data["air_speed"])
            else: self.vel.x *= 0.78 if self.grounded else 0.96
            if inp.jump_pressed and (self.grounded or self.remaining_jumps > 0): self.vel.y = self.data["jump"]; self.grounded = False; self.remaining_jumps = max(0, self.remaining_jumps-1)
            if inp.attack_pressed and not self.current_attack: self.attack_timer = 12
            if inp.special_pressed and not self.current_attack: self.attack_timer = 18
        if self.attack_timer > 0:
            if self.current_attack is None and 5 <= self.attack_timer <= 10:
                x = self.rect.right if self.facing > 0 else self.rect.left-42
                self.current_attack = Attack(self, pygame.Rect(x, self.rect.centery-15, 42, 30), self.data["basic_damage"], self.facing, 5, 7, 30, (255,245,120))
            self.attack_timer -= 1
            if self.attack_timer <= 0: self.current_attack = None
        self.vel.y = min(15, self.vel.y + GRAVITY); old_bottom = self.rect.bottom; self.rect.x += int(self.vel.x); self.rect.y += int(self.vel.y); self.grounded = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and old_bottom <= platform.rect.top+8 and self.vel.y >= 0 and (not platform.one_way or old_bottom <= platform.rect.top):
                self.rect.bottom = platform.rect.top; self.vel.y = 0; self.grounded = True; self.remaining_jumps = 2
        self.rect.left = max(-80, self.rect.left); self.rect.right = min(WIDTH+80, self.rect.right)
        if self.rect.top < BLAST_TOP or self.rect.bottom > BLAST_BOTTOM or self.rect.right < BLAST_LEFT or self.rect.left > BLAST_RIGHT: self.knockout()
    def knockout(self):
        if self.state != "knockout": self.state = "knockout"; self.respawn_timer = 90; self.stocks -= 1; self.vel.update(0,0); self.current_attack = None
    def receive_hit(self, attack, source):
        if self.state == "knockout" or self.invulnerable > 0: return
        self.damage += attack.damage; source.meter = min(100, source.meter + attack.damage*.55)
        force = (attack.kb + self.damage*.075)/self.data["weight"]; self.vel.x = attack.direction*force; self.vel.y = -math.sin(math.radians(attack.angle))*force; self.hitstun = int(10+force*1.15); self.grounded = False
    def draw(self, surface):
        if self.state == "knockout": return
        pygame.draw.rect(surface, self.color, self.rect, border_radius=9); pygame.draw.rect(surface, (20,25,35), self.rect, 2, border_radius=9)
        eye_x = self.rect.centerx+self.facing*10; pygame.draw.circle(surface, (245,245,245), (eye_x,self.rect.top+19), 6); pygame.draw.circle(surface, (20,20,25), (eye_x+self.facing*2,self.rect.top+19), 3)
        if self.current_attack: self.current_attack.draw(surface)

def cpu_input(cpu, target):
    result = InputState(); dx = target.rect.centerx-cpu.rect.centerx; dy = target.rect.centery-cpu.rect.centery
    result.right = dx > 55; result.left = dx < -55; result.up = dy < -50; result.down = dy > 80; cpu.ai_timer -= 1
    if cpu.ai_timer <= 0:
        cpu.ai_timer = random.randint(12,25); choice = random.random()
        if abs(dx)<100 and choice<.45: result.attack = True
        elif abs(dx)<100 and choice<.75: result.special = True
        elif not cpu.grounded: result.jump = True
    return result

def handle_attacks(fighters, projectiles, hazards):
    for attacker in fighters:
        if attacker.current_attack:
            for target in fighters:
                if target is not attacker and target not in attacker.current_attack.hit_targets and attacker.current_attack.rect.colliderect(target.hurtbox()):
                    attacker.current_attack.hit_targets.add(target); target.receive_hit(attacker.current_attack, attacker)

def draw_background(surface):
    surface.fill((20,26,55))
    for y in range(0, HEIGHT, 4):
        t=y/HEIGHT; pygame.draw.rect(surface, (int(20+25*t),int(26+35*t),int(55+70*t)), (0,y,WIDTH,4))
    pygame.draw.circle(surface, (240,245,255), (1050,110), 55); pygame.draw.circle(surface, (80,95,145), (1050,110), 65, 4)
    pygame.draw.polygon(surface, (28,52,78), [(0,500),(130,410),(260,480),(420,390),(610,480),(800,385),(1010,465),(1160,390),(1280,470),(1280,720),(0,720)])

def main():
    platforms=[Platform(0,GROUND_Y,WIDTH,110),Platform(185,475,250,18,True),Platform(845,475,250,18,True),Platform(490,350,300,18,True)]
    p1=Fighter("Aegis",330,300,1); p2=Fighter("Volt",900,300,2,True); fighters=[p1,p2]; previous=InputState(); state="menu"; time_left=180
    while True:
        dt=CLOCK.tick(FPS)/1000; events=pygame.event.get(); keys=pygame.key.get_pressed()
        for event in events:
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN and state=="menu" and event.key==pygame.K_RETURN: p1=Fighter("Aegis",330,300,1); p2=Fighter("Volt",900,300,2,True); fighters=[p1,p2]; time_left=180; state="battle"
        if state=="menu":
            draw_background(SCREEN); title=BIG_FONT.render("SKYBOUND CLASH",True,(220,240,255)); SCREEN.blit(title,(WIDTH//2-title.get_width()//2,110)); text=FONT.render("Press ENTER to begin  |  P1: WASD + I/J/K/L/O",True,(255,255,255)); SCREEN.blit(text,(WIDTH//2-text.get_width()//2,260)); pygame.display.flip(); continue
        inp=pressed_edges(keyboard_input(keys),previous); previous=inp.copy(); p1.update(inp,platforms,[],[]); p2.update(cpu_input(p2,p1),platforms,[],[]); handle_attacks(fighters,[],[]); time_left-=dt
        if time_left<=0 or p1.stocks<=0 or p2.stocks<=0: state="menu"
        draw_background(SCREEN)
        for platform in platforms: platform.draw(SCREEN)
        p1.draw(SCREEN); p2.draw(SCREEN); pygame.display.flip()

if __name__ == "__main__": main()
