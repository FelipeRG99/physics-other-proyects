import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
plt.rcParams['animation.ffmpeg_path'] = r'C:\ffmpeg\bin\ffmpeg.exe'

from Scripts.functions import heat_equation_numeric_1D
################### INPUTS ########################
save_inp=str(input("Quieres guardar la simulacion? (y/n)"))
kind_update=str(input("Quieres que la simulacion se actualice en tiempo real o por frame?(frame/real)"))
###################  Función de actualización ################### 
def update_by_frames_1d(frame):
    global u
    u=heat_equation_numeric_1D(u,dt,dx,a)
    pcm.set_array([u])
    T_mean=np.mean(u)
    axis.set_title(f"Distribución térmica - t: {frame * dt:.3f} s, T media: {round(T_mean,2)}Cº")
    return pcm
def update_real_time_1d(frame):
    global u
    for i in range(1,n_t+1):
        u=heat_equation_numeric_1D(u,dt,dx,a)
    pcm.set_array([u])
    T_mean=np.mean(u)
    axis.set_title(f"Distribución térmica - t: {frame * dt*n_t:.3f} s, T media: {round(T_mean,2)}Cº")
    return pcm
if kind_update=='frame':
    update=update_by_frames_1d
elif kind_update=='real':
    update=update_real_time_1d
###################  Definir parámetros del problema ################### 
a = 110
length = 50  # mm
time = 5  # seconds
nodes = 80

###################  Inicialización ################### 
dx = length / (nodes - 1)
dt = 0.5 * dx**2 /a #condicion de estabilidad
t_nodes = int(time / dt) + 1
################### Condiciones de contorno ################### 
u = np.zeros(nodes) + 20  # La placa inicia a 20°C
u[0] = 100  # Condición de frontera (borde izq)
u[-1] = 20  # Condición de frontera (borde der)

####################  Configuración de la figura ################### 
fig, axis = plt.subplots()
pcm = axis.pcolormesh([u], cmap=plt.cm.jet, vmin=np.min(u), vmax=np.max(u))
plt.colorbar(pcm, ax=axis)
axis.set_ylim([-2, 3])
####################  Crear la animación ################### 
fps=30
n_t=int(1/(fps*dt))+1
frames = int(time *fps) if kind_update=='real' else int(time/dt)#time*frames
ani = animation.FuncAnimation(fig, update,frames=frames, interval=10,repeat=False)
# Guardar la animación como MP4 o GIF
#ani.save("heat_distribution.gif", writer=writer)  # Para MP4
if save_inp=='y':
    ani.save("results/heat_distribution_1D.mp4", writer="ffmpeg", fps=30)  # Para GIF
else:
    plt.show()
