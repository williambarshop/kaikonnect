import os, shutil, glob, sys, subprocess, importlib

#From stackoverflow #12332975
def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

try:
    import optparse
    package_list=["optparse"]
except:
    #Let's make sure we have the packages we need here to start...
    for each_package in package_list:
        print "Making sure that package \"{0}\" is installed...".format(each_package)
        install(each_package)
        importlib.import_module(each_package)



parser = optparse.OptionParser()
parser.add_option("-s","--no_sudo",action="store_false",dest="no_sudo",default=False) #False means don't use sudo.  This will depend on how users are given permission to access the docker host
parser.add_option("-r","--raw_folder",action="store",type="string",dest="raw_folder") #If this has a value, we'll convert Thermo raw files to mzML using a docker container and place them inside the mzml folder
parser.add_option("-m","--mzML_folder",action="store",type="string",dest="mzml_folder")
parser.add_option("-o","--output_folder",action="store",type="string",dest="output_folder")
parser.add_option("-f","--fasta",action="store",type="string",dest="fasta_file")


#KAIKO OPTIONS
parser.add_option("--kaiko_topk",action="store",type="int",dest="kaiko_topk",default=1)
parser.add_option("--kaiko_beam_size",action="store",type="float",dest="best_prop_pep")
parser.add_option("--best_prop_pep",action="store",type="float",dest="best_prop_pep")


#TAG_GRAPH OPTIONS




(options,args) = parser.parse_args()

#Let's establish some directories for later reference
starting_dir=os.getcwd()
os.chdir(options.output_dir)
full_output_dir=os.getcwd()
os.chdir(options.starting_dir)


if options.no_sudo:
    sudo_str=""
else:
    sudo_str="sudo "


#### CHECK FOR REQUIRED FOLDERS AND OPTIONS ####

#Check to make sure an mzML folder is supplied-- at least -- and if it doesn't exist, let's go ahead and make it
if options.mzml_folder is None:
    print "ERROR: You'll need to supply an mzML folder location via \"--mzML_folder {value}\""
    sys.exit(2)
else:
    if not os.path.isdir(options.mzML_folder):
        try:
            os.mkdir(options.mzML_folder)
        except:
            print "Failed to make directory {0} !\nPlease ensure that you have rights to make this directory, or that it isn\'t a file already.".format(options.mzML_folder)

#Check to make sure an output folder is supplied-- at least -- and if it doesn't exist, let's go ahead and make it
if options.output_folder is None:
    print "ERROR: You'll need to supply an output folder location via \"--output_folder {value}\""
    sys.exit(2)
else:
    if not os.path.isdir(options.output_folder):
        try:
            os.mkdir(options.output_folder)
        except:
            print "Failed to make directory {0} !\nPlease ensure that you have rights to make this directory, or that it isn\'t a file already.".format(options.output_folder)





#### HANDLE THERMO RAW CONVERSION ####

if options.raw_folder is not None:
    print "We're going to start by converting your Thermo raw files to mzML and place the output in the mzML folder..."
    os.chdir(options.raw_folder)
    full_raw_path=os.getcwd()
    for each_raw in glob.glob("*.raw"):
        print "Going to execute...","{0}docker run --rm -e WINEDEBUG=-all -v {1}:/data chambm/pwiz-skyline-i-agree-to-the-vendor-licenses wine msconvert {2}".format(sudo_str, full_raw_path, each_raw)
        os.system("{0}docker run --rm -e WINEDEBUG=-all -v {1}:/data chambm/pwiz-skyline-i-agree-to-the-vendor-licenses wine msconvert {2}".format(sudo_str, full_raw_path, each_raw))
        os.rename(each_raw.rsplit(".",1)[0]+".mzML",options.mzML_folder)
    os.chdir(starting_dir)





#Alright, let's get things moving.  We're going to generate our mgf files from the mzml inputs.
print "We're going to convert the mzML files to mgf files..."
os.chdir(options.mzml_folder)
full_path_mzml=os.getcwd()
os.system("{0}docker run -v {1}:/mzml_input/ kaikonnect /bin/bash -c \"source python3 && python /kaikonnect/convert_mzml.py\"".format(sudo_str, options.mzml_folder))
#Move mgf file(s) to output dir... Will feed to Kaiko...
for each_mgf in glob.glob("*.mgf"):
    os.rename(each_mgf,full_output_dir)
os.chdir(starting_dir)

print "All done with mgf conversion from mzML!"

#subprocess.call("{0} bash docker run -v {1}:/mzml_input/ kaikonnect source python3 && python /kaikonnect/convert_mzml.py".format(sudo_str, options.mzml_folder),shell=True)

print "Let's move on to working with the outputs for searching with Kaiko."

if not os.path.isdir(os.path.join(starting_dir,"Kaiko/")):
    print "\n\nERROR: We can't find the Kaiko folder! Please make sure:\n1. You are running this script from the kaikonnect basedir folder\n2. You have run the \'tag_grab.sh\' setup script!"
    sys.exit(2)
docker run --name kaiko --rm -v $(pwd)/model/kaiko_model/:/app/model -v $(pwd)/mgf_input:/app/mgf_input -v $(pwd)/decode_output:/app/decode_output kaiko
os.system("{0}docker run --rm -v {1}:/app/model -v {2}:/app/mgf_input -v {2}/decode_output:/app/decode_output kaiko /bin/bash -c \"python ./src/kaiko_main.py --mgf_dir mgf_input/ --train_dir model/ --multi_decode --beam_search --beam_size {3}".format(sudo_str,os.path.join(starting_dir,"Kaiko/model/kaiko_model/"),options.output_dir,options.kaiko_beam_size)

sudo_str
os.path.join(starting_dir,"Kaiko/model/kaiko_model/")
options.output_dir
options.kaiko_beam_size
