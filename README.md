# Organizador de Finanzas Personal

Aplicación web hecha con **Streamlit** para llevar el control de tus ingresos y gastos de forma simple y visual: registra transacciones, define presupuestos por categoría y recibe alertas cuando te excedes.

## Funcionalidades

- **Registro de transacciones**: agrega ingresos o gastos con descripción, monto, fecha y categoría desde un formulario.
- **Importación desde CSV**: sube un archivo `.csv` con varias transacciones a la vez.
- **Presupuestos por categoría**: define un presupuesto mensual para cada categoría y recibe una alerta cuando lo superas.
- **Filtros**: filtra tus transacciones por categoría y por rango de fechas (este mes, mes pasado, este año, o un rango personalizado).
- **Tabla editable**: edita o elimina transacciones directamente en la tabla, y descarga tus datos como CSV.
- **Resumen financiero**: total de ingresos, total de gastos, balance y gasto promedio del periodo filtrado.
- **Alertas automáticas**: te avisa si tus gastos superan tus ingresos, si ya llegaste al 80% de tus ingresos en gastos, o si te pasaste de algún presupuesto.
- **Análisis visual**: gráficas de barras con gastos e ingresos por categoría.
- Los datos se guardan automáticamente en archivos CSV locales (`transacciones.csv` y `presupuestos.csv`), así que no se pierden al cerrar la app.

## Categorías disponibles

Comidas, Transporte, Salud, Ocio, Hogar, Ahorro, Mascota, Internet, Gastos fijos, Vehículos, Trabajo, Otros.

## Cómo correrla localmente

Este proyecto usa [uv](https://docs.astral.sh/uv/) como gestor de dependencias:

```bash
git clone https://github.com/paulinacarrero/organizador_finanzas.git
cd organizador_finanzas
uv sync
uv run streamlit run app.py
```

Si prefieres usar `pip` en lugar de `uv`:

```bash
pip install streamlit pandas
streamlit run app.py
```

## Formato para importar transacciones desde CSV

El archivo debe tener exactamente estas columnas, con la fecha en formato `AAAA-MM-DD` y el tipo como `Ingreso` o `Gasto`:

```csv
descripcion,monto,fecha,categoria,tipo
Alquiler,320000,2026-05-01,Hogar,Gasto
Sueldo,1000000,2026-05-02,Trabajo,Ingreso
Comida,45000,2026-05-03,Comidas,Gasto
```

## Tecnologías

- Python
- [Streamlit](https://streamlit.io/)
- [pandas](https://pandas.pydata.org/)
- [uv](https://docs.astral.sh/uv/)

## Autora

Paulina Carrero
