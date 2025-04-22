import numpy as np

def heat_equation_numeric_1D(u,dt,dx,a):
    w=u.copy()
    d_ux = (w[:-2] - 2 * w[1:-1] + w[2:]) / dx**2
    u[1:-1] = w[1:-1] + dt * a *d_ux

    return u
def heat_equation_numeric_2D(u,dt,dx,dy,a):
    w = u.copy()

    # Optimización: Sin bucles
    dd_ux = (w[:-2, 1:-1] - 2 * w[1:-1, 1:-1] + w[2:, 1:-1]) / dx**2
    dd_uy = (w[1:-1, :-2] - 2 * w[1:-1, 1:-1] + w[1:-1, 2:]) / dy**2

    u[1:-1, 1:-1] = w[1:-1, 1:-1] + dt * a * (dd_ux + dd_uy)

    return u
def boundary_conditions_2d(u,nodes,temperature=100,kind=''):
    #extremos de la placa con temperatura
    if kind=='square':
        u[0, :] = temperature
        u[-1, :] = temperature

        u[:, 0] = temperature
        u[:, -1] = temperature
    # punto con temperatura
    elif kind=='points':
        x_ini=int(nodes/2)
        x_radius=25
        u[0,x_ini-x_radius:x_ini+x_radius ]=temperature
        u[-1,x_ini-x_radius:x_ini+x_radius ]=temperature
    return u
def analytical_equation_pro(x, t, T0, T1, T2, L, n, a):
    # Creating the arrays
    u = np.zeros((len(t), len(x), len(n)))
    t = t.reshape((len(t), 1, 1))
    x = x.reshape((1, len(x), 1))
    n = n.reshape((1, 1, len(n)))
    # Define ue (reshape x because this operation will be done after summing over n)
    ue = T1 + (T2 - T1) * x.reshape((1, x.shape[1])) / L
    # Previously they were numbers, now they must be arrays depending on n
    f_term_one = np.where(n % 2 == 0, 0, 2)  # 1 - (-1)^{n} → if even = 0, if odd = 2
    f_term_two = np.where(n % 2 == 0, 1, -1)  # (-1)^{n} → if even = 1, if odd = -1
    T = (2.0 / (n * np.pi)) * ((T0 - T1) * f_term_one + (T2 - T1) * f_term_two) * np.exp(-a * (n * np.pi / L) ** 2 * t) * np.sin(n * np.pi * x / L)
    #          (1,1,n)                    (1,1,n)                                     (t,1,n)                                (1,x,n)
    # ue plus the sum over all Fourier components n
    u = ue + np.sum(T, axis=-1)
    return u