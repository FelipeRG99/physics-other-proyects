import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
import matplotlib.gridspec as gridspec

from Scripts.functions import apiCall,from_textResponse_to_json,bodyAPI,session
#################################################################################################
###################################         INPUTS      #########################################
#################################################################################################
filename='test'
PLANETS_NAMES={'Sun':'10','Mercury':'199','Venus':'299','Earth':'399','Moon':'301','Mars':'499','Jupiter':'599','Saturn':'699','Uranus':'799','Neptune':'899'}
N_BODY=int(input('How many bodies?'))
EXCLUDE_MERCURY=input('Do you want to exclude Mercury?y/n')
SAVE=input('Do you want to save the plot?y/n')
#################################################################################################
###################################         CALCULATE      ######################################
#################################################################################################
exclude_list=[]
if EXCLUDE_MERCURY=='y':
    exclude_list.append('Mercury')

#obtain physycal vlaues of the bodies calling HORIZON API
list_planets=[]
add_exc=0
for i,name in enumerate(list(PLANETS_NAMES.keys())):
    if i>=N_BODY+add_exc:
        break
    if name not in exclude_list:
        list_planets.append(bodyAPI(name=name,date='2024-02-06'))
    else:
        add_exc+=1

#add bodies to the system to calculate solutions
system=session()
for body in list_planets:
    system.add_body(body.gmfactor,body.velociy,body.position,body.name,normalized=True)

################################## CALC. ##########################################
t_fin=350
t_n_space=1001
t_span = (0, t_fin)
t_points = np.linspace(0, t_fin, t_n_space)
sol=system.calc(t_span,t_points)['y']
#################################################################################################
###################################             PLOT      ######################################
#################################################################################################
################### PLOT INPUTS ##########################
n_factor=int(t_n_space/t_fin)+1#factor to make frame~1 day
frames=t_n_space//n_factor

position_max=np.max(np.abs(sol[0:N_BODY*3]))#calc. the calculate the furthest distance
colors = ['yellow','green', 'red', 'blue',  'orange', 'purple', 'pink', 'brown', 'black', 'magenta', 'gray', 'cyan',
            'lime', 'teal', 'indigo', 'violet', 'gold', 'silver', 'beige']

#fig, ax = plt.subplots()
fig = plt.figure(figsize=(15, 6))
fig.suptitle(f"Solar System with {N_BODY}-body", fontsize=16)
gs = gridspec.GridSpec(1, 2, width_ratios=[3, 2]) 
fig.facecolor='whitesmoke'
fig.edgecolor='k'

#3d figure
ax3D = fig.add_subplot(gs[0], projection='3d')  
ax3D.set_xlabel("x(AU)")
ax3D.set_ylabel("y(AU)")
ax3D.set_xlim([-position_max,position_max])
ax3D.set_ylim([-position_max,position_max])
plt.grid(linestyle='--')

#2d figure
ax = fig.add_subplot(gs[1]) 
ax.set_xlabel("x(AU)")
#ax.set_ylabel("y(AU)")
ax.set_xlim([-position_max,position_max])
ax.set_ylim([-position_max,position_max])
plt.grid(linestyle='--')
################## CREATE POINTS/LINES ##########################
points2D=[]
lines2D=[]
points3D=[]
lines3D=[]
for n_bod in range(N_BODY):

    point, = ax.plot([], [], colors[n_bod],marker='o',label=list_planets[n_bod].name)  
    line, = ax.plot([], [], colors[n_bod],linestyle='-', lw=2)

    point3D, = ax3D.plot([], [], [], colors[n_bod],marker='o',label=list_planets[n_bod].name)  
    line3D, = ax3D.plot([], [], [], colors[n_bod],linestyle='-', lw=2)

    points2D.append(point)
    lines2D.append(line)

    points3D.append(point3D)
    lines3D.append(line3D)
ax.legend(bbox_to_anchor=(1.15, 1),fancybox=True, shadow=True)
################## GENERATE ANIMATION ##########################
def update(frame):

    fig.suptitle(f"Solar System with {N_BODY}-body : {round(t_fin*frame*n_factor/t_n_space,2)} days", fontsize=16)
    for n_bod in range(N_BODY):

        x, y,z = sol[n_bod*3, frame*n_factor], sol[n_bod*3+1, frame*n_factor], sol[n_bod*3+2, frame*n_factor]
        ######################### 2D ##########################
        points2D[n_bod].set_data([x], [y])#add the position in this frame to the point
        lines2D[n_bod].set_data(sol[n_bod*3, :frame*n_factor], sol[n_bod*3+1, :frame*n_factor])#add the trayectory in this frame to the line
        ######################### 2D ##########################
        points3D[n_bod].set_data([x], [y])#add the position in this frame to the point
        points3D[n_bod].set_3d_properties([z])
        lines3D[n_bod].set_data(sol[n_bod*3, :frame*n_factor], sol[n_bod*3+1, :frame*n_factor])#add the trayectory in this frame to the line
        lines3D[n_bod].set_3d_properties(sol[n_bod*3+2, :frame*n_factor])
################## SAVE/PLOT ##########################
ani = animation.FuncAnimation(fig, update, frames=frames, interval=50,blit=False,repeat=False)

if SAVE=='y':
    ani.save(f'{filename}.mp4', writer="ffmpeg")
else:
    plt.show()