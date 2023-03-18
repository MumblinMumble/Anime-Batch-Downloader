from selenium import webdriver
import time
import os
import traceback

def download_wait(path_to_downloads):
    dl_wait = True
    while dl_wait:
        time.sleep(10*60)
        dl_wait = False
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('.crdownload'):
                dl_wait = True

def renameall(path_to_downloads):
    os.chdir(path_to_downloads)
    for fname in os.listdir(path_to_downloads):
        if fname.endswith('.mp4'):
            continue
        else:
            dst = fname + '.mp4'
            src = fname
            os.rename(src, dst)

if __name__ == "__main__":
    renameall(r'C:\Users\Amodh\Downloads\AUTODOWNLOAD')
    options = webdriver.ChromeOptions()
    path_to_downloads = r'C:\Users\Amodh\Downloads\AUTODOWNLOAD'
    prefs = {'download.default_directory' : path_to_downloads}
    options.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome(executable_path=r'C:\Users\Amodh\Downloads\CollegePrograms\AnimeAutoDownloaderTest\chromedriver',chrome_options=options)

    link = 'http://srv4.uploadsara.net/user/sajjad/Tv%20Series/Fresh%20Off%20The%20Boat/'
    ep = 1

    while ep <= 24:
        driver.get(str(link))
        try:
            to_dwn = "Fresh Off The Boat S05E"
            if ep < 10:
                to_dwn = to_dwn +"0"
            to_dwn = to_dwn + str(ep)
            # download = download.find_element_by_partial_link_text(str(to_dwn))
            download = driver.find_element_by_partial_link_text(str(to_dwn)+' [1080p x265] [Ariamov..>')
            download = download.get_attribute("href")
            driver.get(str(download))
        except Exception:
            traceback.print_exc()
            print("Ep "+str(ep)+" was not downloaded")
            ep+=1
            continue
        download_wait(path_to_downloads)
        ep+=1

    # driver.quit()
    # time.sleep(24*60*60)
    # renameall(path_to_downloads)