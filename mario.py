# coding=utf-8
"""Circles, collisions and gravity"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import random
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.performance_monitor as pm

#Definimos la clase Controller 
class Controller:

    def __init__(self):
        self.fillPolygon = True
        self.x = -0.5
        self.y = 0.0
        self.jump = False
        self.g = np.array([0.0, -1.0], dtype=np.float32)
        self.vy = 0

# global controller as communication with the callback function
controller = Controller()

class Shape:
    def __init__(self, vertices, indices, textureFileName=None):
        self.vertices = vertices
        self.indices = indices
        self.textureFileName = textureFileName

# This function will be executed whenever a key is pressed or released
def on_key(window, key, scancode, action, mods):
    
    global controller

    if key == glfw.KEY_SPACE and action ==glfw.PRESS:
        controller.jump = True

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    # Caso en que se cierra la ventana
    elif key == glfw.KEY_ESCAPE and action ==glfw.PRESS:
        glfw.set_window_should_close(window, True)

def createCircle(r,g,b,N):
    # First vertex at the center, white color
    vertices = [0, 0, 0, r, g, b]
    indices = []

    dtheta = 2 * np.pi / N

    for i in range(N):
        theta = i * dtheta
        if r<1.0 and g<1.0 and b<1.0:
            vertices += [
                # vertex coordinates
                0.5 * np.cos(theta), 0.5 * np.sin(theta), 0,

                # color generates varying between 0 and 1
                    r+0.5*np.sin(theta),       g+0.5*np.sin(theta), b+0.5*np.sin(theta)]

            # A triangle is created using the center, this and the next vertex
            indices += [0, i, i+1]

        #Only for White Sillhouette
        else:
            vertices += [
                # vertex coordinates
                0.5 * np.cos(theta), 0.5 * np.sin(theta), 0, r, g, b]

            # A triangle is created using the center, this and the next vertex
            indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

    vertices = np.array(vertices, dtype =np.float32)
    indices = np.array(indices, dtype= np.uint32)


    return Shape(vertices, indices)
    

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Mind Controlled Quad", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)


    # Creating our shader program and telling OpenGL to use it
    pipeline = es.SimpleTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.5, 0.5, 0.5, 1.0)

    # Creating shapes on GPU memory
    shapeQuad = bs.createColorQuad(0.6, 0.6, 0.9)
    gpuQuad = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuQuad)
    gpuQuad.fillBuffers(shapeQuad.vertices, shapeQuad.indices, GL_STATIC_DRAW)

    shapeFloor = bs.createColorQuad(0.9, 0.9, 0.9)
    gpuFloor = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuFloor)
    gpuFloor.fillBuffers(shapeFloor.vertices, shapeFloor.indices, GL_STATIC_DRAW)

    shapeCircle = createCircle(1, 1, 0, 32)
    gpuCircle = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuCircle)
    gpuCircle.fillBuffers(shapeCircle.vertices, shapeCircle.indices, GL_STATIC_DRAW)

    coinpos=[[0.2, 0.4, 0.0],[0.45, 0.4, 0.0],[0.7, 0.4, 0.0]]

    y_pos1 = np.linspace(0, 0.5, 75)
    y_pos2 = np.linspace(0.5, 0, 75)

    y_pos = np.concatenate((y_pos1, y_pos2))

    for i in range(len(y_pos)):
        y_pos[i] = y_pos[i] * (1.5-y_pos[i])**2 * 0.7
        

    
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    t0 = glfw.get_time()

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)
    n=1

    deltax = 0.1
    deltay = 0.15

    drawcoins = [True, True, True]

    while not glfw.window_should_close(window):
        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        # Using GLFW to check for input events
        glfw.poll_events()

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            controller.x -= 0.005
        
        elif (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            controller.x += 0.005

        if controller.jump:
            controller.y=y_pos[n]
            n+=1

            if controller.y==0:
                n=1
                controller.jump = False


        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Drawing the Quad with the given transformation
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, np.matmul(
                tr.translate(0, -0.6, 0),
                tr.scale(2, 1, 1)
            ))
        pipeline.drawCall(gpuFloor)

        # Drawing the Quad with the given transformation
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, np.matmul(
                tr.translate(controller.x, controller.y, 0.0),
            #    tr.rotationZ(controller.theta)
                tr.scale(0.1, 0.2, 1)
            ))
        pipeline.drawCall(gpuQuad)

        #Aca las monedas
        for i in range(len(drawcoins)):
            if abs(controller.x - coinpos[i][0]) < deltax and abs(controller.y- coinpos[i][1]) < deltay:
                drawcoins[i] = False

            if drawcoins[i]:
                glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, np.matmul(
                    tr.translate(coinpos[i][0],coinpos[i][1],coinpos[i][2]),
                #    tr.rotationZ(controller.theta)
                    tr.uniformScale(0.1)
                ))
                pipeline.drawCall(gpuCircle)
        


        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuQuad.clear()
    gpuFloor.clear()

    glfw.terminate()