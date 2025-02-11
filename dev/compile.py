# Importing required module
import subprocess
import concurrent.futures
from os import walk
import os, signal
from os import listdir
from os.path import isfile, join
import  os
import multiprocessing
from fnmatch import fnmatch
import sys
import tlsh, json


root    ='/media/raisul/clones_100k'
meta_path = '/home/raisul/pun_dataset/meta'
bin_path = '/home/raisul/DATA'

project_name = 'x86_O2_d4_mingw32_PE' 
bin_project_path = os.path.join(bin_path,project_name)

if not os.path.exists(bin_project_path):
    os.makedirs(bin_project_path)




manager = multiprocessing.Manager()
Global = manager.Namespace()

Global.total_c_compile = 0
Global.total_make = 0


c_pattern = "*.c"
makefile_pattern = "makefile"


def create_bin_path(src_path):
      
    thash = tlsh.hash(open(src_path, 'rb').read())
    bin_output_path = os.path.join(bin_project_path ,thash )
    return thash, bin_output_path


def save_meta(thash , src_path , bin_path , compile_command, compiler, flags ):
    print('here')
    meta_json_file_path = os.path.join(meta_path , thash) +'.json'
    meta_dict = {
        
            'src_path':src_path,
            'bin_path':bin_path,
            'compiler':compiler,
            'flags':flags,
            'compile_command':compile_command
    }

    if os.path.isfile(meta_json_file_path):
        with open(meta_json_file_path) as old_json_file:
            json_data  = json.load(old_json_file)
            
    else: 
        json_data = {}

    print(json_data)

    json_data[project_name] = meta_dict

    with open(meta_json_file_path, "w", encoding='utf-8') as jsonfile:
        json.dump(json_data, jsonfile , ensure_ascii=False, indent=4)


def compile(src_file_path):

    try:
        thash, bin_output_path = create_bin_path(src_file_path)
        src_dir_path, src_file_name = os.path.split(os.path.abspath(src_file_path))
        compiler = 'x86_64-w64-mingw32-gcc ' #' gcc '
        flags = ' -gdwarf-4 -O2  '


        if os.path.isfile(bin_output_path):
            return

        command = compiler + flags + '-o '+ bin_output_path +' '+ src_file_path
        process = subprocess.Popen(command ,shell=True) 
        
        Global.total_make  = Global.total_make  +1
        process.wait(timeout=10)

        if os.path.isfile(bin_output_path): #check if bin file generated. can fail
            save_meta(thash , src_file_path , bin_path , compile_command=command, compiler=compiler, flags = flags )
    except Exception as e:
         print (e)
##############################################


def make(makefile_dir_path):

    # print('makefile_dir_path',makefile_dir_path)
    makeCommand = 'make -C '+makefile_dir_path
    # print(makeCommand)
    
    process = subprocess.Popen(makeCommand, shell=True, start_new_session=True)
    Global.total_c_compile = Global.total_c_compile +1
    process.wait(timeout=10)






import pickle


all_c_paths = []

all_make_dir_paths = []
# for path, subdirs, files in os.walk(root):
#     print("ok")

#     if len(all_c_paths)%1000==0:
#          print("Now" , len(all_c_paths))
#     for name in files:
#         file_path = os.path.join(path, name)
        

#         if fnmatch(name.lower(), c_pattern):
#                     c_file_path = os.path.join(path, name)
#                     all_c_paths.append(c_file_path)
                    
#         elif fnmatch(name.lower(), makefile_pattern):
#                     all_make_dir_paths.append( path)



# with open('c_files_n_projs.ignore.pkl', 'wb') as f:
#     pickle.dump([all_c_paths,all_make_dir_paths] , f)
    
with open('c_files_n_projs.ignore.pkl', 'rb') as file:
    all_c_paths,all_make_dir_paths  = pickle.load(file)  



all_c_paths= all_c_paths[0:10000]

if __name__ == "__main__":  # Allows for the safe importing of the main module
    print("There are {} CPUs on this machine".format( multiprocessing.cpu_count()))
    number_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(number_processes)
    results = pool.map_async(compile, all_c_paths)
    pool.close()
    pool.join()


