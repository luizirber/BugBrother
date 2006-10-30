from math import sqrt

class point2(object):
    """
    Simple class that store data needed to generate reports, like
    the time that a insect stayed in the point (start_time - end_time)
    and in which areas the point is contained.
    """
        
    def __init__(self):
        self.x = None
        self.y = None
        self.start_time = None
        self.end_time = None

if __name__ == "__main__":
    listie = []        
    for i in range(1,15):
        point = point2()
        point.x = i
        point.y = i*2
        point.start_time = i*3
        point.end_time = i*4
        listie.append(point)
    first_point = listie[0]
    previous_point = listie[1]
    current_point = None
    print 'c'
    print 'f', first_point.x, first_point.y, first_point.start_time, first_point.end_time
    print 'p', previous_point.x, previous_point.y, previous_point.start_time, previous_point.end_time
    track_lenght = 0
    total_time = 0
    for point in listie[2:]:
        current_point = point
        print '\nc', current_point.x, current_point.y, current_point.start_time, current_point.end_time
        temp = pow( (previous_point.x - current_point.x) +
                    (previous_point.y - current_point.y), 2)
        track_lenght += sqrt(temp)
        total_time += point.end_time - point.start_time
        first_point = previous_point
        previous_point = current_point
        print 'f', first_point.x, first_point.y, first_point.start_time, first_point.end_time
        print 'p', previous_point.x, previous_point.y, previous_point.start_time, previous_point.end_time
    print "lenght", track_lenght        
    print "time", total_time
