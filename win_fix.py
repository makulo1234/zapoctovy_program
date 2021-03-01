from ctypes import windll

# Windows fix pre high-DPI obrazovky
def win_dpi_fix():
    try:
        windll.shcore.SetProcessDpiAwareness(2) # windows version >= 8.1
    except:
        windll.user32.SetProcessDPIAware() # win 8.0 or less 