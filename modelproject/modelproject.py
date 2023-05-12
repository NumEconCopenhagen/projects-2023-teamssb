from types import SimpleNamespace
from scipy import optimize
import sympy as sm
import math
import ipywidgets as widgets
import matplotlib.pyplot as plt

class MalthusModelClass:

    def __init__(self):
        self.par = SimpleNamespace(beta=0.2, delta=2, tau=0.1, eta=0.4, mu=0.4, alpha=1/3, A=4, X=9, T=200, g=1.02)
        self.c = None
        self.n = None
        self.u = None

    def find_ss_l(self):
        """Output: Steady state value of population """
        result = optimize.root_scalar(lambda L: L-(self.par.eta/self.par.mu)**(1/self.par.alpha)*self.par.A*self.par.X, bracket=[-5000,5000], method='brentq')
        return result.root
    
    def find_ss_y(self):
        """Output: Steady state value of population """
        result = optimize.root_scalar(lambda y: y-(self.par.mu/self.par.eta), bracket=[-500,500], method='brentq')
        return result.root

    def simulate_malthus_l(self,T):
        """Simulating the labor force
        
        Args: 
        T: time periods of simulation
        
        """
        
        # create lists for diagonal line s and population L
        l_values = []
        s_values = []

        # create the population movement
        for l in range(0,T):
                l_new = (self.par.eta)*(self.par.A*self.par.X)**(self.par.alpha)*l**(1-self.par.alpha)+(1-self.par.mu)*l                
                l_values.append(l_new)
    
        for l in range(0,T):
                s_new = l
                s_values.append(s_new)

        # steady state
        ss = self.find_ss_l()
 
        # plot
        plt.figure(figsize=(5,5))
        plt.plot(s_values, l_values, label=r'$L_{t+1}=\eta (AX)^\alpha L_t^{1-\alpha}+(1-\mu)L_t$', color = 'blue')
        plt.plot(s_values, s_values, label='45 degree line', color = 'black')
        plt.scatter(ss, ss, c='g', linewidths=3, label='Steady State')
        plt.text(ss, ss, '({}, {})'.format(round(ss,2), round(ss,2)))
        plt.xlim(0,T)
        plt.ylim(0,T)
        plt.ylabel('$L_{t+1}$')
        plt.xlabel('$L_t$')
        plt.grid(True)
        plt.legend()
        
        return plt.show()
    
    def _plot_widget(self,alpha, eta, A, X, mu):
          self.par.mu = mu
          self.par.X = X
          self.par.A = A
          self.par.eta = eta
          self.par.alpha = alpha
          self.simulate_malthus_l(100)

    def plot_widget(self):
        widgets.interact(self._plot_widget, 
                            alpha = widgets.FloatSlider(description = r'alpha',min=0.01,max =0.65,step=0.02,value=1/3),
                            mu = widgets.FloatSlider(description = r'mu',min=0.01,max =0.99,step=0.02,value=0.4),
                            eta = widgets.FloatSlider(description = r'eta',min=0.01,max =0.60,step=0.02,value=0.4),
                            X = widgets.FloatSlider(description = r'X',min=1,max =10,step=1,value=4),
                            A = widgets.FloatSlider(description = r'A',min=1,max =10,step=1,value=9),
                            T = widgets.IntSlider(description = r'T',min=1,max=10,step=1,value=9))
        
    
    def simulate_malthus_l_tech(self,T):
        """Simulating the model with technological growth

        Args: 
        T: Time periods of simulaiton
        
        """
        
        # create lists for diagonal line s and population L
        l_values = []
        s_values = []

        #create technological growth
        A_values = [self.par.A * (self.par.g)**t for t in range(T)]

        # create the population movement
        for l, A in enumerate(A_values):
                    l_new = (self.par.eta)*(A**self.par.X)**(self.par.alpha)*l**(1-self.par.alpha)+(1-self.par.mu)*l                
                    l_values.append(l_new)
    
        for l in range(0,T):
                s_new = l
                s_values.append(s_new)
 
        # plot
        plt.figure(figsize=(5,5))
        plt.plot(s_values, l_values, label=r'$L_{t+1}=\eta (AX)^\alpha L_t^{1-\alpha}+(1-\mu)L_t$', color = 'blue')
        plt.ylabel('$L$')
        plt.xlabel('$t$')
        plt.grid(True)
        
        return plt.show()
    
    def find_ss_lx_tech(self):
        """Output: Steady state value of population"""

        result = optimize.root_scalar(lambda l_x: l_x-(self.par.eta/(self.par.g+self.par.mu-1)), bracket=[-5000,5000], method='brentq')
        return result.root
    
    def find_ss_y_tech(self):
        """Output: Steady state value of population"""

        result = optimize.root_scalar(lambda y: y-((self.par.g+self.par.mu-1)/self.par.eta), bracket=[-5000,5000], method='brentq')
        return result.root
    


class MalthusMicroModelClass:

    def __init__(self):
            self.par = SimpleNamespace(beta=0.2, delta=2, tau=0.1, eta=0.4, mu=0.4, alpha=1/3, A=4, X=9, T=200)
            self.c = None
            self.n = None
            self.u = None 

    def utility_func(self, c, n):
        return (1-self.par.beta)*math.log(c) + self.par.beta*math.log(n) 
    
    def solve(self):

        """Solves the household utility maximization problem for given income

        Args: 
        Class attributes 

        Output:
        c = Optimal consumption 
        n = Optimal number of off spring
        
        """
        
        y=100  # given income 
        
        obj = lambda x: -self.utility_func(x[0], x[1])
        
        budget_constraint = lambda x: y*(1-self.par.tau) - x[0] - self.par.delta*x[1]
        constraints = [{'type': 'ineq', 'fun': budget_constraint}]
        x0 = [y/2, y/2]
        
        sol = optimize.minimize(obj, x0, method='SLSQP', constraints=constraints)
        self.c = sol.x[0]
        self.n = sol.x[1]
        self.u = self.utility_func(self.c, self.n)

        print(f"Optimal consumption: {self.c:.2f}")
        print(f"Optimal number of off spring: {self.n:.2f}")                             

    def simulate_malthus_micro_l(self,T):
        """Simulating the model""

        Args: 
        T: Time periods of simulaiton
        
        """
        # create lists for diagonal line s and population L 
        l_values = []
        s_values = []
         
        # Create the population movement
        for l in range(0,self.par.T):
                l_new = ((self.par.beta*self.par.tau-self.par.beta-self.par.tau+1)/self.par.delta)*(self.par.A*self.par.X)**(self.par.alpha)*(l)**(1-self.par.alpha)+(1-self.par.mu)*l                
                l_values.append(l_new)
                l = l_new

        for l in range(0,self.par.T):
                s_new = l
                s_values.append(s_new)

        plt.figure(figsize=(5,5))
        plt.plot(s_values, l_values, label=r'$L_{t+1}=\eta (AX)^\alpha L_t^{1-\alpha}+(1-\mu)L_t$', color = 'green')
        plt.plot(s_values, s_values, label='45 degree line', color = 'black')
        plt.xlim(0,T)
        plt.ylim(0,T)
        plt.ylabel('$L_{t+1}$')
        plt.xlabel('$L_t$')
        plt.grid(True)
        plt.legend()

        return plt.show()
    
    def _plot_widget(self, tau):
          self.par.tau =tau
          self.simulate_malthus_micro_l(50)

    def plot_widget(self):
        widgets.interact(self._plot_widget, 
                            tau = widgets.FloatSlider(description = r'tau',min=0.01,max =0.80,step=0.01,value=0.10))


class QualityQuantity:

    def __init__(self):
            self.par = SimpleNamespace(gamma=0.5, beta=0.7, tau_q=0.5, tau_e=0.6, g=0.5, y=100)
            self.c = None
            self.n = None
            self.e = None  
            self.u = None
            
    def utility_func(self,c,n,e):
        return (1-self.par.gamma)*math.log(c) + self.par.gamma*(math.log(n) + self.par.beta* math.log(e/(e+self.par.g)))

    def solve(self):

        """Solves the household utility maximization problem for given income

        Args: 
        Class attributes 

        Output:
        c = Optimal consumption 
        n = Optimal number of off spring
        e = Optimal education investment
        """
        
        obj = lambda x: -self.utility_func(x[0], x[1], x[2])
        
        budget_constraint = lambda x: self.par.y-x[0]-(self.par.tau_q + self.par.tau_e*x[2])*x[1]*self.par.y
        constraints = [{'type': 'ineq', 'fun': budget_constraint}]
        x0 = [self.par.y/3, self.par.y/3, self.par.y/3]
        
        sol = optimize.minimize(obj, x0, method='SLSQP', constraints=constraints)
        self.c = sol.x[0]
        self.n = sol.x[1]
        self.e = sol.x[2]
        self.u = self.utility_func(self.c, self.n,self.e)

        print(f"Optimal consumption: {self.c:.2f}")
        print(f"Optimal number of off spring: {self.n:.2f}")
        print(f"Optimal education investments: {self.e:.3f}")
