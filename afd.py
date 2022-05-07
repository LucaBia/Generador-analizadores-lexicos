import re as regex
from binarytree import Node as BinaryTreeNode

class Node:
    def __init__(self, data, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right

    @staticmethod
    def convert_to_binary_tree(parent_node, binary_tree_parent=None):
        if binary_tree_parent is None:
            binary_tree_parent = BinaryTreeNode(ord(parent_node.data))

        if parent_node.left is not None and parent_node.left.data is not None:
            binary_tree_parent.left = BinaryTreeNode(ord(parent_node.left.data))
            Node.convert_to_binary_tree(parent_node.left, binary_tree_parent.left)

        if parent_node.right is not None and parent_node.right.data is not None:
            binary_tree_parent.right = BinaryTreeNode(ord(parent_node.right.data))
            Node.convert_to_binary_tree(parent_node.right, binary_tree_parent.right)

        return binary_tree_parent


class RETree:
    def __init__(self, initial_regular_expression):
        self.current_node_head = None
        self.temp_roots = []
        self.get_nodes(initial_regular_expression, None)

    def get_tree(self):
        return Node.convert_to_binary_tree(self.current_node_head)

    def add_node(self, temp_root_index, content, left, right, use_head_for):
        if temp_root_index is None:
            self.current_node_head = Node(content, left, right) if self.current_node_head is None else (Node(content, self.current_node_head, right) if use_head_for == 'l' else Node(content, left, self.current_node_head))
        else:
            if temp_root_index == len(self.temp_roots):
                self.temp_roots.append(Node(content, left, right))
            elif temp_root_index < len(self.temp_roots):
                self.temp_roots[temp_root_index] = Node(content, left, right) if self.temp_roots[temp_root_index] is None else (Node(content, self.temp_roots[temp_root_index], right) if use_head_for == 'l' else Node(content, left, self.temp_roots[temp_root_index]))

    @staticmethod
    def get_final_of_expression(partial_expression):
        i = 0
        while i < len(partial_expression):
            if partial_expression[i] == '«':
                parentheses_counter = 1
                for j in range(i+1, len(partial_expression)):
                    if partial_expression[j] in ['«', '»']: parentheses_counter = parentheses_counter + 1 if partial_expression[j] == '«' else parentheses_counter - 1

                    if parentheses_counter == 0 and partial_expression[j] == '»':
                        extra = 2 if j + 1 < len(partial_expression) and partial_expression[j+1] in ['±', '+', '?'] else 0
                        fin = j + extra
                        return fin

            elif regex.match(r'[a-zA-Z±"\'/*=.|()[\]{} ]', partial_expression[i]):
                fin = i
                for j in range(i + 1, len(partial_expression)):
                    if not regex.match(r'[a-zA-Z±"\'/*=.|()[\]{} ]', partial_expression[j]): break
                    fin = j
                return fin
            i += 1


    def get_nodes(self, partial_expression, temp_root_index):
        i = 0
        while i < len(partial_expression):
            if partial_expression[i] == '«':
                if i == 0:
                    parentheses_counter = 1
                    for j in range(i+1, len(partial_expression)):
                        if partial_expression[j] in ['«', '»']: parentheses_counter = parentheses_counter + 1 if partial_expression[j] == '«' else parentheses_counter - 1

                        if parentheses_counter == 0:
                            extra = 2 if partial_expression[j] == '»' and j + 1 < len(partial_expression) and partial_expression[j+1] in ['±', '+', '?'] else 0
                            fin = j + extra
                            self.get_nodes(partial_expression[i+1:fin], temp_root_index)
                            i = j
                            break
                else:
                    if partial_expression[i-1] in ['»', '±', '+', '?'] or regex.match(r'[a-zA-Z"\'/*=.|()[\]{} ]', partial_expression[i-1]):
                        fin_sub_re = self.get_final_of_expression(partial_expression[i:])
                        fin = i + 1 + fin_sub_re
                        self.get_nodes(partial_expression[i:fin], len(self.temp_roots))

                        sub_tree_root = self.temp_roots.pop() if temp_root_index is None else self.temp_roots.pop(temp_root_index + 1)
                        if sub_tree_root is not None: self.add_node(temp_root_index, '.', None, sub_tree_root, 'l')
                        i = i + fin + 1

            elif regex.match(r'[a-zA-Z#"\'/*=.|()[\]{} ]', partial_expression[i]):
                if ((temp_root_index is None and self.current_node_head is None) or i == 0) and i + 1 < len(partial_expression) and regex.match(r'[a-zA-Z#"\'/*=.|()[\]{} ]', partial_expression[i+1]):
                    if i + 2 < len(partial_expression) and partial_expression[i+2] in ['±', '+', '?']:
                        self.add_node(temp_root_index, '.', Node(partial_expression[i]), Node(partial_expression[i+2], Node(partial_expression[i+1]), None), 'l')
                        i += 2
                    else:
                        self.add_node(temp_root_index, '.', Node(partial_expression[i]), Node(partial_expression[i+1]), 'l')
                        i += 1
                elif (temp_root_index is None and self.current_node_head is not None) or i != 0:
                    self.add_node(temp_root_index, '.', None, Node(partial_expression[i]), 'l')
                else:
                    self.add_node(temp_root_index, partial_expression[i], None, None, 'l')

                if i + 1 < len(partial_expression):
                    if partial_expression[i+1] in ['±', '+', '?']:
                        self.add_node(temp_root_index, partial_expression[i+1], Node(partial_expression[i]), None, 'l')
                    elif partial_expression[i+1] == '»':
                        if i + 2 < len(partial_expression) and partial_expression[i+2] in ['±', '+', '?']:
                            self.add_node(temp_root_index, partial_expression[i+2], Node(partial_expression[i]), None, 'l')

            elif partial_expression[i] in ['¦']:
                fin_sub_re = self.get_final_of_expression(partial_expression[i+1:])
                fin = i + 1 + fin_sub_re + 1
                self.get_nodes(partial_expression[i+1:fin], len(self.temp_roots))

                sub_tree_root = self.temp_roots.pop() if temp_root_index is None else self.temp_roots.pop(temp_root_index + 1)
                if sub_tree_root is not None: self.add_node(temp_root_index, partial_expression[i], Node(partial_expression[i-1]), sub_tree_root, 'l')

                if fin < len(partial_expression) and partial_expression[fin] == '»':
                    if fin + 1 < len(partial_expression) and partial_expression[fin+1] in ['±', '+', '?']:
                        self.add_node(temp_root_index, partial_expression[fin+1], Node(partial_expression[fin+1]), None, 'l')

                i = i + fin + 1
            else:
                pass
            i += 1


class Estado:
    def __init__(self, val, anul, prima_pos, ult_pos, next_pos):
        self.val = val
        self.anul = anul
        self.prima_pos = prima_pos
        self.ult_pos = ult_pos
        self.next_pos = next_pos


class AFD:
    def __init__(self, re, draw=False, print_tree=False):
        self.data = {}
        self.tree = None
        self.alfabeto = []
        self.transiciones = {}
        self.print_tree = print_tree
        self.construct_tree(re)
        self.init_estados()
        self.get_transiciones()

        if draw:
            self.draw()

    def construct_tree(self, re):
        re = '«' + re + '»#'
        retree = RETree(re)
        self.tree = retree.get_tree()
        if self.print_tree:
            print(self.tree)

    def init_estados(self):
        cont = 1

        # Se inicializa el diccionario de estados
        for i in self.tree.postorder:
            self.data[str(cont)] = Estado(chr(i.value), None, None, None, [])
            i.value = cont
            cont += 1

        # Extraigo letras de la expresion
        for hoja in self.tree.leaves:
            if regex.match(r'[a-zA-Z"\'/*=.|()[\]{} ]', self.data[str(hoja.value)].val) and self.data[str(hoja.value)].val not in self.alfabeto:
                self.alfabeto.append(self.data[str(hoja.value)].val)

        self.alfabeto.sort()

        for node in self.tree.postorder:
            self.anul(node)
            self.prima_y_ult(node)
            self.next_pos(node)

    def accepts(self, word, characters):
        return self.simulacion(word, characters)

    def simulacion(self, word, characters):
        for char in word:
            belongs_to = False
            for key in self.alfabeto:
                if characters.get(key):
                    if char in characters[key]:
                        belongs_to = True
                        break
                else:
                    return False
            if not belongs_to:
                return False

        current_state = 'S0'

        for char in word:
            llave = ''
            alfabeto_key = None

            for key in self.alfabeto:
                if char in characters[key]:
                    alfabeto_key = key

            for key, value in self.transiciones.items():
                if value['name'] == current_state and value[alfabeto_key] is not None:
                    llave = key
                elif value['name'] == current_state and value[alfabeto_key] is None:
                    return False

            current_state = self.transiciones[llave][alfabeto_key]

        for key, value in self.transiciones.items():
            if value['name'] == current_state:
                states = key
                for specialChar in ['[', ']', ' ']:
                    states = states.replace(specialChar, '')
                states = states.split(',')

                return True if str(self.tree.right.value) in states else False

    def get_transiciones(self):
        # Se genera la tabla de transiciones
        cont = 0

        # El primer valor de la tabla son las primeras posiciones de la raiz del arbol
        self.transiciones[str(self.data[str(self.tree.value)].prima_pos)] = {
            'name': 'S' + str(cont),
        }

        for letra in self.alfabeto:
            self.transiciones[str(self.data[str(self.tree.value)].prima_pos)][letra] = None

        cont += 1
        continuar = True
        while (continuar):
            initial_size = len(self.transiciones)
            keys = list(self.transiciones.keys())

            for key in keys:
                for letra in self.alfabeto:
                    if self.transiciones[key][letra] is None:
                        new_state = []
                        state = key

                        for specialChar in ['[', ']', ' ']:
                            state = state.replace(specialChar, '')
                        state = state.split(',')

                        for i in state:
                            if self.data[str(i)].val == letra: new_state.append(self.data[str(i)].next_pos)

                        new_state = [item for sublist in new_state for item in sublist]
                        new_state = list(set(new_state))
                        new_state.sort()

                        if len(new_state) > 0:
                            if str(new_state) not in self.transiciones:
                                self.transiciones[str(new_state)] = {
                                    'name': 'S' + str(cont)
                                }

                                for letter in self.alfabeto:
                                    self.transiciones[str(new_state)][letter] = None

                                cont += 1
                                self.transiciones[key][letra] = self.transiciones[str(new_state)]['name']
                            else:
                                self.transiciones[key][letra] = self.transiciones[str(new_state)]['name']

            final_size = len(self.transiciones)

            if initial_size == final_size:
                continuar = not all(self.transiciones.values())

    def anul(self, node):
        # Es anul si te puede devolver Epsilon (~)
        if self.data[str(node.value)].val == '¦' and node.left and node.right:
            self.data[str(node.value)].anul = self.data[str(node.left.value)].anul or self.data[str(node.right.value)].anul
        elif self.data[str(node.value)].val == '.' and node.left and node.right:
            self.data[str(node.value)].anul = self.data[str(node.left.value)].anul and self.data[str(node.right.value)].anul
        elif self.data[str(node.value)].val in ['±', '?', '~']:
            self.data[str(node.value)].anul = True
        else:
            self.data[str(node.value)].anul = False

    def prima_y_ult(self, node):
        if self.data[str(node.value)].val in ['¦', '?'] and node.left and node.right:
            # Se obtienen todas las primeras posiciones de ambos hijos
            self.data[str(node.value)].prima_pos = [item for sublist in [self.data[str(node.left.value)].prima_pos, self.data[str(node.right.value)].prima_pos] for item in sublist]
            self.data[str(node.value)].ult_pos = [item for sublist in [self.data[str(node.left.value)].ult_pos, self.data[str(node.right.value)].ult_pos] for item in sublist]
        elif self.data[str(node.value)].val == '.' and node.left and node.right:
            if self.data[str(node.left.value)].anul:
                # Si el hijo izquierdo es anul, se obtiene la primera posición de sus hijos
                self.data[str(node.value)].prima_pos = [item for sublist in [self.data[str(node.left.value)].prima_pos, self.data[str(node.right.value)].prima_pos] for item in sublist]
            else:
                # Si el hijo izquierdo no es anul, se obtiene la primera posición del hijo izquierdo
                self.data[str(node.value)].prima_pos = [item for sublist in [self.data[str(node.left.value)].prima_pos] for item in sublist]

            if self.data[str(node.right.value)].anul:
                self.data[str(node.value)].ult_pos = [item for sublist in [self.data[str(node.left.value)].ult_pos, self.data[str(node.right.value)].ult_pos] for item in sublist]
            else:
                self.data[str(node.value)].ult_pos = [item for sublist in [self.data[str(node.right.value)].ult_pos] for item in sublist]
        elif self.data[str(node.value)].val in ['±', '+']:
            # Se obtiene la primera posición de su hijo
            self.data[str(node.value)].prima_pos = [item for sublist in [self.data[str(node.left.value)].prima_pos] for item in sublist]
            self.data[str(node.value)].ult_pos = [item for sublist in [self.data[str(node.left.value)].ult_pos] for item in sublist]
        elif self.data[str(node.value)].val == '~':
            self.data[str(node.value)].prima_pos = []
            self.data[str(node.value)].ult_pos = []
        else:
            self.data[str(node.value)].prima_pos = [node.value]
            self.data[str(node.value)].ult_pos = [node.value]

    def next_pos(self, node):
        # Para cada una de las ultimas posiciones se agregan las ultimas posiciones de sus hijos de la derecha
        if self.data[str(node.value)].val == '.' and node.left and node.right:
            for ult_pos in self.data[str(node.left.value)].ult_pos:
                for prim_pos in self.data[str(node.right.value)].prima_pos:
                    if prim_pos not in self.data[str(node.left.value)].next_pos:
                        self.data[str(ult_pos)].next_pos.append(prim_pos)

        # Para cada ultima posicion de su hijo se agregan las ultimas posiciones de sus hijos de la derecha
        elif self.data[str(node.value)].val == '±':
            for ult_pos in self.data[str(node.left.value)].ult_pos:
                for prim_pos in self.data[str(node.left.value)].prima_pos:
                    if prim_pos not in self.data[str(node.left.value)].next_pos:
                        self.data[str(ult_pos)].next_pos.append(prim_pos)