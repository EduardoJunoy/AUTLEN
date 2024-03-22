import ast
from ast import NodeVisitor
from typing import Optional

class ASTNestedIfCounter(NodeVisitor):
    '''
    Esta clase es un visitante personalizado para un Árbol Sintáctico Abstracto (AST),
    diseñado para contar el número de if anidados en el árbol.

    Funcionamiento:
        - __init__: Inicializa el visitante. 'nested_if_counter' mantiene un seguimiento del número de if anidados,
          'if_counter' es un contador para los if visitados, 'if_stack' es una pila para mantener un seguimiento de los
          if anidados.

        - visit_If: Método que se invoca para cada nodo del AST de tipo 'If'. Actualiza el contador de if visitados y
          añade el contador a la pila.

        - generic_visit: Método que se invoca para cada nodo del AST. Actualiza el contador de if anidados si el nodo
          actual es un nodo de tipo 'If'. Llama al método 'generic_visit' de la clase padre para visitar los nodos hijos
          del nodo actual.
        
    Devuelve el número de if anidados en el árbol AST.
    '''
    def __init__(self):
        self.nested_if_counter = 0
        self.if_counter = 0
        self.if_stack = []

    def visit_If(self, node):
        '''
        Método que se invoca para cada nodo del AST de tipo 'If'. Actualiza el contador de if visitados y
        añade el contador a la pila.
        
        Parámetros:
            - node: Nodo del AST a visitar.
        '''
        self.if_counter += 1
        self.if_stack.append(self.if_counter)
        self.generic_visit(node)
        self.if_stack.pop()
        self.if_counter -= 1

    def generic_visit(self, node):
        '''
        Método que se invoca para cada nodo del AST. Actualiza el contador de if anidados si el nodo
        actual es un nodo de tipo 'If'. Llama al método 'generic_visit' de la clase padre para visitar
        los nodos hijos del nodo actual.

        Parámetros:
            - node: Nodo del AST a visitar.
        
        Returns:
            - nested_if_counter: Número de if anidados en el árbol AST.
        '''
        if isinstance(node, ast.If): # si el nodo es de tipo 'If', actualizamos el contador de if anidados
            self.nested_if_counter = max(self.nested_if_counter, len(self.if_stack)) # escogemos el máximo entre el contador actual y el tamaño de la pila
        super().generic_visit(node)
        return self.nested_if_counter

class ASTDotVisitor(NodeVisitor):
    '''
    Esta clase es un visitante personalizado para un Árbol Sintáctico Abstracto (AST),
    diseñado para generar una representación visual del árbol en formato Graphviz.

    Funcionamiento:
        - __init__: Inicializa el visitante. 'level' mantiene un seguimiento del nivel actual en el árbol durante la visita,
          'node_counter' es un contador para los nodos visitados, 'last_parent' guarda el ID del último nodo padre visitado,
          'last_field_name' almacena el nombre del último campo visitado, y 'dot_graph' es una lista para acumular las
          líneas de la representación Graphviz.

        - generic_visit: Método que se invoca para cada nodo del AST. Construye la representación de Graphviz para el nodo,
          manejando los valores primitivos y las relaciones entre nodos. Los nodos y sus conexiones se añaden a 'dot_graph'.
          
        - print_dot_graph: Imprime la representación Graphviz acumulada en 'dot_graph'.

    No hay parámetros de salida, pero se genera una salida visual (Graphviz) del árbol AST.
    '''

    def __init__(self) -> None:
        self.level = 0
        self.node_counter = 0
        self.previous_node_id: Optional[int] = None
        self.last_visited_field = ""
        self.dot_graph = []

    def generic_visit(self, node: ast.AST) -> None:
        '''
        Método que se invoca para cada nodo del AST. Construye la representación de Graphviz para el nodo,

        Parámetros:
            - node: Nodo del AST a visitar.
        '''
        indent = ''
        #indent = '    ' * self.level # <-- Descomentar para indentar el árbol
        type_to_string = ""

        for field, value in ast.iter_fields(node): # iteramos sobre los campos y valores del nodo
            if not isinstance(value, (list, ast.AST)): # si el valor no es una lista ni un nodo AST, es decir, es un valor primitivo
                value_str = f"'{value}'" if isinstance(value, str) else str(value) # convertimos el valor a string
                type_to_string += f"{field}={value_str if value is not None else 'None'}, "

        if self.level == 0 and not self.dot_graph: # si es el primer nodo visitado, y la lista esta vacia, añadimos la cabecera del grafo
            self.dot_graph.append('digraph {')

        if self.previous_node_id is not None: # si el nodo tiene un padre, añadimos una relación entre el padre y el nodo actual
            self.dot_graph.append(f'{indent}s{self.previous_node_id} -> s{self.node_counter}[label="{self.last_visited_field}", shape=box]')

        if type_to_string: # si el nodo tiene valores primitivos, los añadimos a la representación
            type_to_string = type_to_string[:-2]  # quitamos la última coma y el espacio
        self.dot_graph.append(f'{indent}s{self.node_counter}[label="{type(node).__name__}({type_to_string})", shape=box]')

        # actualizacion de valores
        node_counter = self.node_counter
        self.level += 1
        self.node_counter += 1

        # casos en los que value si es una instancia de ast.AST o una lista de instancias de ast.AST
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value: # iteramos sobre los elementos de la lista
                    if isinstance(item, ast.AST): # si el valor es una instancia de ast.AST, visitamos el nodo
                        self.previous_node_id = node_counter
                        self.last_visited_field = field
                        self.visit(item)
            elif isinstance(value, ast.AST): # si el valor es una instancia de ast.AST, visitamos el nodo
                self.previous_node_id = node_counter
                self.last_visited_field = field
                self.visit(value)

        self.level -= 1 # actualizamos el nivel
        if self.level == 0: # si es el último nodo visitado, añadimos la llave de cierre del grafo e imprimimos el grafo
            self.dot_graph.append('}')
            self.print_dot_graph(indent)

    def print_dot_graph(self, indent):
        '''
        Imprime la representación Graphviz acumulada en 'dot_graph', teniendo en cuenta la indentación.
        '''
        for line in self.dot_graph:
            if line == 'digraph {' or line == '}':
                print(line)
            else:
                if indent == '':
                    print("    " + line)
                else:
                    print(line)
