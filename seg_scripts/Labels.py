import json

class Labels:
    def __init__(self, filename=None, scale_factor=1/0.39844):
        self.scale_factor = scale_factor
        
        self.valve_WT_multiplier = 4
        self.valve_WT_svc_ivc_multiplier = 4
        self.ring_thickness_multiplier = 4
        self.LV_neck_WT_multiplier = 2.00
        self.RV_WT_multiplier = 3.50
        self.LA_WT_multiplier = 2.00
        self.RA_WT_multiplier = 2.00
        self.Ao_WT_multiplier = 2.00
        self.PArt_WT_multiplier = 2.00

        self.set_wt_params()

        self.LV_BP_label = 1
        self.LV_myo_label = 2
        self.RV_BP_label = 3
        self.LA_BP_label = 4
        self.RA_BP_label = 5
        self.Ao_BP_label = 6
        self.PArt_BP_label = 7
        self.LPV1_label = 8
        self.LPV2_label = 9
        self.RPV1_label = 10
        self.RPV2_label = 11
        self.LAA_label = 12
        self.SVC_label = 13
        self.IVC_label = 14
        self.LV_neck_label = 101
        self.RV_myo_label = 103
        self.LA_myo_label = 104
        self.RA_myo_label = 105
        self.Ao_wall_label = 106
        self.PArt_wall_label = 107
        self.MV_label = 201
        self.TV_label = 202
        self.AV_label = 203
        self.PV_label = 204
        self.plane_LPV1_label = 205
        self.plane_LPV2_label = 206
        self.plane_RPV1_label = 207
        self.plane_RPV2_label = 208
        self.plane_LAA_label = 209
        self.plane_SVC_label = 210
        self.plane_IVC_label = 211
        self.LPV1_ring_label = 221
        self.LPV2_ring_label = 222
        self.RPV1_ring_label = 223
        self.RPV2_ring_label = 224
        self.LAA_ring_label = 225
        self.SVC_ring_label = 226
        self.IVC_ring_label = 227
        if filename is not None:
            self.load(filename)

    def set_wt_params(self) : 
        self.valve_WT = self.scale_factor * self.valve_WT_multiplier
        self.valve_WT_svc_ivc = self.scale_factor * self.valve_WT_svc_ivc_multiplier
        self.ring_thickness = self.scale_factor * self.ring_thickness_multiplier
        self.LV_neck_WT = self.scale_factor * self.LV_neck_WT_multiplier
        self.RV_WT = self.scale_factor * self.RV_WT_multiplier
        self.LA_WT = self.scale_factor * self.LA_WT_multiplier
        self.RA_WT = self.scale_factor * self.RA_WT_multiplier
        self.Ao_WT = self.scale_factor * self.Ao_WT_multiplier
        self.PArt_WT = self.scale_factor * self.PArt_WT_multiplier


    def load(self, filename):
        with open(filename) as f:
            data = json.load(f)
        self.valve_WT = data.get('valve_WT', self.valve_WT)
        self.valve_WT_svc_ivc = data.get('valve_WT_svc_ivc', self.valve_WT_svc_ivc)
        self.ring_thickness = data.get('ring_thickness', self.ring_thickness)
        self.LV_neck_WT = data.get('LV_neck_WT', self.LV_neck_WT)
        self.RV_WT = data.get('RV_WT', self.RV_WT)
        self.LA_WT = data.get('LA_WT', self.LA_WT)
        self.RA_WT = data.get('RA_WT', self.RA_WT)
        self.Ao_WT = data.get('Ao_WT', self.Ao_WT)
        self.PArt_WT = data.get('PArt_WT', self.PArt_WT)

        self.LV_BP_label = data.get('LV_BP_label', self.LV_BP_label)
        self.LV_myo_label = data.get('LV_myo_label', self.LV_myo_label)
        self.RV_BP_label = data.get('RV_BP_label', self.RV_BP_label)
        self.LA_BP_label = data.get('LA_BP_label', self.LA_BP_label)
        self.RA_BP_label = data.get('RA_BP_label', self.RA_BP_label)
        self.Ao_BP_label = data.get('Ao_BP_label', self.Ao_BP_label)
        self.PArt_BP_label = data.get('PArt_BP_label', self.PArt_BP_label)
        self.LPV1_label = data.get('LPV1_label', self.LPV1_label)
        self.LPV2_label = data.get('LPV2_label', self.LPV2_label)
        self.RPV1_label = data.get('RPV1_label', self.RPV1_label)
        self.RPV2_label = data.get('RPV2_label', self.RPV2_label)
        self.LAA_label = data.get('LAA_label', self.LAA_label)
        self.SVC_label = data.get('SVC_label', self.SVC_label)
        self.IVC_label = data.get('IVC_label', self.IVC_label)
        self.LV_neck_label = data.get('LV_neck_label', self.LV_neck_label)
        self.RV_myo_label = data.get('RV_myo_label', self.RV_myo_label)
        self.LA_myo_label = data.get('LA_myo_label', self.LA_myo_label)
        self.RA_myo_label = data.get('RA_myo_label', self.RA_myo_label)
        self.Ao_wall_label = data.get('Ao_wall_label', self.Ao_wall_label)
        self.PArt_wall_label = data.get('PArt_wall_label', self.PArt_wall_label)
        self.MV_label = data.get('MV_label', self.MV_label)
        self.TV_label = data.get('TV_label', self.TV_label)
        self.AV_label = data.get('AV_label', self.AV_label)
        self.PV_label = data.get('PV_label', self.PV_label)
        self.plane_LPV1_label = data.get('plane_LPV1_label', self.plane_LPV1_label)
        self.plane_LPV2_label = data.get('plane_LPV2_label', self.plane_LPV2_label)
        self.plane_RPV1_label = data.get('plane_RPV1_label', self.plane_RPV1_label)
        self.plane_RPV2_label = data.get('plane_RPV2_label', self.plane_RPV2_label)
        self.plane_LAA_label = data.get('plane_LAA_label', self.plane_LAA_label)
        self.plane_SVC_label = data.get('plane_SVC_label', self.plane_SVC_label)
        self.plane_IVC_label = data.get('plane_IVC_label', self.plane_IVC_label)
        self.LPV1_ring_label = data.get('LPV1_ring_label', self.LPV1_ring_label)
        self.LPV2_ring_label = data.get('LPV2_ring_label', self.LPV2_ring_label)
        self.RPV1_ring_label = data.get('RPV1_ring_label', self.RPV1_ring_label)
        self.RPV2_ring_label = data.get('RPV2_ring_label', self.RPV2_ring_label)
        self.LAA_ring_label = data.get('LAA_ring_label', self.LAA_ring_label)
        self.SVC_ring_label = data.get('SVC_ring_label', self.SVC_ring_label)
        self.IVC_ring_label = data.get('IVC_ring_label', self.IVC_ring_label)

    def load_wt_params(self, filename_wt): 
        with open(filename_wt, 'r') as f:
            data = json.load(f)
        self.scale_factor = data.get('scale_factor', self.scale_factor)

        self.valve_WT_multiplier = data.get('valve_WT_multiplier', self.valve_WT_multiplier)
        self.valve_WT_svc_ivc_multiplier = data.get('valve_WT_svc_ivc_multiplier', self.valve_WT_svc_ivc_multiplier)
        self.ring_thickness_multiplier = data.get('ring_thickness_multiplier', self.ring_thickness_multiplier)
        self.LV_neck_WT_multiplier = data.get('LV_neck_WT_multiplier', self.LV_neck_WT_multiplier)
        self.RV_WT_multiplier = data.get('RV_WT_multiplier', self.RV_WT_multiplier)
        self.LA_WT_multiplier = data.get('LA_WT_multiplier', self.LA_WT_multiplier)
        self.RA_WT_multiplier = data.get('RA_WT_multiplier', self.RA_WT_multiplier)
        self.Ao_WT_multiplier = data.get('Ao_WT_multiplier', self.Ao_WT_multiplier)
        self.PArt_WT_multiplier = data.get('PArt_WT_multiplier', self.PArt_WT_multiplier)

        self.set_wt_params() 

    def get_dictionary(self) :
        data = {
            'scale_factor': self.scale_factor,
            'valve_WT': self.valve_WT,
            'valve_WT_svc_ivc': self.valve_WT_svc_ivc,
            'ring_thickness': self.ring_thickness,
            'LV_neck_WT': self.LV_neck_WT,
            'RV_WT': self.RV_WT,
            'LA_WT': self.LA_WT,
            'RA_WT': self.RA_WT,
            'Ao_WT': self.Ao_WT,
            'PArt_WT': self.PArt_WT,
            'LV_BP_label': self.LV_BP_label,
            'LV_myo_label': self.LV_myo_label,
            'RV_BP_label': self.RV_BP_label,
            'LA_BP_label': self.LA_BP_label,
            'RA_BP_label': self.RA_BP_label,
            'Ao_BP_label': self.Ao_BP_label,
            'PArt_BP_label': self.PArt_BP_label,
            'LPV1_label': self.LPV1_label,
            'LPV2_label': self.LPV2_label,
            'RPV1_label': self.RPV1_label,
            'RPV2_label': self.RPV2_label,
            'LAA_label': self.LAA_label,
            'SVC_label': self.SVC_label,
            'IVC_label': self.IVC_label,
            'LV_neck_label': self.LV_neck_label,
            'RV_myo_label': self.RV_myo_label,
            'LA_myo_label': self.LA_myo_label,
            'RA_myo_label': self.RA_myo_label,
            'Ao_wall_label': self.Ao_wall_label,
            'PArt_wall_label': self.PArt_wall_label,
            'MV_label': self.MV_label,
            'TV_label': self.TV_label,
            'AV_label': self.AV_label,
            'PV_label': self.PV_label,
            'plane_LPV1_label': self.plane_LPV1_label,
            'plane_LPV2_label': self.plane_LPV2_label,
            'plane_RPV1_label': self.plane_RPV1_label,
            'plane_RPV2_label': self.plane_RPV2_label,
            'plane_LAA_label': self.plane_LAA_label,
            'plane_SVC_label': self.plane_SVC_label,
            'plane_IVC_label': self.plane_IVC_label,
            'LPV1_ring_label': self.LPV1_ring_label,
            'LPV2_ring_label': self.LPV2_ring_label,
            'RPV1_ring_label': self.RPV1_ring_label,
            'RPV2_ring_label': self.RPV2_ring_label,
            'LAA_ring_label': self.LAA_ring_label,
            'SVC_ring_label': self.SVC_ring_label,
            'IVC_ring_label': self.IVC_ring_label,
        }
        return data
    
    def print(self) :
        data = self.get_dictionary()
        for k, v in data.items() :
            print(f"{k}: {v}")
    
    def print_label_explanation(self) :
        data = self.get_dictionary()
        print("LABELS:")
        expl= ["Wall thickness Scale factor",
            "Valve wall thickness",
            "Valve wall thickness SVC/IVC",
            "Ring thickness",
            "LV neck wall thickness",
            "RV wall thickness",
            "LA wall thickness",
            "RA wall thickness",
            "Ao wall thickness",
            "PArt wall thickness",
            "LV blood pool",
            "LV myocardium",
            "RV blood pool",
            "LA blood pool",
            "RA blood pool",
            "Ao blood pool",
            "PArt blood pool",
            "LPV1",
            "LPV2",
            "RPV1",
            "RPV2",
            "LAA",
            "SVC",
            "IVC",
            "LV neck",
            "RV myocardium",
            "LA myocardium",
            "RA myocardium",
            "Ao wall",
            "PArt wall",
            "MV",
            "TV",
            "AV",
            "PV",
            "plane LPV1",
            "plane LPV2",
            "plane RPV1",
            "plane RPV2",
            "plane LAA",
            "plane SVC",
            "plane IVC",
            "LPV1 ring",
            "LPV2 ring",
            "RPV1 ring",
            "RPV2 ring",
            "LAA ring",
            "SVC ring",
            "IVC ring"]
        
        for ix, k in enumerate(data.keys()) :
            print(f"{k}: {expl[ix]}")

    def save(self, filename):
        data = self.get_dictionary()
        with open(filename, 'w') as f:
            json.dump(data, f)