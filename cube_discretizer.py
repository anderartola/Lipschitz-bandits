import numpy as np

class CubeDiscretizer:
    def __init__(self, dimensions, max_depth=10):
        """
        Initialize the CubeDiscretizer with a given number of dimensions.
        
        Args:
            dimensions (int): Number of dimensions of the cube.
            max_depth (int): Maximum depth of subdivision.
        """
        self.dimensions = dimensions
        self.max_depth = max_depth
        self.cubes = [{"lower": np.zeros(dimensions), "upper": np.ones(dimensions), "depth": 0}]
    
    def subdivide_cube(self, cube_index):
        """
        Subdivide a specific cube into smaller subcubes.
        
        Args:
            cube_index (int): Index of the cube to be subdivided.
        """
        if cube_index < 0 or cube_index >= len(self.cubes):
            raise ValueError("Invalid cube index.")
        
        cube = self.cubes[cube_index]
        if cube["depth"] >= self.max_depth:
            raise ValueError("Maximum depth reached for this cube.")
        
        lower, upper = cube["lower"], cube["upper"]
        step = (upper - lower) / 2  # New cube size
        new_cubes = []
        for offsets in np.ndindex(*[2] * self.dimensions):
            offset = np.array(offsets)
            new_lower = lower + offset * step
            new_upper = new_lower + step
            new_cubes.append({"lower": new_lower, "upper": new_upper, "depth": cube["depth"] + 1})
        
        # Replace the original cube with its subdivisions
        self.cubes.extend(new_cubes)
    
    def subdivide_cube_and_extend(self, cube):
        """
        Subdivide the given cube and extend self.cubes with the new cubes.
        
        Args:
            cube (dict): The cube to subdivide and extend self.cubes with.
        """
        if cube["depth"] >= self.max_depth:
            raise ValueError("Maximum depth reached for this cube.")
        lower, upper = cube["lower"], cube["upper"]
        step = (upper - lower) / 2
        for offsets in np.ndindex(*[2] * self.dimensions):
            offset = np.array(offsets)
            new_lower = lower + offset * step
            new_upper = new_lower + step
            self.cubes.append({"lower": new_lower, "upper": new_upper, "depth": cube["depth"] + 1})
    
    def get_cubes(self):
        """
        Return all current cubes.
        
        Returns:
            List[Dict]: A list of dictionaries, each containing 'lower', 'upper', and 'depth'.
        """
        return self.cubes
    def count_cubes_by_depth(self, depth):
        """
        Count the number of cubes at a specific depth level.
        
        Args:
            depth (int): The depth level to count cubes.
        
        Returns:
            int: Number of cubes at the specified depth level.
        """
        if depth < 0 or depth > self.max_depth:
            raise ValueError("Invalid depth level. Depth must be between 0 and max_depth.")
        return sum(1 for cube in self.cubes if cube["depth"] == depth)
    
    def get_cubes_by_depth(self, depth):
        """
        Return all cubes at a specific depth level.
        
        Args:
            depth (int): The depth level to filter cubes.
        
        Returns:
            List[Dict]: A list of cubes at the specified depth level.
        """
        if depth < 0 or depth > self.max_depth:
            raise ValueError("Invalid depth level. Depth must be between 0 and max_depth.")
        return [cube for cube in self.cubes if cube["depth"] == depth]
    
    
