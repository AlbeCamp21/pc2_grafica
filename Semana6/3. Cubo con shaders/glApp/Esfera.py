import pygame
from .Mesh import *
from .Utils import format_vertices
from .Graphics_Data import *
from math import sin, cos, pi


class Esfera(Mesh):

    def __init__(self, program_id, radio=1.0, sectores=36, capas=18, location=pygame.Vector3(0, 0, 0)):
        coordinates, normals = self.crear_geometria_esfera(radio, sectores, capas)
        triangles = self.crear_indices(sectores, capas)        
        vertices = format_vertices(coordinates, triangles)
        vertex_normals = format_vertices(normals, triangles)        
        colors = []
        for i in range(len(vertices)):
            colors.append(1.0)
            colors.append(1.0)
            colors.append(1.0)
        
        super().__init__(program_id, vertices, colors, GL_TRIANGLES, location)
        v_normals = Graphics_Data("vec3", vertex_normals)
        v_normals.create_variable(program_id, "vertex_normal")
    
    def crear_geometria_esfera(self, radio, sectores, capas):
        positions = []
        normals = []        
        for i in range(capas + 1):
            angulo_capa = pi/2 - i*pi/capas
            xy = radio * cos(angulo_capa)
            z = radio * sin(angulo_capa)            
            for j in range(sectores+1):
                angulo_sector = j*2*pi / sectores
                x = xy * cos(angulo_sector)
                y = xy * sin(angulo_sector)
                positions.append((x, y, z))                
                longitud = (x*x + y*y + z*z) ** 0.5
                if longitud > 0:
                    normals.append((x/longitud, y/longitud, z/longitud))
                else:
                    normals.append((0.0, 1.0, 0.0))        
        return positions, normals
    
    def crear_indices(self, sectores, capas):
        indices = []
        for i in range(capas):
            for j in range(sectores):
                primero = i * (sectores+1) + j
                segundo = primero + sectores + 1
                indices.append(primero)
                indices.append(segundo)
                indices.append(primero+1)
                indices.append(segundo)
                indices.append(segundo+1)
                indices.append(primero+1)
        return indices
