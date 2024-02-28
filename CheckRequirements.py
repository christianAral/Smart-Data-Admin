import os
from sys import exit
from pathlib import Path
try:
    from importlib.metadata import distributions
except ModuleNotFoundError:
    print("\nModuleNotFoundError: No module named 'importlib.metadata'"
        '\n\tIt looks like there might be something wrong '
        'with your python installation. We just tried '
        'importing importlib.metadata which is a part of '
        "Python standard library but it couldn't be found. Please "
        'try updating your Python to 3.8 or higher and then running the '
        'script again!\n'
    )
    print("Press any key to exit...")
    os.system("pause >nul")
    exit()
try: 
    from colorama import init, Fore, Back, Style
    init()
except:
    Fore = type("", (), {})()
    Back = type("", (), {})()
    Style = type("", (), {})()
    Fore.WHITE = ''
    Back.RED = ''
    Style.RESET_ALL = ''

def CheckRequirements():
    _REQUIREMENTS_PATH = Path(__file__).with_name("requirements.txt")
    _REQUIREMENTS_STR = str(_REQUIREMENTS_PATH).replace('\\','/')
    with open(_REQUIREMENTS_PATH,'r', encoding='utf-16') as reqs:
        requirements = [req.split('==')[0].lower() for req in reqs.read().split('\n')]

    # Get installed packages
    installed_packages_list = [d.name.lower() for d in distributions()]

    # Check if required package is installed
    for requirement in requirements:
        if requirement not in installed_packages_list:
            
            errStyle = Back.RED + Fore.WHITE

            message = (errStyle +
                       f'This function requires {", ".join(requirements)}. '
                       f'To continue, please install them with one of the commands below:{Style.RESET_ALL}\n'
                       f'    {errStyle}pip install -r "{_REQUIREMENTS_STR}"      {Style.RESET_ALL}\n'
                       f'    {errStyle}conda install --file "{_REQUIREMENTS_STR}"{Style.RESET_ALL}')

            print(message,end="\n\n")
            print("Press any key to exit...")
            os.system("pause >nul")
            exit()
    print('Requirements Met')

CheckRequirements()