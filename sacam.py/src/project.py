#!/usr/bin/env python

from math import pi, sqrt
import cPickle
from zlib import compress, decompress

import pygtk
pygtk.require('2.0')
import gobject
import gtk.gdk

from areas import shape, point

class project(object):
    """
    this class contains data used to define a project. almost all this
    attributes could be saved in and loaded from a XML file.
    """
    
    attributes = {}
    refimage = None
    experiment_list = []
    filename = None
    
    def __init__(self):
        self.current_experiment = experiment()
        self.bug_max_velocity = 3
        self.bug_size = 39 
    
    def save_project(self):
        temp = cPickle.dumps(self)
        proj = compress(temp)
        print self.filename
        projfile = file(self.filename,"w")
        projfile.write(proj)
        projfile.close()
    
    def load_project(self):
        projfile = file(self.filename,"r")
        temp = projfile.read()
        projfile.close()
        proj = decompress(temp)
        self = cPickle.loads(proj)
        
    
class experiment(object):
    """
    a project consist of various experiment. every experiment is an instance
    of this class. this is also saved in and loadable from a XML file.
    """
    
    point_list = []
    areas_list = []
    start_time = None
    end_time = None
    extra_attributes = {}
    measurement_unit = None
    scale_ratio = None
    track = None
    experiment_name = None
    
    def __init__(self):
        self.threshold = 0x30
        self.release_area = [400, 400, 480, 640]
        
    def save_experiment(self):
        pass
    
    def prepare_areas_list(self):
        for area in self.areas_list:
            for point in self.point_list:
                temp_list = []
                if area.shape.contains(point):
                    if not area.started:
                        temp_list.append(point)
                        area.started = True                    
                    else:
                        temp_list.append(point)
                else:
                    if area.started:
                        temp_list.append(point)
                        area.point_list.append(temp_list)
                        temp_list = []                    
                    area.started = False                    
            
    def prepare_stats(self):
        pass
         #PrepararGradeApresentacaoEstatisticas
             #Para cada area
                #HoraInicio
                #HoraFim
                #Permanencia (Fim - Inicio)
                #Trajeto
                #VelLinearMedia
                #DesvPadrao - VelLinear
                #VelAngularMedia
                #DesvPadrao - VelAngular
                #Tortuosidade
                
         #PrepararGradeApresentacaoSintese
            #Area
            #Tempo de permanencia
            #Tempo(%)
            #TrajetoTotal (cm)
            #Trajeto (%)
           #calcular para point_list do experimento 
            #TempoTotal
            #ComprimentoTotal
            
            
         #ProcessamentoEstatisticas
            #for area in areas_list:
#                track_lenght = 0;
#                total_time = 0;
#                for list in area.point_list:
#                    first_point = list[0]
#                    previous_point = list[1]
#                    current_point = None
#                    for point in list[2:]:
#                        current_point = point
#                        temp = pow( (previous_point.x - current_point.x) +
#                                     previous_point.y - current_point.y), 2)
#                        track_lenght += sqrt(temp)
#                        total_time += point.end_time - point.start_time
#                        
#
#                        first_point = previous_point
#                        previous_point = current_point

#                area.track_lenght = track_lenght
#                area.total_time = total_time
         
         #ProcessamentoRelatorioEstatisticas
            #
    