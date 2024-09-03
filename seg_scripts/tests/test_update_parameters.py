from seg_scripts.parameters import Labels, WallThickness, VeinCutoff, Parameters

def main():
    # 0. Create a Parameters with default values 
    existing_params = Parameters()
    existing_params.LAA_label = 651 # Example modification
    existing_params.ring_thickness_multiplier = 0.001  # Example modification
    existing_params.PArt_cutoff = 0.3  # Example modification

    basename = 'params' 
    existing_params.save_labels(f'{basename}_labels.json')
    existing_params.save_thickness(f'{basename}_thickness.json')
    existing_params.save_vein_cutoff(f'{basename}_vein_cutoff.json')

    print('Existing parameters:')
    existing_params.print_all()
    
    # 1. Modify some parameters:
    params = Parameters()
    params.SVC_label = 100  # Example modification
    params.ring_thickness = 1.5  # Example modification
    params.PArt_cutoff = 0.5  # Example modification

    # 2. Update the parameters with the modified values
    # TO-DOL: These functions are not working properly
    params.update_labels(f'{basename}_labels.json')
    params.update_thickness(f'{basename}_thickness.json')
    params.update_vein_cutoff(f'{basename}_vein_cutoff.json')

    print('\n\nUpdated parameters:')
    params.print_all()


if __name__ == '__main__' : 
   main()
   
    