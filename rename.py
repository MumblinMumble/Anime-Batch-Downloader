import os

def renameall(path_to_downloads):
    os.chdir(path_to_downloads)
    for fname in os.listdir(path_to_downloads):
        if fname.endswith('.mp4'):
            continue
        else:
            dst = fname + '.mp4'
            src = fname
            os.rename(src, dst)

path_to_downloads = r'C:\Users\Amodh\Downloads\AUTODOWNLOAD'
renameall(path_to_downloads)