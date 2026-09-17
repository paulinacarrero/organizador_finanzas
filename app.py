from datetime import date, timedelta

import pandas as pd
import streamlit as st


ARCHIVO_DATOS = "transacciones.csv"
ARCHIVO_PRESUPUESTOS = "presupuestos.csv"

categorias = [
    "Comidas",
    "Transporte",
    "Salud",
    "Ocio",
    "Hogar",
    "Ahorro",
    "Mascota",
    "Internet",
    "Gastos fijos",
    "Vehiculos",
    "Trabajo",
    "Otros",
]

def mostrar_titulos():
    st.title("Organizador de Finanzas Personal")
    st.write("lleva el control de tus gastos e ingresos de manera simple y visual")
    st.caption("Version 1.0")


def inicializar_estado():
    if "transacciones" not in st.session_state:
        st.session_state.transacciones = cargar_transacciones()
    if "presupuestos" not in st.session_state:
        st.session_state.presupuestos = cargar_presupuestos()


def guardar_transacciones():
    df = pd.DataFrame(st.session_state.transacciones)
    df.to_csv(ARCHIVO_DATOS, index=False)


def guardar_presupuestos():
    presupuestos = [
        {"categoria": categoria, "presupuesto": presupuesto}
        for categoria, presupuesto in st.session_state.presupuestos.items()
        if presupuesto > 0
    ]
    df = pd.DataFrame(presupuestos, columns=["categoria", "presupuesto"])
    df.to_csv(ARCHIVO_PRESUPUESTOS, index=False)


def normalizar_tipo(tipo):
    return str(tipo).strip().capitalize()


def convertir_monto(monto):
    monto_convertido = pd.to_numeric(monto, errors="coerce")
    if pd.isna(monto_convertido):
        return 0
    return float(monto_convertido)


def crear_transaccion(descripcion, monto, fecha, categoria, tipo):
    return {
        "descripcion": str(descripcion).strip(),
        "monto": convertir_monto(monto),
        "fecha": fecha,
        "categoria": str(categoria).strip(),
        "tipo": normalizar_tipo(tipo),
    }


def cargar_transacciones():
    try:
        df = pd.read_csv(ARCHIVO_DATOS)
    except Exception:
        return []

    transacciones = []
    for _, fila in df.iterrows():
        transacciones.append(
            crear_transaccion(
                fila["descripcion"],
                fila["monto"],
                date.fromisoformat(str(fila["fecha"])),
                fila["categoria"],
                fila["tipo"],
            )
        )

    return transacciones


def cargar_presupuestos():
    try:
        df = pd.read_csv(ARCHIVO_PRESUPUESTOS)
    except Exception:
        return {}

    presupuestos = {}
    for _, fila in df.iterrows():
        categoria = str(fila["categoria"]).strip()
        presupuesto = convertir_monto(fila["presupuesto"])
        if categoria and presupuesto > 0:
            presupuestos[categoria] = presupuesto
    return presupuestos


def formatear_pesos(valor):
    return f"${valor:,.0f}".replace(",", ".")


def mostrar_formulario():
    with st.form("Nueva_transaccion"):
        descripcion = st.text_input("Descripcion del gasto o ingreso", placeholder="Escribe la descripcion de la operacion")
        monto = st.number_input("Monto", step=1, min_value=0, format="%d")
        fecha = st.date_input("Fecha")
        categoria = st.selectbox("Categoria", categorias)
        tipo = st.radio("Tipo", ["Ingreso", "Gasto"], horizontal=True)
        enviado = st.form_submit_button("Enviar")

    if enviado:
        st.session_state.transacciones.append(crear_transaccion(descripcion, monto, fecha, categoria, tipo))
        st.success("Transaccion agregada con exito")


def importar_csv():
    with st.expander("importar desde csv", expanded=True):
        st.markdown(
            """
            Para importar movimientos:

            1. Crea un archivo en Excel, Google Sheets o Bloc de notas.
            2. Guarda el archivo con extension `.csv`.
            3. La primera fila debe tener estas columnas exactas:
               `descripcion,monto,fecha,categoria,tipo`
            4. La fecha debe estar en formato `AAAA-MM-DD`, por ejemplo `2026-05-01`.
            5. En `tipo` escribe solamente `Ingreso` o `Gasto`.

            Ejemplo:

            ```csv
            descripcion,monto,fecha,categoria,tipo
            Alquiler,320000,2026-05-01,Hogar,Gasto
            Sueldo,1000000,2026-05-02,Trabajo,Ingreso
            Comida,45000,2026-05-03,Comidas,Gasto
            ```
            """
        )
        archivo = st.file_uploader("subir archivo csv", type=["csv"])
        importar = st.button("importar transacciones")

        if importar:
            if archivo is None:
                st.warning("Primero sube un archivo CSV.")
                return

            try:
                df = pd.read_csv(archivo)
            except Exception:
                st.error("El archivo no es un CSV valido.")
                return

            columnas_esperadas = ["descripcion", "monto", "fecha", "categoria", "tipo"]
            columnas_faltantes = [columna for columna in columnas_esperadas if columna not in df.columns]

            if columnas_faltantes:
                st.error("El CSV debe tener estas columnas: descripcion, monto, fecha, categoria, tipo.")
                return

            transacciones_importadas = []
            for _, fila in df.iterrows():
                transacciones_importadas.append(
                    crear_transaccion(
                        fila["descripcion"],
                        fila["monto"],
                        date.fromisoformat(str(fila["fecha"])),
                        fila["categoria"],
                        fila["tipo"],
                    )
                )

            st.session_state.transacciones.extend(transacciones_importadas)
            st.success(f"Se importaron {len(transacciones_importadas)} transacciones.")


def obtener_categorias_disponibles():
    categorias_disponibles = categorias.copy()
    for transaccion in st.session_state.transacciones:
        categoria = transaccion["categoria"]
        if categoria not in categorias_disponibles:
            categorias_disponibles.append(categoria)
    return categorias_disponibles


def obtener_rango_fechas_rapido(opcion, fecha_minima, fecha_maxima):
    hoy = date.today()

    if opcion == "Este mes":
        desde = hoy.replace(day=1)
        hasta = hoy
    elif opcion == "Mes pasado":
        primer_dia_mes_actual = hoy.replace(day=1)
        ultimo_dia_mes_pasado = primer_dia_mes_actual - timedelta(days=1)
        desde = ultimo_dia_mes_pasado.replace(day=1)
        hasta = ultimo_dia_mes_pasado
    elif opcion == "Este ano":
        desde = hoy.replace(month=1, day=1)
        hasta = hoy
    else:
        desde = fecha_minima
        hasta = fecha_maxima

    return desde, hasta


def mostrar_filtros():
    fecha_desde = date.today()
    fecha_hasta = date.today()

    if st.session_state.transacciones:
        fechas = []
        for transaccion in st.session_state.transacciones:
            fechas.append(transaccion["fecha"])

        fecha_desde = min(fechas)
        fecha_hasta = max(fechas)

    st.subheader("Filtros")
    categorias_disponibles = obtener_categorias_disponibles()
    categorias_seleccionadas = st.multiselect("categorias", categorias_disponibles, default=categorias_disponibles)
    filtro_rapido = st.selectbox("rango de fechas", ["Todas", "Este mes", "Mes pasado", "Este ano", "Personalizado"])

    if filtro_rapido == "Personalizado":
        desde = st.date_input("desde", value=fecha_desde)
        hasta = st.date_input("hasta", value=fecha_hasta)
    else:
        desde, hasta = obtener_rango_fechas_rapido(filtro_rapido, fecha_desde, fecha_hasta)
        st.caption(f"Mostrando desde {desde} hasta {hasta}")

    return categorias_seleccionadas, desde, hasta


def mostrar_presupuestos():
    with st.expander("Presupuesto por categoria"):
        categorias_disponibles = obtener_categorias_disponibles()
        categoria = st.selectbox("categoria del presupuesto", categorias_disponibles)
        presupuesto_actual = st.session_state.presupuestos.get(categoria, 0)
        presupuesto = st.number_input(
            "presupuesto mensual",
            min_value=0,
            step=1000,
            value=int(presupuesto_actual),
            format="%d",
        )

        if st.button("Guardar presupuesto"):
            if presupuesto > 0:
                st.session_state.presupuestos[categoria] = float(presupuesto)
            else:
                st.session_state.presupuestos.pop(categoria, None)
            guardar_presupuestos()
            st.success("Presupuesto guardado.")


def filtrar_transacciones(transacciones, categorias_seleccionadas, desde, hasta):
    transacciones_filtradas = []

    for transaccion in transacciones:
        categoria_en_filtro = transaccion["categoria"] in categorias_seleccionadas
        fecha_en_rango = desde <= transaccion["fecha"] <= hasta

        if categoria_en_filtro and fecha_en_rango:
            transacciones_filtradas.append(transaccion)

    return transacciones_filtradas


def mostrar_transacciones(transacciones):
    st.subheader("transacciones registradas:")
    if transacciones:
        df = pd.DataFrame(transacciones)
        df.insert(0, "eliminar", False)

        st.caption("Edita los datos directamente en la tabla. Marca eliminar para borrar una fila.")
        df_editado = st.data_editor(
            df,
            num_rows="fixed",
            hide_index=True,
            column_config={
                "eliminar": st.column_config.CheckboxColumn("Eliminar"),
                "descripcion": st.column_config.TextColumn("Descripcion"),
                "monto": st.column_config.NumberColumn("Monto", min_value=0, step=1, format="%d"),
                "fecha": st.column_config.DateColumn("Fecha"),
                "categoria": st.column_config.SelectboxColumn("Categoria", options=obtener_categorias_disponibles()),
                "tipo": st.column_config.SelectboxColumn("Tipo", options=["Ingreso", "Gasto"]),
            },
        )

        if st.button("Guardar cambios de la tabla"):
            transacciones_a_eliminar = set()

            for posicion, fila in df_editado.iterrows():
                transaccion = transacciones[posicion]

                if fila["eliminar"]:
                    transacciones_a_eliminar.add(id(transaccion))
                    continue

                fecha = fila["fecha"]
                if isinstance(fecha, pd.Timestamp):
                    fecha = fecha.date()
                elif isinstance(fecha, str):
                    fecha = date.fromisoformat(fecha)

                transaccion.update(
                    crear_transaccion(
                        fila["descripcion"],
                        fila["monto"],
                        fecha,
                        fila["categoria"],
                        fila["tipo"],
                    )
                )

            st.session_state.transacciones = [
                transaccion
                for transaccion in st.session_state.transacciones
                if id(transaccion) not in transacciones_a_eliminar
            ]
            guardar_transacciones()
            st.success("Cambios guardados.")
            st.rerun()

        csv = pd.DataFrame(transacciones).to_csv(index=False).encode("utf-8")
        st.download_button(
            "Descargar transacciones",
            data=csv,
            file_name="mis_transacciones.csv",
            mime="text/csv",
        )
    else:
        st.info("No hay transacciones registradas.")


def calcular_totales(transacciones):
    total_ingresos = sum(t["monto"] for t in transacciones if t["tipo"] == "Ingreso")
    total_gastos = sum(t["monto"] for t in transacciones if t["tipo"] == "Gasto")
    balance = total_ingresos - total_gastos
    return total_ingresos, total_gastos, balance


def crear_resumen_mensual(transacciones):
    if not transacciones:
        return pd.DataFrame()

    df = pd.DataFrame(transacciones)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["mes"] = df["fecha"].dt.strftime("%Y-%m")

    resumen = df.pivot_table(
        index="mes",
        columns="tipo",
        values="monto",
        aggfunc="sum",
        fill_value=0,
    )

    if "Ingreso" not in resumen.columns:
        resumen["Ingreso"] = 0
    if "Gasto" not in resumen.columns:
        resumen["Gasto"] = 0

    resumen = resumen[["Ingreso", "Gasto"]]
    resumen["Balance"] = resumen["Ingreso"] - resumen["Gasto"]
    return resumen.sort_index()


def mostrar_alertas(transacciones, total_ingresos, total_gastos, balance):
    if balance < 0:
        st.error("Alerta: tus gastos superan tus ingresos en el periodo filtrado.")
    elif total_gastos > total_ingresos * 0.8 and total_ingresos > 0:
        st.warning("Cuidado: tus gastos ya superan el 80% de tus ingresos.")
    else:
        st.success("Tus ingresos cubren los gastos del periodo filtrado.")

    gastos_por_categoria = sumar_por_categoria(transacciones, "Gasto")
    for categoria, presupuesto in st.session_state.presupuestos.items():
        gasto_categoria = gastos_por_categoria.get(categoria, 0)
        if gasto_categoria > presupuesto:
            exceso = gasto_categoria - presupuesto
            st.warning(
                f"Presupuesto superado en {categoria}: gastaste {formatear_pesos(gasto_categoria)} "
                f"de {formatear_pesos(presupuesto)}. Exceso: {formatear_pesos(exceso)}."
            )


def mostrar_resumen(transacciones):
    if not transacciones:
        st.info("No hay transacciones registradas para calcular el resumen.")
        return

    st.subheader("Resumen financiero")

    total_ingresos, total_gastos, balance = calcular_totales(transacciones)
    gastos = [t["monto"] for t in transacciones if t["tipo"] == "Gasto"]
    gasto_promedio = total_gastos / len(gastos) if gastos else 0

    st.metric("Total ingresos", formatear_pesos(total_ingresos))
    st.metric("Total gastos", formatear_pesos(total_gastos))
    st.metric("Balance", formatear_pesos(balance))
    st.metric("Gasto promedio", formatear_pesos(gasto_promedio))

    st.subheader("Alertas")
    mostrar_alertas(transacciones, total_ingresos, total_gastos, balance)

def sumar_por_categoria(transacciones, tipo):
    totales = {}

    for transaccion in transacciones:
        if transaccion["tipo"] != tipo:
            continue

        categoria = transaccion["categoria"]
        monto = transaccion["monto"]

        if categoria not in totales:
            totales[categoria] = 0
        totales[categoria] += monto

    return dict(sorted(totales.items(), key=lambda item: item[1], reverse=True))


def mostrar_analisis(transacciones):
    gastos_por_categoria = sumar_por_categoria(transacciones, "Gasto")
    ingresos_por_categoria = sumar_por_categoria(transacciones, "Ingreso")

    if not gastos_por_categoria and not ingresos_por_categoria:
        st.info("No hay ingresos ni gastos registrados para analizar.")
        return

    if gastos_por_categoria:
        st.subheader("Gastos por categoria")
        st.bar_chart(gastos_por_categoria)
    else:
        st.info("No hay gastos registrados para analizar.")

    if ingresos_por_categoria:
        st.subheader("Ingresos por categoria")
        st.bar_chart(ingresos_por_categoria)
    else:
        st.info("No hay ingresos registrados para analizar.")


def mostrar_pestanas(transacciones):
    tab_resumen, tab_movimiento, tab_analisis = st.tabs(["Resumen", "Movimiento", "Analisis"])

    with tab_resumen:
        mostrar_resumen(transacciones)

    with tab_movimiento:
        mostrar_transacciones(transacciones)

    with tab_analisis:
        mostrar_analisis(transacciones)


mostrar_titulos()
inicializar_estado()
with st.sidebar:
    mostrar_formulario()
    importar_csv()
    mostrar_presupuestos()
    categorias_filtradas, fecha_desde, fecha_hasta = mostrar_filtros()

transacciones_filtradas = filtrar_transacciones(
    st.session_state.transacciones,
    categorias_filtradas,
    fecha_desde,
    fecha_hasta,
)
mostrar_pestanas(transacciones_filtradas)
guardar_transacciones()
guardar_presupuestos()
