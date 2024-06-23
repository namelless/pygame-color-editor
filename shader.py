import sys
from array import array
import time
import math
import pygame
from pygame.locals import *
import moderngl

class Bar:
    def __init__(self, pos, size, reverse=False) -> None:
        self.pos = list(pos)
        self.size = list(size)
        self.rect = pygame.Rect(*self.pos, *self.size)
        self.reverse = reverse
        

    def render(self, surface,ratio):
        size = list(self.size)
        size[0] *= ratio
        if not self.reverse:
            pygame.draw.rect(surface,(255,255,255),(self.pos[0],self.pos[1],*size))
            pygame.draw.rect(surface,(0,0,0),(*self.pos,*self.size),3)
        else:
            pygame.draw.rect(surface,(255,0,0),(self.pos[0],self.pos[1],*self.size))
            pygame.draw.rect(surface,(0,255,0),(self.pos[0]+self.size[0]-size[0],self.pos[1],*size))            
            pygame.draw.rect(surface,(0,0,0),(*self.pos, *self.size),3)


def surf_to_texture(surf, ctx):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
    tex.swizzle = 'BGRA'
    tex.write(surf.get_view('1'))
    return tex

def test_color(surf, factor = 2):
    size = surf.get_size()
    s = surf.copy()
    pygame.init()
    screen = pygame.display.set_mode(size, pygame.OPENGL | pygame.DOUBLEBUF)
    
    ctx = moderngl.create_context()

    clock = pygame.time.Clock()


    quad_buffer = ctx.buffer(data=array('f', [
        # position (x, y), uv coords (x, y)
        -1.0, 1.0, 0.0, 0.0,  # topleft
        1.0, 1.0, 1.0, 0.0,   # topright
        -1.0, -1.0, 0.0, 1.0, # bottomleft
        1.0, -1.0, 1.0, 1.0,  # bottomright
    ]))

    with open('shaders/vert_shader.glsl') as f:
        vert_shader = f.read()


    with open('shaders/frag_shader.glsl') as f:
        frag_shader = f.read()
    program = ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
    render_object = ctx.vertex_array(program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

    t = 0
    last_time = time.time()
    rgb = [1/factor,1/factor,1/factor]
    coords = [80,20]
    lenght = 250
    bars = [Bar((coords[0],coords[1]+i*50),(lenght,15)) for i in range(3)]
    holding = -1
    clicking = False
    while True:
        dt = time.time() - last_time
        last_time = time.time()
        t += 1 * dt
        mpos = pygame.mouse.get_pos()
        surf.blit(s,(0,0))
        for i, point in enumerate(rgb):
            bars[i].render(surf, point)
            pos = [coords[0]+lenght*point,coords[1]+i*50+ 8]
            pygame.draw.circle(surf,(255,255,255),pos,10)
            pygame.draw.circle(surf,(0,0,0),pos,10,3)
            if  bars[i].rect.collidepoint(*mpos) and clicking:
                holding = i
            if holding == i:
                rgb[i] = min(max(mpos[0] - coords[0],0),lenght)/lenght


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_q:
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == BUTTON_LEFT:
                    clicking = True
            if event.type == MOUSEBUTTONUP:
                if event.button == BUTTON_LEFT:
                    clicking = False
                    holding = -1                    
        
        frame_tex = surf_to_texture(surf, ctx)
        frame_tex.use(0)
        
        program['tex'] = 0
        program['ratios'].value = [rgb[i] * factor for i in range(3)]
        render_object.render(mode=moderngl.TRIANGLE_STRIP)
        
        pygame.display.flip()
        
        frame_tex.release()
        
        clock.tick(60)
        