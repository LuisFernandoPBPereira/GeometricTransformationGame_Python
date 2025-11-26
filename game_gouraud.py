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
    "angle": 0,
    "scale": 1.0,
    "shx": 0.0,
}
player = player_default.copy()

portal_rect = pygame.Rect(780, GROUND_Y - 80, 60, 80)

spikes = [pygame.Rect(500, GROUND_Y - 40, 60, 40), pygame.Rect(550, GROUND_Y - 40, 60, 40),
          pygame.Rect(250, GROUND_Y - 40, 60, 40), pygame.Rect(200, GROUND_Y - 40, 60, 40)]

platforms = [
    pygame.Rect(300, GROUND_Y - 160, 150, 20),
    pygame.Rect(550, GROUND_Y - 240, 150, 20)
]

enemies = [
    {"rect": pygame.Rect(350, GROUND_Y - 40, 40, 40), "dir": 1, "min": 330, "max": 470},
    {"rect": pygame.Rect(600, GROUND_Y - 280, 40, 40), "dir": -1, "min": 550, "max": 650},
    {"rect": pygame.Rect(320, GROUND_Y - 200, 40, 40), "dir": 1, "min": 300, "max": 420}
]

# ---------- MATRIZES ----------
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

# ---------- GOURAUD SHADING 2D ----------
light_dir = (0.6, -0.8)
ld_len = math.hypot(*light_dir)
light_dir = (light_dir[0]/ld_len, light_dir[1]/ld_len)

def vertex_normal(p1, p2, p3):
    # normal do triângulo em 2D (perpendicular à aresta)
    x1,y1 = p1
    x2,y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    return (-dy, dx)

def dot(a,b): return a[0]*b[0] + a[1]*b[1]

def compute_vertex_lighting(points):
    lights = []
    n = len(points)
    for i in range(n):
        p_prev = points[(i-1)%n]
        p = points[i]
        p_next = points[(i+1)%n]

        nx, ny = vertex_normal(p_prev, p, p_next)
        ln = math.hypot(nx,ny)
        if ln == 0: ln = 1
        nx /= ln
        ny /= ln

        intensity = max(0.1, dot((nx,ny), light_dir))
        lights.append(intensity)
    return lights

def draw_polygon_gouraud(surface, points, base_color):
    triang = []
    for i in range(1, len(points)-1):
        triang.append((points[0], points[i], points[i+1]))

    intens = compute_vertex_lighting(points)

    tris_i = []
    for i in range(1, len(points)-1):
        tris_i.append((intens[0], intens[i], intens[i+1]))

    for (p1,p2,p3), (i1,i2,i3) in zip(triang, tris_i):
        max_x = int(max(p1[0], p2[0], p3[0]))
        min_x = int(min(p1[0], p2[0], p3[0]))
        max_y = int(max(p1[1], p2[1], p3[1]))
        min_y = int(min(p1[1], p2[1], p3[1]))

        def edge(a,b,c):
            return (c[0]-a[0])*(b[1]-a[1]) - (c[1]-a[1])*(b[0]-a[0])

        area = edge(p1,p2,p3)
        if area == 0:
            continue

        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                p = (x+0.5, y+0.5)
                w1 = edge(p2,p3,p) / area
                w2 = edge(p3,p1,p) / area
                w3 = edge(p1,p2,p) / area

                if w1 >= 0 and w2 >= 0 and w3 >= 0:
                    intensity = w1*i1 + w2*i2 + w3*i3
                    r = min(255, int(base_color[0] * intensity))
                    g = min(255, int(base_color[1] * intensity))
                    b = min(255, int(base_color[2] * intensity))
                    surface.set_at((x,y), (r,g,b))

# ------------------------------------------

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

    # Rotação ao pular
    if not player["on_ground"]:
        player["angle"] += 300 * dt
    else:
        player["angle"] = 0

    # FÍSICA
    player["x"] += player["vx"] * dt
    player["vy"] += 900 * dt
    player["y"] += player["vy"] * dt

    if player["y"] >= GROUND_Y - 40:
        player["y"] = GROUND_Y - 40
        player["vy"] = 0
        player["on_ground"] = True
        player["scale"] = 1.0

    for plat in platforms:
        if plat.collidepoint(player["x"], player["y"] + 40) and player["vy"] >= 0:
            player["y"] = plat.y - 40
            player["vy"] = 0
            player["on_ground"] = True
            player["scale"] = 1.0

    for e in enemies:
        e["rect"].x += e["dir"] * 120 * dt
        if e["rect"].x < e["min"] or e["rect"].x > e["max"]:
            e["dir"] *= -1
        if e["rect"].collidepoint(player["x"], player["y"]):
            reset_game()

    for s in spikes:
        if s.collidepoint(player["x"], player["y"]):
            reset_game()

    if player["y"] > HEIGHT:
        reset_game()

    if portal_rect.collidepoint(player["x"], player["y"]):
        print("VOCÊ VENCEU!")
        running=False

    # ---- DESENHO ----
    screen.fill((35,35,60))
    pygame.draw.rect(screen, (90,90,120), (0,GROUND_Y, WIDTH, 300))

    for plat in platforms:
        pygame.draw.rect(screen,(200,200,200),plat)

    pygame.draw.rect(screen,(80,255,160),portal_rect)
    screen.blit(FONT.render("PORTAL",True,(255,255,255)),(portal_rect.x, portal_rect.y-20))

    for sp in spikes:
        pygame.draw.polygon(screen,(255,80,80),[(sp.x,sp.y+40),(sp.x+30,sp.y),(sp.x+60,sp.y+40)])

    # Inimigos ainda com flat color
    for e in enemies:
        shx = math.sin(pygame.time.get_ticks() * 0.005) * 0.6
        enemy_shape = [(-20,-20),(20,-20),(20,20),(-20,20)]
        M_e = mat_mul(mat_translate(e["rect"].centerx, e["rect"].centery), mat_shear(shx))
        pts_e = [apply(M_e, p) for p in enemy_shape]
        pygame.draw.polygon(screen,(255,120,120),pts_e)

    # --- PERSONAGEM COM GOURAUD SHADING ---
    M = build_player_matrix(player)
    pts = [apply(M,p) for p in base_shape]
    draw_polygon_gouraud(screen, pts, (200,150,250))

    screen.blit(FONT.render("Acesse o portal!", True,(255,255,255)), (20,20))
    pygame.display.flip()

pygame.quit()
sys.exit()
