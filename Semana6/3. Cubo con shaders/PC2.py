from glApp.PyOGApp import *
from glApp.Utils import *
from glApp.Axes import *
from glApp.Esfera import *
from glApp.Uniform import *

vertex_shader = r'''
#version 330 core

in vec3 position;
in vec3 vertex_color;
in vec3 vertex_normal;

uniform mat4 projection_mat;
uniform mat4 model_mat;
uniform mat4 view_mat;

out vec3 frag_color;
out vec3 frag_normal;
out vec3 frag_pos;
out vec3 light_pos;

void main()
{
    // Posición de la luz = posición de la cámara
    light_pos = vec3(inverse(model_mat) * 
                     vec4(view_mat[3][0], view_mat[3][1], view_mat[3][2], 1.0));

    gl_Position = projection_mat * inverse(view_mat) * model_mat * vec4(position, 1.0);

    frag_normal = mat3(transpose(inverse(model_mat))) * vertex_normal;
    frag_pos = vec3(model_mat * vec4(position, 1.0));
    frag_color = vertex_color;
}
'''

fragment_shader = r'''
#version 330 core

in vec3 frag_color;
in vec3 frag_normal;
in vec3 frag_pos;
in vec3 light_pos;

out vec4 final_color;

uniform vec3 mat_ambient;
uniform vec3 mat_diffuse;
uniform vec3 mat_specular;
uniform float mat_shininess;

void main()
{
    vec3 light_color = vec3(1.0, 1.0, 1.0);
    float ambient_strength = 0.2;
    float specular_strength = 0.5;
    
    vec3 norm = normalize(frag_normal);
    vec3 light_dir = normalize(light_pos - frag_pos);
    
    // Componente ambiental
    vec3 ambient = ambient_strength * mat_ambient * light_color;
    
    // Componente difusa
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * mat_diffuse * light_color;
    
    // Componente especular
    vec3 view_dir = normalize(light_pos - frag_pos);
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), mat_shininess);
    vec3 specular = specular_strength * spec * mat_specular * light_color;
    
    vec3 result = (ambient + diffuse + specular) * frag_color;
    final_color = vec4(result, 1.0);
}
'''

class EsferaConMaterial:

    def __init__(self, program_id, material, posicion, radio=1.5):
        self.esfera = Esfera(program_id, radio=radio, sectores=36, capas=18, location=posicion)
        self.program_id = program_id
        self.material = material
        self.angulo_rotacion = 0.0        
        # uniforms para materiales
        self.ambient_uniform = Uniform("vec3", material['ambient'])
        self.ambient_uniform.find_variable(program_id, "mat_ambient")        
        self.diffuse_uniform = Uniform("vec3", material['diffuse'])
        self.diffuse_uniform.find_variable(program_id, "mat_diffuse")        
        self.specular_uniform = Uniform("vec3", material['specular'])
        self.specular_uniform.find_variable(program_id, "mat_specular")        
        self.shininess_uniform = Uniform("float", material['shininess'])
        self.shininess_uniform.find_variable(program_id, "mat_shininess")
    
    def draw(self, delta_angulo=0.0):
        self.angulo_rotacion += delta_angulo
        self.esfera.transformation_mat = rotate(self.esfera.transformation_mat, delta_angulo, 'y', True)
        self.ambient_uniform.load()
        self.diffuse_uniform.load()
        self.specular_uniform.load()
        self.shininess_uniform.load()

        self.esfera.draw()

class EscenaTresEsferas(PyOGApp):

    def __init__(self):
        super().__init__(850, 200, 1000, 800)
        self.esfera_metal = None
        self.esfera_agua = None
        self.esfera_opaca = None
        self.axes = None
    
    def initialise(self):
        self.program_id = create_program(vertex_shader, fragment_shader)        
        # materiales
        material_metal = {
            'ambient': [0.7, 0.7, 0.75],
            'diffuse': [0.7, 0.7, 0.8],
            'specular': [0.9, 0.9, 0.95],
            'shininess': 128.0
        }        
        material_agua = {
            'ambient': [0.05, 0.1, 0.2],
            'diffuse': [0.1, 0.3, 0.6],
            'specular': [0.8, 0.9, 1.0],
            'shininess': 64.0
        }        
        material_opaco = {
            'ambient': [0.3, 0.1, 0.1],
            'diffuse': [0.8, 0.2, 0.2],
            'specular': [0.1, 0.1, 0.1],
            'shininess': 8.0
        }
        
        self.esfera_metal = EsferaConMaterial(self.program_id, material_metal, pygame.Vector3(-7.0, 0.0, 0.0), radio=2.0)
        self.esfera_agua = EsferaConMaterial(self.program_id, material_agua, pygame.Vector3(0.0, 0.0, 0.0), radio=2.0)
        self.esfera_opaca = EsferaConMaterial(self.program_id, material_opaco, pygame.Vector3(7.0, 0.0, 0.0), radio=2.0)
        
        self.axes = Axes(self.program_id, pygame.Vector3(0, 0, 0))
        self.camera = Camera(self.program_id, self.screen_width, self.screen_height)
        glEnable(GL_DEPTH_TEST)
    
    def camera_init(self):
        pass
    
    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program_id)
        self.camera.update()        
        self.axes.draw()        
        self.esfera_metal.draw(0.05)
        self.esfera_agua.draw(0.05)
        self.esfera_opaca.draw(0.05)

EscenaTresEsferas().mainloop()
