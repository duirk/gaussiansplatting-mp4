import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
import gradio as gr

def extract_points_from_video(video_path):
    # Abrir el video
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    points = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Salir si no hay más frames

        # Procesar solo los frames que queremos (cada 17 frames)
        if frame_count % 17 == 0:
            # Convertir el frame a RGB
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, _ = img_rgb.shape
            
            # Extraer puntos (x, y, color)
            for y in range(height):
                for x in range(width):
                    points.append((x, y, img_rgb[y, x].tolist()))  # Agregar el color del píxel

        frame_count += 1

    cap.release()  # Liberar el video
    return points

def rotate_and_scale(points, angle, scale):
    transformed_points = []
    for point in points:
        # Calcular las coordenadas 3D (X,Y,Z) para cada punto en función del ángulo de rotación y escala.
        x = point[0] * np.cos(np.radians(angle)) - point[1] * np.sin(np.radians(angle))
        y = point[0] * np.sin(np.radians(angle)) + point[1] * np.cos(np.radians(angle))
        z = point[2][0] * scale  # Escalar el color en Z (usando solo el canal rojo como ejemplo)
        transformed_points.append((x, y, z))
    return transformed_points

def draw_3d_scene(points):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Extraer las coordenadas
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    zs = [point[2] for point in points]
    
    # Crear un scatter plot
    ax.scatter(xs, ys, zs, marker='o')  # Asegurarse de que las dimensiones coincidan
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()

def save_obj(points, filename="output.obj"):
    with open(filename, 'w') as f:
        for point in points:
            f.write(f"v {point[0]} {point[1]} {point[2]}\n")
    return filename

def interact_with_controls(video_path, angle, scale):
    points = extract_points_from_video(video_path)
    transformed_points = rotate_and_scale(points, angle, scale)
    draw_3d_scene(transformed_points)
    obj_file = save_obj(transformed_points)  # Guardar el archivo OBJ
    return f"Escena 3D actualizada. Archivo OBJ guardado como: {obj_file}"

# Crear una interfaz de usuario en Gradio
iface = gr.Interface(
    fn=interact_with_controls,
    inputs=[
        gr.inputs.Textbox(label="Ruta del video MP4"),
        gr.inputs.Slider(minimum=0, maximum=360, label="Ángulo de rotación"),
        gr.inputs.Slider(minimum=0.1, maximum=3.0, label="Escala")
    ],
    outputs="text"  # Puedes cambiar el tipo de salida según tus necesidades
)

iface.launch()
