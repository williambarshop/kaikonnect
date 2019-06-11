import pandas
import os
import glob
import collections
import sys
from tqdm.autonotebook import tqdm
from pyteomics import mzml
from pyteomics import mass

input_path="/kaiko_output/"
output_path="/kaiko_output/taggraph_input/"

if not os.path.isdir(output_path):
    try:
        os.mkdir(output_path)
    except:
        print "\n\n\nERROR: Failed to make directory {0}".format(output_path)
        sys.exit(2)


#To read mzML files for scan trigger m/z's
def ingest_mzML(input_file):
    #mzml_reader=mzml.read(input_file.split(".",1)[0]+".mzml",iterative=True)
    mzml_reader=mzml.read(input_file.split(".",1)[0]+".mzML",iterative=True)
    parsed_scans=[]
    for each_scan in tqdm(mzml_reader):
        if each_scan['ms level']==2:
            this_scan={}
            this_scan['scan']=int(each_scan['index'])+1
            this_scan['z']=each_scan['precursorList']['precursor'][0]['selectedIonList']['selectedIon'][0]['charge state']
            this_scan['m/z']=each_scan['precursorList']['precursor'][0]['selectedIonList']['selectedIon'][0]['selected ion m/z']
            this_scan["RT"]=each_scan['scanList']['scan'][0]['scan start time']
            parsed_scans.append(this_scan)
            #this_dataset=this_group.create_dataset(str(each_scan['index']),compression="gzip",compression_opts=9,dtype="float32",data=numpy.column_stack((each_scan['m/z array'],each_scan['intensity array'])).T)
            #this_dataset.attrs["scan_index"]=each_scan['index']
    print "done reading from with file {0}".format(input_file)
    new_df=pandas.DataFrame(parsed_scans)
    del mzml_reader
    return new_df

#We will only support the default search modifications used similarly with PEAKS
def convert_sequence(input_seq_str):
    output_seq_str=input_seq_str
    output_seq_str=output_seq_str.replace("Mmod","M(+15.99)")
    output_seq_str=output_seq_str.replace("Cmod","C(+57.02)")
    output_seq_str=output_seq_str.replace(",","")
    return output_seq_str

def generate_mod_list(input_seq_str):
    mod_list=[]
    for x in input_seq_str.split(","):
        if "Mmod" in x:
            mod_list.append("Oxidation (M)")
            continue
        elif "Cmod" in x:
            mod_list.append("Carbamidomethylation")
            continue
    return "; ".join(mod_list)


def convert_row(input_row):
    output_row=input_row
    #print output_row.keys()
    recon_row=collections.OrderedDict()
    recon_row["Fraction"]="%02d" % (int(output_row['scan_x'].split(":")[0]))
    recon_row["Scan"]=output_row['scan_x'].split(":")[1]
    recon_row["Source File"]=output_row["File"].split(".",1)[0]+".mzML"
    try:
        recon_row["Peptide"]=convert_sequence(output_row["output_seq"])
    except Exception as e:
        return None
    recon_row["Tag Length"]=output_row["output_seq"].count(",")+1  #Actually just length
    recon_row["ALC (%)"]=output_row["output_score"]
    recon_row["length"]=output_row["output_seq"].count(",")+1
    recon_row["m/z"]=float(input_row['m/z'])
    recon_row["z"]=int(input_row['z'])
    recon_row["RT"]=input_row['RT']
    ### THESE DO NOT SEEM TO BE CONSUMED BY TAGGRAPH ###
    recon_row["Area"]=""
    recon_row["Mass"]=""
    recon_row["ppm"]=""
    ### BUT THOSE BELOW HERE ARE... ###
    recon_row["PTM"]=generate_mod_list(output_row["output_seq"])
    recon_row["local confidence (%)"]=" ".join(["50"]*(recon_row["length"])) # These are placeholders. Kaiko does not provide this.
    recon_row["tag (>=0%)"]=""
    recon_row["mode"]="HCD" #Fixed for now...
    
    return recon_row#",".join([str(x) for x in output_row.tolist()])

data_frames=[]
os.chdir(input_path)
for each_file in tqdm(glob.glob("*.mzML_out.txt")):
#for each_file in tqdm(glob.glob("*.mzml_out.txt")):
    print "Handling file \"{0}\"...".format(each_file)
    #data_frames[each_file]=
    this_df=pandas.read_csv(each_file,sep="\t")
    this_df["File"]=each_file
    this_df["scan_number"]=this_df["scan"].str.split(":").str.get(1)
    this_df["scan_number"]=this_df["scan_number"].astype(int)
    ingestion_output=ingest_mzML(each_file)
    
    merged_df=this_df.merge(ingestion_output,how='inner',right_on='scan',left_on="scan_number")
    data_frames.append(merged_df)
combined_df=pandas.concat(data_frames)#from_dict(data_frames,orient="index")


new_rows=[]#We actually want all the fractions into a single file

for each_file in tqdm(combined_df['File'].unique()):
    df_view=combined_df[combined_df["File"]==each_file]
    for index,each_row in tqdm(df_view.iterrows(),total=df_view.shape[0]):
        out_row=convert_row(each_row)
        if out_row is None:
            continue
        new_rows.append(out_row)
    #final_df.to_csv(each_file+"_mockPEAKS.csv")
final_df=pandas.DataFrame(new_rows)
final_df.to_csv(os.path.join(output_path,"combined_mockPEAKS_input.csv"))
