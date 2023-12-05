# Docker README
> Instructions for using four-chamber mesh generation pipeline

## Install 
Install `docker` and then run the following:
```
docker pull cemrg/seg-4ch
```
Once finished, call the container without arguments to see if it worked: 
```
> docker run --rm cemrg/seg-4ch 

    usage: 
        Docker entrypoint: 

        USAGE:

            docker run --rm --volume=[path2points]:/data cermg/seg-4ch MODE [help] [options]

        path2points: path to the main directory

        Choose MODE from the following list:
            - origin or spacing (either do the same thing)
            - cylinders
            - svc_ivc
            - slicers
            - crop_svc_ivc
            - myo
            - valve_planes
            - clean_seg
            - labels

        Use the option 'help' to get the help page specific to each mode.
```

## Quick guide

The docker container has an entrypoint that handles all the works. You only need to run 
```
docker --rm --volume=/path/to/case/segmentations:/data MODE 
```

> Use `docker --rm --volume=/path/to/case/segmentations:/data MODE help` to see specifics on how to run.

Run the following modes in order: 
|   | MODE           | Required Arguments                 | Old pipeline script      |
|---|----------------|------------------------------------|--------------------------|
| 1 | `origin`       | `--output-file origin_spacing.txt` | `find_origin_spacing.py` |
| 2 | `cylinders`    |                                    | `create_cylinders.py`    |
| 3 | `svc_ivc`      |                                    | `create_svc_ivc.py`      |
| 4 | `slicers`      |                                    | `create_slicers.py`      |
| 5 | `crop`         |                                    | `crop_svc_ivc.py`        |
| 6 | `myo`          |                                    | `create_myo.py`          |
| 7 | `valve_planes` |                                    | `create_valve_planes.py` |
| 8 | `clean_seg`    |                                    | `clean_seg.py`           |

## Full explanation for segmentation

1. Prepare your working folder `/path/to/case`, create a folder `segmentations` inside
2. Copy “points.txt”, “labels.txt”, “origin_spacing.txt” 
3. Move end-diastolic image CT image into folder and call that directory `ct`
4. Move segmented CT into "segmentations" folder.
5. Manually split and relabel pulmonary veins. You can use CemrgApp for this
6. Export the segmentation as `seg_corrected.nrrd` with the new tags 
        LSPV = 8
        LIPV = 9
        RSPV = 10
        RIPV = 11
        LAA = 12

> you can use another name for seg_corrected, as the container allows the user to set the name

Your folder should look like this: 
    + `/path/to/case/` 
      + `segmentations/`
        + `ct/`
        + `seg_corrected.nrrd`

1. **Run** `docker run --rm --volume=/path/to/case/segmentations:/data origin --output-file origin_spacing.txt` 

2.  **Run** `docker run --rm --volume=/path/to/case/segmentations:/data cylinders `

3.  **Run** `docker run --rm --volume=/path/to/case/segmentations:/data svc_ivc `

4.  **Run** `docker run --rm --volume=/path/to/case/segmentations:/data slicers ` 

5.  **Run** `docker run --rm --volume=/path/to/case/segmentations:/data crop `
    
6.  **Run** `docker run --rm --volume=/path/to/case/segmentations:/data myo `
    
7.  **Run** `docker run --rm --volume=/path/to/case/segmentations:/data valve_planes `

8.  **Run** `docker run --rm --volume=/path/to/case/segmentations:/data clean_seg`
    
9.  Load .nrrd and manually clean valve ring

10. Export segmentation as “seg_final.nrrd”

11. **Run** `segSmoothing.sh /heart_folder/segmentations`

## Meshing

1. **Run** `meshing.py /heart_folder`

2. cd into the meshing folder (inside heart folder)
3. **Run** `bash generate_heart_mesh_Cesare.sh`

4. **Run** `bash mesh_post.sh /heart_folder` 
   
>  watch out mesh tool path currently hard-coded 














