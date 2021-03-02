from ctypes import windll

def win_dpi_fix():
    """
    Windows fix for high-DPI displays
    """
    try:
        windll.shcore.SetProcessDpiAwareness(2) # Win version >= 8.1
    except:
        windll.user32.SetProcessDPIAware() # Win 8.0 or less 