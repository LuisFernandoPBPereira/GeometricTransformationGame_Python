import pygame
import math
import sys

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GeometricTransformationGame")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 18)

GROUND_Y = HEIGHT - 100

# Personagem
base_shape = [(-30,-40),(30,-40),(40,40),(-20,40)]

player_default = {
    "x": 100,
    "y": GROUND_Y - 40,
    "vx": 0,
    "vy": 0,
    "on_ground": True,
    "direction": 1,
    "transformed": False,
    "angle": 0,
    "scale": 1.0,
    "shx": 0.0,
}
player = player_default.copy()

# Elementos variáveis por fase
portal_rect = None
spikes = []
platforms = []
enemies = []


# ---------------- MATRIZES ----------------
def mat_mul(A,B):
    C = [[0]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                C[i][j] += A[i][k] * B[k][j]
    return C

def mat_translate(tx,ty): return [[1,0,tx],[0,1,ty],[0,0,1]]
def mat_scale(sx,sy): return [[sx,0,0],[0,sy,0],[0,0,1]]
def mat_rotate(a):
    r=math.radians(a); c=math.cos(r); s=math.sin(r)
    return [[c,-s,0],[s,c,0],[0,0,1]]
def mat_shear(shx): return [[1,shx,0],[0,1,0],[0,0,1]]
def mat_reflect(dir): return [[dir,0,0],[0,1,0],[0,0,1]]

def apply(M,p):
    x,y=p
    nx=M[0][0]*x + M[0][1]*y + M[0][2]
    ny=M[1][0]*x + M[1][1]*y + M[1][2]
    return (nx,ny)


def build_player_matrix(p):
    S = mat_scale(p["scale"], p["scale"])
    Sh = mat_shear(p["shx"])
    R = mat_rotate(p["angle"])
    Rf = mat_reflect(p["direction"])
    T = mat_translate(p["x"], p["y"])
    return mat_mul(T, mat_mul(Rf, mat_mul(R, mat_mul(Sh, S))))


def reset_player():
    global player
    player = player_default.copy()


# ---------------- CARREGAR FASES ----------------
def load_level(level):
    global portal_rect, spikes, platforms, enemies
    # -----------------------------------------
    # ============ FASE 1 (original) ==========
    # -----------------------------------------
    if level == 1:
        portal_rect = pygame.Rect(780, GROUND_Y - 80, 60, 80)

        spikes = [
            pygame.Rect(500, GROUND_Y - 40, 60, 40),
            pygame.Rect(550, GROUND_Y - 40, 60, 40),
            pygame.Rect(250, GROUND_Y - 40, 60, 40),
            pygame.Rect(200, GROUND_Y - 40, 60, 40)
        ]

        platforms = [
            pygame.Rect(300, GROUND_Y - 160, 150, 20),
            pygame.Rect(550, GROUND_Y - 240, 150, 20)
        ]

        enemies = [
            {"rect": pygame.Rect(350, GROUND_Y - 40, 40, 40), "dir": 1, "min": 330, "max": 470},
            {"rect": pygame.Rect(600, GROUND_Y - 280, 40, 40), "dir": -1, "min": 550, "max": 650},
            {"rect": pygame.Rect(320, GROUND_Y - 200, 40, 40), "dir": 1, "min": 300, "max": 420}
        ]


    # -----------------------------------------
    # ============ FASE 2 (Acesso difícil) ==========
    # -----------------------------------------
    elif level == 2:
        portal_rect = pygame.Rect(740, GROUND_Y - 440, 60, 80)

        spikes = [
            pygame.Rect(150, GROUND_Y - 40, 60, 40),
            pygame.Rect(210, GROUND_Y - 40, 60, 40),
            pygame.Rect(270, GROUND_Y - 40, 60, 40),
            pygame.Rect(330, GROUND_Y - 40, 60, 40),
            pygame.Rect(390, GROUND_Y - 40, 60, 40),
            pygame.Rect(450, GROUND_Y - 40, 60, 40),
            pygame.Rect(510, GROUND_Y - 40, 60, 40),
            pygame.Rect(570, GROUND_Y - 40, 60, 40),
            pygame.Rect(630, GROUND_Y - 40, 60, 40),
            pygame.Rect(690, GROUND_Y - 40, 60, 40),
            pygame.Rect(750, GROUND_Y - 40, 60, 40),
            pygame.Rect(810, GROUND_Y - 40, 60, 40),

            pygame.Rect(290, GROUND_Y - 190, 60, 40),
            pygame.Rect(500, GROUND_Y - 290, 60, 40)
        ]

        platforms = [
            pygame.Rect(200, GROUND_Y - 150, 150, 20),
            pygame.Rect(420, GROUND_Y - 250, 150, 20),
            pygame.Rect(650, GROUND_Y - 350, 150, 20),

            # acesso ao portal
            # pygame.Rect(720, GROUND_Y - 200, 140, 20),
            # pygame.Rect(760, GROUND_Y - 300, 120, 20),
        ]

        enemies = [
            {"rect": pygame.Rect(220, GROUND_Y - 190, 40, 40), "dir": 1, "min": 200, "max": 330},
            {"rect": pygame.Rect(450, GROUND_Y - 290, 40, 40), "dir": -1, "min": 420, "max": 540},
            {"rect": pygame.Rect(680, GROUND_Y - 390, 40, 40), "dir": 1, "min": 650, "max": 780}
        ]


    # -----------------------------------------
    # ============ FASE 3 (desafio extra) ==========
    # -----------------------------------------
    elif level == 3:
        portal_rect = pygame.Rect(200, GROUND_Y - 420, 60, 80)

        spikes = [
            pygame.Rect(350, GROUND_Y - 40, 60, 40),
            pygame.Rect(410, GROUND_Y - 40, 60, 40),
            pygame.Rect(470, GROUND_Y - 40, 60, 40),

            pygame.Rect(600, GROUND_Y - 260, 60, 40),
            pygame.Rect(260, GROUND_Y - 190, 60, 40)
        ]

        platforms = [
            pygame.Rect(250, GROUND_Y - 150, 150, 20),
            pygame.Rect(500, GROUND_Y - 220, 150, 20),
            pygame.Rect(700, GROUND_Y - 300, 150, 20),
            pygame.Rect(400, GROUND_Y - 380, 150, 20),
        ]

        enemies = [
            {"rect": pygame.Rect(520, GROUND_Y - 260, 40, 40), "dir": 1, "min": 500, "max": 620},
            {"rect": pygame.Rect(720, GROUND_Y - 340, 40, 40), "dir": -1, "min": 700, "max": 820},
            {"rect": pygame.Rect(300, GROUND_Y - 190, 40, 40), "dir": 1, "min": 250, "max": 380},
            {"rect": pygame.Rect(420, GROUND_Y - 420, 40, 40), "dir": 1, "min": 400, "max": 520},
        ]


# -----------------------------------------------------------------------

def draw_polygon(points, color):
    pygame.draw.polygon(screen, color, points)
    pygame.draw.polygon(screen, (20,20,20), points, 2)


# -----------------------------------------
# -------------- LOOP PRINCIPAL ------------
# -----------------------------------------
level = 1
load_level(level)

running=True
while running:
    dt=clock.tick(60)/1000

    for e in pygame.event.get():
        if e.type==pygame.QUIT: 
            running=False

        if e.type==pygame.KEYDOWN:
            if (e.key==pygame.K_SPACE or e.key==pygame.K_UP) and player["on_ground"]:
                player["vy"] = -580
                player["on_ground"] = False
                player["scale"] *= 1.3

    keys=pygame.key.get_pressed()
    player["vx"] = 0

    if keys[pygame.K_LEFT]:
        player["vx"] = -230
        player["direction"] = -1
    if keys[pygame.K_RIGHT]:
        player["vx"] = 230
        player["direction"] = 1

    # Rotação ao pular
    if not player["on_ground"]:
        player["angle"] += 300 * dt
    else:
        player["angle"] = 0

    # Física
    player["x"] += player["vx"] * dt
    player["vy"] += 900 * dt
    player["y"] += player["vy"] * dt

    # Chão
    if player["y"] >= GROUND_Y - 40:
        player["y"] = GROUND_Y - 40
        player["vy"] = 0
        player["on_ground"] = True
        player["scale"] = 1.0

    # Plataformas
    for plat in platforms:
        if plat.collidepoint(player["x"], player["y"] + 40) and player["vy"] >= 0:
            player["y"] = plat.y - 40
            player["vy"] = 0
            player["on_ground"] = True
            player["scale"] = 1.0

    # Inimigos
    for e in enemies:
        e["rect"].x += e["dir"] * 120 * dt
        if e["rect"].x < e["min"] or e["rect"].x > e["max"]:
            e["dir"] *= -1

        if e["rect"].collidepoint(player["x"], player["y"]):
            reset_player()

    # Espinhos
    for s in spikes:
        if s.collidepoint(player["x"], player["y"]):
            reset_player()

    # Cair
    if player["y"] > HEIGHT:
        reset_player()

    # Vitória da fase
    if portal_rect.collidepoint(player["x"], player["y"]):
        level += 1
        if level > 3:
            print("🏆 VOCÊ ZEROU O JOGO!")
            running = False
        else:
            print(f"➡ Indo para a fase {level}...")
            load_level(level)
            reset_player()

    # ================== DESENHO ======================
    screen.fill((35,35,60))
    pygame.draw.rect(screen, (90,90,120), (0,GROUND_Y, WIDTH, 300))

    for plat in platforms:
        pygame.draw.rect(screen,(200,200,200),plat)

    pygame.draw.rect(screen,(80,255,160),portal_rect)
    screen.blit(FONT.render("PORTAL",True,(255,255,255)),(portal_rect.x, portal_rect.y-20))

    for sp in spikes:
        pygame.draw.polygon(screen,(255,80,80),[(sp.x,sp.y+40),(sp.x+30,sp.y),(sp.x+60,sp.y+40)])

    # inimigos
    for e in enemies:
        shx = math.sin(pygame.time.get_ticks() * 0.005) * 0.6
        enemy_shape = [(-20,-20),(20,-20),(20,20),(-20,20)]
        M_e = mat_mul(mat_translate(e["rect"].centerx, e["rect"].centery), mat_shear(shx))
        pts_e = [apply(M_e, p) for p in enemy_shape]
        draw_polygon(pts_e,(255,120,120))

    M = build_player_matrix(player)
    pts = [apply(M,p) for p in base_shape]
    draw_polygon(pts,(200,150,250))

    screen.blit(FONT.render(f"FASE {level}", True,(255,255,255)), (20,20))
    pygame.display.flip()

pygame.quit()
sys.exit()
