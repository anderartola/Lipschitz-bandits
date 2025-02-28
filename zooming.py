import numpy as np
from cube_discretizer import CubeDiscretizer
import matplotlib.pyplot as plt
class BanditInstance:
    def __init__(self, param_dim, L, beta, delta, max_pulls):
        #Define the bandit instance
        self.L = L
        self.param_dim = param_dim
        self.beta = beta
        self.delta = delta
        self.max_pulls = max_pulls
        self.consumed_budget = 0
        self.optimal = None
        self.converged = False
        self.m = 1
        self.l_m = 1/2**self.m
        self.n_m = 2**(self.beta*self.m)

        
        #Initilize the CubeDiscretizer instance
        self.cube_discretizer = CubeDiscretizer(dimensions = self.param_dim, max_depth = self.max_pulls)
        
        #Initilize the set of active cubes in the first round, i.e., subdivide the initial cube
        self.cube_discretizer.subdivide_cube(0)
        
        #Get current active cubes
        self.active_cubes = self.cube_discretizer.get_cubes()
        
        
    def get_phase_state(self):
        return {"m": self.m, "current_cubes": self.cube_discretizer.cubes, "n_m" : self.n_m, "l_m": self.l_m}
    

    def execute_phase(self, cubes_with_empirical_mean):
        """
        Executes a single phase of the bandit algorithm.

        Parameters:
        empirical_mean [Dict]: A list of dictionaries coressponding to the cubes in the current phase. Each dictionary contains the keys "upper" "lower" "depth" and "empirical_mean".

        This method performs the following steps:
        2. Determines the maximum empirical mean among the current cubes
        3. Eliminates cubes that do not meet the criteria based on the empirical mean.
        4. Updates the consumed budget.
        5. Checks if the budget is exhausted and sets the optimal cube if converged.
        6. If not converged, partitions the active cubes and updates the phase parameters.
        """
        print("Current phase befor execution: m=", self.m,"----------------------------------")
        
        max_current_empirical_mean = np.max([cube["empirical_mean"] for cube in cubes_with_empirical_mean]).squeeze()
        elimination_threshold = 2*(1+self.L)*self.l_m + 2 * self.delta
        #print("Current max_current_empirical:", max_current_empirical_mean)
        #print("Cubes are eliminated if max_current_empirical_mean - empirical_mean_of_cube > 2*(1+L)*l_m + 2*delta=", 2*(1+self.L)*self.l_m + 2*self.delta)
        
        #self.active_cubes = self.cube_discretizer.get_cubes()
        
        #self.active_cubes = [cube for cube in self.cube_discretizer.get_cubes() if max_current_empirical_mean - cube["empirical_mean"] < elimination_threshold]
        self.active_cubes = [cube for cube in cubes_with_empirical_mean if max_current_empirical_mean - cube["empirical_mean"] < elimination_threshold]
        
        # print("Phase m=", self.m)
        # print("Number of total cubes:", self.cube_discretizer.count_cubes_by_depth(self.m))
        # print("Number of active cubes:", len(self.active_cubes))
        # print("Pulls consumed in this phase", self.n_m * self.cube_discretizer.count_cubes_by_depth(self.m))
        # print("Pulls per cub in this phase", self.n_m)
        
        self.consumed_budget += self.n_m * self.cube_discretizer.count_cubes_by_depth(self.m)
        self.budget_next_phase =  (self.n_m * 2**self.beta) * len(self.active_cubes)*2**self.param_dim
        # print("Budget remaining:", self.max_pulls - self.consumed_budget)
        # print("Next phase will consume", self.budget_next_phase)
        
        if self.budget_next_phase > self.max_pulls-self.consumed_budget:
            
            self.converged = True
            
            #Modulo using the leftover pulls
            optimal_cube = max(cubes_with_empirical_mean, key=lambda d: d['empirical_mean'])
            self.optimal = (optimal_cube["lower"] + optimal_cube["upper"]) / 2
            print("Unconsumed budget:", self.max_pulls - self.consumed_budget)
            #self.active_cubes=cubes_with_empirical_mean
            
        
        else:
            #Update current list of cubes by partitioning active cubes
            for active_cube in self.active_cubes:
                self.cube_discretizer.subdivide_cube_and_extend(active_cube)
            
            #Update the phase parameters
            self.m= self.m + 1
            self.l_m = self.l_m / 2
            self.n_m=2**(self.beta*self.m)
            
    def use_uncomsumed_budget(self, cubes_with_empirical_mean):
        """Includes uniformaly pulled arms in the active cubes after the last phase.

        Args:
            cubes_with_empirical_mean (list): A list of the cubes that are still active after the last rounds, together with the empirical rewards obtained pulling them in a key "extra_empirical_mean" and the number of times they were pulled in a key ""new_pulls"".
        """
        print("print(cubes_with_empirical_mean)", cubes_with_empirical_mean)
        for cube in cubes_with_empirical_mean:
            cube["total_empirical_mean"] = 1/(cube["new_pulls"] + self.n_m) * ( self.n_m * cube["empirical_mean"] + cube["new_pulls"] * cube["extra_empirical_mean"])
            optimal_cube = max(cubes_with_empirical_mean, key=lambda d: d['empirical_mean'])
            self.optimal = (optimal_cube["lower"] + optimal_cube["upper"]) / 2
            self.consumed_budget += cube["new_pulls"]
        
        print("Final unconsummed budget:", self.max_pulls - self.consumed_budget)
        
    def plot_cubes(self):
        """
        Plot all cubes in 1D or 2D.
        - Cubes at the maximum depth are plotted in red.
        - Other cubes are plotted in black.
        """
        if self.dimensions not in [1, 2]:
            raise ValueError("This function only supports 1D or 2D.")
        
        # Get the maximum depth of the cubes
        max_depth = max(cube["depth"] for cube in self.cube_discretizer.get_cubes())
        
        plt.figure()
        
        for cube in self.cubes:
            lower, upper = cube["lower"], cube["upper"]
            depth = cube["depth"]
            
            # Plot the cube based on its dimension and depth
            if self.dimensions == 1:
                # In 1D, we plot as lines
                color = 'red' if depth == max_depth else 'black'
                plt.plot([lower[0], upper[0]], [0, 0], color=color, lw=5)
                
            elif self.dimensions == 2:
                # In 2D, we plot as rectangles
                color = 'red' if depth == max_depth else 'black'
                plt.gca().add_patch(plt.Rectangle((lower[0], lower[1]), upper[0] - lower[0], upper[1] - lower[1], color=color))
        
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()
