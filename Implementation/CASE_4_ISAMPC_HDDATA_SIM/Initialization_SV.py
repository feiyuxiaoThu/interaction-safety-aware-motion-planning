import numpy as np
from numpy.linalg import matrix_power

class Initialization_SV( ): # Initialize SV
    def __init__(self, Params):
        
        self.Ts       = Params['Ts']
        self.N        = Params['N']
        self.Models   = Params['Models']
        self.N_Lane   = Params['N_Lane']
        self.N_M      = Params['N_M']
        self.N_Car    = Params['N_Car']
        self.L_Bound  = Params['L_Bound']
        self.L_Center = Params['L_Center']
        self.DSV      = Params['DSV']
        self.H        = Params['H']
        
    def Initialize_MU_M_P(self, X_State): # initialized all information for each SV
        N_M = self.N_M
        N = self.N
        N_Car = self.N_Car
        H = self.H
        Models = self.Models
        L_Center = self.L_Center
        
        X_State_0 = X_State[0] 
        MU_0 = list( ) 
        M_0 = list( )   
        X_Hat_0 = list( ) 
        Y_0 = list( ) 
        X_Pre_0 = list( )
        X_Po_All_0 = list( ) 
        X_Var_0 = list( ) 
        Y_Var_0 = list( ) 
        p_m = np.diag(np.array([1, 1, 1, 1, 1, 1]))*1e-6
        p_0 = list( ) 
        P_0 = list( ) 
        REF_Speed_0 = list( ) 
        REF_Lane_0 = list( ) 
        REF_Speed_All_0 = list( ) 
        
        for i in range(N_Car):
            if (i == 0) or (i == 4): 
                mu_0 = np.array([0.51, 0.49, 0, 0.0, 0, 0, 0])
                m_0 = np.argmax(mu_0)
                MU_0.append(mu_0)
                M_0.append(m_0)
                x_hat_m = X_State_0[i] 
                x_hat_0 = [x_hat_m, x_hat_m, None, None, None, None, None] 
                p_0 = [p_m, p_m, None, None, None, None, None] 
                X_Hat_0.append(x_hat_0) 
                P_0.append(p_0) 
                ref_all_0 = [x_hat_m[1], x_hat_m[1], None, None, None, None, None]
                REF_Speed_0.append(ref_all_0[m_0])
                REF_Lane_0.append(L_Center[0])
                REF_Speed_All_0.append(ref_all_0)
            elif (i == 1) or (i == 2) or (i == 3) or (i == 6): 
                mu_0 = np.array([0, 0, 0.33, 0.34, 0.33, 0, 0])
                m_0 = np.argmax(mu_0)
                MU_0.append(mu_0)
                M_0.append(m_0)
                x_hat_m = X_State_0[i] 
                x_hat_0 = [ None, None, x_hat_m, x_hat_m, x_hat_m, None, None] 
                p_0 = [None, None, p_m, p_m, p_m, None, None]
                X_Hat_0.append(x_hat_0) 
                P_0.append(p_0) 
                ref_all_0 = [None, None, x_hat_m[1], x_hat_m[1], x_hat_m[1], None, None] 
                REF_Speed_0.append(ref_all_0[m_0])
                REF_Lane_0.append(L_Center[1])
                REF_Speed_All_0.append(ref_all_0)
            elif (i == 5): 
                mu_0 = np.array([0, 0, 0, 0, 0, 0.49, 0.51])
                m_0 = np.argmax(mu_0)
                MU_0.append(mu_0)
                M_0.append(m_0)
                x_hat_m = X_State_0[i] 
                x_hat_0 = [None, None, None, None, None, x_hat_m, x_hat_m] 
                p_0 = [None, None, None, None, None, p_m, p_m]
                X_Hat_0.append(x_hat_0) 
                P_0.append(p_0) 
                ref_all_0 = [None, None, None, None, None, x_hat_m[1], x_hat_m[1]] 
                REF_Speed_0.append(ref_all_0[m_0])
                REF_Lane_0.append(L_Center[2])
                REF_Speed_All_0.append(ref_all_0)

        for i in range(N_Car):
            K_Lon = Models[M_0[i]][0]
            K_Lat = Models[M_0[i]][1]
            y_0 = H@X_State_0[i] 
            x_pre_0 = self.VelocityTracking(X_State_0[i], X_State_0[i][1], M_0[i], N, K_Lon, K_Lat)
            Y_0.append(y_0)
            X_Pre_0.append(x_pre_0)  
        
        for i in range(N_Car):
            temp_tra = list( )
            temp_x_var = list( )
            temp_y_var = list( )
            for j in range(N_M):
                if np.sum(X_Hat_0[i][j]) == None:
                    temp_tra.append(None)
                    temp_x_var.append(None)
                    temp_y_var.append(None)
                else:
                    K_Lon = Models[j][0]
                    K_Lat = Models[j][1]
                    temp_tra.append(self.VelocityTracking(X_Hat_0[i][j], X_Hat_0[i][j][1], j, N, K_Lon, K_Lat))
                    temp_x_var.append(np.array([0]*(N + 1)))
                    temp_y_var.append(np.array([0]*(N + 1)))
            X_Po_All_0.append(temp_tra)
            X_Var_0.append(temp_x_var)
            Y_Var_0.append(temp_y_var)
        
        return MU_0, M_0, Y_0, X_Hat_0, P_0, X_Pre_0, X_Po_All_0, X_Var_0, Y_Var_0, REF_Speed_0, REF_Lane_0, REF_Speed_All_0
            
    def VelocityTracking(self, x_ini, ref, m, n_step, K_Lon, K_Lat): # velocity tracking model
        Ts = self.Ts
        L_Center = self.L_Center
        DSV = self.DSV
        k_lo_1 = K_Lon[0]
        k_lo_2 = K_Lon[1]
        k_la_1 = K_Lat[0]
        k_la_2 = K_Lat[1]
        k_la_3 = K_Lat[2]
        vx_ref = ref 
        if (m == 0) or (m == 2):
            y_ref = L_Center[0]
        elif (m == 1) or (m == 3) or (m == 5):
            y_ref = L_Center[1]
        elif (m == 4) or (m == 6):
            y_ref = L_Center[2]
        F = np.array([[1, Ts, Ts**2/2, 0, 0, 0],
                      [0, 1-k_lo_1*Ts**2/2, Ts-k_lo_2*(Ts**2)/2, 0, 0, 0],
                      [0, -k_lo_1*Ts, 1-k_lo_2*Ts, 0, 0, 0],
                      [0, 0, 0, 1-k_la_1*(Ts**3)/6, Ts-k_la_2*(Ts**3)/6, Ts**2/2-k_la_3*(Ts**3)/6],
                      [0, 0, 0, -k_la_1*(Ts**2)/2, 1-k_la_2*(Ts**2)/2, Ts-k_la_3*(Ts**2)/2],
                      [0, 0, 0, -k_la_1*Ts, -k_la_2*Ts, 1-k_la_3*Ts]]) 
        E = np.array([0, k_lo_1*(Ts**2)/2*vx_ref, k_lo_1*Ts*vx_ref, \
                      (Ts**3)/6*k_la_1*y_ref, (Ts**2)/2*k_la_1*y_ref, Ts*k_la_1*y_ref]) 
        
        X_KF = np.zeros((DSV, n_step+1))
        X_KF[:, 0] = x_ini
            
        for i in range(1, n_step+1):
            X_KF[:, i] = (F@X_KF[:, i-1]) + E
            
        return X_KF

