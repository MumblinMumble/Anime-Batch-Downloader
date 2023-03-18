from selenium import webdriver
import time
import os
import subprocess
import traceback
import sys
import requests
from idm import IDMan
from selenium.webdriver.common.by import By
# from rename import renameall

class DriverBuilder():
    '''Setting up selenium chrome driver'''

    def get_driver(self, download_location=None, headless=False):
        driver = self._get_chrome_driver(download_location, headless)
        driver.set_window_size(1400, 700)
        return driver

    def _get_chrome_driver(self, download_location, headless):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # CHANGE PATH TO YOUR CHROME EXECUTABLE FILE IN CASE OF ERROR
        chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        if download_location:
            prefs = {'download.default_directory': download_location,
                     'download.prompt_for_download': False,
                     'download.directory_upgrade': True,
                     'safebrowsing.enabled': False,
                     'safebrowsing.disable_download_protection': True}

            chrome_options.add_experimental_option('prefs', prefs)

        if headless:
            chrome_options.add_argument("--headless")


        driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)

        if headless:
            self.enable_download_in_headless_chrome(driver, download_location)

        return driver

    def enable_download_in_headless_chrome(self, driver, download_dir):
        """
        there is currently a "feature" in chrome where
        headless does not allow file download: https://bugs.chromium.org/p/chromium/issues/detail?id=696481
        This method is a hacky work-around until the official chromedriver support for this.
        Requires chrome version 62.0.3196.0 or above.
        """

        # add missing support for chrome "send_command"  to selenium webdriver
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
        command_result = driver.execute("send_command", params)
        print("response from browser:")
        for key in command_result:
            print("result:" + key + ":" + str(command_result[key]))

def download_wait(path_to_downloads,driver):
    dl_wait = True
    time_passed = 0
    time_to_wait_min = 2
    driver.get('chrome://downloads/')
    while dl_wait:
        dl_wait = False
        time.sleep(5)
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('.crdownload'):
                downloading_filename = fname
                progress = getDownLoadProgress(driver)
                details = progress[1]
                speed = details[7:15]
                percent = progress[0]
                time_left = details[37:41].split(" ")
                print(f"Percent: {percent} || Time Passed/Left: {time_passed} m / {time_left[0]} {time_left[1][0]} || Speed: {speed}") 
                dl_wait = True
        time.sleep(time_to_wait_min*60)
        time_passed += time_to_wait_min
    return downloading_filename

def getDownLoadProgress(driver):
    print(driver.current_url)
    progress = driver.execute_script('''
    
    var tag = document.querySelector('downloads-manager').shadowRoot;
    var intag = tag.querySelector('downloads-item').shadowRoot;
    var progress_tag = intag.getElementById('progress');
    var progress = null;
    if(progress_tag) {
        progress = progress_tag.value;
    }
    var details_tag = intag.getElementById('description');
    var details = null;
    if(details_tag) {
        details = details_tag.innerHTML;
    }

    return [progress, details];
    
    ''')
    return progress

def no_such_element(str,driver):
    try:
        driver.find_element(By.PARTIAL_LINK_TEXT(str))
        return True
    except:
        return False

def rename(path_to_downloads, old_name, new_name):
    cwd = os.getcwd()
    os.chdir(path_to_downloads)
    old_name = old_name.split(".")[0]
    for fname in os.listdir(path_to_downloads):
        if fname.split(".")[0] == old_name:
            dst = new_name+"."+fname.split(".")[-1]
            src = fname
            os.rename(src, dst)
            break
    os.chdir(cwd)

def downloadPython(url, filename):
    with open(filename, 'wb') as f:
        response = requests.get(url, stream=True)
        total = response.headers.get('content-length')

        if total is None:
            f.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            for data in response.iter_content(chunk_size=max(int(total / 1000), 1024 * 1024)):
                downloaded += len(data)
                f.write(data)
                done = int(50 * downloaded / total)
                sys.stdout.write('\r[{}{}]'.format('█' * done, '.' * (50 - done)))
                sys.stdout.flush()
    sys.stdout.write('\n')

if __name__ == "__main__":

    options = webdriver.ChromeOptions()
    
    download_location = 'Download'
    path_to_downloads = os.path.join(os.getcwd(), download_location)

    DriverBuilderObj = DriverBuilder()

    driver = DriverBuilderObj._get_chrome_driver(download_location=path_to_downloads, headless=False)

    # link = input("\nEnter Anime Link: ")
    link = "https://yugenanime.ro/watch/15523/overlord-iv/"
    sep = "/"
    # split_link = link.split(sep)
    # split_link.remove("category")
    # link = sep.join(split_link)

    # start = int(input("Enter Start Episode Number: "))
    start = 5
    # end = int(input("Enter End Episode Number: "))
    end = 13
    ep = start
    allowed_types = ['HDP','1080','720','360','-']

    while ep <= end:
        print("\nEPISODE "+str(ep))
        download = None
        print("\nLoading Link.....")
        print(str(link + str(ep) + "/"))
        driver.get(str(link + str(ep)))
        print("Link Found.")
        try:
            print("Finding Download Button.....")
            btn = driver.find_element(By.NAME,'player-download')
            btn = btn.get_attribute("href")
            print("Button Found.")
            print("Loading Download Page.....")
            driver.get(str(btn))
            print("Page Found.")
            print("Checking Allowed Types.....")
            check = False
            for i in allowed_types:
                if no_such_element(i,driver):
                    download = driver.find_element(By.PARTIAL_LINK_TEXT(i))
                    print(i+" found.")
                    check = True
                    break
                print(i+" not found.")
            if not check:
                print("No Links Found.")
                print("Ep "+str(ep)+" was not downloaded\n")
                ep+=1
                continue
            download = download.get_attribute("href")
        except Exception:
            traceback.print_exc()
            print("Ep "+str(ep)+" was not downloaded\n")
            ep+=1
            continue
        
        print("Intializing Download.....")
        driver.get(str(download))
        print("Download Started.") 


        ## Bad Method
        # dwn_file = download_wait(path_to_downloads,driver)
        # new_name = link.split("/")[-1]+str(ep)
        # rename(path_to_downloads, dwn_file, new_name)
        
        ## Python Method
        # downloadPython(str(download),link.split("/")[-1]+str(ep)+".mp4")

        ## IDM Method
        # downloader = IDMan()
        # url = str(download)
        # downloader.download(url, path_to_downloads, output=link.split("/")[-1]+str(ep)+".mp4", referrer=None, cookie=None, postData=None, user=None, password=None, confirm = False, lflag = None, clip=False)

        ## Aria2c
        command = "aria2c"
        options = str(download)
        # Create list with arguments for subprocess.run
        args=[]
        args.append(command)
        args.append(options)

        shell = subprocess.Popen(args, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        ep+=1
    driver.quit()
    
    # renameall(path_to_downloads)