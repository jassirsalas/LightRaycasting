import sys, pygame
import numpy as np

class Wall:
    def __init__(self, pos_i, pos_f):
        self.pos_i = pygame.math.Vector2(pos_i)
        self.pos_f = pygame.math.Vector2(pos_f)

    def draw(self):
        pygame.draw.line(screen, (176, 255, 70), self.pos_i, self.pos_f, 1)



class Box:
    def __init__(self, pos, dimension):
        self.pos = pos
        self.dimension = dimension
    
    def draw(self):
        pygame.draw.rect(screen, (255,255,255), pygame.Rect(self.pos, self.dimension), width=1)


class Ray:
    def __init__(self, pos, angle):
        self.pos = pygame.math.Vector2(pos)
        self.angle = angle
        self.dir = pygame.math.Vector2(100, 0).rotate(angle)


    def hit_wall(self, wall):
        x1, y1 = self.pos
        x2, y2 = self.pos + self.dir

        x3, y3 = wall.pos_i
        x4, y4 = wall.pos_f

        t_num = ( ( x1 - x3 )*( y3 - y4 ) - ( y1 - y3 )*( x3 - x4 ) )
        u_num = ( ( x1 - x2 )*( y1 - y3 ) - ( y1 - y2 )*( x1 - x3 ) )
        denom = ( ( x1 - x2 )*( y3 - y4 ) - ( y1 - y2 )*( x3 - x4 ) )

        if denom == 0: # Lineas paralelas
            return

        t =  t_num / denom
        u = -u_num / denom

        if (u>0 and u<1) and (t>0):
            # print(round(t, 3), round(u, 3))
            xx_t, yy_t = x1 + t*(x2-x1), y1 + t*(y2-y1)
            # pygame.draw.circle(screen, (255,255,255), (xx_t, yy_t), 4)

            v = pygame.math.Vector2(xx_t, yy_t)

            return v
        else:
            return

        # return pygame.math.Vector2(xx_t, yy_t)

    def draw_light(self, pos):
        pygame.draw.line(screen, (82,82,82), self.pos, self.pos + self.dir)


    def draw(self, pos, walls):
        self.pos = pygame.math.Vector2(pos)

        min_v = np.inf
        
        for ww in walls:
            vv = self.hit_wall(ww)
            
            if vv:
                dist = self.pos.distance_to(vv)

                if dist < min_v:
                    min_v = dist

        if min_v == np.inf:
            min_v = 0
        
        xx = min_v * np.cos(np.radians(self.angle))
        yy = min_v * np.sin(np.radians(self.angle))
        
        new_v = pygame.math.Vector2((xx,yy))
        
        # pygame.draw.aaline(screen, (102, 102, 102), self.pos, self.pos + self.dir)
        pygame.draw.aaline(screen, (213, 213, 213), self.pos, self.pos + new_v)
        # pygame.draw.circle(screen, (213, 213, 213), self.pos, 25)




# Init
pygame.init()

# Clock
clock = pygame.time.Clock()

# Screen
pygame.display.set_caption("Light")
size = width, height = 600, 600
screen = pygame.display.set_mode(size)


n = 180
ray_objects = []
for i in range(n):
    r = Ray((150, 300), 0 + i*360/n)
    ray_objects.append(r)


N_wall = 7
wall_objects = []
for k in range(N_wall):
    x1, y1 = np.random.randint(width), np.random.randint(height)
    x2, y2 = np.random.randint(width), np.random.randint(height)
    w = Wall((x1, y1), (x2, y2))
    wall_objects.append(w)


wall_objects.append( Wall( (-1, -1), (width, 0)) )
wall_objects.append( Wall( (-1, -1), (0, height)) )
wall_objects.append( Wall( (width, 0), (width, height)) )
wall_objects.append( Wall( (0, height), (width, height)) )

# wall_objects.append( Box( (100, 100), (100, 100)) )


# xoff, yoff = np.random.randint(width), np.random.randint(height)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Delta time
    dt = clock.tick(30)

    # Draw
    screen.fill((32,32,32))

    pos = pygame.mouse.get_pos()
    # pos = (xoff, yoff)

    for ri in ray_objects:
        ri.draw(pos, wall_objects)
        # ri.draw_light(pos)

    for wi in wall_objects:
        wi.draw()


    # xoff += 100*(np.random.random_sample()-0.5)
    # yoff += 100*(np.random.random_sample()-0.5)

    # print(dt)
    # Update
    pygame.display.update()