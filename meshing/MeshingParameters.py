import configparser

class MeshingParameters:
    # Default values for the meshing parameters
    DEFAULT_SEGMENTATION = {
        'seg_dir': './',
        'seg_name': 'seg_final_smooth_corrected.inr',
        'mesh_from_segmentation': 1,
        'boundary_relabeling': 0,
    }
    DEFAULT_MESHING = {
        'facet_angle': 30,
        'facet_size': 0.8,    # change this for mesh resolution
        'facet_distance': 4,
        'cell_rad_edge_ratio': 2.0,
        'cell_size': 0.8,     # change this for mesh resolution
        'rescaleFactor': 1000 # rescaling for carp and vtk output
    }
    DEFAULT_LAPLACESOLVER = {
        'abs_toll': 1e-6,
        'rel_toll': 1e-6,
        'itr_max': 700,
        'dimKrilovSp': 500,
        'verbose': 1,
    }
    DEFAULT_OTHERS = {
        'eval_thickness': 1,
    }
    DEFAULT_OUTPUT = {
        'outdir': './myocardium_OUT',
        'name': 'heart_mesh',
        'out_medit': 0,
        'out_carp': 1,
        'out_carp_binary': 0,
        'out_vtk': 1,
        'out_vtk_binary': 0,
        'out_potential': 0,
    }

    DEFAULT_VALUES = {
        'segmentation': DEFAULT_SEGMENTATION,
        'meshing': DEFAULT_MESHING,
        'laplacesolver': DEFAULT_LAPLACESOLVER,
        'others': DEFAULT_OTHERS,
        'output': DEFAULT_OUTPUT
    }
    
    def __init__(self, config_file=None):
        # Load default values
        self.config = configparser.ConfigParser()
        self.config.read_dict(MeshingParameters.DEFAULT_VALUES)

        # Load from a config file if provided
        if config_file:
            self.load(config_file)
       
    def create_dict(self) :
        return {s:dict(self.config.items(s)) for s in self.config.sections()}
    
    def load(self, config_file):
        # Load from a file
        self.config.read(config_file)

    def save(self, filename):
        # Save the configuration to a file
        with open(filename, 'w') as configfile:
            self.config.write(configfile)

    def update(self, section, option, value):
        # Update a specific option in a section
        if section in self.config and option in self.config[section]:
            self.config[section][option] = value
        else:
            raise ValueError(f"{section} or {option} not found in the configuration.")

    def get(self, section, option):
        # Get the value of a specific option in a section
        return self.config.get(section, option)

    def reset_to_defaults(self):
        # Reset the configuration to default values
        self.config.read_dict(MeshingParameters.DEFAULT_VALUES)

    def print_all(self):
        # Print all configuration parameters
        for section in self.config.sections():
            print(f"[{section}]")
            for key, value in self.config.items(section):
                print(f"{key} = {value}")
            print()  # Blank line between sections

    def get_section_keys(self, section):
        # Get all keys in a specific section
        return self.config[section].keys()

# Example usage:
if __name__ == "__main__":
    params = MeshingParameters()
    params.print_all()  # Print the default configuration

    # Update a value
    params.update('meshing', 'facet_size', '1.0')

    # Save to file
    params.save('meshing_params.ini')

    # Load from file
    params.load('meshing_params.ini')

    # Print updated configuration
    params.print_all()
