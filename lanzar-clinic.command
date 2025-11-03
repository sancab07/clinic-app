#!/bin/bash

# 1. Carga conda (a veces está en otra ruta, ahorita te explico)
source ~/anaconda3/bin/activate base

# 2. Ve a tu carpeta de la app
cd /Users/santiagocabas/Desktop/clinic-app

# 3. Lanza streamlit
streamlit run app.py