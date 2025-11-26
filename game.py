"""
Jogo de plataforma com Transformações Geométricas
Você deve alcançar o PORTAL sem tocar nos inimigos ou nas áreas perigosas.

- Translação → movimento
- Rotação → gira no ar
- Escala → fica maior
- Reflexão → vira conforme direção
- Distorção → estica ao correr
"""
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
base_shape = [(-30,-40),(30,-40),(40,40),(-20,40)]  # forma de paralelepípedo em 2D

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

# PORTAL
portal_rect = pygame.Rect(780, GROUND_Y - 80, 60, 80)

# Obstáculos
spikes = [pygame.Rect(500, GROUND_Y - 40, 60, 40), pygame.Rect(550, GROUND_Y - 40, 60, 40), pygame.Rect(250, GROUND_Y - 40, 60, 40), pygame.Rect(200, GROUND_Y - 40, 60, 40)]

platforms = [
    pygame.Rect(300, GROUND_Y - 160, 150, 20),
    pygame.Rect(550, GROUND_Y - 240, 150, 20)
]

enemies = [
    {"rect": pygame.Rect(350, GROUND_Y - 40, 40, 40), "dir": 1, "min": 330, "max": 470},
    {"rect": pygame.Rect(600, GROUND_Y - 280, 40, 40), "dir": -1, "min": 550, "max": 650},
    {"rect": pygame.Rect(320, GROUND_Y - 200, 40, 40), "dir": 1, "min": 300, "max": 420}
]

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

# -------------------------------------------

def build_player_matrix(p):
    S = mat_scale(p["scale"], p["scale"])
    Sh = mat_shear(p["shx"])
    R = mat_rotate(p["angle"])
    Rf = mat_reflect(p["direction"])
    T = mat_translate(p["x"], p["y"])

    return mat_mul(T, mat_mul(Rf, mat_mul(R, mat_mul(Sh, S))))


def reset_game():
    global player
    player = player_default.copy()


def draw_polygon(points, color):
    pygame.draw.polygon(screen, color, points)
    pygame.draw.polygon(screen, (20,20,20), points, 2)

running=True
while running:
    dt=clock.tick(60)/1000

    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
        if e.type==pygame.KEYDOWN:
            if (e.key==pygame.K_SPACE or e.key ==pygame.K_UP) and player["on_ground"]:
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

    # ------ Rotação automática ao pular ------
    if not player["on_ground"]:
        player["angle"] += 300 * dt
    else:
        player["angle"] = 0
    # ------------------------------------------------

    # FÍSICA
    player["x"] += player["vx"] * dt
    player["vy"] += 900 * dt
    player["y"] += player["vy"] * dt

    # chão
    if player["y"] >= GROUND_Y - 40:
        player["y"] = GROUND_Y - 40
        player["vy"] = 0
        player["on_ground"] = True
        player["scale"] = 1.0

    # --- plataformas ---
    for plat in platforms:
        if plat.collidepoint(player["x"], player["y"] + 40) and player["vy"] >= 0:
            player["y"] = plat.y - 40
            player["vy"] = 0
            player["on_ground"] = True
            player["scale"] = 1.0


    # --- inimigos walking ---
    for e in enemies:
        e["rect"].x += e["dir"] * 120 * dt
        if e["rect"].x < e["min"] or e["rect"].x > e["max"]:
            e["dir"] *= -1

        if e["rect"].collidepoint(player["x"], player["y"]):
            reset_game()

    # --- espinhos ---
    for s in spikes:
        if s.collidepoint(player["x"], player["y"]):
            reset_game()

    # --- buraco (cair) ---
    if player["y"] > HEIGHT:
        reset_game()

    # vitória
    if portal_rect.collidepoint(player["x"], player["y"]):
        print("VOCÊ VENCEU!")
        running=False

    # ---------------- DESENHO -------------------
    screen.fill((35,35,60))

    pygame.draw.rect(screen, (90,90,120), (0,GROUND_Y, WIDTH, 300))

    # plataformas
    for plat in platforms:
        pygame.draw.rect(screen,(200,200,200),plat)

    # portal
    pygame.draw.rect(screen,(80,255,160),portal_rect)
    screen.blit(FONT.render("PORTAL",True,(255,255,255)),(portal_rect.x, portal_rect.y-20))

    # espinhos
    for sp in spikes:
        pygame.draw.polygon(screen,(255,80,80),[(sp.x,sp.y+40),(sp.x+30,sp.y),(sp.x+60,sp.y+40)])

    # inimigos
    for e in enemies:
        # efeito de cisalhamento nos inimigos
        shx = math.sin(pygame.time.get_ticks() * 0.005) * 0.6
        enemy_shape = [(-20,-20),(20,-20),(20,20),(-20,20)]
        M_e = mat_mul(mat_translate(e["rect"].centerx, e["rect"].centery), mat_shear(shx))
        pts_e = [apply(M_e, p) for p in enemy_shape]
        draw_polygon(pts_e,(255,120,120))

    # personagem transformado
    M = build_player_matrix(player)
    pts = [apply(M,p) for p in base_shape]
    draw_polygon(pts,(200,150,250))

    mode_msg = "Acesse o portal!"
    screen.blit(FONT.render(mode_msg, True,(255,255,255)), (20,20))

    pygame.display.flip()

pygame.quit()
sys.exit()
