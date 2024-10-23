import os
import json 

UNUSED_TAG = 200
DEFAULT_ETAGS = {
    'T_LV': 1, 
    'T_RV': 2, 
    'T_UNUSED' : UNUSED_TAG,              # unused tag
    'T_LA' : UNUSED_TAG,                  # left atrial wall
    'T_LABP' : UNUSED_TAG,                # left atrial blood pool
    'T_LINFPULMVEINCUT' : UNUSED_TAG,     # left inferior pulmonary vein (cut)
    'T_LSUPPULMVEINCUT' : UNUSED_TAG,     # left superior pulmonary vein (cut)
    'T_RINFPULMVEINCUT' : UNUSED_TAG,       # right inferior pulmonary vein (cut)
    'T_RSUPPULMVEINCUT' : UNUSED_TAG,       # right superior pulmonary vein (cut)
    'T_RA' : UNUSED_TAG,                  # right atrial wall
    'T_RABP' : UNUSED_TAG,                # right atrial blood pool
    'T_LVBP' : UNUSED_TAG,               # left ventricular blood pool
    'T_AORTA' : UNUSED_TAG,               # aorta
    'T_AORTABP' : UNUSED_TAG,             # aortic blood pool
    'T_MITRALVV' : UNUSED_TAG,            # mitral valve
    'T_AORTICVV' : UNUSED_TAG,           # aortic valve
    'T_RVBP' : UNUSED_TAG,                # right ventricular blood pool
    'T_VCINF' : UNUSED_TAG,              # vena cava inferior
    'T_VCSUP' : UNUSED_TAG,               # vena cava superior
    'T_PULMARTERY' : UNUSED_TAG,          # pulmonary artery
    'T_PULMARTERYBP' : UNUSED_TAG,        # pulmonary artery blood pool
    'T_TRICUSPVV' : UNUSED_TAG,           # tricuspic valve
    'T_PULMVV' : UNUSED_TAG             # pulmonic valve
}

class ETagsParameters: 
    def __init__(self, type='base') -> None:
        types = ['base', 'la', 'ra']
        if type not in types : 
            raise ValueError(f'Invalid type for ETagsParameters. Must be one of {types}')
        
        self.type = type
        self.tags = DEFAULT_ETAGS.copy()
        self.update_tags()

    def update_type(self, type) : 
        self.type = type
        self.update_tags()

    def update_tags(self) : 
        tag_names = list(self.tags.keys())
        if self.type == 'base' : 
            self.tags['T_LV'] = 1
            self.tags['T_RV'] = 2
            tag_names.remove('T_LV')
            tag_names.remove('T_RV')

        elif self.type == 'la' : 
            self.tags['T_LV'] = 3
            tag_names.remove('T_LV')

        elif self.type == 'ra' : 
            self.tags['T_LV'] = 4
            tag_names.remove('T_LV')
        
        for tag in tag_names :
            self.tags[tag] = UNUSED_TAG
        
    def save_to_file(self, filename) : 
        filename += '.sh' if not filename.endswith('.sh') else ''
        # list tags different to UNUSED_TAG
        tags_used = {k:v for k,v in self.tags.items() if v != UNUSED_TAG}
        tags_unused = {k:v for k,v in self.tags.items() if v == UNUSED_TAG}

        with open(filename, 'w') as f :
            f.write('#!/bin/bash\n')
            f.write('\n')
            if self.type != 'base' : 
                f.write(f'## CHANGE ONLY THIS LABEL SO THAT THE T_LV = THE LABELOF YOUR {self.type.upper()}')
            else : 
                f.write('## ONLY CHANGE THESE LABELS TO MATCH YOUR MESH LABELS') 
            f.write('\n\n')
            
            for k,v in tags_used.items() : 
                f.write(f'{k}={v}\n')

            f.write('\n')

            for k,v in tags_unused.items() :
                f.write(f'{k}={v}\n')
            

DEFAULT_ATRIA_MAP = { 
    "la": {
    	"phi_min_aorta_side":          -3.15,
    	"begin_interp_aorta_side":     -2.09,
    	"end_interp_aorta_side":       -1.54,
    	"phi_max":                         0,
        "begin_interp_not_aorta":       -0.1,
        "end_interp_not_aorta":          0.7,
        "phi_min_not_aorta":             3.15
    },

    "ra": {
        "phi_min_aorta_side":          -3.15,
        "begin_interp_aorta_side":     -1.0,
        "end_interp_aorta_side":       -0.5,
        "phi_max":                         0,
        "begin_interp_not_aorta":       0.5,
        "end_interp_not_aorta":          2,
        "phi_min_not_aorta":             3.15
    },
    
    "Iz": {
    	"Iz_0": 0,
    	"Iz_1": 0.4,
    	"Iz_2": 0.7,
    	"Iz_3": 1.0
    }
}
class AtriaMapSettings:
    def __init__(self) -> None:
        self.settings = DEFAULT_ATRIA_MAP.copy()

    def save_to_file(self, filename) : 
        filename += '.json' if not filename.endswith('.json') else ''
        with open(filename, 'w') as f : 
            json.dump(self.settings, f, indent=4)

    def load_from_file(self, filename) : 
        filename += '.json' if not filename.endswith('.json') else ''
        with open(filename, 'r') as f : 
            self.settings = json.load(f)

    def update_settings(self, settings) : 
        self.settings = settings

    def change(self, atria, key, value) :
        if atria not in self.settings : 
            raise ValueError(f'{atria} not found in the settings')
        
        if key not in self.settings[atria] : 
            raise ValueError(f'{key} not found in the settings')
        
        self.settings[atria][key] = value

DEFAULT_BACHMANN_BUNDLE = {
    "FEC_height": 0.8,
    "LA": {
    	"phi_min": -0.54,
    	"phi_max": 2,
    	"z_min": 0.0,
    	"z_max": 0.71
    },
    "RA": {
    	"phi_min": -1.85,
    	"phi_max": 1.4,
    	"z_min": 0.0,
    	"z_max": 0.46
    }
}
class BachmannBundleSettings:
    def __init__(self) -> None:
        self.settings = DEFAULT_BACHMANN_BUNDLE.copy()

    def save_to_file(self, filename) : 
        filename += '.json' if not filename.endswith('.json') else ''
        with open(filename, 'w') as f : 
            json.dump(self.settings, f, indent=4)

    def load_from_file(self, filename) : 
        filename += '.json' if not filename.endswith('.json') else ''
        with open(filename, 'r') as f : 
            self.settings = json.load(f)

    def update_settings(self, settings) : 
        self.settings = settings

    def change(self, atria, key, value) : 
        if atria not in self.settings : 
            raise ValueError(f'{atria} not found in the settings')
        
        if key not in self.settings[atria] : 
            raise ValueError(f'{key} not found in the settings')
        
        self.settings[atria][key] = value

    def change_la(self, key, value) :
       self.change('LA', key, value)

    def change_ra(self, key, value) :
        self.change('RA', key, value)
    
    def change_fec(self, value) : 
        self.settings['FEC_height'] = value

DEFAULT_MESH_TAGS = {
	"LV": 1,
	"RV": 2,
	"LA": 3,
	"RA": 4,
	"Ao": 5,
	"PArt": 6,
	"MV": 7,
	"TV": 8,
	"AV": 9,
	"PV": 10,
	"LSPV": 11,
	"LIPV": 12,
	"RSPV": 13,
	"RIPV": 14,
	"LAA": 15,
	"SVC": 16,
	"IVC": 17,
	"LAA_ring": 18,
	"SVC_ring": 19,
	"IVC_ring": 20,
	"LSPV_ring": 21,
	"LIPV_ring": 22,
	"RSPV_ring": 23,
	"RIPV_ring": 24,
	"FEC_LV": 25,
	"BB": 26,
	"AV_plane": 27,
	"FEC_RV": 28,
	"FEC_SV": 29
}