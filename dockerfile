#Define una imagen base para Python
FROM python:3

#Instala la libreria del sistema para usar Tkinter
RUN apt-get update && apt-get install -y tk

#Establece el directorio de trabajo
WORKDIR /usr/src/app

#Copia el archivo de dependencias y luego lo instala
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

#Copia el resto de los archivos del proyecto
COPY . .

#comando para ejecutar tu aplicación
CMD [ "python", "main.py" ]