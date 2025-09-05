#Brandon Salazar
#Daniel Paz

import csv
from datetime import datetime

# Estructuras de datos
usuarios = {}  # id_u: {'name': str, 'loans': int}
libros = {}  # id_l: {'title': str, 'loans': int}
titulo_a_id = {}  # title: id_l
historial = []  # [{'id_libro': str, 'titulo_libro': str, 'fecha_prestamo': str, 'fecha_devolucion': str}]
prestamos_actuales = {}  # id_l: {'id_u': str, 'name_u': str, 'prestamo': str}

def cargar_usuarios(nombre_archivo):
    try:
        inconsistencias = []
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            lector = csv.reader(f)
            next(lector)  # Saltar header
            vistos = set()
            for fila in lector:
                if len(fila) != 6:
                    continue
                id_u, nombre_u, _, _, _, _ = fila
                clave = (id_u, nombre_u)
                if clave in vistos:
                    continue
                vistos.add(clave)
                if id_u not in usuarios:
                    usuarios[id_u] = {'nombre': nombre_u, 'prestamos': 0}
                    print(f"id_usuario creado: {id_u}, nombre_usuario: {nombre_u}")
                else:
                    if usuarios[id_u]['nombre'] != nombre_u:
                        inconsistencias.append(f"Nombre de usuario inconsistente para id {id_u}: {usuarios[id_u]['nombre']} vs {nombre_u}")
        if inconsistencias:
            print("Inconsistencias encontradas en usuarios:")
            for inc in inconsistencias:
                print(inc)
    except FileNotFoundError:
        print("nombre del archivo no existe o no se encuentra")

def cargar_libros(nombre_archivo):
    try:
        inconsistencias = []
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            lector = csv.reader(f)
            next(lector)  # Saltar header
            vistos = set()
            for fila in lector:
                if len(fila) != 6:
                    continue
                _, _, id_l, titulo_l, _, _ = fila
                clave = (id_l, titulo_l)
                if clave in vistos:
                    continue
                vistos.add(clave)
                if id_l in libros:
                    if libros[id_l]['titulo'] != titulo_l:
                        inconsistencias.append(f"Título inconsistente para id_libro {id_l}: {libros[id_l]['titulo']} vs {titulo_l}")
                else:
                    if titulo_l in titulo_a_id:
                        if titulo_a_id[titulo_l] != id_l:
                            inconsistencias.append(f"ID inconsistente para título {titulo_l}: {titulo_a_id[titulo_l]} vs {id_l}")
                            continue
                    libros[id_l] = {'titulo': titulo_l, 'prestamos': 0}
                    titulo_a_id[titulo_l] = id_l
                    print(f"id_libro creado: {id_l}, titulo_libro: {titulo_l}")
        if inconsistencias:
            print("Inconsistencias encontradas en libros:")
            for inc in inconsistencias:
                print(inc)
    except FileNotFoundError:
        print("nombre del archivo no existe o no se encuentra")

def cargar_prestamos(nombre_archivo):
    try:
        acciones_fallidas = []
        registros = []
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            lector = csv.reader(f)
            next(lector)  # Saltar header
            for fila in lector:
                if len(fila) != 6:
                    continue
                id_u, nombre_u, id_l, titulo_l, prestamo_str, devolucion_str = fila
                try:
                    prestamo_dt = datetime.strptime(prestamo_str, '%Y-%m-%d')
                    devolucion_dt = None if not devolucion_str else datetime.strptime(devolucion_str, '%Y-%m-%d')
                except ValueError:
                    acciones_fallidas.append(f"Formato de fecha inválido en registro: {fila}")
                    continue
                registros.append({
                    'id_u': id_u,
                    'nombre_u': nombre_u,
                    'id_l': id_l,
                    'titulo_l': titulo_l,
                    'prestamo_dt': prestamo_dt,
                    'devolucion_dt': devolucion_dt,
                    'prestamo_str': prestamo_str,
                    'devolucion_str': devolucion_str
                })
        
        # Ordenar por fecha de préstamo
        registros.sort(key=lambda x: x['prestamo_dt'])
        
        for reg in registros:
            if reg['id_u'] not in usuarios:
                acciones_fallidas.append(f"Usuario {reg['id_u']} no existe para préstamo de {reg['id_l']} en {reg['prestamo_str']}")
                continue
            if reg['id_l'] not in libros:
                acciones_fallidas.append(f"Libro {reg['id_l']} no existe para préstamo en {reg['prestamo_str']}")
                continue
            if usuarios[reg['id_u']]['nombre'] != reg['nombre_u']:
                acciones_fallidas.append(f"Nombre de usuario inconsistente en préstamo para id {reg['id_u']}: {usuarios[reg['id_u']]['nombre']} vs {reg['nombre_u']}")
                continue
            if libros[reg['id_l']]['titulo'] != reg['titulo_l']:
                acciones_fallidas.append(f"Título de libro inconsistente en préstamo para id {reg['id_l']}: {libros[reg['id_l']]['titulo']} vs {reg['titulo_l']}")
                continue
            
            # Intentar préstamo
            if reg['id_l'] in prestamos_actuales:
                acciones_fallidas.append(f"Préstamo no realizado para libro {reg['id_l']} ({reg['titulo_l']}) a usuario {reg['id_u']} en {reg['prestamo_str']} porque se encuentra actualmente en préstamo")
                continue
            
            # Realizar préstamo
            usuarios[reg['id_u']]['prestamos'] += 1
            libros[reg['id_l']]['prestamos'] += 1
            prestamos_actuales[reg['id_l']] = {
                'id_u': reg['id_u'],
                'nombre_u': reg['nombre_u'],
                'prestamo': reg['prestamo_str']
            }
            
            revertir = False
            if reg['devolucion_dt']:
                if reg['devolucion_dt'] < reg['prestamo_dt']:
                    acciones_fallidas.append(f"Fecha de devolución anterior a préstamo para libro {reg['id_l']} en {reg['prestamo_str']}")
                    revertir = True
                else:
                    del prestamos_actuales[reg['id_l']]
            
            if revertir:
                # Revertir préstamo
                usuarios[reg['id_u']]['prestamos'] -= 1
                libros[reg['id_l']]['prestamos'] -= 1
                del prestamos_actuales[reg['id_l']]
            else:
                # Agregar a historial siempre, con devolucion_str que puede ser ''
                historial.append({
                    'id_libro': reg['id_l'],
                    'titulo_libro': reg['titulo_l'],
                    'fecha_prestamo': reg['prestamo_str'],
                    'fecha_devolucion': reg['devolucion_str']
                })
        
        if acciones_fallidas:
            print("Acciones fallidas en préstamos:")
            for fa in acciones_fallidas:
                print(fa)
    except FileNotFoundError:
        print("nombre del archivo no existe o no se encuentra")

def mostrar_historial():
    print("Historial de prestamos")
    print("|id_libro|titulo_libro|Fecha_prestamo|Fecha_Devolucion|")
    for h in historial:
        print(f"|{h['id_libro']}|{h['titulo_libro']}|{h['fecha_prestamo']}|{h['fecha_devolucion']}|")

def mostrar_usuarios():
    print("usuarios del sistema")
    print("|id_usuario|nombre_usuario|Prestamos totales|")
    for id_u in sorted(usuarios):
        data = usuarios[id_u]
        print(f"|{id_u}|{data['nombre']}|{data['prestamos']}|")

def mostrar_libros_prestados():
    print("|id_libro|nombre_libro|Cantidad de veces Prestado|")
    for id_l in sorted(libros):
        data = libros[id_l]
        if data['prestamos'] > 0:
            print(f"|{id_l}|{data['titulo']}|{data['prestamos']}|")

def mostrar_estadisticas():
    total_prestamos = sum(data['prestamos'] for data in libros.values())
    libros_max = []
    usuarios_max = []
    if libros:
        prestamos_max_libro = max(data['prestamos'] for data in libros.values())
        libros_max = [data['titulo'] for data in libros.values() if data['prestamos'] == prestamos_max_libro]
    if usuarios:
        prestamos_max_usuario = max(data['prestamos'] for data in usuarios.values())
        usuarios_max = [data['nombre'] for data in usuarios.values() if data['prestamos'] == prestamos_max_usuario]
    total_usuarios = len(usuarios)
    cadena_libros = ', '.join(libros_max)
    cadena_usuarios = ', '.join(usuarios_max)
    print("|Total de Prestamos|Libro(s) mas Prestado|Usuario(s) mas Activo|Total de usuarios|")
    print(f"|{total_prestamos}|{cadena_libros}|{cadena_usuarios}|{total_usuarios}|")

def mostrar_vencidos():
    print("|id_libro|nombre_libro|id_usuario|nombre_usuario|fecha_prestamo|Estado|")
    for id_l in sorted(prestamos_actuales):
        prestamo = prestamos_actuales[id_l]
        titulo = libros[id_l]['titulo']
        print(f"|{id_l}|{titulo}|{prestamo['id_u']}|{prestamo['nombre_u']}|{prestamo['prestamo']}|No devuelto aun|")

def exportar_html():
    total_prestamos = sum(data['prestamos'] for data in libros.values())
    libros_max = []
    usuarios_max = []
    if libros:
        prestamos_max_libro = max(data['prestamos'] for data in libros.values())
        libros_max = [data['titulo'] for data in libros.values() if data['prestamos'] == prestamos_max_libro]
    if usuarios:
        prestamos_max_usuario = max(data['prestamos'] for data in usuarios.values())
        usuarios_max = [data['nombre'] for data in usuarios.values() if data['prestamos'] == prestamos_max_usuario]
    total_usuarios = len(usuarios)
    cadena_libros = ', '.join(libros_max)
    cadena_usuarios = ', '.join(usuarios_max)
    
    with open('reportes.html', 'w', encoding='utf-8') as f:
        f.write('<html><head><title>Reportes Biblioteca</title></head><body>')
        
        f.write('<h1>Historial de Prestamos</h1>')
        f.write('<table border="1"><tr><th>id_libro</th><th>titulo_libro</th><th>Fecha_prestamo</th><th>Fecha_Devolucion</th></tr>')
        for h in historial:
            f.write(f'<tr><td>{h["id_libro"]}</td><td>{h["titulo_libro"]}</td><td>{h["fecha_prestamo"]}</td><td>{h["fecha_devolucion"]}</td></tr>')
        f.write('</table>')
        
        f.write('<h1>Usuarios del Sistema</h1>')
        f.write('<table border="1"><tr><th>id_usuario</th><th>nombre_usuario</th><th>Prestamos totales</th></tr>')
        for id_u in sorted(usuarios):
            data = usuarios[id_u]
            f.write(f'<tr><td>{id_u}</td><td>{data["nombre"]}</td><td>{data["prestamos"]}</td></tr>')
        f.write('</table>')
        
        f.write('<h1>Listado de Libros Prestados</h1>')
        f.write('<table border="1"><tr><th>id_libro</th><th>nombre_libro</th><th>Cantidad de veces Prestado</th></tr>')
        for id_l in sorted(libros):
            data = libros[id_l]
            if data['prestamos'] > 0:
                f.write(f'<tr><td>{id_l}</td><td>{data["titulo"]}</td><td>{data["prestamos"]}</td></tr>')
        f.write('</table>')
        
        f.write('<h1>Estadisticas de la Biblioteca</h1>')
        f.write('<table border="1"><tr><th>Total de Prestamos</th><th>Libro(s) mas Prestado</th><th>Usuario(s) mas Activo</th><th>Total de usuarios</th></tr>')
        f.write(f'<tr><td>{total_prestamos}</td><td>{cadena_libros}</td><td>{cadena_usuarios}</td><td>{total_usuarios}</td></tr>')
        f.write('</table>')
        
        f.write('<h1>Prestamos Vencidos</h1>')
        f.write('<table border="1"><tr><th>id_libro</th><th>nombre_libro</th><th>id_usuario</th><th>nombre_usuario</th><th>fecha_prestamo</th><th>Estado</th></tr>')
        for id_l in sorted(prestamos_actuales):
            prestamo = prestamos_actuales[id_l]
            titulo = libros[id_l]['titulo']
            f.write(f'<tr><td>{id_l}</td><td>{titulo}</td><td>{prestamo["id_u"]}</td><td>{prestamo["nombre_u"]}</td><td>{prestamo["prestamo"]}</td><td>No devuelto aun</td></tr>')
        f.write('</table>')
        
        f.write('</body></html>')
    print("Reportes exportados a reportes.html")

# Menú principal
while True:
    print("\n1. Cargar usuarios")
    print("2. Cargar libros")
    print("3. Cargar registros de prestamos")
    print("4. Mostrar historial prestamos")
    print("5. Mostrar listado de usuarios")
    print("6. Mostrar listado de libros prestados")
    print("7. Mostrar estadísticas de prestamos")
    print("8. Mostrar prestamos vencidos")
    print("9. Exportar todos los reportes a HTML")
    print("10. Salir")
    opcion = input("Seleccione una opción: ")
    
    if opcion == '1':
        nombre_archivo = input("Ingrese el nombre del archivo (.txt o .lfa): ")
        cargar_usuarios(nombre_archivo)
    elif opcion == '2':
        nombre_archivo = input("Ingrese el nombre del archivo (.txt o .lfa): ")
        cargar_libros(nombre_archivo)
    elif opcion == '3':
        nombre_archivo = input("Ingrese el nombre del archivo (.txt o .lfa): ")
        cargar_prestamos(nombre_archivo)
    elif opcion == '4':
        mostrar_historial()
    elif opcion == '5':
        mostrar_usuarios()
    elif opcion == '6':
        mostrar_libros_prestados()
    elif opcion == '7':
        mostrar_estadisticas()
    elif opcion == '8':
        mostrar_vencidos()
    elif opcion == '9':
        exportar_html()
    elif opcion == '10':
        print("Programa finalizado :p")
        break
    else:
        print("Opción inválida.")