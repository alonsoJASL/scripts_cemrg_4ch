# FOUR-CHAMBER EXAMPLE FOR UNIVERSAL ATRIAL COORDINATES AND FIBRE MAPPING

Download the mesh for the example here (ask for access):

https://www.dropbox.com/scl/fo/mcyolm81t5zp0gt7ixka0/h?dl=0&rlkey=hdwqu0ru2a8irn5gqj4ai6wkj

This is mesh01 from my four-chamber heart failure cohort. 

# Step 0 - bash 0_convert_surfaces.sh

This extracts the atria and all the surfaces and landmarks you need for the universal atrial coordinates (UACs). 
If you are running this for the first time, the right atrial appendage apex will be selected automatically. 
However, because this is not always great, you can select the RAA apex manually (for instance on Paraview),
save the coordinates in a file and re-run the code above, making sure the flag --raa_apex_file points to
the file you just saved. When you re-run the code, it will ask you if you want to re-compute only the 
RAA base. Say 'y' and the code will replace the automatically selected apex with the one you selected 
and will recompute the RAA base accordingly. Now you are good to go with the UACs

# Step 1 - bash 1_la_4ch_endo.sh /path/to/folder/

For this step, you need to have access to the CEMRG docker (speak to Jose about that). You can then login 
into docker and run this script, where /path/to/folder/ is the FULL path to the folder with LA_endo and 
RA_endo folders, created above.

This will compute UACs on the LA endo and map both endocardial and epicardial fibres onto it. This will also map
the Bachmann bundle. 

# Step 2 - bash 2_ra_4ch_endo.sh /path/to/folder/

For this step, you need to have access to the CEMRG docker (speak to Jose about that). You can then login 
into docker and run this script, where /path/to/folder/ is the FULL path to the folder with LA_endo and 
RA_endo folders, created above.

This will compute UACs on the RA endo and map both endocardial and epicardial fibres onto it. This will also map
the Bachmann bundle, crista terminalis, pectinate muscles and sinoatrial node. 

# Step 3 - bash 3_map_2d_to_3d.sh

This will map the mesh from the endocardium to the 3D mesh (both LA and RA), will generate the sheet direction
and will remap back to the biatrial mesh and to the four-chamber mesh.

Check the VTK files with Paraview. You should be all done.

Take time to check the parfiles folder, especially the file input_tags_setup.json, where the code looks at the 
tags on the four-chamber mesh to extract all surfaces. If these are not setup correctly, the code won't work.
