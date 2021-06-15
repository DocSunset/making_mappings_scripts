import xml.etree.ElementTree as ET
import sys

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__":
  print(colors.HEADER + colors.BOLD + 
        "### --- VERIFYING XML DOCUMENTS --- ###"
        + colors.ENDC)

  for filename in sys.argv[1:len(sys.argv)]:
    try:
      tree = ET.parse(str(filename))
      print(colors.OKGREEN + "{} passed".format(filename))
    except ET.ParseError as e:
      print(colors.FAIL + "{} failed: {}, {}".format(filename, e.code, e.position))
    except FileNotFoundError:
      print(colors.WARNING + "{} not found".format(filename))

  print(colors.ENDC + colors.HEADER + "DONE" + colors.ENDC)
