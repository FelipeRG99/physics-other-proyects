repo where i post small projects related to physics or other similar things when i am bored (very bored XD)

# Physics

# [Heat distributions 🔥](Heat_distributions) 

Simulation numerically and analitically of hte heat distributuion resolving the differential equations and more. Here you can find the resolution both numerically, for 1D and 2D, and analitically for a specific cases in 1D. Of course you can see the heat distribution in real time and download it.       
**Some results** 🎥

<div style="display: flex; justify-content: center; gap: 20px;">

  <div style="text-align: center;">
    <p><strong>1D Heat Distribution</strong></p>
    <img src="Heat_Equations\results\heat_distribution_1D.gif" width="400">
  </div>
  <div style="text-align: center;">
    <p><strong>1D Heat Distribution</strong></p>
    <img src="Heat_Equations\results\heat_distribution_2D.gif" width="400">
  </div>

</div>

# [N-body problem 🪐](N_body) 

This contains the resolution of the N-body problem using the BDF method to resolve the ODE (ordinary diferential equations) system, specificaly using the function from scipy.integrate, solve_ivp. Also uses the Horizon API from NASA to get real data to use in the simulation. The results achieved are great, for example, in a 4 body problem, Sun-Earth-Moon-Jupiter, in forecast of 350 days the errors are less than 3% compared to the real data.
**Some results** 🎥

<div style="display: flex; justify-content: center; gap: 20px;">

  <div style="text-align: center;">
    <p><strong>3-Body Example</strong></p>
      <img src="N_Body\ImgVideo\3body.gif" width="400">
  </div>
  
  <div style="text-align: center;">
    <p><strong>7-Body Example</strong></p>
      <img src="N_Body\ImgVideo\7body.gif" width="400">
  </div>

</div>