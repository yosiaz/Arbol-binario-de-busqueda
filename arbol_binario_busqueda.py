import re
import sys
import tkinter as tk
from tkinter import ttk, messagebox

#un árbol muy inclinado, por ejemplo, números ya ordenados genera recursion profunda 
sys.setrecursionlimit(20000)

#ENTRADA
def interpretar_entrada(texto):
    """Convierte el texto del usuario en una lista de enteros POSITIVOS
    Acepta separadores: comas, espacios, punto y coma
    Ejemplo: "50, 30  70;20\\n40" -> [50, 30, 70, 20, 40]

    Devuelve una tupla (numeros, invalidos):
      - numeros:   lista de enteros positivos, en el mismo orden en que se escribieron
      - invalidos: lista de textos que no son enteros positivos"""
    fragmentos = [t for t in re.split(r"[,;\s]+", texto.strip()) if t]

    numeros = []
    invalidos = []
    for fragmento in fragmentos:
 #Un entero positivo valido: solo dígitos 0-9 
        if re.fullmatch(r"\+?[0-9]+", fragmento) and int(fragmento) >= 0:
            numeros.append(int(fragmento))
        else:
            invalidos.append(fragmento)
    return numeros, invalidos


# NODO Y ÁRBOL BINARIO DE BUSQUEDA
class Nodo:
    """
    Un nodo del árbol garda un valor y las referencias a sus dos hijos
    Si un hijo no existe, vale None
    """

    __slots__ = ("valor", "izquierdo", "derecho") 

    def __init__(self, valor):
        self.valor = valor
        self.izquierdo = None  # subarbol con valores MENORES
        self.derecho = None    # subarbol con valores MAYORES


class ArbolBinarioBusqueda:
    def __init__(self):
        self.raiz = None
        self.tamano = 0  # cantidad de nodos


    # INSERCIÓN
    def insertar(self, valor):
        """
        Algoritmo:
          1. Si el árbol está vacío, el valor se convierte en la raíz
          2. Si no, se parte de la raíz y se compara:
               - valor < nodo actual  -> ir a la izquierda
               - valor > nodo actual  -> ir a la derecha
               - valor == nodo actual -> duplicado, no se inserta
          3. Al llegar a un hueco (None), ahí se coloca el nuevo nodo

        Devuelve (insertado, camino):
          - insertado: True si se insertó, False si era duplicado.
          - camino: lista de (valor_del_nodo, "izquierda"/"derecha") que
            describe las decisiones tomadas
        """
        camino = []

        # Caso 1: arbol vacío -> el nuevo nodo es la raíz
        if self.raiz is None:
            self.raiz = Nodo(valor)
            self.tamano += 1
            return True, camino

        # Caso 2: bajar por el arbol hasta encontrar el lugar correcto
        actual = self.raiz
        while True:
            if valor == actual.valor:
                return False, camino 

            if valor < actual.valor:
                camino.append((actual.valor, "izquierda"))
                if actual.izquierdo is None:        # hueco encontrado
                    actual.izquierdo = Nodo(valor)
                    break
                actual = actual.izquierdo            # seguir bajando
            else:  # valor > actual.valor
                camino.append((actual.valor, "derecha"))
                if actual.derecho is None:          # hueco encontrado
                    actual.derecho = Nodo(valor)
                    break
                actual = actual.derecho              # seguir bajando

        self.tamano += 1
        return True, camino

# RECORRIDO INORDEN
    def recorrido_inorden(self):
        """Recorrido Inorden
        Para cada nodo:
          1. Se recorre todo su subárbol izquierdo (valores menores)
          2. Se visita el nodo (se agrega su valor al resultado)
          3. Se recorre todo su subárbol derecho (valores mayores)"""
        resultado = []

        def visitar(nodo):
            if nodo is None:         
                return
            visitar(nodo.izquierdo)   # 1) izquierda
            resultado.append(nodo.valor)  # 2) raíz 
            visitar(nodo.derecho)     # 3) derecha

        visitar(self.raiz)
        return resultado

    # POSICIONES PARA DIBUJAR
    def calcular_posiciones(self):
        posiciones = {}
        contador = [0]  # lista para poder modificarla dentro de la función interna

        def asignar(nodo, nivel):
            if nodo is None:
                return
            asignar(nodo.izquierdo, nivel + 1)
            posiciones[nodo.valor] = (contador[0], nivel)  # columna = turno inorden
            contador[0] += 1
            asignar(nodo.derecho, nivel + 1)

        asignar(self.raiz, 0)
        return posiciones

    def hijos_de(self):
        """
        Devuelve una lista de aristas (valor_padre, valor_hijo) para dibujar
        las líneas que unen cada nodo con sus hijos
        """
        aristas = []
        pila = [self.raiz] if self.raiz else []
        while pila:
            nodo = pila.pop()
            for hijo in (nodo.izquierdo, nodo.derecho):
                if hijo is not None:
                    aristas.append((nodo.valor, hijo.valor))
                    pila.append(hijo)
        return aristas


# 3) INTERFAz
class AplicacionABB:
    #ventana principal

    COLOR_NODO = "#BBDEFB"       # azul claro: nodo normal
    COLOR_NUEVO = "#FFB74D"      # naranja: nodo recién insertado
    COLOR_ACTUAL = "#FFF176"     # amarillo: nodo que se visita ahora (inorden)
    COLOR_VISITADO = "#A5D6A7"   # verde: nodo ya visitado (inorden)
    COLOR_LINEA = "#546E7A"      # líneas entre nodos
    COLOR_BORDE = "#0D47A1"

    EJEMPLO = "30, 80, 60, 20, 100, 50, 10, 40, 90, 70"  

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Árbol Binario de Busqueda")
        self.ventana.geometry("1000x720")
        self.ventana.minsize(600, 400)

        self.arbol = ArbolBinarioBusqueda()  # el arbol actual
        self.ocupado = False              

        self._crear_widgets()

    # Construcción de la interfaz
    def _crear_widgets(self):
        marco_entrada = ttk.Frame(self.ventana, padding=10)
        marco_entrada.pack(fill="x")

        ttk.Label(
            marco_entrada,
            text="Ingresa números (mínimo 2) separados por comas o espacios:",
        ).pack(anchor="w")

        fila = ttk.Frame(marco_entrada)
        fila.pack(fill="x", pady=(4, 0))

        self.var_texto = tk.StringVar()
        self.entrada = ttk.Entry(fila, textvariable=self.var_texto, font=("Consolas", 12))
        self.entrada.pack(side="left", fill="x", expand=True)
        self.entrada.focus()
        # Presionar Enter equivale a "Construir árbol
        self.entrada.bind("<Return>", lambda evento: self.construir_instantaneo())

    #botones
        marco_botones = ttk.Frame(self.ventana, padding=(10, 0))
        marco_botones.pack(fill="x")

        self.botones = []  # guardamos los botones para poder bloquearlos en las animaciones
        definiciones = [
            ("1. Construir árbol", self.construir_instantaneo),
            ("1. Construir paso a paso", self.construir_paso_a_paso),
            ("2. Recorrido Inorden", self.recorrer_inorden),
            ("Cargar ejemplo", self.cargar_ejemplo),
            ("Limpiar", self.limpiar),
        ]
        for texto, comando in definiciones:
            boton = ttk.Button(marco_botones, text=texto, command=comando)
            boton.pack(side="left", padx=(0, 6), pady=6)
            self.botones.append(boton)

        #control de velocidad de las animaciones
        ttk.Label(marco_botones, text="Velocidad:").pack(side="left", padx=(16, 4))
        self.var_retardo = tk.IntVar(value=800)
        # Se invierte el valor: mover a la derecha = más rápido.
        self.escala = ttk.Scale(
            marco_botones, from_=1500, to=150, orient="horizontal",
            length=140, variable=self.var_retardo,
        )
        self.escala.pack(side="left")
#canvas donde se dibuja el arbol
        marco_canvas = ttk.Frame(self.ventana, padding=(10, 0))
        marco_canvas.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(marco_canvas, bg="white", highlightthickness=1,
                                highlightbackground="#B0BEC5")
        barra_x = ttk.Scrollbar(marco_canvas, orient="horizontal", command=self.canvas.xview)
        barra_y = ttk.Scrollbar(marco_canvas, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=barra_x.set, yscrollcommand=barra_y.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")
        marco_canvas.rowconfigure(0, weight=1)
        marco_canvas.columnconfigure(0, weight=1)

        # resultado del recorrido
        marco_resultado = ttk.Frame(self.ventana, padding=(10, 6))
        marco_resultado.pack(fill="x")
        ttk.Label(marco_resultado, text="Resultado Inorden:",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.var_resultado = tk.StringVar(value="—")
        ttk.Label(marco_resultado, textvariable=self.var_resultado,
                  font=("Consolas", 12), wraplength=950, foreground="#1B5E20").pack(anchor="w")


#utilidades de interfaz
    def _bloquear(self, bloqueado):
        self.ocupado = bloqueado
        estado = "disabled" if bloqueado else "normal"
        for boton in self.botones:
            boton.configure(state=estado)

    def _retardo(self):
        #espera entre pasos de una animación
        return int(self.var_retardo.get())


    def _leer_numeros(self):
        numeros, invalidos = interpretar_entrada(self.var_texto.get())

        #informa si existe algún dato invalido
        if invalidos:
            lista = ", ".join(f"«{x}»" for x in invalidos)
            messagebox.showerror(
                "Datos inválidos",
                f"Estos datos no son enteros positivos válidos:\n\n{lista}\n\n"
                "Solo se aceptan números enteros mayores o igual que cero (0, 1, 2, 3, ...).\n"
            )
            return None

        #mínimo 2 números
        if len(numeros) < 2:
            messagebox.showwarning(
                "Cantidad insuficiente",
                f"Debes ingresar al menos 2 numeros",
            )
            return None

        #no guarda repetidos, así que se insertará una sola vez cada valor.
        vistos, repetidos = set(), []
        for n in numeros:
            if n in vistos and n not in repetidos:
                repetidos.append(n)
            vistos.add(n)
        if repetidos:
            messagebox.showinfo(
                "Números repetidos",
                "Estos números están repetidos y solo se insertarán una vez en el árbol:\n\n"
                + ", ".join(map(str, repetidos)),
            )

        return numeros


    # construcción del arbol
    def construir_instantaneo(self):
        if self.ocupado:
            return
        numeros = self._leer_numeros()
        if numeros is None:
            return

        self._reiniciar_vista()
        try:
            # Se inserta en el mismo orden en que el usuario escribio los números
            for valor in numeros:
                self.arbol.insertar(valor)
            self.dibujar()
        except RecursionError:
            self._error_recursion()

#animacion
    def construir_paso_a_paso(self):
        if self.ocupado:
            return
        numeros = self._leer_numeros()
        if numeros is None:
            return

        self._reiniciar_vista()
        self._bloquear(True)
        self._paso_construccion(numeros, 0)

    def _paso_construccion(self, numeros, i):
        if i >= len(numeros):
            self._bloquear(False)
            self.dibujar()
            return

        valor = numeros[i]
        insertado, _camino = self.arbol.insertar(valor)
        self.dibujar(nuevo=valor if insertado else None)
        self.ventana.after(self._retardo(), lambda: self._paso_construccion(numeros, i + 1))


    # recorrido inorden (
    def recorrer_inorden(self):
        if self.ocupado:
            return
        if self.arbol.raiz is None:
            messagebox.showinfo("Sin árbol", "Primero construye el árbol.")
            return

        try:
            orden = self.arbol.recorrido_inorden()  # el ordenamiento sale de aqui
        except RecursionError:
            self._error_recursion()
            return

        self.var_resultado.set("")
        self._bloquear(True)
        self._paso_inorden(orden, 0)

    def _paso_inorden(self, orden, j):
        if j >= len(orden):
            self._bloquear(False)
            self.dibujar(visitados=set(orden))
            self.var_resultado.set(" → ".join(map(str, orden)))
            return

        self.dibujar(actual=orden[j], visitados=set(orden[:j]))
        self.var_resultado.set(" → ".join(map(str, orden[: j + 1])))
        self.ventana.after(self._retardo(), lambda: self._paso_inorden(orden, j + 1))

    #otros botones
    def cargar_ejemplo(self):
        self.var_texto.set(self.EJEMPLO)

    def limpiar(self):
        self.var_texto.set("")
        self._reiniciar_vista()

    def _reiniciar_vista(self):
        # el arbol, el canvas y el resultado
        self.arbol = ArbolBinarioBusqueda()
        self.canvas.delete("all")
        self.var_resultado.set("—")

    def _error_recursion(self):
        messagebox.showerror(
            "Arbol demasiado profundo",
            "El árbol es tan profundo que supera el límite de recursión de Python.\n")
        self._bloquear(False)


    # dibujo del arbol
    def dibujar(self, nuevo=None, actual=None, visitados=()):
        self.canvas.delete("all")
        if self.arbol.raiz is None:
            return

        posiciones = self.arbol.calcular_posiciones()

        #tamaño de los nodos, crece si hay números con muchos dígitos
        max_digitos = max(len(str(v)) for v in posiciones)
        radio = max(20, 5 * max_digitos + 10)
        espacio_x = 2 * radio + 12   # separación horizontal entre columnas
        espacio_y = 2 * radio + 28   # separación vertical entre niveles
        margen = radio + 20


        columnas = max(c for c, _ in posiciones.values())
        ancho_arbol = columnas * espacio_x + 2 * margen
        ancho_canvas = max(self.canvas.winfo_width(), 1)
        desplazamiento = max(0, (ancho_canvas - ancho_arbol) // 2)

        def a_pantalla(valor):
            columna, nivel = posiciones[valor]
            return (desplazamiento + margen + columna * espacio_x,
                    margen + nivel * espacio_y)

        #lineas entre padre e hijo
        for padre, hijo in self.arbol.hijos_de():
            x1, y1 = a_pantalla(padre)
            x2, y2 = a_pantalla(hijo)
            self.canvas.create_line(x1, y1, x2, y2, fill=self.COLOR_LINEA, width=2)

        #circulos con el valor 
        visitados = set(visitados)
        for valor in posiciones:
            x, y = a_pantalla(valor)

            # elige el color segun el estado del nodo
            if valor == actual:
                color = self.COLOR_ACTUAL
            elif valor in visitados:
                color = self.COLOR_VISITADO
            elif valor == nuevo:
                color = self.COLOR_NUEVO
            else:
                color = self.COLOR_NODO

            self.canvas.create_oval(x - radio, y - radio, x + radio, y + radio,
                                    fill=color, outline=self.COLOR_BORDE, width=2)
            self.canvas.create_text(x, y, text=str(valor), font=("Segoe UI", 11, "bold"))


        xr, yr = a_pantalla(self.arbol.raiz.valor)
        self.canvas.create_text(xr, yr - radio - 10, text="raíz",
                                font=("Segoe UI", 8, "italic"), fill="#B71C1C")

        caja = self.canvas.bbox("all")
        if caja:
            self.canvas.configure(scrollregion=(0, 0, caja[2] + margen, caja[3] + margen))

def main():
    ventana = tk.Tk()
    AplicacionABB(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    main()