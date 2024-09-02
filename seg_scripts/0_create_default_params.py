import os 
import argparse

from seg_scripts.parameters import Parameters
from seg_scripts.common import apply_label_modifications

def main(args):

    bname = args.basename 

    labels_file = f'{bname}_labels.json'
    thickness_file = f'{bname}_thickness.json'
    vein_cutoff_file = f'{bname}_vein_cutoff.json'

    print_labels = args.print_all or args.print_labels
    print_thickness = args.print_all or args.print_thickness
    print_vein_cutoff = args.print_all or args.print_vein_cutoff

    params = Parameters()

    apply_label_modifications(params, getattr(args, 'modify_label', []))

    if print_labels:
        print(f"Saving Labels File: {labels_file}")
        params.save_labels(os.path.join(args.path2points, labels_file))
    
    if print_thickness:
        print(f"Saving Thickness File: {thickness_file}")
        params.save_thickness(os.path.join(args.path2points, thickness_file))
    
    if print_vein_cutoff:
        print(f"Saving Vein File: {vein_cutoff_file}")
        params.save_vein_cutoff(os.path.join(args.path2points, vein_cutoff_file))
    


if __name__ == '__main__' : 
    input_args = argparse.ArgumentParser(description='Create files with default parameters (Optional)')
    input_args.add_argument('path2points', type=str, help='Path to the points file')
    input_args.add_argument('--basename', type=str, help='Base name for the output files ([basename]_labels, [basename]_thickness, [basename]_vein_cutoff)', default='custom')
    input_args.add_argument('--modify-label', type=str, nargs='*', help="Modify label in the format key=value, e.g., --modify-label SVC_label=5 IVC_label=6 RA_BP_label=10")

    print_options_group = input_args.add_argument_group('Print Options')
    print_options_group.add_argument('--print-all', action=argparse.BooleanOptionalAction, help='Print all parameters to the console', default=True)
    print_options_group.add_argument('--print-labels', action=argparse.BooleanOptionalAction, help='Print label parameters to the console', default=False)
    print_options_group.add_argument('--print-thickness', action=argparse.BooleanOptionalAction, help='Print thickness parameters to the console', default=False)
    print_options_group.add_argument('--print-vein-cutoff', action=argparse.BooleanOptionalAction, help='Print vein cutoff parameters to the console', default=False)

    args = input_args.parse_args()
    main(args)
   
    
