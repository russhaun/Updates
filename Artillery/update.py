import os
import requests
import subprocess
from subprocess import CalledProcessError
import sys
import time
from zipfile import ZipFile
from win32api import GetUserNameEx


programfiles = os.environ['Programfiles(x86)']
g_apppath = programfiles + "\\Artillery"
g_configfile = g_apppath + "\\config"
g_batch = g_apppath + "\\artillery_start.bat"
g_pidfile = g_apppath +"\\pid.txt"
HOME_DIR = os.getcwd()
ROOT_PATH = str(HOME_DIR)
RELEASE_PATH = ROOT_PATH + "\\releases"
ROOT_LOG_PATH = ROOT_PATH + "\\logging"
ROOT_LOG_FILE = ROOT_LOG_PATH + "\\updates.txt"
ROOT_CONFIG_BACKUP_PATH = ROOT_PATH + "\\config_backup"
LOG_PATH = str(ROOT_LOG_PATH)
CONFIG_BACKUP_PATH = str(ROOT_CONFIG_BACKUP_PATH)
BATCH_PATH = g_batch
PID_INFO_PATH = g_pidfile
PID = []
#userneme in domain\user format
U_INFO = GetUserNameEx(2) 
for line in os.environ:
    line = line.strip()
    print(line)

def kill_artillery_win():
    '''opens pid.txt file made from artillery.py to grab current
    PID to terminate'''
    try:
        if os.path.isfile(PID_INFO_PATH):
            print('[*] Finding process info.....')
            with open(PID_INFO_PATH, 'r') as id:
                for line in id:
                    line = line.strip()
                    PID.append(line)
            id.close()
            pid = PID[0]
            print(f'[*] Last known ProcessID: {pid}''')
            print('[*] Attempting to kill Artillery now.....')
            try:
                kill_pid = subprocess.check_call(['cmd', '/C', 'taskkill', '/PID', pid])
                ArtilleryStopEvent()
                return True
            except CalledProcessError as err:
                print("[*] Looks like this proccess is dead already. ")
                return False 
        else:
            print('[*] pid.txt was not found\n[*] Artillery must be run @ least once.......')
            pause = input("[*] File was not found press enter to quit:") 
    except Exception as err:
            pass
            #       

        

def restart_artillery_win():
    '''restarts main python file by calling artilley_start.bat 
    after waiting a few seconds to allow previous instance if any to close down'''
    # check to see if artillery is running 
    check = kill_artillery_win()
    if check == True:
        print("[!] Process Killed\n[*] Launching now..... ")
        #make sure proccess is dead wait a sec
        time.sleep(2)
        try:
            if os.path.isfile(g_batch):
                os.chdir(g_apppath)
                os.system('start cmd /K artillery_start.bat')
        except FileNotFoundError as e:
            print("file not found" + str(e))
            pause = input("hit a key")
    else:
        print("[*] Launching now..... ")
        now = os.getcwd()
        time.sleep(2)
        try:
            if os.path.isfile(g_batch):
                os.chdir(g_apppath)
                os.system('start cmd /K artillery_start.bat')
        except FileNotFoundError as e:
            print("file not found" + str(e))
            pause = input("hit a key")
    
#
#

def get_config(cfg):
    '''get various pre-set config options used throughout script'''
    #Current artillery version
    current = ['2.5.5']
    if cfg == 'CurrentBuild':
        return current
    else:
        pass

def srv_update_check():
    '''pulls down latest version info from github to compare with client.if version is not larger
    then client just continues and no updates are performed'''
    info = []
    url = 'https://raw.githubusercontent.com/russhaun/Updates/master/Artillery/ver.txt'
    r = requests.get(url)
    with open("srv_ver.txt", 'w') as v:
            #response is binary have to convert it to utf-8
            response = r.content
            decoded = response.decode(encoding="utf-8")
            #add the version number to our list
            info.append(decoded)
    v.close()
        #delete the version info file. we dont need it any more
    subprocess.call(['cmd', '/C', 'del', 'srv_ver.txt'])
    ver = info[0]
    print("[*] Response from Server:  ok...")
    #print("[*] Servers current release version is: "+str(ver))
    return(ver)


def update_logs(msg):
    '''this logs for update function it runs outside artillery and writes to update dir'''
    with open(ROOT_LOG_FILE, 'a') as log:
        log.write(msg+ "\n")
    log.close()
    #
#put this here for when running script not bundled in exe
try:
    MEI_PATH = sys._MEIPASS
except AttributeError as err:
    MEI_PATH = ROOT_PATH
#create initial dirs if not here for future updates
if os.path.isdir(LOG_PATH):
    pass
else:
    update_logs("[*] Creating log dir.....")
    os.mkdir(LOG_PATH)
        #
time.sleep(1)
    #    
if os.path.isdir(CONFIG_BACKUP_PATH):
    pass
else:
    update_logs("[*] Creating config backup dir.....")
    os.mkdir(CONFIG_BACKUP_PATH)
        #
time.sleep(1)
    #   
if os.path.isdir(RELEASE_PATH):
    pass
else:
    update_logs("[*] Creating release dir.....")
    os.mkdir(RELEASE_PATH)
        #
time.sleep(1)
#set config exists to 0. assuming new install
CONFIG_EXISTS = 0
#put logic here to determine if updates are needed
srv_resp = srv_update_check()
print("[*] Current released version is: "+str(srv_resp))
get_ver = get_config('CurrentBuild')
ver = get_ver[0]
if ver > srv_resp:
    update_logs("[*] Updates have been detected!!!!")
    try:
        url = 'https://codeload.github.com/russhaun/artillery/zip/master'
        r = requests.get(url)
        update_logs("[*] Checking out Git repo version "+str(srv_resp)+"..........\n""[*] Downloading files . Please wait.......")
        # make a nice zip file for later use
        ZIPFILE_NAME = "artillery-master.zip"
        with open(ZIPFILE_NAME, "wb") as code:
            code.write(r.content)
            code.close()
            time.sleep(3)
    except ConnectionRefusedError:
        raise
        #
        #grab a handle to zip archive
    with ZipFile(ZIPFILE_NAME, 'r') as zip_archive:
        os.chdir(RELEASE_PATH)
        r_id ="release_"+ srv_resp
        this_build = RELEASE_PATH+"\\"+str(r_id)
        #remove previous builds
        if os.path.isdir(r_id):
            print("removing previous release")
            subprocess.call(['cmd', '/C', 'rmdir', '/S', '/Q', r_id])
        #
        time.sleep(5)   
        os.mkdir(r_id)
        time.sleep(1)
        os.chdir(r_id)
        print('[*] Extracting all the files now...')
        zip_archive.extractall()
        time.sleep(2)
        print('[*] Done!')
        zip_archive.close()
        #backup existing config file
    if os.path.isdir(g_apppath):
        update_logs("[*] directory already exists......")
        update_logs("[*] checking for existing config file.....")
        #this is config file located in %program Files (x86)%
        if os.path.isfile(g_configfile):
            #set flag to 1
            CONFIG_EXISTS += 1
                #this is the path created at launch
            if os.path.isdir(CONFIG_BACKUP_PATH):
                    #print("[*] Config file present backing up")
                update_logs("[*] Backing up existing config file.....")
                subprocess.run(['cmd', '/C', 'copy', g_configfile, CONFIG_BACKUP_PATH], shell=True, close_fds=True)
            else:
                update_logs("[*] Backup path not here creating......")
                os.mkdir(CONFIG_BACKUP_PATH)
                subprocess.run(['cmd', '/C', 'copy', g_configfile, CONFIG_BACKUP_PATH], shell=True, close_fds=True)
        else:
            update_logs("[*] Config file not found..... continuing")
        #change to extracted files dir
        os.chdir('artillery-master')
        print("[*] Removing existing install.....")
        time.sleep(2)
        #remove existing install
        #subprocess.call(['cmd', '/C', 'rmdir', '/S', '/Q', g_apppath], shell=True)
        print("[*] Successfully removed.....")
        #create new install
        EXTRACTED = os.getcwd()
        time.sleep(2)
        #copy over files from zip archive
        print("[*] Copying archive over.....")
        #shutil.copytree(EXTRACTED, g_apppath)
        time.sleep(1)
        print("[*] Creating program directories")
        #os.makedirs(globals.g_apppath + "\\logs")
        #os.makedirs(globals.g_apppath + "\\database")
        #os.makedirs(globals.g_apppath + "\\src\\program_junk")
        if CONFIG_EXISTS == 1:
            print("[*] Restoring config from backup.....")
            #subprocess.run(['cmd', '/C', 'copy', CONFIG_BACKUP_PATH, g_configfile], shell=True, close_fds=True)
            print("[*] Restore Complete.....")
            DIR_NAME = ROOT_CONFIG_BACKUP_PATH
            OUTPUT_FILENAME = DIR_NAME + '\\config_backup'
            #finalname = OUTPUT_FILENAME
            #switch into the backup dir
            os.chdir(ROOT_CONFIG_BACKUP_PATH)
            print("[*] creating zipfile of backup_config......")
            #shutil.make_archive(OUTPUT_FILENAME, 'zip', DIR_NAME)
            #copy zip to root of folder
            #subprocess.run(['cmd', '/C', 'copy', OUTPUT_FILENAME +".zip", ROOT_PATH], shell=True, close_fds=True)
            print("[*] Install Complete.....")
            time.sleep(3)
            #change back to home folder and delete config_backup we dont need it anymore
            os.chdir(ROOT_PATH)
            #subprocess.call(['cmd', '/C', 'rmdir', '/S', '/Q', root_log_path])
            #subprocess.call(['cmd', '/C', 'rmdir', '/S', '/Q', ROOT_CONFIG_BACKUP_PATH], shell=True)
            #subprocess.call(['cmd', '/C', 'rmdir', '/S', '/Q', "artillery-master"], shell=True)
            #subprocess.call(['cmd', '/C', 'del', "artillery-master.zip"], shell=True, close_fds=True)
            #subprocess.call(['cmd', '/C', 'rmdir', '/S', '/Q', root_log_path],shell=True,close_fds=True)
        else:
            print("[*] skipping no backup performed.....")
        restart_artillery_win()
else:
    update_logs("[*] No updates availible....")
