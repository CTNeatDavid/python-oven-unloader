#!/bin/bash

# Nombre del entorno virtual
VENV_DIR="venv"

# Verifica si el entorno virtual ya existe
if [ ! -d "$VENV_DIR" ]; then
    echo "Creando un entorno virtual en '$VENV_DIR'..."
    python3 -m venv $VENV_DIR
    echo "Entorno virtual creado."
fi

# Activar el entorno virtual
echo "Activando el entorno virtual..."
source $VENV_DIR/bin/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Dependencias instaladas."

# Crear un script para ejecutar el programa fácilmente
RUN_SCRIPT="run_program.sh"
cat <<EOL > $RUN_SCRIPT
#!/bin/bash
source $VENV_DIR/bin/activate
python3 python-oven-unloader.py
EOL

chmod +x $RUN_SCRIPT
echo "Script de ejecución creado: $RUN_SCRIPT"

echo "Configuración completa. Para ejecutar el programa, use ./$RUN_SCRIPT"
