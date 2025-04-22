import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from Scripts.functions import heat_equation_numeric_2D,boundary_conditions_2d
plt.rcParams['animation.ffmpeg_path'] = r'C:\ffmpeg\bin\ffmpeg.exe'


################### INPUTS ########################
save_inp=str(input("Quieres guardar la simulacion? (y/n)"))
kind_update=str(input("Quieres que la simulacion se actualice en tiempo real o por frame?(frame/real)"))
###################  Función de actualización ################### 
def update_by_frames_1d(frame):
    global u
    u=heat_equation_numeric_2D(u,dt,dx,dy,a)
    pcm.set_array(u)
    T_mean=np.mean(u)
    axis.set_title(f"Distribución térmica - t: {frame * dt:.3f} s, T media: {round(T_mean,2)}Cº")
    return pcm
def update_real_time_1d(frame):
    global u
    for i in range(1,n_t+1):
        u=heat_equation_numeric_2D(u,dt,dx,dy,a)
    pcm.set_array(u)
    T_mean=np.mean(u)
    axis.set_title(f"Distribución térmica - t: {frame * dt*n_t:.3f} s, T media: {round(T_mean,2)}Cº")
    return pcm
if kind_update=='frames':
    update=update_by_frames_1d
elif kind_update=='real':
    update=update_real_time_1d
###################  Definir parámetros del problema ################### 
a = 110
length = 50  # mm
time = 5  # seconds
nodes = 100
###################  Inicialización ################### 
dx = length / (nodes-1)
dy = length / (nodes-1)
dt = min(   dx**2 / (4 * a),     dy**2 / (4 * a))

t_nodes = int(time/dt) + 1
u = np.zeros((nodes,nodes)) + 20  # La placa inicia a 20°C

################### Condiciones de contorno ################### 
u=boundary_conditions_2d(u,nodes,temperature=100,kind='points')

####################  Configuración de la figura ################### 
fig, axis = plt.subplots()
pcm = axis.pcolormesh(u, cmap=plt.cm.jet, vmin=np.min(u), vmax=np.max(u))
plt.colorbar(pcm, ax=axis)
#####################  Crear la animación ################### 
fps=30
n_t=int(1/(fps*dt))+1
frames = int(time *fps)#time*frames
ani = animation.FuncAnimation(fig, update, frames=frames, interval=10,repeat=False)
if save_inp=='y':
    ani.save("results/heat_distribution_2D.mp4", writer="ffmpeg", fps=30)  # Para GIF
else:
    plt.show()












