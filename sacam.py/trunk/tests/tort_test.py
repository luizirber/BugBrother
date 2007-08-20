from sacam.cutils import tortuosity
from sacam.areas import Point
from random import random

def build_test_list():
    point_list = []
    for i in xrange(0, 50):
#        point_list.append(Point(random()*100, random()*100))
        point_list.append(Point(i, 10, 0, 0))
    return point_list

if __name__ == "__main__":
    print tortuosity( build_test_list() )
