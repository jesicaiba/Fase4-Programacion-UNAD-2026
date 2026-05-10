import re
import logging
import datetime
from abc import ABC, abstractmethod

logging.basicConfig(
    filename="sistema.log",
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log(nivel, mensaje):
    if nivel == "INFO":
        logging.info(mensaje)
        print(f"  [OK]    {mensaje}")
    elif nivel == "AVISO":
        logging.warning(mensaje)
        print(f"  [AVISO] {mensaje}")
    elif nivel == "ERROR":
        logging.error(mensaje)
        print(f"  [ERROR] {mensaje}")

class ErrorSistema(Exception):
    pass

class ErrorCliente(ErrorSistema):
    pass

class ErrorServicio(ErrorSistema):
    pass

class ErrorReserva(ErrorSistema):
    pass

class ErrorCosto(ErrorSistema):
    pass

class EntidadBase(ABC):
    def __init__(self, codigo):
        self._codigo = codigo

    @property
    def codigo(self):
        return self._codigo

    @abstractmethod
    def describir(self):
        pass

    @abstractmethod
    def validar(self):
        pass

    def __str__(self):
        return self.describir()

class Cliente(EntidadBase):
    def __init__(self, codigo, nombre, correo, telefono):
        super().__init__(codigo)
        self.nombre   = nombre
        self.correo   = correo
        self.telefono = telefono
        self._reservas = []

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ErrorCliente(f"Nombre '{valor}' invalido. Minimo 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not re.match(patron, str(valor)):
            raise ErrorCliente(f"Correo '{valor}' invalido.")
        self._correo = valor

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if not str(valor).isdigit() or len(str(valor)) < 7:
            raise ErrorCliente(f"Telefono '{valor}' invalido. Solo digitos minimo 7.")
        self._telefono = str(valor)

    def agregar_reserva(self, reserva):
        self._reservas.append(reserva)

    def mis_reservas(self):
        return self._reservas

    def validar(self):
        return bool(self._nombre and self._correo and self._telefono)

    def describir(self):
        return f"[{self._codigo}] {self._nombre} | {self._correo} | Tel: {self._telefono}"

class Servicio(EntidadBase, ABC):
    def __init__(self, codigo, nombre, disponible=True):
        super().__init__(codigo)
        self._nombre     = nombre
        self._disponible = disponible

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        self._disponible = bool(valor)

    @abstractmethod
    def calcular_costo(self, horas, **kwargs):
        pass

    @abstractmethod
    def validar_horas(self, horas):
        pass

    def validar(self):
        return self._disponible

    def describir(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return f"[{self._codigo}] {self._nombre} | {estado}"

class ReservaSala(Servicio):
    TARIFA_HORA = 50000
    MAX_HORAS   = 12

    def __init__(self, codigo, nombre, capacidad, disponible=True):
        super().__init__(codigo, nombre, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ErrorServicio(f"Capacidad invalida ({capacidad}).")
        self._capacidad = capacidad

    def validar_horas(self, horas):
        if horas <= 0:
            raise ErrorServicio("Las horas deben ser positivas.")
        if horas > self.MAX_HORAS:
            raise ErrorServicio(f"Maximo {self.MAX_HORAS} horas para sala.")

    def calcular_costo(self, horas, descuento=0.0, impuesto=0.19, **kwargs):
        self.validar_horas(horas)
        if not (0.0 <= descuento <= 1.0):
            raise ErrorCosto("Descuento fuera de rango.")
        subtotal = self.TARIFA_HORA * horas * (1 - descuento)
        return round(subtotal * (1 + impuesto), 2)

    def describir(self):
        return f"{super().describir()} | Cap: {self._capacidad} personas | ${self.TARIFA_HORA:,}/hr"

class AlquilerEquipo(Servicio):
    TARIFA_HORA = 30000
    MAX_HORAS   = 48

    def __init__(self, codigo, nombre, tipo, disponible=True):
        super().__init__(codigo, nombre, disponible)
        self._tipo = str(tipo).strip()

    def validar_horas(self, horas):
        if horas <= 0:
            raise ErrorServicio("Las horas deben ser positivas.")
        if horas > self.MAX_HORAS:
            raise ErrorServicio(f"Maximo {self.MAX_HORAS} horas para equipo.")

    def calcular_costo(self, horas, descuento=0.0, impuesto=0.19, **kwargs):
        self.validar_horas(horas)
        if not (0.0 <= descuento <= 1.0):
            raise ErrorCosto("Descuento fuera de rango.")
        subtotal = self.TARIFA_HORA * horas * (1 - descuento)
        return round(subtotal * (1 + impuesto), 2)

    def describir(self):
        return f"{super().describir()} | Tipo: {self._tipo} | ${self.TARIFA_HORA:,}/hr"

class AsesoriaEspecializada(Servicio):
    TARIFA_HORA   = 80000
    MAX_HORAS     = 8
    CARGO_INFORME = 50000

    def __init__(self, codigo, area, asesor, disponible=True):
        super().__init__(codigo, area, disponible)
        self._asesor = str(asesor).strip()

    def validar_horas(self, horas):
        if horas <= 0:
            raise ErrorServicio("Las horas deben ser positivas.")
        if horas > self.MAX_HORAS:
            raise ErrorServicio(f"Maximo {self.MAX_HORAS} horas para asesoria.")

    def calcular_costo(self, horas, descuento=0.0, impuesto=0.19, con_informe=False, **kwargs):
        self.validar_horas(horas)
        if not (0.0 <= descuento <= 1.0):
            raise ErrorCosto("Descuento fuera de rango.")
        subtotal = self.TARIFA_HORA * horas
        if con_informe:
            subtotal += self.CARGO_INFORME
        subtotal *= (1 - descuento)
        return round(subtotal * (1 + impuesto), 2)

    def describir(self):
        return f"{super().describir()} | Asesor: {self._asesor} | ${self.TARIFA_HORA:,}/hr"

class Reserva:
    def __init__(self, codigo, cliente, servicio, horas, **kwargs):
        if not isinstance(cliente, Cliente) or not cliente.validar():
            raise ErrorReserva("El cliente no es valido.")
        if not isinstance(servicio, Servicio):
            raise ErrorReserva("El servicio no es valido.")
        if not servicio.disponible:
            raise ErrorReserva(f"El servicio '{servicio.nombre}' no esta disponible.")
        self._codigo   = codigo
        self._cliente  = cliente
        self._servicio = servicio
        self._horas    = horas
        self._kwargs   = kwargs
        self._estado   = "PENDIENTE"
        self._costo    = 0.0
        self._fecha    = datetime.datetime.now()

    @property
    def codigo(self):
        return self._codigo

    @property
    def estado(self):
        return self._estado

    @property
    def costo(self):
        return self._costo

    def confirmar(self):
        try:
            if self._estado != "PENDIENTE":
                raise ErrorReserva(f"Reserva {self._codigo} no se puede confirmar (estado: '{self._estado}').")
            self._costo  = self._servicio.calcular_costo(self._horas, **self._kwargs)
            self._estado = "CONFIRMADA"
            self._cliente.agregar_reserva(self)
            log("INFO", f"Reserva {self._codigo} CONFIRMADA | {self._cliente.nombre} | {self._servicio.nombre} | {self._horas}h | ${self._costo:,.0f}")
        except (ErrorServicio, ErrorCosto) as e:
            raise ErrorReserva(f"No se pudo confirmar {self._codigo}: {e}") from e

    def cancelar(self):
        try:
            if self._estado not in ("PENDIENTE", "CONFIRMADA"):
                raise ErrorReserva(f"Reserva {self._codigo} no se puede cancelar (estado: '{self._estado}').")
            self._estado = "CANCELADA"
            log("AVISO", f"Reserva {self._codigo} CANCELADA.")
        except ErrorReserva as e:
            log("ERROR", str(e))
            raise

    def procesar(self):
        try:
            if self._estado != "CONFIRMADA":
                raise ErrorReserva(f"Reserva {self._codigo} no se puede procesar (estado: '{self._estado}').")
            self._estado = "PROCESADA"
            log("INFO", f"Reserva {self._codigo} PROCESADA exitosamente.")
        except ErrorReserva as e:
            log("ERROR", str(e))
            raise
        finally:
            logging.debug(f"Procesamiento finalizado: {self._codigo}")

    def __str__(self):
        return (f"[{self._codigo}] {self._estado:10} | "
                f"{self._cliente.nombre:22} | {self._servicio.nombre:25} | "
                f"{self._horas}h | ${self._costo:>10,.0f} | "
                f"{self._fecha.strftime('%Y-%m-%d %H:%M')}")

class GestorSoftwareFJ:

    CLIENTES_BASE = [
        ("J1",  "Jesica Ibanez",    "jesica.ibanez@unad.edu.co",   "3001234567"),
        ("J2",  "Carlos Mendoza",   "carlos.mendoza@gmail.com",     "3012345678"),
        ("J3",  "Laura Rios",       "laura.rios@empresa.co",        "3023456789"),
        ("J4",  "Andres Castillo",  "andres.castillo@hotmail.com",  "3034567890"),
        ("J5",  "Maria Fernandez",  "maria.fernandez@unad.edu.co",  "3045678901"),
        ("J6",  "Luis Herrera",     "luis.herrera@gmail.com",       "3056789012"),
        ("J7",  "Valentina Cruz",   "valentina.cruz@empresa.co",    "3067890123"),
        ("J8",  "Diego Morales",    "diego.morales@gmail.com",      "3078901234"),
        ("J9",  "Sofia Vargas",     "sofia.vargas@hotmail.com",     "3089012345"),
        ("J10", "Camilo Torres",    "camilo.torres@unad.edu.co",    "3090123456"),
    ]

    SERVICIOS_BASE = [
        ("sala",     "S1",  "Sala Innovacion",       20),
        ("sala",     "S2",  "Sala Conferencias",     50),
        ("sala",     "S3",  "Sala Coworking",        10),
        ("equipo",   "S4",  "Laptop Dell XPS",       "Computador"),
        ("equipo",   "S5",  "Proyector Epson",       "Proyector"),
        ("equipo",   "S6",  "Camara Sony 4K",        "Camara"),
        ("equipo",   "S7",  "Tablet iPad Pro",       "Tablet"),
        ("asesoria", "S8",  "Ingenieria Software",   "Dr. Luis Herrera"),
        ("asesoria", "S9",  "Ciberseguridad",        "Mg. Ana Ruiz"),
        ("asesoria", "S10", "Bases de Datos",        "Dr. Pedro Soto"),
    ]

    RESERVAS_BASE = [
        ("R1",  "J1",  "S1",  3,  {"descuento": 0.10}),
        ("R2",  "J2",  "S8",  2,  {"con_informe": True}),
        ("R3",  "J3",  "S4",  5,  {"descuento": 0.05}),
        ("R4",  "J4",  "S2",  4,  {}),
        ("R5",  "J5",  "S9",  1,  {"con_informe": True}),
        ("R6",  "J6",  "S5",  6,  {"descuento": 0.15}),
        ("R7",  "J7",  "S10", 3,  {}),
        ("R8",  "J8",  "S3",  2,  {"descuento": 0.20}),
        ("R9",  "J9",  "S6",  8,  {}),
        ("R10", "J10", "S7",  4,  {"descuento": 0.10}),
    ]

    def __init__(self):
        self._clientes  = {}
        self._servicios = {}
        self._reservas  = {}
        self._contador_cliente = 11
        self._contador_reserva = 11
        self._cargar_clientes()
        self._cargar_servicios()
        self._cargar_reservas()

    def _generar_codigo_cliente(self):
        codigo = f"J{self._contador_cliente}"
        self._contador_cliente += 1
        return codigo

    def _generar_codigo_reserva(self):
        codigo = f"R{self._contador_reserva}"
        self._contador_reserva += 1
        return codigo

    def _cargar_clientes(self):
        for codigo, nombre, correo, tel in self.CLIENTES_BASE:
            try:
                cliente = Cliente(codigo, nombre, correo, tel)
                self._clientes[codigo] = cliente
            except ErrorCliente as e:
                log("ERROR", f"Error cargando cliente {codigo}: {e}")

    def _cargar_servicios(self):
        for fila in self.SERVICIOS_BASE:
            tipo   = fila[0]
            codigo = fila[1]
            nombre = fila[2]
            param  = fila[3]
            try:
                if tipo == "sala":
                    srv = ReservaSala(codigo, nombre, param)
                elif tipo == "equipo":
                    srv = AlquilerEquipo(codigo, nombre, param)
                else:
                    srv = AsesoriaEspecializada(codigo, nombre, param)
                self._servicios[codigo] = srv
            except ErrorServicio as e:
                log("ERROR", f"Error cargando servicio {codigo}: {e}")

    def _cargar_reservas(self):
        for codigo, cod_cli, cod_srv, horas, kwargs in self.RESERVAS_BASE:
            try:
                cliente  = self._clientes.get(cod_cli)
                servicio = self._servicios.get(cod_srv)
                if cliente and servicio:
                    reserva = Reserva(codigo, cliente, servicio, horas, **kwargs)
                    self._reservas[codigo] = reserva
            except ErrorReserva as e:
                log("ERROR", f"Error cargando reserva {codigo}: {e}")

    def registrar_cliente(self, nombre, correo, telefono):
        try:
            codigo  = self._generar_codigo_cliente()
            cliente = Cliente(codigo, nombre, correo, telefono)
            self._clientes[codigo] = cliente
            log("INFO", f"Cliente registrado: {cliente.describir()}")
            return cliente
        except ErrorCliente as e:
            log("ERROR", f"Registro fallido: {e}")
            return None

    def listar_clientes(self):
        return list(self._clientes.values())

    def listar_servicios(self):
        return list(self._servicios.values())

    def listar_reservas(self):
        return list(self._reservas.values())

    def crear_reserva(self, cod_cliente, cod_servicio, horas, **kwargs):
        try:
            cliente  = self._clientes.get(cod_cliente)
            servicio = self._servicios.get(cod_servicio)
            if cliente is None:
                raise ErrorReserva(f"No existe el cliente '{cod_cliente}'.")
            if servicio is None:
                raise ErrorReserva(f"No existe el servicio '{cod_servicio}'.")
            codigo  = self._generar_codigo_reserva()
            reserva = Reserva(codigo, cliente, servicio, horas, **kwargs)
            self._reservas[codigo] = reserva
            log("INFO", f"Reserva {codigo} creada | {cliente.nombre} -> {servicio.nombre} | {horas}h")
            return reserva
        except ErrorReserva as e:
            log("ERROR", f"Reserva fallida: {e}")
            return None

    def confirmar_reserva(self, codigo):
        reserva = self._reservas.get(codigo)
        if not reserva:
            log("ERROR", f"No existe la reserva '{codigo}'.")
            return
        try:
            reserva.confirmar()
        except ErrorReserva as e:
            log("ERROR", str(e))

    def cancelar_reserva(self, codigo):
        reserva = self._reservas.get(codigo)
        if not reserva:
            log("ERROR", f"No existe la reserva '{codigo}'.")
            return
        try:
            reserva.cancelar()
        except ErrorReserva as e:
            log("ERROR", str(e))

    def procesar_reserva(self, codigo):
        reserva = self._reservas.get(codigo)
        if not reserva:
            log("ERROR", f"No existe la reserva '{codigo}'.")
            return
        try:
            reserva.procesar()
        except ErrorReserva as e:
            log("ERROR", str(e))


def separador():
    print("\n" + "-" * 60)

def pausar():
    input("\n  Presiona Enter para continuar...")

def menu_principal(gestor):
    while True:
        print("\n" + "=" * 60)
        print("          SISTEMA SOFTWARE FJ")
        print("=" * 60)
        print("  1.  Registrar nuevo cliente")
        print("  2.  Ver clientes registrados")
        print("  3.  Ver servicios disponibles")
        print("  4.  Crear una reserva")
        print("  5.  Ver todas las reservas")
        print("  6.  Confirmar una reserva")
        print("  7.  Cancelar una reserva")
        print("  8.  Procesar una reserva")
        print("  9.  Salir")
        print("-" * 60)
        opcion = input("  Elige una opcion (1-9): ").strip()

        if   opcion == "1": menu_registrar_cliente(gestor)
        elif opcion == "2": menu_ver_clientes(gestor)
        elif opcion == "3": menu_ver_servicios(gestor)
        elif opcion == "4": menu_crear_reserva(gestor)
        elif opcion == "5": menu_ver_reservas(gestor)
        elif opcion == "6": menu_confirmar_reserva(gestor)
        elif opcion == "7": menu_cancelar_reserva(gestor)
        elif opcion == "8": menu_procesar_reserva(gestor)
        elif opcion == "9":
            print("\n  Hasta luego!\n")
            break
        else:
            print("\n  Opcion no valida. Elige entre 1 y 9.")

def menu_registrar_cliente(gestor):
    separador()
    print("  REGISTRAR NUEVO CLIENTE")
    separador()
    nombre   = input("  Nombre completo  : ").strip()
    correo   = input("  Correo           : ").strip()
    telefono = input("  Telefono         : ").strip()
    cliente  = gestor.registrar_cliente(nombre, correo, telefono)
    if cliente:
        print(f"\n  Cliente registrado con codigo: {cliente.codigo}")
    pausar()

def menu_ver_clientes(gestor):
    separador()
    print("  CLIENTES REGISTRADOS")
    separador()
    clientes = gestor.listar_clientes()
    print(f"  {'COD':<6} {'NOMBRE':<22} {'CORREO':<32} {'TELEFONO'}")
    print("  " + "-" * 72)
    for c in clientes:
        partes = c.describir().split("|")
        cod_nom  = partes[0].strip()
        correo   = partes[1].strip() if len(partes) > 1 else ""
        telefono = partes[2].strip() if len(partes) > 2 else ""
        cod = cod_nom.replace("[","").replace("]","").split(" ")[0].strip()
        nom = " ".join(cod_nom.replace("[","").replace("]","").split(" ")[1:]).strip()
        nom = nom.split("]")[-1].strip()
        print(f"  {cod:<6} {nom:<22} {correo:<32} {telefono}")
    pausar()

def menu_ver_servicios(gestor):
    separador()
    print("  SERVICIOS DISPONIBLES")
    separador()
    print(f"  {'COD':<5} {'NOMBRE':<28} {'TIPO':<12} {'TARIFA':>12}  {'LIMITE'}")
    print("  " + "-" * 65)
    for s in gestor.listar_servicios():
        if isinstance(s, ReservaSala):
            tipo   = "Sala"
            tarifa = ReservaSala.TARIFA_HORA
            limite = "max 12h"
        elif isinstance(s, AlquilerEquipo):
            tipo   = "Equipo"
            tarifa = AlquilerEquipo.TARIFA_HORA
            limite = "max 48h"
        else:
            tipo   = "Asesoria"
            tarifa = AsesoriaEspecializada.TARIFA_HORA
            limite = "max  8h"
        print(f"  {s.codigo:<5} {s.nombre:<28} {tipo:<12} ${tarifa:>8,}/hr  {limite}")
    pausar()

def menu_crear_reserva(gestor):
    separador()
    print("  CREAR NUEVA RESERVA")
    separador()

    print("  CLIENTES:")
    print(f"  {'COD':<6} {'NOMBRE'}")
    print("  " + "-" * 30)
    for c in gestor.listar_clientes():
        partes  = c.describir().split("|")
        cod_nom = partes[0].strip()
        cod = cod_nom.replace("[","").replace("]","").split(" ")[0].strip()
        nom = " ".join(cod_nom.replace("[","").replace("]","").split(" ")[1:]).strip()
        nom = nom.split("]")[-1].strip()
        print(f"  {cod:<6} {nom}")

    cod_cliente = input("\n  Codigo del cliente (ej: J1) : ").strip().upper()

    separador()
    print("  SERVICIOS:")
    print(f"  {'COD':<5} {'NOMBRE':<28} {'TARIFA':>12}  {'LIMITE'}")
    print("  " + "-" * 52)
    for s in gestor.listar_servicios():
        if isinstance(s, ReservaSala):
            tarifa = ReservaSala.TARIFA_HORA
            limite = "max 12h"
        elif isinstance(s, AlquilerEquipo):
            tarifa = AlquilerEquipo.TARIFA_HORA
            limite = "max 48h"
        else:
            tarifa = AsesoriaEspecializada.TARIFA_HORA
            limite = "max  8h"
        print(f"  {s.codigo:<5} {s.nombre:<28} ${tarifa:>8,}/hr  {limite}")

    cod_servicio = input("\n  Codigo del servicio (ej: S1): ").strip().upper()

    try:
        horas = float(input("  Numero de horas             : ").strip())
    except ValueError:
        print("  [ERROR] Ingresa un numero valido.")
        pausar()
        return

    try:
        desc      = input("  Descuento en % (0 si no hay): ").strip()
        descuento = float(desc) / 100 if desc else 0.0
    except ValueError:
        descuento = 0.0

    con_informe = False
    if cod_servicio in ("S8", "S9", "S10"):
        resp = input("  Incluir informe escrito? (s/n): ").strip().lower()
        con_informe = resp == "s"

    reserva = gestor.crear_reserva(
        cod_cliente, cod_servicio, horas,
        descuento=descuento, con_informe=con_informe
    )

    if reserva:
        print(f"\n  Reserva creada con codigo: {reserva.codigo}")
        if input("  Confirmarla ahora? (s/n)  : ").strip().lower() == "s":
            gestor.confirmar_reserva(reserva.codigo)
    pausar()

def menu_ver_reservas(gestor):
    separador()
    print("  TODAS LAS RESERVAS")
    separador()
    reservas = gestor.listar_reservas()
    if not reservas:
        print("  No hay reservas.")
    else:
        print(f"  {'COD':<5} {'ESTADO':<11} {'CLIENTE':<22} {'SERVICIO':<25} {'H':>3} {'COSTO':>12}")
        print("  " + "-" * 82)
        for r in reservas:
            print(f"  {r}")
    pausar()

def seleccionar_reserva(gestor, accion):
    separador()
    print(f"  {accion.upper()} RESERVA")
    separador()
    reservas = gestor.listar_reservas()
    if not reservas:
        print("  No hay reservas.")
        pausar()
        return None
    for r in reservas:
        print(f"  {r}")
    return input(f"\n  Codigo de reserva a {accion} (ej: R1): ").strip().upper()

def menu_confirmar_reserva(gestor):
    codigo = seleccionar_reserva(gestor, "confirmar")
    if codigo:
        gestor.confirmar_reserva(codigo)
    pausar()

def menu_cancelar_reserva(gestor):
    codigo = seleccionar_reserva(gestor, "cancelar")
    if codigo:
        gestor.cancelar_reserva(codigo)
    pausar()

def menu_procesar_reserva(gestor):
    codigo = seleccionar_reserva(gestor, "procesar")
    if codigo:
        gestor.procesar_reserva(codigo)
    pausar()

if __name__ == "__main__":
    gestor = GestorSoftwareFJ()
    menu_principal(gestor)