import os 
import argparse

from MeshingParameters import MeshingParameters

LIST_OF_SECTIONS = ['segmentation', 'meshing', 'output', 'laplacesolver', 'others']
def get_param_modifications(modifications, allowed_sections):
    res = {}
    if modifications : 
        try : 
            for mod in modifications:
                key, value = mod.split('=')
                value = str(value)

                if key in allowed_sections:
                    print(f"[common] Set {key} to {value} in the label object.")
                    res[key] = value
                else:
                    print(f"[WARNING] Label '{key}' does not exist in the provided object.")
        except ValueError as e:
            print(f"[ERROR] Invalid modification format: {mod}. Expected format is 'key=value'. Error: {e}")
    else:
        print("[common] No label modifications were provided.")
    
    return res

def main(args):
    bdir = args.base_dir
    bname = args.filename

    output_file = os.path.join(bdir, bname)
    params = MeshingParameters()
    
    for section in LIST_OF_SECTIONS:
        dict_section = get_param_modifications(getattr(args, f'modify_{section}'), params.get_section_keys(section))
        for k,v in dict_section.items():
            params.update(section, k, v)
    
    # override single modifications
    if args.seg_dir is not None:
        params.update('segmentation', 'seg_dir', args.seg_dir)
    
    if args.seg_name is not None:
        params.update('segmentation', 'seg_name', args.seg_name)

    if args.name is not None:
        params.update('output', 'name', args.name)

    if args.outdir is not None:
        params.update('output', 'outdir', args.outdir)

    if args.print:
        print("=== Printing all parameters ===")
        params.print_all()

    params.save(output_file)


if __name__ == '__main__' : 
    input_args = argparse.ArgumentParser(description='Create files with default parameters (Optional)')
    input_args.add_argument('--base-dir', type=str, help='Path to the points file')
    input_args.add_argument('--filename', type=str, help='output filename', default='heart_data')
    input_args.add_argument('--print', action=argparse.BooleanOptionalAction, default=False, help='Print the parameters to the console')

    common_params_group = input_args.add_argument_group('Common Parameters')
    common_params_group.add_argument('--modify-segmentation', '-segmentation', type=str, nargs='*', help="Modify label in the format key=value, e.g., --modify-segmentation seg_dir=NAME seg_name=NAME mesh_from_segmentation=1 boundary_relabeling=0")
    common_params_group.add_argument('--modify-meshing', '-meshing', type=str, nargs='*', help="Modify label in the format key=value, e.g., --modify-meshing facet_angle=30 facet_size=0.8 facet_distance=4 cell_rad_edge_ratio=2.0 cell_size=0.8 rescaleFactor=1000")
    common_params_group.add_argument('--modify-output', '-output', type=str, nargs='*', help="Modify label in the format key=value, e.g., --modify-output outdir=NAME name=NAME out_medit=0 out_carp=1 out_carp_binary=0 out_vtk=1 out_vtk_binary=0 out_potential=0")

    other_params_group = input_args.add_argument_group('Other Parameters')
    other_params_group.add_argument('--modify-laplacesolver', '-laplacesolver', type=str, nargs='*', help="Modify label in the format key=value, e.g., --modify-laplacesolver abs_toll=1e-6 rel_toll=1e-6 itr_max=700 dimKrilovSp=500 verbose=1")
    other_params_group.add_argument('--modify-others', '-others', type=str, nargs='*', help="Modify label in the format key=value, e.g., --modify-others eval_thickness=1")

    override_modifications = input_args.add_argument_group('Single Modifications')
    override_modifications.add_argument('--seg_dir', type=str, help='Path to the segmentation directory', default=None)
    override_modifications.add_argument('--seg_name', type=str, help='Name of the segmentation file', default=None)
    override_modifications.add_argument('--name', type=str, help='Output mesh name', default=None)
    override_modifications.add_argument('--outdir', type=str, help='Output directory', default=None)
    
    args = input_args.parse_args()
    main(args)
   
    
