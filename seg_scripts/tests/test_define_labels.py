from seg_scripts.parameters import Labels, WallThickness, Parameters

def main():
    # 1. Create a Labels object with default values
    labels = Labels()
    print("Initial Labels:")
    labels.print_label_explanation()

    # Save the default labels to a file
    labels_file = 'labels.json'
    labels.save(labels_file)
    print(f"Default labels saved to {labels_file}\n")

    # 2. Create a WallThickness object with default values
    wall_thickness = WallThickness(spacings=0.39844)
    print("Initial Wall Thickness:")
    print(wall_thickness.get_dictionary())

    # Save the default thickness values to a file
    thickness_file = 'thickness.json'
    wall_thickness.save(thickness_file)
    print(f"Default wall thickness saved to {thickness_file}\n")

    # 3. Create a Parameters object using the saved files
    params = Parameters(label_file=labels_file, thickness_file=thickness_file)
    print("Initial Parameters (Labels and Thickness):")
    params.print_all()

    # 4. Modify some label and thickness parameters
    # Modify labels
    params.labels.LV_BP_label = 99  # Example modification
    params.labels.RA_BP_label = 100  # Example modification
    params.LAA_label = 651 # Example modification

    # Modify thickness parameters
    params.thickness.LV_neck_WT = 5.0  # Example modification
    params.thickness.PArt_WT_multiplier = 2.5  # Example modification
    params.LAA_WT = 30.0  # Example modification
    params.ring_thickness_multiplier = 0.001  # Example modification

    # 5. Print the modified parameters to the console
    print("\nModified Parameters (Labels and Thickness):")
    params.print_all()

    # 6. Save the modified values back to the files
    params.save_labels(labels_file)
    params.save_thickness(thickness_file)
    print(f"\nModified labels and thickness saved to {labels_file} and {thickness_file}")


if __name__ == '__main__' : 
   main()
   
    