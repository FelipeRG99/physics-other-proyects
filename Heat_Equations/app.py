import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
import streamlit as st
import streamlit.components.v1 as components
from time import sleep
plt.rcParams['animation.ffmpeg_path'] = r'C:\ffmpeg\bin\ffmpeg.exe'

from Scripts.functions import heat_equation_numeric_1D
###############################################################################################################################
###############################################################################################################################
###############################################################################################################################
# Variables de sesion
if "session_sim_done" not in st.session_state:
    st.session_state.session_sim_done = False  # Guarda si la simulación está activa
if "session_u" not in st.session_state:
    st.session_state.session_u = np.array([])
if "session_inputs" not in st.session_state:
    st.session_state.session_inputs = []

################### INPUTS STREAMLIT ########################
st.title("Simulación Numerica de la Distribucion de temperatura 1D 🔥")
st.write("Simulación que muestra la evolución de la temperatura sobre una barra 1D donde se puede configurar temperatura inicial, y de los extremos de la barra")

# Configuración de controles
#fps = st.slider("FPS (Cuadros por segundo)", min_value=5, max_value=60, value=30, step=5)
###################  Función de actualización ################### 
def update_progress_bar(frame):
    global simulation_done
    progress_text.progress(int(100*(frame+1)/frames), f"Cargando... {frame+1}/{frames}")
    if frame+1==frames:
        simulation_done=True    
def update_by_frames_1d(frame):
    global u
    u=heat_equation_numeric_1D(u,dt,dx,a)
    pcm.set_array([u])
    T_mean=np.mean(u)
    axis.set_title(f"Distribución térmica - t: {frame * dt:.3f} s, T media: {round(T_mean,2)}Cº")
    update_progress_bar(frame)
    return pcm
def update_real_time_1d(frame):
    global u
    global u_time
    global t_frames
    for i in range(1,n_t+1):
        u=heat_equation_numeric_1D(u,dt,dx,a)
        u_time[frame,:]=u
        t_frames[frame]=frame * dt*n_t
    pcm.set_array([u])
    T_mean=np.mean(u)
    axis.set_title(f"Distribución térmica - t: {frame * dt*n_t:.3f} s, T media: {round(T_mean,2)}Cº")
    update_progress_bar(frame)
    return pcm
# Función para validar entradas numéricas
def get_number_input(label, column, default=0.0,range=[-np.inf,1000]):
    value = column.text_input(label, value=str(default))
    try:
        value= float(value)
        if value>=range[0] and value<=range[1]:
            return value
        else:
            st.warning(f"Por favor, introduce un número en el rango válido para {label}.")
            return default            
    except ValueError:
        st.warning(f"Por favor, introduce un número válido para {label}.")
        return default
########################### SIDEBAR ##################################
sideb=st.sidebar
sideb.title("Variables")
sideb.write('General')
col1= sideb.columns(1)[0]
update_mode =col1.selectbox("Modo de actualización", options=["Por cuadro", "Tiempo real"], index=1)
save_mode =col1.selectbox("Guardar resultado", options=["Si", "No"], index=1)
modo_map = {"Por cuadro": "frame","Tiempo real": "real","Si":"y","No":"n"}
# Obtener el valor real
kind_update = modo_map[update_mode]
save_inp = modo_map[save_mode]
simulation_done=False

if kind_update=='frame':
    update=update_by_frames_1d
elif kind_update=='real':
    update=update_real_time_1d
###################  Definir parámetros del problema ################### 
nodes = 80
################### Condiciones de contorno ################### 
sideb.write('Simulación 1D')
col1= sideb.columns(1)[0]
a= get_number_input("Coef. difusión(mm/s)", col1, default=110,range=[1,1100])  # coef. de difusion mm/s
length= get_number_input("Longitud (mm)", col1, default=50,range=[1,1000])  # length
time= get_number_input("Tiempo (s)", col1, default=2,range=[0.1,60])  # length
t0= get_number_input("Temperatura inicial(Cº)", col1, default=20,range=[0,1000])  # Condición de frontera (INICIAL)
tizq  = get_number_input("Temperatura borde izq.(Cº)", col1, default=30,range=[0,1000])  # Condición de frontera (borde izq)
tder = get_number_input("Temperatura borde der.(Cº)", col1, default=30,range=[0,1000])  # Condición de frontera (borde der)
st.session_state.session_inputs = [t0,tizq,tder]
u = np.zeros(nodes) + t0  
u[0]  =tizq
u[-1]  = tder
###################  Inicialización ################### 
dx = length / (nodes - 1)
dt = 0.5 * dx**2 /a #condicion de estabilidad
t_nodes = int(time / dt) + 1
####################  Configuración de la figura ################### 
fig, axis = plt.subplots()
pcm = axis.pcolormesh([u], cmap=plt.cm.jet, vmin=np.min(u), vmax=np.max(u))
plt.colorbar(pcm, ax=axis)
axis.set_xticklabels(labels=np.linspace(0,length,9,dtype=int))
axis.set_ylim([-2, 3])
axis.set_xlabel("L(mm)")
axis.set_ylabel("T(Cº)")
####################  Crear la animación ################### 
run_simulation = st.button("Iniciar Simulación")
fps=30
n_t=int(1/(fps*dt))+1
frames = int(time *fps) if kind_update=='real' else int(time/dt)#time*frames
u_time=np.zeros((frames,nodes))
t_frames=np.zeros(frames)
if run_simulation:
    #with st.status("Simulación en curso... 🔄", expanded=True) as status:
    progress_text = st.empty()
    with progress_text.container():
        ani = animation.FuncAnimation(fig, update,frames=frames, interval=10,repeat=False)
    # Guardar la animación como MP4 o GIF
    #ani.save("heat_distribution.gif", writer=writer)  # Para MP4
    if save_inp=='y':
        ani.save("results/heat_distribution_1D.mp4", writer="ffmpeg", fps=fps)
    else:
        components.html(ani.to_jshtml(fps=fps), height=1000)
        #plt.show()
if simulation_done:#remove progress
    sleep(0.1)
    progress_text.empty() 
###############################################################################################################################
###############################################################################################################################
###############################################################################################################################
st.title("Simulación Analitica de la Distribucion de temperatura 1D 🔥")
st.write("Simulación que muestra la evolución de la temperatura sobre una barra 1D donde se puede configurar temperatura inicial, y de los extremos de la barra")


# 📌 Botón para iniciar simulación
if run_simulation:
    st.session_state.session_sim_done = True  # Guarda el estado en session_state
    st.session_state.session_u=u_time
if st.session_state.session_sim_done:
    stslider = st.slider("Selecciona el valor de t:", min_value=0, max_value=frames-1, value=frames-1, step=1)
    fig, ax = plt.subplots()
    T_mean=np.mean(st.session_state.session_u[stslider])
    ax.plot(st.session_state.session_u[stslider])
    ax.set_xlabel("L(mm)")
    ax.set_ylabel("T(Cº)")
    ax.set_ylim([min(st.session_state.session_inputs),max(st.session_state.session_inputs)])
    ax.set_title(f"Distribución térmica - t: {stslider * dt*n_t:.3f} s, T media: {round(T_mean,2)}Cº")
    ax.legend()
    ax.grid()
    st.pyplot(fig)
# 📌 Generar datos
#x = np.linspace(0, 10, 400)  # Valores de x
#y = np.sin(t * x)  # Función y = sin(t * x)
#
## 📌 Crear la figura y actualizar el gráfico
#fig, ax = plt.subplots()
#ax.plot(x, y, label=f"sin({t} * x)")
#ax.set_xlabel("x")
#ax.set_ylabel("y")
#ax.legend()
#ax.grid()
#
## 📌 Mostrar en Streamlit
#st.pyplot(fig)