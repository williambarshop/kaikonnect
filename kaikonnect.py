import os, shutil, glob, sys, subprocess, importlib, time

#From stackoverflow #12332975
def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

package_list=["optparse"]  #Packages users may be unlikely to have....

for each_package in package_list:
    try:
        #import optparse
        globals()[each_package]=importlib.import_module(each_package)
    except Exception as e:
        print e
        #Let's make sure we have the packages we need here to start...
        print "Making sure that package \"{0}\" is installed...".format(each_package)
        install(each_package)
        globals()[each_package]=importlib.import_module(each_package)



parser = optparse.OptionParser()
parser.add_option("-s","--no_sudo",action="store_false",dest="no_sudo",default=False) #False means don't use sudo.  This will depend on how users are given permission to access the docker host
parser.add_option("-r","--raw_folder",action="store",type="string",dest="raw_folder") #If this has a value, we'll convert Thermo raw files to mzML using a docker container and place them inside the mzml folder
parser.add_option("-m","--mzML_folder",action="store",type="string",dest="mzml_folder")
parser.add_option("-o","--output_folder",action="store",type="string",dest="output_folder")


#KAIKO OPTIONS
parser.add_option("--kaiko_topk",action="store",type="int",dest="kaiko_topk",default=1)
parser.add_option("--kaiko_beam_size",action="store",type="int",dest="kaiko_beam_size",default=5)


#TAG_GRAPH OPTIONS
parser.add_option("-f","--fasta",action="store",type="string",dest="fasta")

parser.add_option("--tg_per_fraction",action="store_true",dest="tg_outputPerFraction",default=False)
parser.add_option("--tg_FDR_cutoff",action="store",type="float",dest="tg_FDRCutoff",default=0.01)
parser.add_option("--tg_logEM_cutoff",action="store",type="int",dest="tg_logEMCutoff",default=2)
parser.add_option("--tg_Display_Protein_Num",action="store",type="int",dest="tg_DisplayProteinNum",default=3)
parser.add_option("--tg_ExperimentName",action="store",type="string",dest="tg_ExperimentName",default="Expt_{0}".format(time.strftime("%Y-%m-%d_%H-%M")))


(options,args) = parser.parse_args()



def makeDirCheck(dir_to_make): #Helper function for making directories if they don't exist....
    if not os.path.isdir(dir_to_make):
        try:
            os.mkdir(dir_to_make)
        except:
            print "\n\nERROR: Failed to make directory {0} !\nPlease ensure that you have rights to make this directory, or that it isn\'t a file already.".format(dir_to_make)




#Let's establish the starting directory...
starting_dir=os.getcwd()

#Check if we'll be using sudo...
if options.no_sudo:
    sudo_str=""
else:
    sudo_str="sudo "

if options.fasta is None:
    print "\n\nERROR: You'll need to supply a fasta location via \"--fasta {value}\""
    sys.exit(2)

#### CHECK FOR REQUIRED FOLDERS AND OPTIONS ####

#Check to make sure an mzML folder is supplied-- at least -- and if it doesn't exist, let's go ahead and make it
if options.mzml_folder is None:
    print "\n\nERROR: You'll need to supply an mzML folder location via \"--mzML_folder {value}\""
    sys.exit(2)
else:
    makeDirCheck(options.mzml_folder)
#    if not os.path.isdir(options.mzml_folder):
#        try:
#            os.mkdir(options.mzml_folder)
#        except:
#            print "\n\nERROR: Failed to make directory {0} !\nPlease ensure that you have rights to make this directory, or that it isn\'t a file already.".format(options.mzml_folder)

os.chdir(options.mzml_folder)
full_mzml_dir=os.getcwd() #For later reference...
os.chdir(starting_dir)


#Check to make sure an output folder is supplied-- at least -- and if it doesn't exist, let's go ahead and make it
if options.output_folder is None:
    print "\n\nERROR: You'll need to supply an output folder location via \"--output_folder {value}\""
    sys.exit(2)
else:
    makeDirCheck(options.output_folder)
#    if not os.path.isdir(options.output_folder):
#        try:
#            os.mkdir(options.output_folder)
#        except:
#            print "\n\nERROR: Failed to make directory {0} !\nPlease ensure that you have rights to make this directory, or that it isn\'t a file already.".format(options.output_folder)

os.chdir(options.output_folder)
full_output_dir=os.getcwd() #For later reference...
os.chdir(starting_dir)




#### HANDLE THERMO RAW CONVERSION ####

if options.raw_folder is not None:
    print "\n\n\nPROGRESS: We're going to start by converting your Thermo raw files to mzML and place the output in the mzML folder...\n\n\n"
    os.chdir(options.raw_folder)
    full_raw_path=os.getcwd()
    for each_raw in glob.glob("*.raw"):
        print "PROGRESS: Going to execute...","{0}docker run --rm -e WINEDEBUG=-all -v {1}:/data chambm/pwiz-skyline-i-agree-to-the-vendor-licenses wine msconvert {2}".format(sudo_str, full_raw_path, each_raw)
        os.system("{0}docker run --rm -e WINEDEBUG=-all -v {1}:/data chambm/pwiz-skyline-i-agree-to-the-vendor-licenses wine msconvert {2}".format(sudo_str, full_raw_path, each_raw))
        os.rename(each_raw.rsplit(".",1)[0]+".mzML",os.path.join(full_mzml_dir,each_raw.rsplit(".",1)[0]+".mzML"))
    os.chdir(starting_dir)





#Alright, let's get things moving.  We're going to generate our mgf files from the mzml inputs.
print "\n\n\nPROGRESS: We're going to convert the mzML files to mgf files...\n\n\n"
os.chdir(full_mzml_dir)
full_path_mzml=os.getcwd()
cmd_str_tmp="{0}docker run --rm -v {1}:/mzml_input/ kaikonnect bash -c \"source activate python3 && python /kaikonnect/convert_mzml.py\"".format(sudo_str, full_mzml_dir)
print "\n\n\nPROGRESS: About to execute command : ",cmd_str_tmp,"\n\n\n"
os.system(cmd_str_tmp)
#os.system("{0}docker run -v {1}:/mzml_input/ kaikonnect /bin/bash -c \"source python3 && python /kaikonnect/convert_mzml.py\"".format(sudo_str, full_mzml_dir))
#Move mgf file(s) to output dir... Will feed to Kaiko...
for each_mgf in glob.glob("*.mgf"):
    os.rename(each_mgf,os.path.join(full_output_dir,each_mgf))
os.chdir(starting_dir)

print "\n\n\nPROGRESS: All done with mgf conversion from mzML!"



#### KAIKO DENOVO SEQUENCING EXECUTION ####

print "\n\n\nPROGRESS: Let's move on to working with the outputs for searching with Kaiko."

if not os.path.isdir(os.path.join(starting_dir,"Kaiko/")):
    print "\n\nERROR: We can't find the Kaiko folder! Please make sure:\n1. You are running this script from the kaikonnect basedir folder\n2. You have run the \'tag_grab.sh\' setup script!"
    sys.exit(2)

print "\n\n\n=================== Kaiko Execution is now starting. ===================\n\n\n"



makeDirCheck(os.path.join(full_output_dir,"decode_output/"))
#if not os.path.isdir(os.path.join(full_output_dir,"decode_output/")):
#    try:
#        os.mkdir(os.path.join(full_output_dir,"decode_output/"))
#    except:
#        print "\n\nERROR: Failed to make directory {0} !\nPlease ensure that you have rights to make this directory, or that it isn\'t a file already.".format(os.path.join(full_output_dir,"decode_output/"))


tmp_cmd_str="{0}docker run --rm -v {1}:/app/model -v {2}:/app/mgf_input -v {2}/decode_output:/app/decode_output kaiko /bin/bash -c \"python ./src/kaiko_main.py --mgf_dir mgf_input/ --train_dir model/ --multi_decode --beam_search --beam_size {3} --topk {4}\"".format(sudo_str,os.path.join(starting_dir,"Kaiko/model/"),full_output_dir,options.kaiko_beam_size,options.kaiko_topk)
print "About to execute command {0}".format(tmp_cmd_str)
os.system(tmp_cmd_str)
print "\n\n\n=================== Kaiko Execution has now finished ===================\n\n\n"

print "\n\n\n=================== Starting file conversion to PEAKS style csv ===================\n\n\n"

os.chdir(starting_dir)
full_path_mzml=os.getcwd()
###We're going to copy the mzML files over to the output dir of kaikonnect, which right now is the decode_output folder from Kaiko.
for each_mzml in glob.glob(os.path.join(full_mzml_dir,"*.mzML")):
    shutil.copy(each_mzml,os.path.join(os.path.join(full_output_dir,"decode_output/"),each_mzml.rsplit("/",1)[1]))

### And we're going to make a folder for the converted TagGraph inputs to be dumped...
#For later reference...
tg_input_dir=os.path.join(full_output_dir,"decode_output/taggraph_input/")
makeDirCheck(tg_input_dir)

#if not os.path.isdir(os.path.join(full_output_dir,"decode_output/taggraph_input/")):
#    try:
#        os.mkdir(os.path.join(full_output_dir,"decode_output/taggraph_input/"))
#    except:
#        print "\n\nERROR: Failed to make directory {0} !\nPlease ensure that you have rights to make this directory, or that it isn\'t a file already.".format(os.path.join(full_output_dir,"decode_output/taggraph_input/"))

cmd_str_tmp="{0}docker run --rm -v {1}/decode_output/:/kaiko_output/ kaikonnect bash -c \"source activate python2 && python /kaikonnect/taggraph_interconnect.py\"".format(sudo_str, full_output_dir)
print "\n\n\nPROGRESS: About to execute command : ",cmd_str_tmp,"\n\n\n"
os.system(cmd_str_tmp)

#Move those mzml copies into the taggraph input folder to allow taggraph to have a go at them....
print "about to stage mzML files..."
#print glob.glob(os.path.join(os.path.join(full_mzml_dir,"decode_output/"),"*.mzML")),"the glob!"
#print "from folder {0}".format(os.path.join(os.path.join(full_mzml_dir,"decode_output/")))
for each_mzml in glob.glob(os.path.join(os.path.join(full_output_dir,"decode_output/"),"*.mzML")):
    print "moving file {0} to {1}".format(each_mzml,os.path.join(os.path.join(full_output_dir,"decode_output/taggraph_input/"),each_mzml.rsplit("/",1)[1]))
    os.rename(each_mzml,os.path.join(os.path.join(full_output_dir,"decode_output/taggraph_input/"),each_mzml.rsplit("/",1)[1]))


#We'll also make a folder for the taggraph config...
makeDirCheck(os.path.join(full_output_dir,"decode_output/taggraph_input/config/"))
#copy the template, and we'll run some sed commands to replace with proper values...
tg_params_path=os.path.join(full_output_dir,"decode_output/taggraph_input/config/tg_template.params")
shutil.copy(os.path.join(starting_dir,"tg_template.params"),tg_params_path)

#Now we'll copy the fasta file into place...
tg_fasta_location=os.path.join(full_output_dir,"decode_output/taggraph_input/",os.path.basename(options.fasta))
shutil.copy(options.fasta,tg_fasta_location)
#and we'll have to generate the FMindex for this fasta...

#This dict holds the replacement options k:v pairs to sed into the staged config file
tag_graph_options={"{REPLACE_outputPerFraction}":options.tg_outputPerFraction,"{REPLACE_FDRCutoff}":options.tg_FDRCutoff,"{REPLACE_logEMCutoff}":options.tg_logEMCutoff,"{REPLACE_DisplayProteinNum}":options.tg_DisplayProteinNum,"{REPLACE_ExperimentName}":options.tg_ExperimentName,"{REPLACE_fasta_base}":os.path.basename(options.fasta).rsplit(".",1)[0]}

for each_option in tag_graph_options.keys():
    each_value=tag_graph_options[each_option]
    sed_cmd="sed -i \'s/{0}/{1}/\' {2}".format(each_option,each_value,tg_params_path)
    print "\nAbout to execute command: {0}".format(sed_cmd)
    os.system(sed_cmd)
print "\n\n\nPROGRESS: The TagGraph configuration file has been generated at {0}".format(tg_params_path)

print "\n\n\n=================== TagGraph Execution is now starting. ===================\n\n\n"

#cmd_str_tmp="{0}docker run --rm -v {1}:/taggraph_input/ inf/taggraph bash -c \"python scripts/Build_FMIndex_new.py -f {2} -o {3} && ls && python runTG.py /taggraph_input/config/tg_template.params\"".format(sudo_str, tg_input_dir, "/taggraph_input/{0}".format(os.path.basename(options.fasta)), "/taggraph_input/")
cmd_str_tmp="{0}docker run --rm -v {1}:/taggraph_input/ inf/taggraph bash -c \"cd /taggraph_input/ && python /opt/bio/tools/taggraph/TagGraph.1.7.1/scripts/BuildFMIndex.py -f {2} && ls && cd /opt/bio/tools/taggraph/TagGraph.1.7.1 && python runTG.py /taggraph_input/config/tg_template.params\"".format(sudo_str, tg_input_dir, "/taggraph_input/{0}".format(os.path.basename(options.fasta)), "/taggraph_input/")
print "\n\n\nPROGRESS: About to execute command : ",cmd_str_tmp,"\n\n\n"
os.system(cmd_str_tmp)

print "\n\n\n=================== TagGraph Execution is now finished. ===================\n\n\n"
print "Relevant outputs should be available under the folder: {0}".format(full_output_dir)
