import os 
import argparse

from seg_scripts.parameters import Parameters
from seg_scripts.common import apply_label_modifications

def main(args):

    bname = args.basename 

    labels_file = f'{bname}_labels.json'
    thickness_file = f'{bname}_thickness.json'
    vein_cutoff_file = f'{bname}_vein_cutoff.json'

    save_labels = args.save_all or args.save_labels
    save_thickness = args.save_all or args.save_thickness
    save_vein_cutoff = args.save_all or args.save_vein_cutoff

    params = Parameters()

    apply_label_modifications(params, getattr(args, 'modify_label', []))

    print(params.vein_cutoff)

    if save_labels:
        print(f"Saving Labels File: {labels_file}")
        params.save_labels(os.path.join(args.path2points, labels_file))
    
    if save_thickness:
        print(f"Saving Thickness File: {thickness_file}")
        params.save_thickness(os.path.join(args.path2points, thickness_file))
    
    if save_vein_cutoff:
        print(f"Saving Vein File: {vein_cutoff_file}")
        params.save_vein_cutoff(os.path.join(args.path2points, vein_cutoff_file))
    


if __name__ == '__main__' : 
    input_args = argparse.ArgumentParser(description='Create files with default parameters (Optional)')
    input_args.add_argument('path2points', type=str, help='Path to the points file')
    input_args.add_argument('--basename', type=str, help='Base name for the output files ([basename]_labels, [basename]_thickness, [basename]_vein_cutoff)', default='custom')
    input_args.add_argument('--modify-label', type=str, nargs='*', help="Modify label in the format key=value, e.g., --modify-label SVC_label=5 IVC_label=6 RA_BP_label=10")

    save_options_group = input_args.add_argument_group('save Options')
    save_options_group.add_argument('--save-all', action=argparse.BooleanOptionalAction, help='Save all parameters to the console', default=True)
    save_options_group.add_argument('--save-labels', action=argparse.BooleanOptionalAction, help='Save label parameters to the console', default=False)
    save_options_group.add_argument('--save-thickness', action=argparse.BooleanOptionalAction, help='Save thickness parameters to the console', default=False)
    save_options_group.add_argument('--save-vein-cutoff', action=argparse.BooleanOptionalAction, help='Save vein cutoff parameters to the console', default=False)

    args = input_args.parse_args()
    main(args)
   
    
