import json 
import numpy as np

# Utility functions
def load_from_file(filename, defaults):
    if filename is None:
        return defaults
    try:
        with open(filename) as f:
            data = json.load(f)
        return {key: data.get(key, default) for key, default in defaults.items()}
    except FileNotFoundError:
        print(f"File {filename} not found. Using defaults.")
        return defaults
    except json.JSONDecodeError:
        print(f"Error decoding {filename}. Using defaults.")
        return defaults

def save_to_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def save_update_file(filename, data, defaults) : 
    existing_data = load_from_file(filename, defaults)
    existing_data.update(data)

    save_to_file(filename, existing_data)

class Labels:
    # Dictionary to hold label names and their corresponding explanations
    LABELS_INFO = {
        'LV_BP_label': "LV blood pool",
        'LV_myo_label': "LV myocardium",
        'RV_BP_label': "RV blood pool",
        'LA_BP_label': "LA blood pool",
        'RA_BP_label': "RA blood pool",
        'Ao_BP_label': "Ao blood pool",
        'PArt_BP_label': "PArt blood pool",
        'LPV1_label': "LPV1",
        'LPV2_label': "LPV2",
        'RPV1_label': "RPV1",
        'RPV2_label': "RPV2",
        'LAA_label': "LAA",
        'SVC_label': "SVC",
        'IVC_label': "IVC",
        'LV_neck_label': "LV neck",
        'RV_myo_label': "RV myocardium",
        'LA_myo_label': "LA myocardium",
        'RA_myo_label': "RA myocardium",
        'Ao_wall_label': "Ao wall",
        'PArt_wall_label': "PArt wall",
        'MV_label': "Mitral Valve",
        'TV_label': "Tricuspid Valve",
        'AV_label': "Aortic Valve",
        'PV_label': "Pulmonary Artery Valve",
        'plane_LPV1_label': "plane LPV1",
        'plane_LPV2_label': "plane LPV2",
        'plane_RPV1_label': "plane RPV1",
        'plane_RPV2_label': "plane RPV2",
        'plane_LAA_label': "plane LAA",
        'plane_SVC_label': "plane SVC",
        'plane_IVC_label': "plane IVC",
        'LPV1_ring_label': "LPV1 ring",
        'LPV2_ring_label': "LPV2 ring",
        'RPV1_ring_label': "RPV1 ring",
        'RPV2_ring_label': "RPV2 ring",
        'LAA_ring_label': "LAA ring",
        'SVC_ring_label': "SVC ring",
        'IVC_ring_label': "IVC ring"
    }

    # Define default values for labels
    DEFAULT_VALUES = {
        'LV_BP_label': 1,
        'LV_myo_label': 2,
        'RV_BP_label': 3,
        'LA_BP_label': 4,
        'RA_BP_label': 5,
        'Ao_BP_label': 6,
        'PArt_BP_label': 7,
        'LPV1_label': 8,
        'LPV2_label': 9,
        'RPV1_label': 10,
        'RPV2_label': 11,
        'LAA_label': 12,
        'SVC_label': 13,
        'IVC_label': 14,
        'LV_neck_label': 101,
        'RV_myo_label': 103,
        'LA_myo_label': 104,
        'RA_myo_label': 105,
        'Ao_wall_label': 106,
        'PArt_wall_label': 107,
        'MV_label': 201,
        'TV_label': 202,
        'AV_label': 203,
        'PV_label': 204,
        'plane_LPV1_label': 205,
        'plane_LPV2_label': 206,
        'plane_RPV1_label': 207,
        'plane_RPV2_label': 208,
        'plane_LAA_label': 209,
        'plane_SVC_label': 210,
        'plane_IVC_label': 211,
        'LPV1_ring_label': 221,
        'LPV2_ring_label': 222,
        'RPV1_ring_label': 223,
        'RPV2_ring_label': 224,
        'LAA_ring_label': 225,
        'SVC_ring_label': 226,
        'IVC_ring_label': 227,
    }
    
    def __init__(self, filename=None):
        """
        Initializes the Labels object. This sets default values for the labels and wall thickness parameters.
        If filename or thickness_file is provided, it loads the configuration from those files.
        
        :param filename: JSON file containing label and parameter configuration.
        """
      
        # Initialize default label values and store them in instance attributes
        # Using a dictionary to handle label names dynamically
        self.labels = Labels.DEFAULT_VALUES.copy()
        # Load label configurations from a file if provided
        if filename is not None:
            self.load(filename)

    @classmethod
    def __init_subclass__(cls):
        # This method is called automatically when the class is defined.
        for tag_name in cls.LABELS_INFO.keys():
            # Define a getter function dynamically
            def getter(self, label_name=tag_name):
                return self.labels[label_name]
            
            # Define a setter function dynamically
            def setter(self, value, label_name=tag_name):
                self.labels[label_name] = value
            
            # Use `property()` to create a dynamic property with getter and setter
            setattr(cls, tag_name, property(getter, setter))

    def get_default_label_value(self, label_name):
        """
        Returns default values for specific labels. This function handles the mapping
        of label names to their default numerical values.
        
        :param label_name: Name of the label for which the default value is requested.
        :return: Default numerical value for the label.
        """
        
        return Labels.DEFAULT_VALUES.get(label_name, None)  # Return None if label is not found

    def print_label_explanation(self):
        """
        Prints a description of all labels and their current values.
        """
        print("LABELS:")
        for label, explanation in Labels.LABELS_INFO.items():
            value = getattr(self, label, None)
            print(f"{label}: {value} - {explanation}")
    
    def print(self):
        """
        Prints the current label values and wall thickness parameters.
        """
        self.print_label_explanation()

    def save(self, filename):
        # Save the label data to a file
        save_to_file(filename, self.labels)

    def update(self, filename):
        # Update the label data in a file
        save_update_file(filename, self.labels, Labels.DEFAULT_VALUES)

    def load(self, filename):
        # Load the label data from a file
        self.labels = load_from_file(filename, self.labels)

    def get_dictionary(self):
        # Return the labels as a dictionary
        return self.labels
    
    def back_to_default(self):
        # Reset all labels to their default values
        self.labels = Labels.DEFAULT_VALUES.copy()

    def get_attribute_list(self) :
        return list(self.labels.keys())
    
    def equals(self, other) :
        """
        Compare the current labels with another Labels object
        """
        response = True
        for key in self.labels : 
            if self.labels[key] != other.labels[key] : 
                response = False
                break
        
        return response
    
    def __getattr__(self, name):
        if name in self.labels:
            return self.labels[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        if name in ('labels'):
            super().__setattr__(name, value)
        elif name in self.labels:
            self.labels[name] = value
        else:
            super().__setattr__(name, value)


class WallThickness:
    DEFAULT_MULTIPLIERS = {
        'valve_WT_multiplier': 4,
        'valve_WT_svc_ivc_multiplier': 4,
        'ring_thickness_multiplier': 2,
        'LV_neck_WT_multiplier': 2.00,
        'RV_WT_multiplier': 3.50,
        'LA_WT_multiplier': 2.00,
        'RA_WT_multiplier': 2.00,
        'Ao_WT_multiplier': 2.00,
        'PArt_WT_multiplier': 2.00
    }
    def __init__(self, thickness_file=None, spacings=0.39844):
        self.scale_factor = 1 / spacings
        
        # Default multipliers for the thickness parameters
        self.multipliers = WallThickness.DEFAULT_MULTIPLIERS.copy()
        
        # Initialize the actual thickness parameters using the multipliers and scale factor
        self.thickness_params = {key.replace('_multiplier', ''): self.scale_factor * multiplier 
                                 for key, multiplier in self.multipliers.items()}

        # If a file is provided, load the thickness parameters
        if thickness_file:
            self.load_from_file(thickness_file)

    def set_scale_factor(self, spacings, ceiling=False):
        self.scale_factor = 1 / spacings
        if ceiling:
            self.scale_factor = np.ceil(self.scale_factor)
        
        if self.scale_factor < 0.5: 
            print(f'WARNING: Spacing is too large for the scale factor to be meaningful, might cause problems.\n Scale factor: {self.scale_factor}')
        for key in self.multipliers:
            self.update_thickness_param(key.replace('_multiplier', ''))

    @classmethod
    def __init_subclass__(cls):
        for multiplier_name in cls.DEFAULT_MULTIPLIERS.keys():
            thickness_name = multiplier_name.replace('_multiplier', '')
        
            def getter(self, label_name=multiplier_name):
                return self.multipliers[label_name]
            
            def getter(self, label_name=thickness_name):
                return self.thickness_params[label_name]

            def setter(self, value, label_name=multiplier_name):
                self.multipliers[label_name] = value
                self.update_thickness_param(label_name.replace('_multiplier', ''))
            
            def setter(self, value, label_name=thickness_name):
                self.thickness_params[label_name] = value
                self.update_multiplier(label_name)

            setattr(cls, multiplier_name, property(getter, setter))
            setattr(cls, thickness_name, property(getter, setter))
        
    def load_from_file(self, filename):
        data = load_from_file(filename, self.get_dictionary())
        
        # Update both multipliers and thickness parameters from the loaded data
        for key in self.multipliers:
            if key in data:
                self.multipliers[key] = data[key]
                self.update_thickness_param(key.replace('_multiplier', ''))
        
        for key in self.thickness_params:
            if key in data:
                self.thickness_params[key] = data[key]
                self.update_multiplier(key)
    
    def save(self, filename):
        # Save both the multipliers and the thickness parameters to a file
        save_to_file(filename, self.get_dictionary())

    def update(self, filename):
        # Update the multipliers and thickness parameters in a file
        save_update_file(filename, self.get_dictionary(), self.get_default_dictionary())

    def get_dictionary(self):
        # Return both multipliers and thickness parameters as a dictionary
        data = {**self.multipliers, **self.thickness_params}
        data['scale_factor'] = self.scale_factor
        return data
    
    def get_default_dictionary(self):
        default_data = WallThickness.DEFAULT_MULTIPLIERS.copy()
        default_data.update({key.replace('_multiplier', ''): self.scale_factor * multiplier
                                for key, multiplier in WallThickness.DEFAULT_MULTIPLIERS.items()})
        default_data['scale_factor'] = self.scale_factor

        return default_data
    
    def update_thickness_param(self, param_name):
        # Update the thickness parameter based on the corresponding multiplier and scale factor
        multiplier_name = param_name + '_multiplier'
        if multiplier_name in self.multipliers:
            self.thickness_params[param_name] = self.scale_factor * self.multipliers[multiplier_name]
    
    def update_multiplier(self, param_name):
        # Update the multiplier based on the corresponding thickness parameter and scale factor
        multiplier_name = param_name + '_multiplier'
        if param_name in self.thickness_params and self.scale_factor != 0:
            self.multipliers[multiplier_name] = self.thickness_params[param_name] / self.scale_factor

    def back_to_default(self):
        # Reset all multipliers to their default values
        self.multipliers = WallThickness.DEFAULT_MULTIPLIERS.copy()
        # Update the thickness parameters based on the new multipliers
        for key in self.thickness_params:
            self.update_multiplier(key)

    def get_attribute_list(self) :
        return ['scale_factor']  + list(self.multipliers.keys()) + list(self.thickness_params.keys()) 
    
    def equals(self, other) :
        """
        Compare the current thickness with another WallThickness object
        """
        response = True
        for key in self.multipliers : 
            if self.multipliers[key] != other.multipliers[key] : 
                response = False
                break
        
        for key in self.thickness_params : 
            if self.thickness_params[key] != other.thickness_params[key] : 
                response = False
                break
        
        if self.scale_factor != other.scale_factor : 
            response = False
        
        return response
    
    def __getattr__(self, name):
        # Handle dynamic access to multipliers and thickness parameters
        if name in self.multipliers:
            return self.multipliers[name]
        elif name in self.thickness_params:
            return self.thickness_params[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        if name in ('multipliers', 'thickness_params', 'scale_factor'):
            super().__setattr__(name, value)
        elif name in self.multipliers:
            self.multipliers[name] = value
            self.update_thickness_param(name.replace('_multiplier', ''))
        elif name in self.thickness_params:
            self.thickness_params[name] = value
            self.update_multiplier(name)
        else:
            super().__setattr__(name, value)

class VeinCutoff : 
    DEFAULT_VALUES = {
        'SVC_bp_cutoff' : 0.2, 
        'IVC_bp_cutoff' : 0.2, 
        'Aorta_bp_cutoff' : 1, 
        'PArt_bp_cutoff' : 1, 
        'Aorta_open_cutoff' : 0.65, 
        'PArt_open_cutoff' : 0.7
    }

    def __init__(self, filename=None):
        self.vein_cutoff = VeinCutoff.DEFAULT_VALUES.copy()
        if filename is not None:
            self.load(filename)

        @classmethod
        def __init_subclass__(cls):
            for tag_name in cls.DEFAULT_VALUES.keys():
                def getter(self, label_name=tag_name):
                    return self.vein_cutoff[label_name]
                
                def setter(self, value, label_name=tag_name):
                    self.vein_cutoff[label_name] = value
                
                setattr(cls, tag_name, property(getter, setter))
        
    def get_default_label_value(self, label_name):
        return VeinCutoff.DEFAULT_VALUES.get(label_name, None)
    
    def save(self, filename):
        save_to_file(filename, self.vein_cutoff)

    def update(self, filename):
        save_update_file(filename, self.vein_cutoff, VeinCutoff.DEFAULT_VALUES)

    def load(self, filename):
        self.vein_cutoff = load_from_file(filename, self.vein_cutoff)

    def get_dictionary(self):
        return self.vein_cutoff     
    
    def back_to_default(self):
        self.vein_cutoff = VeinCutoff.DEFAULT_VALUES.copy()
    
    def get_attribute_list(self) :
        return list(self.vein_cutoff.keys())
    
    def equals(self, other) :
        """
        Compare the current vein cutoff with another VeinCutoff object
        """
        response = True
        for key in self.vein_cutoff : 
            if self.vein_cutoff[key] != other.vein_cutoff[key] : 
                response = False
                break
        
        return response
    
    def __getattr__(self, name):
        if name in self.vein_cutoff:
            return self.vein_cutoff[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        if name in ('vein_cutoff'):
            super().__setattr__(name, value)
        elif name in self.vein_cutoff:
            self.vein_cutoff[name] = value
        else:
            super().__setattr__(name, value)  


class Parameters:
    def __init__(self, label_file=None, thickness_file=None, spacings=0.39844, vein_cutoff_file=None):
        # Create instances of Labels and Thickness
        self.labels = Labels(filename=label_file)
        self.thickness = WallThickness(thickness_file=thickness_file, spacings=spacings)
        self.vein_cutoff = VeinCutoff(filename=vein_cutoff_file)
        self.aux_labels = []

    def __getattr__(self, name):
        # Delegate attribute access to labels or thickness objects if the attribute exists in them
        if name in self.labels.labels:
            return getattr(self.labels, name)
        elif name in self.thickness.multipliers or name in self.thickness.thickness_params or name == 'scale_factor':
            return getattr(self.thickness, name)
        elif name in self.vein_cutoff.vein_cutoff:
            return getattr(self.vein_cutoff, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        # Delegate attribute setting to labels or thickness objects if the attribute exists in them
        if 'labels' in self.__dict__ and name in self.labels.labels:
            setattr(self.labels, name, value)
        elif 'thickness' in self.__dict__ and (name in self.thickness.multipliers or name in self.thickness.thickness_params):
            setattr(self.thickness, name, value)
        elif 'vein_cutoff' in self.__dict__ and name in self.vein_cutoff.vein_cutoff:
            setattr(self.vein_cutoff, name, value)
        else:
            super().__setattr__(name, value)

    def save_labels(self, filename):
        # Save the labels to a file
        self.labels.save(filename)

    def save_thickness(self, filename):
        # Save the thickness parameters to a file
        self.thickness.save(filename)

    def save_vein_cutoff(self, filename):
        self.vein_cutoff.save(filename)

    def update_labels(self, filename):
        # Update the labels in a file
        self.labels.update(filename)

    def update_thickness(self, filename):
        # Update the thickness parameters in a file
        self.thickness.update(filename)

    def update_vein_cutoff(self, filename):
        self.vein_cutoff.update(filename)

    def set_scale_factor(self, spacings, ceiling=False):
        # Set the scale factor for thickness parameters
        self.thickness.set_scale_factor(spacings, ceiling)

    def load_labels(self, filename):
        # Load the labels from a file
        self.labels.load(filename)

    def load_thickness(self, filename):
        # Load the thickness parameters from a file
        self.thickness.load_from_file(filename)

    def load_vein_cutoff(self, filename):
        self.vein_cutoff.load(filename)

    def print_all(self):
        # Print all labels and thickness parameters
        print("Labels:")
        for key, value in self.labels.get_dictionary().items():
            print(f"{key}: {value}")
        
        print("\nWall Thickness Parameters:")
        for key, value in self.thickness.get_dictionary().items():
            print(f"{key}: {value}")

        print("\nVein Cutoff:")
        for key, value in self.vein_cutoff.get_dictionary().items():
            print(f"{key}: {value}")

    def back_to_default(self):
        # Reset all labels and thickness parameters to their default values
        self.labels.back_to_default()
        self.thickness.back_to_default()
        self.vein_cutoff.back_to_default()

    def get_attribute_list(self) :
        return self.labels.get_attribute_list() + self.thickness.get_attribute_list() + self.vein_cutoff.get_attribute_list()
    
    def create_non_existing_label(self) : 
        """
        Returns a new label that is not in the current labels
        """
        for label in range(1, 1000) : 
            if label not in self.labels.labels.values() and label not in self.aux_labels : 
                self.aux_labels.append(label)
                return label
        return None 
    
    def rm_aux_labels(self) :
        self.aux_labels = []

    def equals(self, other) : 
        """
        Compare the current parameters with another Parameters object
        """
        
        return self.labels.equals(other.labels) and self.thickness.equals(other.thickness) and self.vein_cutoff.equals(other.vein_cutoff) 
        