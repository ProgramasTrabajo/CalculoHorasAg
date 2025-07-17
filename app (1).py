
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

# --- FUNCIONES BASE --- #
def convertir_a_str(hora):
    if isinstance(hora, time):
        return hora.strftime("%H:%M:%S")
    elif isinstance(hora, str):
        return hora
    return None

def calcular_horas(inicio_raw, fin_raw, refrigerio_inicio_raw=None, refrigerio_fin_raw=None):
    formato = "%H:%M:%S"
    inicio_str = convertir_a_str(inicio_raw)
    fin_str = convertir_a_str(fin_raw)
    refrigerio_inicio_str = convertir_a_str(refrigerio_inicio_raw)
    refrigerio_fin_str = convertir_a_str(refrigerio_fin_raw)

    if not inicio_str or not fin_str:
        return [0]*8

    try:
        inicio = datetime.strptime(inicio_str, formato)
        fin = datetime.strptime(fin_str, formato)
        if fin <= inicio:
            fin += timedelta(days=1)

        minutos_refrigerio = 0
        if refrigerio_inicio_str and refrigerio_fin_str:
            ri = datetime.strptime(refrigerio_inicio_str, formato).time()
            rf = datetime.strptime(refrigerio_fin_str, formato).time()
            if ri == time(13, 0) and rf == time(14, 0):
                minutos_refrigerio = 60
            elif ri == time(12, 0) and rf == time(12, 45):
                minutos_refrigerio = 45

        minutos_diurnos_total = 0
        minutos_nocturnos_total = 0

        actual = inicio
        while actual < fin:
            hora = actual.time()
            if time(6, 0) <= hora < time(22, 0):
                minutos_diurnos_total += 1
            else:
                minutos_nocturnos_total += 1
            actual += timedelta(minutes=1)

        total_minutos = minutos_diurnos_total + minutos_nocturnos_total

        if minutos_refrigerio > 0:
            if minutos_diurnos_total >= minutos_refrigerio:
                minutos_diurnos_total -= minutos_refrigerio
            else:
                restante = minutos_refrigerio - minutos_diurnos_total
                minutos_diurnos_total = 0
                minutos_nocturnos_total = max(0, minutos_nocturnos_total - restante)
            total_minutos -= minutos_refrigerio

        minutos_normales = min(total_minutos, 480)
        minutos_extras = max(0, total_minutos - 480)

        minutos_diurnos_normales = 0
        minutos_nocturnos_normales = 0
        actual = inicio
        minutos_asignados = 0
        while actual < fin and minutos_asignados < minutos_normales:
            hora = actual.time()
            if time(6, 0) <= hora < time(22, 0):
                minutos_diurnos_normales += 1
            else:
                minutos_nocturnos_normales += 1
            minutos_asignados += 1
            actual += timedelta(minutes=1)

        horas_diurnas = minutos_diurnos_normales / 60
        horas_nocturnas = minutos_nocturnos_normales / 60

        horas_extra_25 = min(minutos_extras, 120) / 60
        horas_extra_35 = max(minutos_extras - 120, 0) / 60

        horas_extra_25_nocturna = 0
        horas_extra_35_nocturna = 0

        if inicio.time() >= time(15, 0) and inicio.time() < time(20, 0):
            horas_extra_25_nocturna = horas_extra_25
            horas_extra_35_nocturna = round(horas_diurnas, 2) - horas_extra_25_nocturna
            horas_extra_25 = 0
            horas_extra_35 = horas_extra_35 - horas_extra_35_nocturna

        if inicio.time() >= time(20, 0) and inicio.time() < time(22, 0):
            horas_extra_25_nocturna = round(horas_diurnas, 2)
            horas_extra_35_nocturna = 0
            horas_extra_25 = horas_extra_25 - horas_extra_25_nocturna

        if fin.time() >= time(22, 0):
            horas_extra_35_nocturna = ((fin - datetime.combine(fin.date(), time(22, 0))).seconds / 60)/60
            horas_extra_35 = horas_extra_35-horas_extra_35_nocturna

        if fin.time() < time(6, 0):
            inicio = datetime.combine(fin.date(), time(22, 0)) - timedelta(days=1)  # 10:00 PM del día anterior
            diferencia = fin - inicio
            horas_extra_35_nocturna = (diferencia.seconds / 60) / 60
            horas_extra_35 = horas_extra_35-horas_extra_35_nocturna

        total_horas = (minutos_diurnos_total + minutos_nocturnos_total) / 60

        return max(round(horas_diurnas, 2), 0), max(round(horas_nocturnas, 2), 0),                max(round(minutos_normales / 60, 2), 0), max(round(horas_extra_25, 2), 0),                max(round(horas_extra_35, 2), 0), max(round(horas_extra_25_nocturna, 2), 0),                max(round(horas_extra_35_nocturna, 2), 0), max(round(total_horas, 2), 0)

    except Exception:
        return [0]*8

# --- FUNCIONALIDAD STREAMLIT --- #
st.title("Formulario de Ingreso de Datos del Trabajador")

# Formularios para ingresar datos
codigo = st.text_input("Código del Trabajador")
nombre = st.text_input("Nombre Completo")
fecha_nacimiento = st.date_input("Fecha de Nacimiento")
sexo = st.selectbox("Sexo", ["Masculino", "Femenino"])
estado_civil = st.selectbox("Estado Civil", ["Soltero", "Casado", "Divorciado"])
dni = st.text_input("DNI")
correo = st.text_input("Correo Electrónico")
telefono = st.text_input("Teléfono")
domicilio = st.text_input("Domicilio")
tipo_contrato = st.selectbox("Tipo de Contrato", ["Intermitente", "Completo"])
centro_costo = st.text_input("Centro de Costo")
cargo = st.text_input("Cargo")
regimen_laboral = st.text_input("Régimen Laboral")
fecha_ingreso = st.date_input("Fecha de Ingreso")
sueldo_base = st.number_input("Sueldo Base", min_value=0)
bonificacion_nocturna = st.number_input("Bonificación Nocturna", min_value=0)
horas_extras = st.number_input("Horas Extras", min_value=0)

# Botón para calcular
if st.button("Calcular Horas"):
    # Procesar la información para calcular horas
    horas = calcular_horas(
        fecha_ingreso, fecha_nacimiento,  # Ejemplo de parámetros de hora
    )
    
    # Mostrar resultados
    st.write("Horas diurnas: ", horas[0])
    st.write("Horas nocturnas: ", horas[1])
    st.write("Horas extras 25%: ", horas[3])
    st.write("Horas extras 35%: ", horas[4])
    st.write("Total horas: ", horas[7])
