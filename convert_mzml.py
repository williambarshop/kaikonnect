import pandas as pd
import sys
import re
import time
from pyteomics import mzml,auxiliary
import gzip
import glob
import os
import sys
import time
import os.path

input_folder="."

def inspect_mzML_file(fpath):
    spectra = []
    #with gzip.open(fpath, 'rb') as f:
    for obj in mzml.read(fpath):
        spectra.append(obj)
    return spectra

def inspect_mgf_file(fpath):
    start_line = "BEGIN IONS"
    end_line = "END IONS"
    spectra_location = []
    with open(fpath, mode="r") as f:
        line = True
        while line:
            _location = f.tell()
            line = f.readline()
            if start_line in line:
                spectra_location.append(_location)
                while end_line not in line:
                    line = f.readline()
    return spectra_location


def generate_mgf_without_annotation(mzml_spectra, file_index=0, out_file='out.mgf'):
    num_spectra = 0
    with open(out_file, 'w') as f:
        for spectrum in mzml_spectra:
            if spectrum['ms level'] != 2:
                continue
            scan = int(spectrum['id'].split('scan=')[1])
            try:
            
                mz_arr = spectrum['m/z array']
                int_arr = spectrum['intensity array']
                rtsec = 60.0*(spectrum['scanList']['scan'][0]['scan start time'])
                selectedIon = spectrum['precursorList']['precursor'][0]['selectedIonList']['selectedIon'][0]

                assert len(mz_arr) == len(int_arr), "[ERR] Wrong data format: len(mz_arr) != len(int_arr)"

                print("BEGIN IONS", file=f)
                print("TITLE={0}.{1}".format(file_index, scan), file=f)
                print("PEPMASS={0}".format(selectedIon['selected ion m/z']), file=f)
                # sometimes they don't have a charge info. if so, we use the annotation file
                if 'charge state' in selectedIon:
                    print("CHARGE={0:d}+".format(int(selectedIon['charge state'])), file=f)
                else:
                    print("CHARGE={0:d}+".format(999), file=f)
                print("SCANS={0}:{1}".format(file_index, scan), file=f)
                print("RTINSECONDS={0}".format(rtsec), file=f)
                print("SEQ=UNKNOWN", file=f)
                for i in range(len(mz_arr)):
                    print("{0} {1}".format(mz_arr[i], int_arr[i]), file=f)
                print("END IONS", file=f)
                num_spectra += 1
            except:
                print('[ERR]', scan, spectrum)
                continue
                    
        return num_spectra

def generate_mgf_files(data_dir, dest_dir='./'):
    # collect mzML files
    mzML_files = glob.glob(data_dir + "/*.mzML")
    
    mzML_log_handler = open(dest_dir + '/mgf_list.log', 'w')
    print("id\tmgf_file\tnum_scans\ttotal_scans", file=mzML_log_handler)
    
    start_time = time.time()
    num_mzML_files = len(mzML_files)
    total_scans = 0
    for i, mzML_file in enumerate(mzML_files):
#         if i < 207: continue  ## for debugging
#         if i > 207: break
        common_name = os.path.basename(mzML_file).rsplit('.mzML.gz')[0]
    
        if os.path.exists(dest_dir + '/' + common_name + '.mgf'):
            print('[{0:3d}/{1:3d}] {2}, Already exists' \
                  .format(i+1,
                          num_mzML_files,
                          common_name))
            continue
            
    
        seq_file = glob.glob(data_dir + '/' + common_name + "*.txt")
        msg = ""
        scan_ids = []
        num_spectra = 0
        mzml_spectra = inspect_mzML_file(mzML_file)
        
        if len(seq_file) == 1:    
            annotated = get_annotated_pepseq(seq_file[0])
            scan_ids = list(annotated.Scan)
            pepseqs = list(annotated.pepseq)
            charges = list(annotated.Charge)
            num_scans = len(scan_ids)
            num_spectra = generate_mgf(mzml_spectra,
                                       scan_ids,
                                       pepseqs,
                                       charges,
                                       file_index = i,
                                       out_file=dest_dir + '/' + common_name + '.mgf')
        else:
            num_spectra = generate_mgf_without_annotation(mzml_spectra,
                                                          file_index=i,
                                                          out_file=dest_dir + '/' + common_name + '.mgf')
            num_scans = num_spectra
        total_scans += num_spectra
        msg = "SUCCESS"
        print('[{0:3d}/{1:3d}] {2}, {3:d}/{4:d}/{5:d}, {6:.2f}sec' \
                  .format(i+1,
                          num_mzML_files,
                          common_name,
                          num_spectra,
                          num_scans,
                          total_scans,
                          time.time()-start_time))
        print("{0}\t{1}\t{2}\t{3}".format(i, common_name, num_spectra, total_scans), file=mzML_log_handler)
        sys.stdout.flush()

generate_mgf_files(input_folder)
