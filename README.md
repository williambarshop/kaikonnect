# Kaikonnect
A wrapper to server as an interconnect between Kaiko and TagGraph for open modification searching.
Thanks to the structures of Kaiko and TagGraph, Kaikonnect is capable of taking in several .mzML or Thermo .raw simultaneously for joint analysis.

## Prerequisites:
1. Docker
2. Python 2.7
3. optparse for python 2.7 (this should be installed automatically via pip during execution if not found)

### First, clone the repo:
``` git clone https://github.com/wohllab/kaikonnect ```

and change into the new directory...

``` cd kaikonnect/ ```

### Second, docker builds and downloads:
This interconnect will bind Kaiko (the PNNL variant of DeepNovo) and the Elias lab's TagGraph softwares together.
Accordingly, both will need to be downloaded.  For Kaiko, we will also download the default model from MassIVE over FTP.  If you are attempting to connect from within a controlled environment, you may find it necessary to stage the model manually.  Please refer to the ``` tag_grab.sh ``` script for the relevant URLs.

To download all necessary components, and build the docker images, run:
``` sh tag_grab.sh ```

When prompted, enter root password to elevate access for "sudo" commands.  This is necessary to build docker images, unless your user has been granted special permissions.

### Third, let's execute Kaikonnect!
If using Thermo instrument data, Kaikonnect will use the available pwiz docker image to convert the raw data to mzML through msconvert under wine.  Otherwise, we can take in mzML files directly.  In all cases, users are required to provide the mzML_folder argument.  This argument will either be used as the data input, or as the mzML file output after conversion.

An example command line, with the provided data **(staged when running tag_grab.sh)**:

``` python kaikonnect.py --mzML_folder example/mzml_files/ --output_folder test_output/ --fasta example/ex.fasta ```

For additional configuration options, run:
```
$ python kaikonnect.py --help
Usage: kaikonnect.py [options]

Options:
  -h, --help            show this help message and exit
  -s, --no_sudo
  -r RAW_FOLDER, --raw_folder=RAW_FOLDER
  -m MZML_FOLDER, --mzML_folder=MZML_FOLDER
  -o OUTPUT_FOLDER, --output_folder=OUTPUT_FOLDER
  --kaiko_topk=KAIKO_TOPK
  --kaiko_beam_size=KAIKO_BEAM_SIZE
  -f FASTA, --fasta=FASTA
  --tg_per_fraction
  --tg_FDR_cutoff=TG_FDRCUTOFF
  --tg_logEM_cutoff=TG_LOGEMCUTOFF
  --tg_Display_Protein_Num=TG_DISPLAYPROTEINNUM
  --tg_ExperimentName=TG_EXPERIMENTNAME ```
