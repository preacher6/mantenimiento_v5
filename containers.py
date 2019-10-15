import pygame
import os
import numpy as np
import sympy as sy
import matplotlib.pyplot as plt
from objects import *
from textbox import ListBox
from collections import defaultdict


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SEMIWHITE = (245, 245, 245)
GRAY = (128, 128, 128)
LIGHTGRAY = (192, 192, 192)
GANSBORO = (220, 220, 220)
SLATEGRAY = (112, 128, 144)


class OptionPanels(pygame.sprite.Sprite):
    """Clase para pestañas de opciones"""
    def __init__(self, name, position, cont, active=False, content=None):
        pygame.sprite.Sprite.__init__(self)
        self.load_pics()
        self.name = name
        self.icon = pygame.image.load(os.path.join('icons', name+str('.png')))
        self.active = active
        self.image = self.option_s  # Imagen actual de la pestaña opcion (activa)
        self.image_off = self.option_n
        self.rect = self.image.get_rect()  # Recta de la imagen
        self.rect.x = position[0]
        self.rect.y = position[1]+cont*40
        self.content = content

    def load_pics(self):
        """Cargar imagenes"""
        self.addline_s = pygame.image.load(os.path.join('icons', 'addline_s.png'))
        self.addline_n = pygame.image.load(os.path.join('icons', 'addline_n.png'))
        self.reduceline_s = pygame.image.load(os.path.join('icons', 'reduceline_s.png'))
        self.reduceline_n = pygame.image.load(os.path.join('icons', 'reduceline_n.png'))
        self.pestana_s = pygame.image.load(os.path.join('pics', 'pesta_s.png'))
        self.pestana_n = pygame.image.load(os.path.join('pics', 'pesta_n.png'))
        self.new = pygame.image.load(os.path.join('pics', 'pesta_new.png'))
        self.option_s = pygame.image.load(os.path.join('pics', 'option_s.png'))
        self.option_n = pygame.image.load(os.path.join('pics', 'option_n.png'))
        self.close = pygame.image.load(os.path.join('icons', 'close.png'))
        self.add = pygame.image.load(os.path.join('icons', 'add.png'))
        self.grid = pygame.image.load(os.path.join('pics', 'punto.png'))
        # Acciones
        self.connect_n = pygame.image.load(os.path.join('icons', 'connect_n.png'))
        self.connect_s = pygame.image.load(os.path.join('icons', 'connect_s.png'))
        self.disconnect_n = pygame.image.load(os.path.join('icons', 'disconnect_n.png'))
        self.disconnect_s = pygame.image.load(os.path.join('icons', 'disconnect_s.png'))
        self.move_n = pygame.image.load(os.path.join('icons', 'move_n.png'))
        self.move_s = pygame.image.load(os.path.join('icons', 'move_s.png'))
        self.delete_n = pygame.image.load(os.path.join('icons', 'delete_n.png'))
        self.delete_s = pygame.image.load(os.path.join('icons', 'delete_s.png'))
        self.export_n = pygame.image.load(os.path.join('icons', 'export_n.png'))
        self.export_s = pygame.image.load(os.path.join('icons', 'export_s.png'))
        self.import_n = pygame.image.load(os.path.join('icons', 'import_n.png'))
        self.import_s = pygame.image.load(os.path.join('icons', 'import_s.png'))
        self.rename_n = pygame.image.load(os.path.join('icons', 'rename_n.png'))
        self.rename_s = pygame.image.load(os.path.join('icons', 'rename_s.png'))
        self.save_n = pygame.image.load(os.path.join('icons', 'save_n.png'))
        self.save_s = pygame.image.load(os.path.join('icons', 'save_s.png'))
        self.load_n = pygame.image.load(os.path.join('icons', 'load_n.png'))
        self.load_s = pygame.image.load(os.path.join('icons', 'load_s.png'))
        self.ok_n = pygame.image.load(os.path.join('icons', 'ok_n.png'))
        self.ok_s = pygame.image.load(os.path.join('icons', 'ok_s.png'))
        # Elementos
        self.caja_mini = pygame.image.load(os.path.join('pics', 'caja_mini.png'))
        self.stand_mini = pygame.image.load(os.path.join('pics', 'stand_by_mini.png'))
        self.knn_mini = pygame.image.load(os.path.join('pics', 'knn_mini.png'))
        # Normales
        self.caja = pygame.image.load(os.path.join('pics', 'caja.png'))
        self.stand = pygame.image.load(os.path.join('pics', 'stand_by.png'))
        self.knn = pygame.image.load(os.path.join('pics', 'knn.png'))

    def draw_option(self, screen):
        """Dibujar pestañas de opciones"""
        if self.active:
            screen.blit(self.image, self.rect)
        else:
            screen.blit(self.image_off, self.rect)
        screen.blit(self.icon, (self.rect[0]-2, self.rect[1]+2))


class Container(pygame.sprite.Sprite):
    def __init__(self, pos, cont, tag, content=None):
        pygame.sprite.Sprite.__init__(self)
        self.load_pics()
        self.pos = pos  # Posicion de la pestaña
        self.pos_elem = (pos[0], pos[1]+30)
        self.cont = cont  # Numero actual de pestañas
        self.font = pygame.font.SysFont('Arial', 13)
        self.image = self.pestana_s  # Imagen actual de la pestaña (activa)
        self.image_off = self.pestana_n  # Imagen de pestaña inactiva
        # Rectas
        self.rect = self.image.get_rect()  # Recta de la imagen
        self.rect.x = pos[0] + (120 * (cont - 1))
        self.rect.y = pos[1]
        self.recta_new = self.new.get_rect()
        self.recta_new.x = pos[0] + 120 * cont
        self.recta_new.y = pos[1]
        self.recta_add = self.add.get_rect()
        self.recta_add.x = pos[0] + 120 * cont + 8
        self.recta_add.y = pos[1] + 6
        self.recta_close = self.close.get_rect()
        self.recta_close.x = pos[0] + 89 + (120 * (cont - 1))
        self.recta_close.y = pos[1] + 5
        self.name = 'Untitled_' + str(tag)  # Nombre de la pestaña
        self.selected = True  # Indica si esta activa. Al momento de crearse siempre lo está
        self.content = content
        self.limites = pygame.sprite.Group()
        self.cajas = pygame.sprite.Group()
        self.cont_cajas = 0
        self.all_cajas = 0
        self.knn = pygame.sprite.Group()
        self.cont_knn = 0
        self.all_knn = 0
        self.stand = pygame.sprite.Group()
        self.cont_stand = 0
        self.all_stand = 0
        self.kdn = pygame.sprite.Group()
        self.cont_kdn = 0
        self.all_kdn = 0
        self.module = pygame.sprite.Group()
        self.cont_module = 0
        self.all_module = 0
        self.nodos = pygame.sprite.Group()  # Guarda los nodos disponibles para el contenedor
        self.conections = pygame.sprite.Group()  # Guarda las conexiones del contenedor
        self.list_box = ListBox()
        self.own_items = []  # Lista elementos propios
        self.items = pygame.sprite.Group()  # Grupo sprites de elementos. Con esta se calculan datos
        self.real_items = pygame.sprite.Group()  # Grupo de todas las cajas. Con esta se determina colision entre cajas y otros elementos
        self.keys = [chr(97+value) for value in range(36)]
        self.ini_tag = self.keys[0]
        self.nodos_sistema = {key:pygame.sprite.Group() for key in self.keys}  # Define los nodos del sistema
        self.correct = False  # Indica si es posible obtener confiabilidad del sistema
        self.time = 30000  # Tiempo total del sistema
        self.plot_all = 0
        self.all_connected = False
        self.init_containter()
        self.time_eval = 10000  # Tiempo que se desea evaluar
        self.ploting = False  # Indica si se esta ploteando

    def load_pics(self):
        """Cargar imagenes"""
        self.addline_s = pygame.image.load(os.path.join('icons', 'addline_s.png'))
        self.addline_n = pygame.image.load(os.path.join('icons', 'addline_n.png'))
        self.reduceline_s = pygame.image.load(os.path.join('icons', 'reduceline_s.png'))
        self.reduceline_n = pygame.image.load(os.path.join('icons', 'reduceline_n.png'))
        self.pestana_s = pygame.image.load(os.path.join('pics', 'pesta_s.png'))
        self.pestana_n = pygame.image.load(os.path.join('pics', 'pesta_n.png'))
        self.new = pygame.image.load(os.path.join('pics', 'pesta_new.png'))
        self.option_s = pygame.image.load(os.path.join('pics', 'option_s.png'))
        self.option_n = pygame.image.load(os.path.join('pics', 'option_n.png'))
        self.close = pygame.image.load(os.path.join('icons', 'close.png'))
        self.add = pygame.image.load(os.path.join('icons', 'add.png'))
        self.grid = pygame.image.load(os.path.join('pics', 'punto.png'))
        # Acciones
        self.connect_n = pygame.image.load(os.path.join('icons', 'connect_n.png'))
        self.connect_s = pygame.image.load(os.path.join('icons', 'connect_s.png'))
        self.disconnect_n = pygame.image.load(os.path.join('icons', 'disconnect_n.png'))
        self.disconnect_s = pygame.image.load(os.path.join('icons', 'disconnect_s.png'))
        self.move_n = pygame.image.load(os.path.join('icons', 'move_n.png'))
        self.move_s = pygame.image.load(os.path.join('icons', 'move_s.png'))
        self.delete_n = pygame.image.load(os.path.join('icons', 'delete_n.png'))
        self.delete_s = pygame.image.load(os.path.join('icons', 'delete_s.png'))
        self.export_n = pygame.image.load(os.path.join('icons', 'export_n.png'))
        self.export_s = pygame.image.load(os.path.join('icons', 'export_s.png'))
        self.import_n = pygame.image.load(os.path.join('icons', 'import_n.png'))
        self.import_s = pygame.image.load(os.path.join('icons', 'import_s.png'))
        self.rename_n = pygame.image.load(os.path.join('icons', 'rename_n.png'))
        self.rename_s = pygame.image.load(os.path.join('icons', 'rename_s.png'))
        self.save_n = pygame.image.load(os.path.join('icons', 'save_n.png'))
        self.save_s = pygame.image.load(os.path.join('icons', 'save_s.png'))
        self.load_n = pygame.image.load(os.path.join('icons', 'load_n.png'))
        self.load_s = pygame.image.load(os.path.join('icons', 'load_s.png'))
        self.ok_n = pygame.image.load(os.path.join('icons', 'ok_n.png'))
        self.ok_s = pygame.image.load(os.path.join('icons', 'ok_s.png'))
        # Elementos
        self.caja_mini = pygame.image.load(os.path.join('pics', 'caja_mini.png'))
        self.stand_mini = pygame.image.load(os.path.join('pics', 'stand_by_mini.png'))
        self.knn_mini = pygame.image.load(os.path.join('pics', 'knn_mini.png'))
        # Normales
        self.caja = pygame.image.load(os.path.join('pics', 'caja.png'))
        self.stand = pygame.image.load(os.path.join('pics', 'stand_by.png'))
        self.knn = pygame.image.load(os.path.join('pics', 'knn.png'))
        self.type_plot = 1

    def init_containter(self):
        """Inicializar elementos que tiene el contenedor"""
        self.limites.add(Init((self.pos_elem[0]+40, self.pos_elem[1]+241)))
        self.limites.add(End((self.pos_elem[0]+860, self.pos_elem[1]+241)))
        for limite in self.limites:
            self.nodos.add(limite.nodos)
            self.own_items.append(limite.tag)
            self.items.add(limite)
            self.real_items.add(limite)

    def draw_cont(self, screen):
        """Dibujar icono de pestaña"""
        self.rect.x = self.pos[0] + (120 * (self.cont - 1))
        self.rect.y = self.pos[1]
        self.recta_close.x = self.pos[0] + 89 + (120 * (self.cont - 1))
        self.recta_close.y = self.pos[1] + 5
        if self.selected:
            screen.blit(self.image, self.rect)
        else:
            screen.blit(self.image_off, self.rect)
        screen.blit(self.close, self.recta_close)
        screen.blit(self.font.render(self.name, True, (255, 0, 0)),
                    (self.pos[0]+14+(120*(self.cont-1)), self.pos[1]+7))

    def draw_new(self, screen, cont):
        """Dibujar icono de nueva pestaña"""
        self.recta_new.x = self.pos[0] + 120 * cont
        self.recta_add.x = self.pos[0] + 120 * cont + 8
        screen.blit(self.new, self.recta_new)
        screen.blit(self.add, self.recta_add)

    def draw_elements(self, screen):
        """Dibujar elementos del contenedor"""
        for limit in self.limites:
            limit.draw(screen)

        for caja in self.cajas:
            caja.draw(screen)

        for knn_ind in self.knn:
            knn_ind.draw(screen)

        for stand_ind in self.stand:
            stand_ind.draw(screen)

        for kdn_in in self.kdn:
            kdn_in.draw(screen)

        for module in self.module:
            module.draw(screen)

        for conex_in in self.conections:
            conex_in.draw(screen)
            for limite in self.limites:  # Conexiones de limites
                for nodo in limite.nodos:  # Se recorre un for para ver si algun elemento ha sido conectado
                    if conex_in.elem1.name_element == nodo.name_element and conex_in.elem1.id == nodo.id:
                        nodo.connected = True

                    if conex_in.elem2.name_element == nodo.name_element and conex_in.elem2.id == nodo.id:
                        nodo.connected = True

            for caja in self.cajas:  # Conexiones de cajas
                for nodo in caja.nodos:  # Se recorre un for para ver si algun elemento ha sido conectado
                    if conex_in.elem1.name_element == nodo.name_element and conex_in.elem1.id == nodo.id:
                        nodo.connected = True

                    if conex_in.elem2.name_element == nodo.name_element and conex_in.elem2.id == nodo.id:
                        nodo.connected = True

            for knn_ind in self.knn:  # Conexiones de knn
                for nodo in knn_ind.nodos:  # Se recorre un for para ver si algun elemento ha sido conectado
                    if conex_in.elem1.name_element == nodo.name_element and conex_in.elem1.id == nodo.id:
                        nodo.connected = True

                    if conex_in.elem2.name_element == nodo.name_element and conex_in.elem2.id == nodo.id:
                        nodo.connected = True

            for stand_ind in self.stand:  # Conexiones de standby
                for nodo in stand_ind.nodos:  # Se recorre un for para ver si algun elemento ha sido conectado
                    if conex_in.elem1.name_element == nodo.name_element and conex_in.elem1.id == nodo.id:
                        nodo.connected = True

                    if conex_in.elem2.name_element == nodo.name_element and conex_in.elem2.id == nodo.id:
                        nodo.connected = True

            for kdn_ind in self.kdn:  # Conexiones de knn
                for nodo in kdn_ind.nodos:  # Se recorre un for para ver si algun elemento ha sido conectado
                    if conex_in.elem1.name_element == nodo.name_element and conex_in.elem1.id == nodo.id:
                        nodo.connected = True

                    if conex_in.elem2.name_element == nodo.name_element and conex_in.elem2.id == nodo.id:
                        nodo.connected = True

            for module in self.module:
                for nodo in module.nodos:  # Se recorre un for para ver si algun elemento ha sido conectado
                    if conex_in.elem1.name_element == nodo.name_element and conex_in.elem1.id == nodo.id:
                        nodo.connected = True

                    if conex_in.elem2.name_element == nodo.name_element and conex_in.elem2.id == nodo.id:
                        nodo.connected = True

        self.valid_nodes = 0  # Define cuantos nodos se encuentran desconectados
        for nodo in self.nodos:  # Recorro nodos mirando cuantos estan desconectados
            if not nodo.connected:
                self.valid_nodes += 1
        self.all_connected = False
        if self.valid_nodes == 0 and len(self.nodos)>0:  # Se ejecuta si todos los nodos estan conectados
            self.all_connected = True
            self.build_matriz()  # Construir matriz de conexiones

    def build_matriz(self):
        """Funcion para construir matriz de incidencia"""
        nro_nodos_sistema = len(self.nodos) - len(self.conections)  # Cantidad de nodos totales del sistema
        nro_items = len(self.items)  # Nro de items presentes
        self.matriz_inc = np.zeros((nro_items,
                                    nro_nodos_sistema + 4), dtype=object)  # La columna extra es para almacenar el valor de la confiabilidad para ese elemento
        node = 0
        for value, item in enumerate(self.items):
            self.matriz_inc[value][nro_nodos_sistema] = \
            [element_ind.value for element_ind in self.items if element_ind.tag == item.tag][0]
            self.matriz_inc[value][nro_nodos_sistema + 1] = \
            [element_ind.sym for element_ind in self.items if element_ind.tag == item.tag][0]
            self.matriz_inc[value][nro_nodos_sistema+2] = \
            [element_ind.value_sy for element_ind in self.items if element_ind.tag == item.tag][0]

            for element_ind in self.items:
                if element_ind.tag == item:
                    if element_ind.tipo == 'caja':
                        if element_ind.orientation:
                            self.matriz_inc[value][-1] = 0
                        else:
                            self.matriz_inc[value][-1] = 1
                    else:
                        self.matriz_inc[value][-1] = 0

        for key in self.keys:  # Recorrer etiquetas de nodos del sistema
            if len(self.nodos_sistema[key]) > 0:  # Si ya existen nodos
                for nodo in self.nodos_sistema[key]:  # Recorrer los nodos fisicos anexos al nodo del sistema
                    element = self.own_items.index(nodo.name_element)
                    self.matriz_inc[element][node] = 1
                node += 1
        matriz_inc = self.matriz_inc.copy()
        del_row = []
        ana_rows = []
        num_iter = 0
        irreduced = False
        equation = ''
        variables_sym = matriz_inc[2:, -3].tolist()
        values_sym = matriz_inc[2:, -2].tolist()
        # Diccionario de lo simbolico
        dicto_variables = {k:v for k, v in zip(variables_sym, values_sym)}
        while num_iter < 100:  # Evalua X cantidad de veces los posibles caminos
            num_iter += 1
            for index, row in enumerate(matriz_inc):  # Paralelos
                row_n = row[:-4]  # Toma solo la parte que indica incidencia
                if row_n.tolist() not in ana_rows:  # almacena las filas que no hayan sido evaluadas
                    ana_rows.append(row_n.tolist())
                    put = False
                    for index_2, row_2 in enumerate(matriz_inc):
                        rown_2 = row_2[:-4]
                        if index != index_2:  # Verifica que no sea la misma posicion que se encuentra evaluando
                            if (row_n == rown_2).all():  # Compara si los arreglos son iguales
                                del_row.append(index_2)  # Almacena la posicion del arreglo a eliminar
                                put = True
                                if matriz_inc[index, -4].startswith('('):
                                    matriz_inc[index, -3] = matriz_inc[index, -3]*(1-matriz_inc[index_2, -3])
                                    matriz_inc[index, -4] = matriz_inc[index, -4] + '*(1-' + matriz_inc[
                                        index_2, -4] + ')'
                                else:
                                    matriz_inc[index, -3] = (1-(matriz_inc[index, -3]))*(1-(matriz_inc[index_2, -3]))
                                    matriz_inc[index, -4] = '(1-('+matriz_inc[index, -4]+'))*(1-('+ matriz_inc[index_2, -4]+'))'
                    if matriz_inc[index, -4].startswith("(") and put:
                        matriz_inc[index, -3] = (1-(matriz_inc[index, -3]))
                        matriz_inc[index, -4] = '(1-(' + matriz_inc[index, -4] + '))'
            matriz_inc = np.delete(matriz_inc, del_row, 0)
            del_row = []
            ana_rows = []
            if matriz_inc.shape[0] == 3:  # Si solo quedan 3 filas cumple
                break
            for index, column in enumerate(matriz_inc[:, :-4].T):  # Series
                index_col = np.nonzero(column)[0]
                if np.sum(column) == 2:
                    row_1 = matriz_inc[index_col[0], :-4]
                    row_2 = matriz_inc[index_col[1], :-4]
                    if np.sum(row_1) == 2 and np.sum(row_2) == 2:
                        new_row = abs(row_1 - row_2)
                        matriz_inc[index_col[0], :-4] = new_row
                        del_row.append(index_col[1])
                        matriz_inc[index_col[0], -3] = matriz_inc[index_col[0], -3] *matriz_inc[index_col[1], -3]
                        matriz_inc[index_col[0], -4] = matriz_inc[index_col[0], -4] + '*' + matriz_inc[index_col[1], -4]
                        break
            matriz_inc = np.delete(matriz_inc, del_row, 0)
            del_row = []
        else:
            irreduced = True
        if irreduced:
            self.correct = False
            num_nodos = matriz_inc.shape[1]-2
            g = Graph(num_nodos)
            source = list()
            for row in matriz_inc:
                if np.sum(row[:-4]) == 2:
                    items = row[:-4].nonzero()[0].tolist()
                    g.addEdge(items[0], items[1])
                    g.addEdge(items[1], items[0])
                else:
                    items = row[:-4].nonzero()[0].tolist()
                    source.append(items[0])
            g.printAllPaths(source[0], source[1])
            conf_total = ''
            conf_total_sym = []
            for path in g.path:
                fin = len(path)-1
                count = 0
                conf_linea = ''
                conf_linea_sym = []
                while count+1 <= fin:
                    path_row = [path[count], path[count + 1]]
                    path_row.sort()
                    for row in matriz_inc:
                        if np.sum(row[:-4]) == 2:
                            if path_row == row[:-4].nonzero()[0].tolist():
                                count += 1
                                if not conf_linea:
                                    conf_linea = row[-4]
                                    conf_linea_sym = row[-3]
                                else:
                                    conf_linea += '*'+ row[-4]
                                    conf_linea_sym *= row[-3]
                if not conf_total:
                    conf_total = '(1-(' + conf_linea + '))'
                    conf_total_sym = (1-conf_linea_sym)
                else:
                    conf_total += '*(1-(' + conf_linea + '))'
                    conf_total_sym *= (1 - conf_linea_sym)
            conf_total = '(1-' + conf_total + ')'
            conf_total_sym = (1 - conf_total_sym)
            self.plot_all = conf_total
            t = self.time_eval
            print('La confiabilidad del sistema es: ', eval(conf_total)*100)
            print(conf_total)
            print('eq1', equation)
            func_sym = conf_total_sym
            self.func_sym = func_sym
            dicto_final = dict(zip(variables_sym, values_sym))
            self.func_sym = self.func_sym.subs(dicto_final)
            derivates = 0
            self.dicto_sol = {}
            for elem in variables_sym:
                derivates = sy.diff(func_sym, elem)
                self.dicto_sol[elem] = derivates.subs(dicto_variables)
        else:
            self.correct = True
            self.plot_all = matriz_inc[2, -4]
            t = self.time_eval
            func_sym = matriz_inc[2, -3]
            self.func_sym = func_sym
            dicto_final = dict(zip(variables_sym, values_sym))
            self.func_sym = self.func_sym.subs(dicto_final)
            derivates = 0
            self.dicto_sol = {}
            for elem in variables_sym:
                derivates = sy.diff(func_sym, elem)
                self.dicto_sol[elem] = derivates.subs(dicto_variables)
            """self.soluciones = []
            for deriv in derivates:
                self.soluciones.append(deriv.subs(dicto_variables))"""

    def check_node(self, elem1, elem2):
        """Verificar a que nodo del sistema se conectan los nodos fisicos de los objetos"""
        if len(self.nodos_sistema[self.ini_tag]) == 0:  # Agregarlos al primer nodo
            self.nodos_sistema[self.ini_tag].add(elem1)
            self.nodos_sistema[self.ini_tag].add(elem2)
        else:
            for key in self.keys:  # Recorre las etiquetas de los nodos disponibles
                found = False
                repeated = False
                for elem in self.nodos_sistema[key]:
                    if elem1 == elem:
                        self.nodos_sistema[key].add(elem2)
                        for key_new in self.keys:
                            if key_new != key and not repeated:
                                for elem_new in self.nodos_sistema[key_new]:
                                    if elem_new in self.nodos_sistema[key]:
                                        for dep_elem in self.nodos_sistema[key_new]:
                                            self.nodos_sistema[key].add(dep_elem)
                                        self.nodos_sistema[key_new] = pygame.sprite.Group()
                                        repeated = True
                                        break
                        found = True
                        break
                    elif elem2 == elem:
                        self.nodos_sistema[key].add(elem1)
                        for key_new in self.keys:
                            if key_new != key and not repeated:
                                for elem_new in self.nodos_sistema[key_new]:
                                    if elem_new in self.nodos_sistema[key]:
                                        for dep_elem in self.nodos_sistema[key_new]:
                                            self.nodos_sistema[key].add(dep_elem)
                                        self.nodos_sistema[key_new] = pygame.sprite.Group()
                                        repeated = True
                                        break
                        found = True
                        break
                if found:
                    break
            if found == False:
                for key in self.keys:
                    if len(self.nodos_sistema[key]) == 0:
                        self.nodos_sistema[key].add(elem1)
                        self.nodos_sistema[key].add(elem2)
                        break

    def system_plot(self):
        if self.type_plot == 1:  # Confiabilidad
            t = np.linspace(0, int(self.time), 500)
            plt.style.use('seaborn')  # pretty matplotlib plots
            plt.cla()
            plt.plot(t, eval(self.plot_all), c='blue',)
            plt.xlabel('t')
            plt.ylabel(r'$p(t|\beta,\alpha)$')
        else:  # Medida de importancia
            if len(self.items)>3:
                t = sy.symbols('t')
                x_vals = np.linspace(0, int(self.time), 500)
                plt.style.use('seaborn')  # pretty matplotlib plots
                plt.cla()
                for index, element in self.dicto_sol.items():
                    lam_x = sy.lambdify(t, element, modules=['numpy'])
                    y_vals = lam_x(x_vals)
                    plt.plot(x_vals, y_vals, label=index)
                    plt.legend()
            else:
                self.type_plot == 1

# This class represents a directed graph
# using adjacency list representation
class Graph:

    def __init__(self, vertices):
        # No. of vertices
        self.V = vertices
        self.path = []

        # default dictionary to store graph
        self.graph = defaultdict(list)

        # function to add an edge to graph

    def addEdge(self, u, v):
        self.graph[u].append(v)

    '''A recursive function to print all paths from 'u' to 'd'. 
    visited[] keeps track of vertices in current path. 
    path[] stores actual vertices and path_index is current 
    index in path[]'''

    def printAllPathsUtil(self, u, d, visited, path):

        # Mark the current node as visited and store in path
        visited[u] = True
        path.append(u)

        # If current vertex is same as destination, then print
        # current path[]
        if u == d:
            #print(path)
            #print('---------')
            self.path.append(path.copy())
        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex
            for i in self.graph[u]:
                if visited[i] == False:
                    self.printAllPathsUtil(i, d, visited, path)

                    # Remove current vertex from path[] and mark it as unvisited
        path.pop()
        visited[u] = False

    # Prints all paths from 's' to 'd'
    def printAllPaths(self, s, d):

        # Mark all the vertices as not visited
        visited = [False] * (self.V)

        # Create an array to store paths
        path = []

        # Call the recursive helper function to print all paths
        self.printAllPathsUtil(s, d, visited, path)