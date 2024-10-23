import os
import argparse 
import json 

from generic_relabel import TARGET_LABELS as tags
from MeshProcessingParameters import ETagsParameters, AtriaMapSettings, BachmannBundleSettings, DEFAULT_MESH_TAGS
import seg_scripts.common as iou

# CONSTANTS
APEX_SEPTUM = 'apex_septum_templates'
ETAGS = 'etags'
ATRIA_MAP_JSON = 'atria_map_settings.json'
BACHMANN_BUNDLE_JSON = 'bachmann_bundle_fec_settings.json'
TAGS_AFIBRES = 'tags_atrial_fibres.json'
TAGS_LVRV = 'tags_lvrv.json'
TAGS_PRESIM = 'tags_presim.json'
TAGS_VFIBRES = 'tags_vent_fibres.json'

FILES = {
    APEX_SEPTUM: ['la.lvapex.vtx', 'la.rvsept_pt.vtx', 'raa_apex.txt', 'ra.lvapex.vtx', 'ra.rvsept_pt.vtx'],
    ETAGS: ['etags_la.sh'  'etags_ra.sh'  'etags.sh']
}

def create_vtx_template(filename, ftype='') :
    filename += '.vtx' if not filename.endswith('.vtx') else '' 
    with open(filename, 'w') as f : 
        f.write(f'1\nextra\nsave_{ftype}_here')

def create_txt_template(filename) : 
    filename += '.txt' if not filename.endswith('.txt') else '' 
    with open(filename, 'w') as f : 
        f.write('coord_x coord_y coord_z')

def main(args) :
    """
    Create parfiles folder and fill it with templates and default files
    Outputs:
        apex_septum_templates   : folder with atria guide points (la.lvapex, la.rvsept_pt, raa_apex, ra.lvapex, ra.rvsept_pt) 
        etags                   : folder with etags scripts used with CARP functions
        atria_map_settings.json 
        bachmann_bundle_fec_settings.json
        tags_atrial_fibres.json
        tags_lvrv.json
        tags_presim.json
        tags_vent_fibres.json
        
    """
    case_folder = args.directory
    parfiles_folder = os.path.join(case_folder, 'parfiles')
    PAR_SDIR = lambda x: os.path.join(parfiles_folder, x)
    
    iou.mymkdir(parfiles_folder)
    iou.mymkdir(PAR_SDIR(APEX_SEPTUM))

    for file in FILES[APEX_SEPTUM] : 
        stype = 'apex' if 'apex' in file else 'septum'
        filepath = os.path.join(PAR_SDIR(APEX_SEPTUM), file)
        if file.endswith('.vtx') : 
            create_vtx_template(filepath, stype)
        else :
            create_txt_template(filepath)
            
    iou.mymkdir(PAR_SDIR(ETAGS))
    etags_obj = ETagsParameters('base')
    etags_obj.save_to_file(os.path.join(PAR_SDIR(ETAGS), 'etags.sh'))

    etags_obj.update_type('la')
    etags_obj.save_to_file(os.path.join(PAR_SDIR(ETAGS), 'etags_la.sh'))

    etags_obj.update_type('ra')
    etags_obj.save_to_file(os.path.join(PAR_SDIR(ETAGS), 'etags_ra.sh'))

    atria_map_settings = AtriaMapSettings()
    atria_map_settings.save_to_file(os.path.join(parfiles_folder, ATRIA_MAP_JSON))

    bachmann_bundle_settings = BachmannBundleSettings()
    bachmann_bundle_settings.save_to_file(os.path.join(parfiles_folder, BACHMANN_BUNDLE_JSON))

    afib_tags = {
	    "LV": DEFAULT_MESH_TAGS["LV"],
	    "RV": DEFAULT_MESH_TAGS["RV"],
	    "LA": DEFAULT_MESH_TAGS["LA"],
	    "RA": DEFAULT_MESH_TAGS["RA"],
	    "mitral": DEFAULT_MESH_TAGS["MV"],
	    "tricuspid": DEFAULT_MESH_TAGS["TV"],
	    "PV_planes": [
                DEFAULT_MESH_TAGS["LSPV"],
                DEFAULT_MESH_TAGS["LIPV"],
                DEFAULT_MESH_TAGS["RSPV"],
                DEFAULT_MESH_TAGS["RIPV"],
                DEFAULT_MESH_TAGS["LAA"]
            ],
	    "VC_planes": [
                DEFAULT_MESH_TAGS["SVC"],
                DEFAULT_MESH_TAGS["IVC"]
            ],
	    "RSPV": DEFAULT_MESH_TAGS["RSPV_ring"],
	    "RIPV": DEFAULT_MESH_TAGS["RIPV_ring"],
	    "LSPV": DEFAULT_MESH_TAGS["LSPV_ring"],
	    "LIPV": DEFAULT_MESH_TAGS["LIPV_ring"],
	    "LAA": DEFAULT_MESH_TAGS["LAA_ring"],
	    "RSPV_vp": DEFAULT_MESH_TAGS["RSPV"],
	    "RIPV_vp": DEFAULT_MESH_TAGS["RIPV"],
	    "LSPV_vp": DEFAULT_MESH_TAGS["LSPV"],
	    "LIPV_vp": DEFAULT_MESH_TAGS["LIPV"],
	    "LAA_vp": DEFAULT_MESH_TAGS["LAA"],
	    "SVC": DEFAULT_MESH_TAGS["SVC_ring"],
	    "IVC": DEFAULT_MESH_TAGS["IVC_ring"],
	    "SVC_vp": DEFAULT_MESH_TAGS["SVC"],
	    "IVC_vp": DEFAULT_MESH_TAGS["IVC"]
    }

    with open(os.path.join(parfiles_folder, TAGS_AFIBRES), 'w') as f : 
        json.dump(afib_tags, f, indent=4)
    
    with open(os.path.join(parfiles_folder, TAGS_LVRV), 'w') as f : 
        json.dump(DEFAULT_MESH_TAGS, f, indent=4)

    presim_tags = DEFAULT_MESH_TAGS.copy()
    # remove FEC_RV and FEC_SV
    presim_tags.pop("FEC_RV")
    presim_tags.pop("FEC_SV")
    with open(os.path.join(parfiles_folder, TAGS_PRESIM), 'w') as f : 
        json.dump(presim_tags, f, indent=4)

    vfib_tags = presim_tags.copy()
    vfib_tags.pop("AV_plane")
    vfib_tags.pop("BB")
    vfib_tags.pop("FEC_LV")
    with open(os.path.join(parfiles_folder, TAGS_VFIBRES), 'w') as f : 
        json.dump(vfib_tags, f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('-dir', '--directory', type=str, required=True, help='Path to case folder')

    args = parser.parse_args()
    main(args)
