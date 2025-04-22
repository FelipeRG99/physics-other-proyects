import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import time
import requests
import matplotlib.gridspec as gridspec
from datetime import datetime,timedelta
import re

########################################################################################################
#################################   SESSION             ################################################
########################################################################################################
class body:
    '''   
    CLASS: base class that defines the characteristics of a body

    PARAMS:
    Gmass : G*M (G gravitational force constant, M mass of the body) km**3/s**2
    velocity: np.array([vx,vy,vz]) km/s
    position : np.array([x,y,z]) km
    name='' : name of the body
    normalized=None : True if there is a unit normalization needed, for example to optimize the calculations
    '''

    def __init__(self,Gmass,velocity,position,name='',normalized=None):
        au= 149597870.700#km
        factor_day=3600*24
        factor_year=factor_day*365
        if normalized:
            factor_v=factor_day/au
            factor_d=1/au
            factor_gm=factor_day**2/au**3
        self.name=name
        self.Gmass=Gmass*factor_gm
        self.velocity=velocity*factor_v
        self.position=position*factor_d

class session():
    '''   
    CLASS: base class for the interaction of the N-bodies added to it
    '''

    def __init__(self):
        self.total_bodies=[]
        self.num_bodies=0

    def add_body(self,Gmass,velocity,position,name='',normalized=None):
        ''' 
        FUNCTION: create body(CLASS) and add it to the total_bodies list
        '''
        body_added=body(Gmass,velocity,position,name,normalized)
        if self.check_body_position(body_added):
            self.total_bodies.append(body_added)
            self.num_bodies+=1
    
    def check_body_position(self,newBody):
        ''' 
        FUNCTION: check that the body is not already added
        '''
        for bod in self.total_bodies:

            if (newBody.position==bod.position).all():

                print(f'The body {newBody.name} has the same position as {bod.name}')

                return False
            
        return True


    def info(self):
        ''' 
        FUNCTION: print the bodies added info
        '''
        for bod in self.total_bodies:
            print(bod.name,' mass',bod.Gmass,' p',bod.position,' v',bod.velocity)

    def create_inputs(self):
        ''' 
        FUNCTION: create inputs from the bodies data to the solve_ivp function
        '''
        p=[]
        v=[]
        m=[]
        for bod in self.total_bodies:
            p.append(bod.position)
            v.append(bod.velocity)
            m.append(bod.Gmass)
        return np.array(p+v).ravel(),m

    def n_bodies_calculation(self,t,inputs,Gmasses):
        ''' 
        FUNCTION: creates the funtion to calculate the N-bodies problem
        '''
        num_bod=self.num_bodies
        positions = inputs[:3*num_bod].reshape((num_bod, 3))  # get positions
        velocities = inputs[3*num_bod:].reshape((num_bod, 3))  # get velocities

        d_positions_dt = velocities  # derivative of position = Velocity
        d_velocities_dt = np.zeros_like(positions)  # Init the aceleration

        for i in range(num_bod): #from the i body calc. all the interactions with the other bodies
           
           for j in range(num_bod):
               
               if i != j:  # dont calc. of himself
                   
                   r_ij = positions[j] - positions[i]  # distance vector
                   norm_r_ij = np.linalg.norm(r_ij)  # norm
                   d_velocities_dt[i] += Gmasses[j] * r_ij / norm_r_ij**3  # Gravitation law       

        return np.concatenate((d_positions_dt.flatten(), d_velocities_dt.flatten())).ravel() 
        
    def calc(self,t_span,t_eval):
        ''' 
        FUNCTION: solves the Gravitation law for N-Bodies with solve_ivp

        PARAMS:
            t_span : time interval [t_ini,t_end]
            t_eval : np.linspace(t_ini,t_end, number of steps)

        RETRURN:
         solution: dict, relevant keys: t for the temporal data and y for the position and velocity data

            solution.y: np.array shape(3*2*N-Bodies,number of steps)

            The solutions have this form:
            np.array(
                [x1,x2,x3,...,xt],[y1,y2,y3,...,yt],[z1,z2,z3,...,zt], #planet 1
                [x1,x2,x3,...,xt],[y1,y2,y3,...,yt],[z1,z2,z3,...,zt], #planet 2
                                            ...
                [vx1,vx2,vx3,...,xt],[vy1,vy2,vy3,...,vyt],[vz1,vz2,vz3,...,vzt], #planet 1
                [vx1,vx2,vx3,...,xt],[vy1,vy2,vy3,...,vyt],[vz1,vz2,vz3,...,vzt], #planet 2
                )
        '''
        inputs,Gmasses=self.create_inputs()
        start=time.time()
        solution = solve_ivp(fun=self.n_bodies_calculation, t_span=t_span, y0=inputs, t_eval=t_eval, args=(Gmasses,), method='BDF')
        print('Calc time: ',round(time.time()-start,4))

        return solution
    
    def plot_solution(self,t_span,t_eval):
        ''' 
        FUNCTION: Calc. the solutuion and plot it
        '''
        solution=self.calc(t_span,t_eval)#calc. solution
        position_max=np.max(np.abs(solution.y[0:self.num_bodies*3]))#calc. the calculate the furthest distance
        colors = ['green', 'red', 'blue', 'yellow', 'orange', 'purple', 'pink', 'brown', 'black', 'white', 'gray', 'cyan',
                   'magenta', 'lime', 'teal', 'indigo', 'violet', 'gold', 'silver', 'beige']
        
        fig=plt.figure(figsize=(15,6))
        gs = gridspec.GridSpec(1, 2, width_ratios=[3, 2]) 
        
        ######### FIRST PLOT 3D #######################
        ax = fig.add_subplot(gs[0], projection='3d')
        for n_bod in range(self.num_bodies):

            #plot  the body orbit
            planet_plt, = ax.plot(solution.y[n_bod*3], solution.y[n_bod*3+1], solution.y[n_bod*3+2],colors[n_bod], label=self.total_bodies[n_bod].name, linewidth=1)
            #plot  the body last point/position
            planet_dot, = ax.plot([solution.y[n_bod*3][-1]], [solution.y[n_bod*3+1][-1]], [solution.y[n_bod*3+2][-1]], 'o', color=colors[n_bod], markersize=7)
        
        ax.set_title(f"The {self.num_bodies}-Body Problem : {t_span[-1]} days")
        ax.set_xlabel("x(AU)")
        ax.set_ylabel("y(AU)")
        ax.set_zlabel("z(AU)")
        ax.set_xlim([-position_max,position_max])
        ax.set_ylim([-position_max,position_max])
        ax.set_zlim([-position_max,position_max])
        plt.grid()
        plt.legend()

        ######### SECOND PLOT 2D #######################
        ax = fig.add_subplot(gs[1])
        for n_bod in range(self.num_bodies):
            
            #plot  the body orbit
            planet_plt, = ax.plot(solution.y[n_bod*3], solution.y[n_bod*3+1],colors[n_bod], label=self.total_bodies[n_bod].name, linewidth=1)
            #plot  the body last point/position
            planet_dot, = ax.plot([solution.y[n_bod*3][-1]], [solution.y[n_bod*3+1][-1]], 'o', color=colors[n_bod], markersize=7)

        ax.set_title(f"The {self.num_bodies}-Body Problem : {t_span[-1]} days")
        ax.set_xlabel("x(AU)")
        ax.set_ylabel("y(AU)")
        ax.set_xlim([-position_max,position_max])
        ax.set_ylim([-position_max,position_max])
        plt.grid()
        plt.legend()

        plt.show()

        return solution
########################################################################################################
#################################       API             ################################################
########################################################################################################
def apiCall(bodyId,date):
    '''   
    FUNCTION: Calls to the HORIZON API and gets data from the desired date

    PARAMS:
        bodyId: Id of the body
        date: start date (YYYY-MM-DD)
    
    RETURNS:
        List line by line of text
    '''

    date_formated = datetime.strptime(date, '%Y-%m-%d')
    next_day = date_formated + timedelta(days=1)

    params = {
        'format': 'text',          # text o json, in this api they are the same
        'EPHEM_TYPE': 'VECTORS',
        'COMMAND': bodyId,              # Body ID, MB returns list of IDs
        'CENTER': '@ssb',        # ssb = barycenter of the solar system
        'STEP_SIZE': '1d',         # time interval
        'START_TIME': date,  # Init date(YYYY-MM-DD)
        'STOP_TIME': next_day.strftime('%Y-%m-%d'),   # end date
        "VEC_TABLE": "2",        
        "VEC_LABELS": "NO" ,
    }

    # API URL
    url = 'https://ssd.jpl.nasa.gov/api/horizons.api'

    # get
    response = requests.get(url, params=params)

    # check
    if response.status_code == 200:
        print("OK")

    else:
        print(f"KO: {response.status_code}")
    
    return response.text.split('\n')[3:]

def isnumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def from_textResponse_to_json(data):
    ''' 
    FUNCTION: process the data from the Horizon API
    
    '''
    dict_data={}
    begin_position_data=False
    begin_column_data=False
    position_data=[]
    columns=[]
    dates=[]

    patron = r'\d{4}-[a-zA-Z]{3}-\d{2}'

    for i,dat in enumerate(data[:]):

        if 'Column meaning' in dat or "$$EOE" in dat:#end of relevant info
            break

        elif 'A.D.' in dat and begin_position_data:
            resultado = re.search(patron, dat).group()
            dates.append(resultado)

        elif "*" in dat:
            begin_column_data=False
            begin_position_data=False    

        elif dat.count('=')>0:#physical info
            '''   
            this info could be splited in these formats:
            (1)    Radius (IAU), km      = 1737.4           GM, km^3/s^2          = 4902.800066, --->['Radius (IAU), km','1737.4 GM, km^3/s^2','4902.800066']
            (2)    Apsidal period        = 3231.50 d,-->['Apsidal period','3231.50 d']        
            '''
            d_split=dat.split('=')
            d_split_middle=d_split[1].strip().split('  ')
            #first split= variable          second split(d_split_middle)=number+' '+variable
            dict_data[d_split[0].strip()]=float(d_split_middle[0].strip()) if isnumber(d_split_middle[0].strip()) else str(d_split_middle[0].strip())

            if  len(d_split)==3:
                #second split(d_split_middle)=number+' '+variable       third split=variable
                dict_data[d_split_middle[-1].strip()]=float(d_split[2].strip()) if isnumber(d_split[2].strip()) else str(d_split[2].strip())

        elif "$$SOE" in dat:#begin of position velocity data
            begin_column_data=False
            begin_position_data=True

        elif begin_position_data:
            position_data+=dat.split()

        elif "JDTDB" in dat:#begin of column data
            begin_column_data=True

        elif begin_column_data:#column data
            columns+=dat.split()

    dict_pos={}
    position_data =[float(pos) if isnumber(pos) else pos for pos in position_data]

    for i in range(len(dates)):
        dict_pos[dates[i]]=dict(zip(columns,position_data[i*len(columns):(i+1)*len(columns)]))

    dict_data['position']=dict_pos
    
    return dict_data

PLANETS_NAMES={'Sun':'10','Mercury':'199','Venus':'299','Earth':'399','Mars':'499','Jupiter':'599','Saturn':'699','Uranus':'799','Neptune':'899','Moon':'301'}
class bodyAPI:
    '''    
    FUNCTION: base CLASS to extract the body data from the API
    '''
    def __init__(self,
                 mass=0,
                 velocity=[0,0,0],
                 position=[0,0,0],
                 name='',
                 date=''):
        self.name=name
        self.mass=mass
        self.date=date

        self.x=position[0]
        self.y=position[1]
        self.z=position[2]            
        self.vx=velocity[0]
        self.vy=velocity[1]
        self.vz=velocity[2]

        self.position=np.array(position)
        self.velociy=np.array(velocity)
        
        if name in PLANETS_NAMES.keys():
            print(f'Gettin data from the API for {self.name}...')
            self.apiData()
    def apiData(self):
        data=apiCall(PLANETS_NAMES[self.name],self.date)
        data_json=from_textResponse_to_json(data)
        data_pos_vel=data_json['position'][list(data_json['position'].keys())[0]]
        #self.mass=mass
        #self.velocity=velocity
        #self.position=position
        self.x=data_pos_vel['X']
        self.y=data_pos_vel['Y']
        self.z=data_pos_vel['Z']        
        self.vx=data_pos_vel['VX']
        self.vy=data_pos_vel['VY']
        self.vz=data_pos_vel['VZ']
        try:
            self.gmfactor=data_json['GM, km^3/s^2']
        except:
            self.gmfactor=data_json['GM (km^3/s^2)']

        self.position=np.array([self.x,self.y,self.z])
        self.velociy=np.array([self.vx,self.vy,self.vz])     
        #self.mass=data_json['GM, km^3/s^2']
