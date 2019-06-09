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
parser.add_option("-m","--mzML_folder",action="store",type="string",dest="mzml_folder")
parser.add_option("-f","--fasta",action="store",type="string",dest="fasta_file")


#KAIKO OPTIONS
parser.add_option("--kaiko_topk",action="store",type="int",dest="kaiko_topk",default=1)
parser.add_option("--kaiko_beam_size",action="store",type="float",dest="best_prop_pep")
parser.add_option("--best_prop_pep",action="store",type="float",dest="best_prop_pep")


#TAG_GRAPH OPTIONS




(options,args) = parser.parse_args()


if options.no_sudo:
    sudo_str=""
else:
    sudo_str="sudo "


#Alright, let's get things moving.  First, we're going to generate our mgf files from the mzml inputs.
print "We're going to get started with converting the mzML files to mgf files..."
os.system("{0}docker run -v {1}:/mzml_input/ kaikonnect source python3 && python /kaikonnect/convert_mzml.py".format(sudo_str, options.mzml_folder))
#subprocess.call("{0} bash docker run -v {1}:/mzml_input/ kaikonnect source python3 && python /kaikonnect/convert_mzml.py".format(sudo_str, options.mzml_folder),shell=True)

print "All done with mgf conversion!\nLet's move on to working with the outputs for searching with Kaiko."
