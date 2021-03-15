import platform
from paint import Paint
if platform.system() == "Windows":
    from win_fix import win_dpi_fix

if __name__ == "__main__":
    if platform.system() == "Windows":
        win_dpi_fix()
    Paint()