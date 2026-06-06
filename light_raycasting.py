import sys
import math
import random
import pygame

class Wall:
    def __init__(self, pos_i, pos_f):
        self.pos_i = pygame.math.Vector2(pos_i)
        self.pos_f = pygame.math.Vector2(pos_f)
        self.is_border = False

    def draw(self, screen):
        if self.is_border:
            # Dibujar los bordes con una línea fina y oscura
            pygame.draw.line(screen, (40, 40, 50), self.pos_i, self.pos_f, 2)
        else:
            # Efecto de barra de neón brillante
            # Resplandor exterior (grueso y de color vibrante)
            pygame.draw.line(screen, (176, 255, 70), self.pos_i, self.pos_f, 5)
            # Núcleo brillante (fino y claro)
            pygame.draw.line(screen, (235, 255, 200), self.pos_i, self.pos_f, 2)


class LightSource:
    def __init__(self, pos, radius, color, fov=360, angle=0.0):
        self.pos = pygame.math.Vector2(pos)
        self.radius = radius
        self.color = color
        self.fov = fov          # Campo de visión en grados (360 para omni)
        self.angle = angle      # Dirección en radianes
        self.radial_surf = self.create_radial_light()

    def create_radial_light(self):
        # Crear una superficie con degradado radial y canal alfa
        surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        # Rellenar con círculos concéntricos de opacidad descendente
        for r in range(self.radius, 0, -2):
            t = 1.0 - (r / self.radius)
            # Caída cuadrática para un degradado más natural y suave
            alpha = int((t ** 2) * 255)
            c = (self.color[0], self.color[1], self.color[2], alpha)
            pygame.draw.circle(surf, c, (self.radius, self.radius), r)
        return surf

    def update_color(self, new_color):
        self.color = new_color
        self.radial_surf = self.create_radial_light()

    def update_radius(self, new_radius):
        self.radius = new_radius
        self.radial_surf = self.create_radial_light()

    def draw_wireframe(self, screen, points):
        # Dibuja los rayos de luz como líneas individuales (modo clásico optimizado)
        for pt in points:
            pygame.draw.aaline(screen, (120, 120, 120), self.pos, pt)

    def draw_glow(self, screen, points):
        if len(points) < 3:
            return
            
        # 1. Crear superficie temporal transparente para la máscara de luz
        temp_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        temp_surface.fill((0, 0, 0, 0))
        
        # 2. Desplazar los puntos de impacto a coordenadas locales de temp_surface
        offset_points = []
        offset_x = self.pos.x - self.radius
        offset_y = self.pos.y - self.radius
        for pt in points:
            offset_points.append((pt.x - offset_x, pt.y - offset_y))
            
        # Si es un foco/linterna, añadimos el centro para cerrar el sector correctamente
        if self.fov < 360:
            offset_points.append((self.radius, self.radius))
            
        # 3. Dibujar el polígono de visibilidad en blanco sólido en la máscara
        pygame.draw.polygon(temp_surface, (255, 255, 255, 255), offset_points)
        
        # 4. Multiplicar la máscara por el degradado radial pre-renderizado
        # Esto hace que la luz solo exista dentro del polígono visible
        temp_surface.blit(self.radial_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # 5. Dibujar additivamente sobre la pantalla
        screen.blit(temp_surface, (offset_x, offset_y), special_flags=pygame.BLEND_RGBA_ADD)

    def get_visibility_points(self, walls, screen_size):
        w, h = screen_size
        
        # Recolectar vértices únicos de todas las paredes
        unique_verts = set()
        for wall in walls:
            unique_verts.add((wall.pos_i.x, wall.pos_i.y))
            unique_verts.add((wall.pos_f.x, wall.pos_f.y))
            
        # Añadir las esquinas de la pantalla como vértices de soporte
        unique_verts.add((0, 0))
        unique_verts.add((w, 0))
        unique_verts.add((w, h))
        unique_verts.add((0, h))
        
        half_fov = math.radians(self.fov) / 2
        start_angle = self.angle - half_fov
        
        angles = []
        
        # 1. Añadir ángulos fijos para asegurar la forma circular en zonas sin paredes
        if self.fov < 360:
            # Añadir límites del cono de luz
            angles.append(start_angle)
            angles.append(self.angle + half_fov)
            
            # Ángulos intermedios cada 10 grados dentro del cono
            start_deg = int(math.degrees(start_angle))
            end_deg = int(math.degrees(self.angle + half_fov))
            for deg in range(start_deg, end_deg + 1, 10):
                angles.append(math.radians(deg))
        else:
            # 360 grados completos
            for deg in range(0, 360, 10):
                angles.append(math.radians(deg))
                
        # 2. Procesar vértices geométricos
        for vx, vy in unique_verts:
            # Ángulo desde la luz hacia el vértice
            theta = math.atan2(vy - self.pos.y, vx - self.pos.x)
            
            # En modo linterna, descartar vértices fuera del cono de luz
            if self.fov < 360:
                diff = (theta - start_angle) % (2 * math.pi)
                if diff > math.radians(self.fov):
                    continue
                    
            # Trazar rayo al vértice y con offsets minúsculos para pasar la esquina
            angles.extend([theta - 0.0001, theta, theta + 0.0001])
            
        # 3. Limpiar, normalizar y ordenar ángulos
        normalized_angles = []
        for a in angles:
            a_norm = (a + math.pi) % (2 * math.pi) - math.pi
            
            # Validar que los ángulos normalizados estén dentro del cono si es spotlight
            if self.fov < 360:
                diff = (a_norm - start_angle) % (2 * math.pi)
                if diff <= math.radians(self.fov) + 0.0002:
                    normalized_angles.append(a_norm)
            else:
                normalized_angles.append(a_norm)
                
        # Eliminar duplicados y ordenar usando ángulo relativo al inicio del cono
        # Esto evita cualquier error de ordenamiento en el límite de envoltura (-pi / pi)
        sorted_angles = sorted(list(set(normalized_angles)), key=lambda a: (a - start_angle) % (2 * math.pi))
        
        # 4. Realizar el trazado de rayos (Raycasting)
        points = []
        px, py = self.pos.x, self.pos.y
        
        for angle in sorted_angles:
            dx = math.cos(angle)
            dy = math.sin(angle)
            min_t = float('inf')
            
            for wall in walls:
                ax, ay = wall.pos_i.x, wall.pos_i.y
                bx, by = wall.pos_f.x, wall.pos_f.y
                
                # Intersección utilizando determinantes 2D optimizados
                denom = dx * (by - ay) - dy * (bx - ax)
                if denom != 0:
                    apx = ax - px
                    apy = ay - py
                    t = (apx * (by - ay) - apy * (bx - ax)) / denom
                    u = (apx * dy - apy * dx) / denom
                    
                    if t >= 0 and 0 <= u <= 1:
                        if t < min_t:
                            min_t = t
                            
            if min_t != float('inf'):
                # Limitar la longitud del rayo a la distancia máxima de luz (radio)
                t_val = min(min_t, self.radius)
                pt = pygame.math.Vector2(px + dx * t_val, py + dy * t_val)
                points.append(pt)
                
        return points


def draw_text(screen, text, pos, font, color=(255, 255, 255), shadow=True):
    if shadow:
        shadow_surf = font.render(text, True, (15, 15, 20))
        screen.blit(shadow_surf, (pos[0] + 2, pos[1] + 2))
    text_surf = font.render(text, True, color)
    screen.blit(text_surf, pos)


# Inicialización de Pygame
pygame.init()
clock = pygame.time.Clock()

# Configuración de Pantalla
pygame.display.set_caption("2D Light & Shadow Simulator")
width, height = 600, 600  # Restaurado a 600x600 como originalmente
screen = pygame.display.set_mode((width, height))

# Colores de Luz Disponibles
LIGHT_COLORS = [
    (255, 230, 180),  # Blanco Cálido
    (0, 255, 255),    # Cyan Neón
    (255, 100, 255),  # Magenta Neón
    (100, 255, 100),  # Verde Neón
    (255, 120, 0),    # Naranja Fuego
    (255, 255, 255),  # Blanco Puro
]
color_idx = 0

# Crear Fuentes de Luz
mouse_light = LightSource((400, 400), radius=350, color=LIGHT_COLORS[color_idx], fov=360)

# Lighthouse (Luz giratoria en el centro)
lighthouse_light = LightSource((width // 2, height // 2), radius=450, color=(0, 255, 255), fov=45)
use_lighthouse = True

# Generar Paredes Iniciales
wall_objects = []

# Paredes aleatorias de prueba (5 paredes)
for _ in range(5):
    x1, y1 = random.randint(50, width-50), random.randint(50, height-50)
    # Longitud razonable
    angle = random.uniform(0, 2 * math.pi)
    length = random.randint(80, 200)
    x2 = int(x1 + math.cos(angle) * length)
    y2 = int(y1 + math.sin(angle) * length)
    
    # Asegurar dentro de los límites
    x2 = max(10, min(width - 10, x2))
    y2 = max(10, min(height - 10, y2))
    
    wall_objects.append(Wall((x1, y1), (x2, y2)))

# Agregar paredes de borde (no editables ni borrables)
borders = [
    Wall((-1, -1), (width, 0)),
    Wall((-1, -1), (0, height)),
    Wall((width, 0), (width, height)),
    Wall((0, height), (width, height))
]
for b in borders:
    b.is_border = True
    wall_objects.append(b)

# Fuentes de Texto
font_title = pygame.font.SysFont("Consolas", 18, bold=True)
font_ui = pygame.font.SysFont("Consolas", 14)

# Estado del Editor
drawing_new_wall = False
new_wall_start = None

hovered_wall = None
hovered_endpoint = None  # 'i' o 'f'
dragging_wall = None
dragging_endpoint = None

# Modos de Visualización
draw_mode = "glow"  # "glow" (relleno suave) o "wireframe" (rayos)
mouse_light_mode = "omni"  # "omni" o "spotlight"

running = True
while running:
    mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
    dt = clock.tick(60)  # Objetivo: 60 FPS
    
    # --- PROCESAMIENTO DE EVENTOS ---
    # Detectar si el cursor está cerca de algún extremo de las paredes (para edición/eliminación)
    hovered_wall = None
    hovered_endpoint = None
    if not drawing_new_wall and dragging_wall is None:
        for wall in wall_objects:
            if wall.is_border:
                continue
            if wall.pos_i.distance_to(mouse_pos) < 12:
                hovered_wall = wall
                hovered_endpoint = 'i'
                break
            elif wall.pos_f.distance_to(mouse_pos) < 12:
                hovered_wall = wall
                hovered_endpoint = 'f'
                break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic Izquierdo
                if hovered_wall is not None:
                    # Iniciar arrastre de extremo
                    dragging_wall = hovered_wall
                    dragging_endpoint = hovered_endpoint
                else:
                    # Iniciar dibujo de nueva pared
                    drawing_new_wall = True
                    new_wall_start = mouse_pos
                    
            elif event.button == 3:  # Clic Derecho
                if hovered_wall is not None:
                    # Borrar pared
                    wall_objects.remove(hovered_wall)
                    hovered_wall = None
                    hovered_endpoint = None
                    
            elif event.button == 4:  # Rueda Arriba (Rotar Spotlight de ratón)
                if mouse_light_mode == "spotlight":
                    mouse_light.angle -= 0.1
            elif event.button == 5:  # Rueda Abajo (Rotar Spotlight de ratón)
                if mouse_light_mode == "spotlight":
                    mouse_light.angle += 0.1
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if dragging_wall is not None:
                    dragging_wall = None
                    dragging_endpoint = None
                elif drawing_new_wall:
                    drawing_new_wall = False
                    # Evitar paredes de longitud cero
                    if new_wall_start.distance_to(mouse_pos) > 8:
                        new_wall = Wall(new_wall_start, mouse_pos)
                        # Insertar antes de los bordes para mantener la estructura limpia
                        wall_objects.insert(len(wall_objects) - 4, new_wall)
                        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                # Alternar modo de dibujo (Glow vs Wireframe)
                draw_mode = "glow" if draw_mode == "wireframe" else "wireframe"
                
            elif event.key == pygame.K_m:
                # Alternar modo de la luz del ratón (Omni vs Spotlight)
                if mouse_light_mode == "omni":
                    mouse_light_mode = "spotlight"
                    mouse_light.fov = 60
                    # Apuntar en dirección inicial arriba
                    mouse_light.angle = -math.pi / 2
                else:
                    mouse_light_mode = "omni"
                    mouse_light.fov = 360
                # Re-renderizar el degradado
                mouse_light.update_color(mouse_light.color)
                
            elif event.key == pygame.K_c:
                # Ciclar color de la luz del ratón
                color_idx = (color_idx + 1) % len(LIGHT_COLORS)
                mouse_light.update_color(LIGHT_COLORS[color_idx])
                
            elif event.key == pygame.K_l:
                # Alternar Lighthouse
                use_lighthouse = not use_lighthouse
                
            elif event.key == pygame.K_r:
                # Resetear paredes (dejar solo bordes)
                wall_objects = [w for w in wall_objects if w.is_border]

    # --- ACTUALIZACIÓN DE ESTADOS ---
    # Actualizar arrastre de pared
    if dragging_wall is not None:
        if dragging_endpoint == 'i':
            dragging_wall.pos_i = pygame.math.Vector2(pygame.mouse.get_pos())
        else:
            dragging_wall.pos_f = pygame.math.Vector2(pygame.mouse.get_pos())

    # Actualizar luz del ratón
    mouse_light.pos = mouse_pos
    
    # Rotación automática de la luz del faro (Lighthouse)
    if use_lighthouse:
        lighthouse_light.angle += 0.01  # 0.6 radianes por segundo aprox.
        # Mantener el ángulo en rango normalizado
        lighthouse_light.angle = (lighthouse_light.angle + math.pi) % (2 * math.pi) - math.pi

    # --- RENDERIZADO ---
    # 1. Fondo ambiente (Habitación oscura)
    screen.fill((14, 14, 18))
    
    # 2. Dibujar rejilla de fondo sutil para dar profundidad
    grid_size = 40
    for x in range(0, width, grid_size):
        pygame.draw.line(screen, (22, 22, 28), (x, 0), (x, height))
    for y in range(0, height, grid_size):
        pygame.draw.line(screen, (22, 22, 28), (0, y), (width, y))

    # 3. Calcular puntos de visibilidad y dibujar luces
    # Luz del faro
    if use_lighthouse:
        lh_points = lighthouse_light.get_visibility_points(wall_objects, (width, height))
        if draw_mode == "glow":
            lighthouse_light.draw_glow(screen, lh_points)
        else:
            lighthouse_light.draw_wireframe(screen, lh_points)

    # Luz del ratón
    mouse_points = mouse_light.get_visibility_points(wall_objects, (width, height))
    if draw_mode == "glow":
        mouse_light.draw_glow(screen, mouse_points)
    else:
        mouse_light.draw_wireframe(screen, mouse_points)

    # 4. Dibujar paredes
    for wall in wall_objects:
        wall.draw(screen)

    # 5. Dibujar pared provisional si se está creando
    if drawing_new_wall:
        pygame.draw.line(screen, (255, 140, 0), new_wall_start, mouse_pos, 4)
        pygame.draw.line(screen, (255, 220, 180), new_wall_start, mouse_pos, 1)

    # 6. Dibujar manejadores de vértices interactivos
    for wall in wall_objects:
        if wall.is_border:
            continue
        # Extremo inicial
        is_hover_i = (hovered_wall == wall and hovered_endpoint == 'i')
        rad_i = 7 if is_hover_i else 4
        col_i = (255, 255, 255) if is_hover_i else (176, 255, 70)
        pygame.draw.circle(screen, col_i, (int(wall.pos_i.x), int(wall.pos_i.y)), rad_i)
        if is_hover_i:
            pygame.draw.circle(screen, (100, 255, 0), (int(wall.pos_i.x), int(wall.pos_i.y)), rad_i + 3, 1)
            
        # Extremo final
        is_hover_f = (hovered_wall == wall and hovered_endpoint == 'f')
        rad_f = 7 if is_hover_f else 4
        col_f = (255, 255, 255) if is_hover_f else (176, 255, 70)
        pygame.draw.circle(screen, col_f, (int(wall.pos_f.x), int(wall.pos_f.y)), rad_f)
        if is_hover_f:
            pygame.draw.circle(screen, (100, 255, 0), (int(wall.pos_f.x), int(wall.pos_f.y)), rad_f + 3, 1)

    # 7. Renderizar HUD (Interfaz de Usuario)
    # Fondo semitransparente para el panel
    hud_bg = pygame.Surface((280, 190), pygame.SRCALPHA)
    hud_bg.fill((10, 10, 15, 200))
    screen.blit(hud_bg, (15, 15))
    pygame.draw.rect(screen, (50, 50, 65), pygame.Rect(15, 15, 280, 190), width=1, border_radius=3)

    # Contenido del HUD
    draw_text(screen, "SIMULADOR DE LUZ 2D", (25, 25), font_title, (0, 255, 255))
    
    fps_val = int(clock.get_fps())
    draw_text(screen, f"FPS: {fps_val}", (25, 50), font_ui, (180, 255, 100))
    
    # Calcular cantidad de rayos
    num_rays = len(mouse_points)
    if use_lighthouse:
        num_rays += len(lh_points)
    draw_text(screen, f"Rayos Trazados: {num_rays}", (25, 68), font_ui, (230, 230, 230))
    
    mode_str = "SUAVE GLOW" if draw_mode == "glow" else "HILOS WIREFRAME"
    draw_text(screen, f"Renderizado: {mode_str}", (25, 86), font_ui, (230, 230, 230))
    
    mlight_str = "OMNI (360°)" if mouse_light_mode == "omni" else "LINTERNA (60°)"
    draw_text(screen, f"Luz Ratón: {mlight_str}", (25, 104), font_ui, (230, 230, 230))
    
    lh_str = "ACTIVO" if use_lighthouse else "INACTIVO"
    draw_text(screen, f"Faro Central: {lh_str}", (25, 122), font_ui, (230, 230, 230))
    
    num_walls = len([w for w in wall_objects if not w.is_border])
    draw_text(screen, f"Paredes creadas: {num_walls}", (25, 140), font_ui, (230, 230, 230))

    # Panel de Ayuda / Controles abajo a la izquierda (evita solapamientos en 600x600)
    help_bg = pygame.Surface((310, 180), pygame.SRCALPHA)
    help_bg.fill((10, 10, 15, 200))
    screen.blit(help_bg, (15, height - 195))
    pygame.draw.rect(screen, (50, 50, 65), pygame.Rect(15, height - 195, 310, 180), width=1, border_radius=3)

    draw_text(screen, "CONTROLES:", (25, height - 185), font_title, (255, 200, 50))
    draw_text(screen, "[Clic Izq + Arrastrar] Dibujar Pared", (25, height - 160), font_ui)
    draw_text(screen, "[Arrastrar Extremo] Rediseñar Pared", (25, height - 142), font_ui)
    draw_text(screen, "[Clic Derecho Extremo] Borrar Pared", (25, height - 124), font_ui)
    draw_text(screen, "[C] Cambiar Color | [R] Resetear Paredes", (25, height - 106), font_ui)
    draw_text(screen, "[M] Cambiar Modo Luz | [L] Toggle Faro", (25, height - 88), font_ui)
    draw_text(screen, "[G] Cambiar Renderizado (Glow/Rays)", (25, height - 70), font_ui, (0, 200, 255))
    if mouse_light_mode == "spotlight":
        draw_text(screen, "[Rueda Ratón] Rotar Linterna", (25, height - 52), font_ui, (255, 150, 0))

    # Actualizar pantalla
    pygame.display.flip()

pygame.quit()
sys.exit()