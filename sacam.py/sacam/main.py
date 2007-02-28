''' Initialization of the software.

    In the future should parse the args. '''

from sacam.interface import Interface

def main(args=None):
    ''' Simple initialization function.'''
    sacam = Interface()
    sacam.main(args)
