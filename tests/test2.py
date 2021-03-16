from JSON4JSON.VarTypes.basicVarTypes import arg
import sys

print(sys.argv)

import argparse

parser = argparse.ArgumentParser()

a = parser.parse_args(sys.argv)
print(a)