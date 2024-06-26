
from types import SimpleNamespace

import numpy as np
from scipy import optimize
from scipy import linalg
import pandas as pd 
import matplotlib.pyplot as plt

class HouseholdSpecializationModelClass:

    def __init__(self):
        """ setup model """

        # a. create namespaces
        par = self.par = SimpleNamespace()
        sol = self.sol = SimpleNamespace()

        # b. preferences
        par.rho = 2.0
        par.nu = 0.001
        par.epsilon = 1.0
        par.omega = 0.5 

        # c. household production
        par.alpha = 0.5
        par.sigma = 1.0

        # d. wages
        par.wM = 1.0
        par.wF = 1.0
        par.wF_vec = np.linspace(0.8,1.2,5)

        # e. targets
        par.beta0_target = 0.4
        par.beta1_target = -0.1

        # f. solution
        sol.LM_vec = np.zeros(par.wF_vec.size)
        sol.HM_vec = np.zeros(par.wF_vec.size)
        sol.LF_vec = np.zeros(par.wF_vec.size)
        sol.HF_vec = np.zeros(par.wF_vec.size)

        sol.beta0 = np.nan
        sol.beta1 = np.nan

    def calc_utility(self,LM,HM,LF,HF):
        """ calculate utility """

        par = self.par
        sol = self.sol

        # a. consumption of market goods
        C = par.wM*LM + par.wF*LF

        # b. home production
        if par.sigma == 0:
            H = np.minimum(HM, HF)
        elif par.sigma == 1:
            H = HM**(1-par.alpha)*HF**par.alpha
        else:
            HM = np.fmax(HM, 1e-07)
            HF = np.fmax(HF, 1e-07)
            inside = (1 - par.alpha) * HM ** ((par.sigma-1)/par.sigma) + par.alpha * HF ** ((par.sigma-1)/par.sigma) 
            H = (inside) ** (par.sigma/(par.sigma -1))

        # c. total consumption utility
        Q = C**par.omega*H**(1-par.omega)
        utility = np.fmax(Q,1e-8)**(1-par.rho)/(1-par.rho)

        # d. disutlity of work
        epsilon_ = 1+1/par.epsilon
        TM = LM+HM
        TF = LF+HF
        disutility = par.nu*(TM**epsilon_/epsilon_+TF**epsilon_/epsilon_)
        
        return utility - disutility

    def solve_discrete(self,do_print=False):
        """ solve model discretely """
        
        par = self.par
        sol = self.sol
        opt = SimpleNamespace()
        
        # a. all possible choices
        x = np.linspace(0,24,49)
        LM,HM,LF,HF = np.meshgrid(x,x,x,x) # all combinations
    
        LM = LM.ravel() # vector
        HM = HM.ravel()
        LF = LF.ravel()
        HF = HF.ravel()

        # b. calculate utility
        u = self.calc_utility(LM,HM,LF,HF)
    
        # c. set to minus infinity if constraint is broken
        I = (LM+HM > 24) | (LF+HF > 24) # | is "or"
        u[I] = -np.inf
    
        # d. find maximizing argument
        j = np.argmax(u)
        
        opt.LM = LM[j]
        opt.HM = HM[j]
        opt.LF = LF[j]
        opt.HF = HF[j]

        # e. print
        if do_print:
            for k,v in opt.__dict__.items():
                print(f'{k} = {v:6.4f}')

        return opt

    def solve_cont(self,do_print=False):
        """ solve model continously """
        
        # define parameters and namespaces
        par = self.par
        sol = self.sol
        opt = SimpleNamespace()
    
        
        # constraints and bounds for optimizer
        constraints_M = ({'type': 'ineq', 'fun': lambda x: 24 - x[0] - x[1]}) 
        constraints_F = ({'type': 'ineq', 'fun': lambda x: 24 - x[2] - x[3]}) 
        constraints = [constraints_M, constraints_F]
        bounds = [(0,24)]*4 

        # call optimizer
        initial_guess = [4]*4
        res = optimize.minimize(
            lambda x: -self.calc_utility(x[0],x[1],x[2],x[3]), initial_guess,
            method='SLSQP', bounds=bounds, constraints=constraints, tol=10e-08)
        
        return res.x   

    def solve_wF_vec(self,discrete=False):
        """ solve model for vector of female wages """

        par = self.par
        sol = self.sol  

        for it in range(par.wF_vec.size):
            par.wF = par.wF_vec[it]
            if discrete == True:
                res = self.solve_discrete()
            else:
                res = self.solve_cont()
                sol.LM_vec[it] = res[0]
                sol.HM_vec[it] = res[1]
                sol.LF_vec[it] = res[2]
                sol.HF_vec[it] = res[3]

   
    def run_regression(self):
        """ run regression """

        par = self.par
        sol = self.sol

        x = np.log(par.wF_vec/par.wM)
        y = np.log(sol.HF_vec/sol.HM_vec)
        A = np.vstack([np.ones(x.size),x]).T
        sol.beta0,sol.beta1 = np.linalg.lstsq(A,y,rcond=None)[0]


    
    def estimate(self,alpha=None,sigma=None,do_print=True):
        """ estimate alpha and sigma """
        par = self.par 
        sol = self.sol
        obj = lambda x: self.est(x)
        result = optimize.minimize(obj, x0 = [0.5,0.1], method = 'Nelder-Mead', bounds = [(0.01,0.99)]*2)

        return result.x
    
    def est(self, x):
        """ help funciton in estimating alpha and sigma """
        par = self.par
        sol = self.sol

        par.alpha = x[0]
        par.sigma = x[1]
        self.solve_wF_vec()
        self.run_regression()
        objective = (par.beta0_target - sol.beta0)**2 + (par.beta1_target - sol.beta1)**2
        return objective
    
class NewHouseholdSpecializationModelClass:

    def __init__(self):
        """ setup model """

        # a. create namespaces
        par = self.par = SimpleNamespace()
        sol = self.sol = SimpleNamespace()

        # b. preferences
        par.rho = 2.0
        par.nu = 0.001
        par.eta = 0.002
        par.epsilon = 1.0
        par.omega = 0.5 

        # c. household production
        par.alpha = 0.5
        par.sigma = 1.0

        # d. wages
        par.wM = 1.0
        par.wF = 1.0
        par.wF_vec = np.linspace(0.8,1.2,5)

        # e. targets
        par.beta0_target = 0.4
        par.beta1_target = -0.1

        # f. solution
        sol.LM_vec = np.zeros(par.wF_vec.size)
        sol.HM_vec = np.zeros(par.wF_vec.size)
        sol.LF_vec = np.zeros(par.wF_vec.size)
        sol.HF_vec = np.zeros(par.wF_vec.size)

        sol.beta0 = np.nan
        sol.beta1 = np.nan

    def calc_utility(self,LM,HM,LF,HF):
        """ calculate utility """

        par = self.par
        sol = self.sol

        # a. consumption of market goods
        C = par.wM*LM + par.wF*LF

        # b. home production
        if par.sigma == 0:
            H = np.minimum(HM, HF)
        elif par.sigma == 1:
            H = HM**(1-par.alpha)*HF**par.alpha
        else:
            HM = np.fmax(HM, 1e-07)
            HF = np.fmax(HF, 1e-07)
            inside = (1 - par.alpha) * HM ** ((par.sigma-1)/par.sigma) + par.alpha * HF ** ((par.sigma-1)/par.sigma) 
            H = (inside) ** (par.sigma/(par.sigma -1))

        # c. total consumption utility
        Q = C**par.omega*H**(1-par.omega)
        utility = np.fmax(Q,1e-8)**(1-par.rho)/(1-par.rho)

        # d. disutlity of work
        epsilon_ = 1+1/par.epsilon
        TM = LM+HM
        TF = LF+HF
        disutility = par.nu*(TM**epsilon_/epsilon_)+par.eta*(TF**epsilon_/epsilon_)
        
        return utility - disutility

    def solve_discrete(self,do_print=False):
        """ solve model discretely """
        
        par = self.par
        sol = self.sol
        opt = SimpleNamespace()
        
        # a. all possible choices
        x = np.linspace(0,24,49)
        LM,HM,LF,HF = np.meshgrid(x,x,x,x) # all combinations
    
        LM = LM.ravel() # vector
        HM = HM.ravel()
        LF = LF.ravel()
        HF = HF.ravel()

        # b. calculate utility
        u = self.calc_utility(LM,HM,LF,HF)
    
        # c. set to minus infinity if constraint is broken
        I = (LM+HM > 24) | (LF+HF > 24) # | is "or"
        u[I] = -np.inf
    
        # d. find maximizing argument
        j = np.argmax(u)
        
        opt.LM = LM[j]
        opt.HM = HM[j]
        opt.LF = LF[j]
        opt.HF = HF[j]

        # e. print
        if do_print:
            for k,v in opt.__dict__.items():
                print(f'{k} = {v:6.4f}')

        return opt

    def solve_cont(self,do_print=False):
        """ solve model continously """
        
        # define parameters and namespaces
        par = self.par
        sol = self.sol
        opt = SimpleNamespace()
    
        
        # constraints and bounds for optimizer
        constraints_M = ({'type': 'ineq', 'fun': lambda x: 24 - x[0] - x[1]}) 
        constraints_F = ({'type': 'ineq', 'fun': lambda x: 24 - x[2] - x[3]}) 
        constraints = [constraints_M, constraints_F]
        bounds = [(0,24)]*4 

        # call optimizer
        initial_guess = [4]*4
        res = optimize.minimize(
            lambda x: -self.calc_utility(x[0],x[1],x[2],x[3]), initial_guess,
            method='SLSQP', bounds=bounds, constraints=constraints)
        
        return res.x   

    def solve_wF_vec(self,discrete=False):
        """ solve model for vector of female wages """

        par = self.par
        sol = self.sol  

        for it in range(par.wF_vec.size):
            par.wF = par.wF_vec[it]
            if discrete == True:
                res = self.solve_discrete()
            else:
                res = self.solve_cont()
                sol.LM_vec[it] = res[0]
                sol.HM_vec[it] = res[1]
                sol.LF_vec[it] = res[2]
                sol.HF_vec[it] = res[3]

   
    def run_regression(self):
        """ run regression """

        par = self.par
        sol = self.sol

        x = np.log(par.wF_vec/par.wM)
        y = np.log(sol.HF_vec/sol.HM_vec)
        A = np.vstack([np.ones(x.size),x]).T
        sol.beta0,sol.beta1 = np.linalg.lstsq(A,y,rcond=None)[0]


    def estimate(self,sigma=None,do_print=True):
        """ estimate sigma """
        par = self.par 
        sol = self.sol
        obj = lambda x: self.est(x)
        result = optimize.minimize(obj, x0 = [0.1], method = 'Nelder-Mead', bounds = [(0.01,0.99)])

        return result.x
    
    def est(self, x):
        """ help function in estimating sigma """
        par = self.par
        sol = self.sol

        par.sigma = x[0]
        self.solve_wF_vec()
        self.run_regression()
        objective = (par.beta0_target - sol.beta0)**2 + (par.beta1_target - sol.beta1)**2
        return objective