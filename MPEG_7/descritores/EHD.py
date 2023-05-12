import sys
from PIL import Image, ImageOps
import numpy as np
import math

class EHD_Descriptor:


    def __init__(self, Thresshold):
        self.threshold = Thresshold

        self.QuantTable = np.array([[0.010867, 0.057915, 0.099526, 0.144849, 0.195573, 0.260504, 0.358031, 0.530128],
                        [0.012266, 0.069934, 0.125879, 0.182307, 0.243396, 0.314563, 0.411728, 0.564319],
                        [0.004193, 0.025852, 0.046860, 0.068519, 0.093286, 0.123490, 0.161505, 0.228960],
                        [0.004174, 0.025924, 0.046232, 0.067163, 0.089655, 0.115391, 0.151904, 0.217745],
                        [0.006778, 0.051667, 0.108650, 0.166257, 0.224226, 0.285691, 0.356375, 0.450972]])


        self.BIN_COUNT = 80
        self.bins = np.zeros(80)

        self.num_block = 1100

        self.NoEdge = 0
        self.vertical_edge = 1
        self.horizontal_edge = 2
        self.non_directional_edge = 3
        self.diagonal_45_degree_edge = 4
        self.diagonal_135_degree_edge = 5

        self.Local_Edge_Histogram = np.zeros(80)
        self.blockSize = -1

    def Quant(self, Local_Edge_Histogram):
    
        Edge_HistogramElement = Local_Edge_Histogram.size
        iQuantValue = 0

        for i in range(Local_Edge_Histogram.size):
        
            for j in range(8):
            
                Edge_HistogramElement[i] = j
                if (j < 7):
                    iQuantValue = (self.QuantTable[i % 5, j] + self.QuantTable[i % 5, j + 1]) / 2.0
                else:
                    iQuantValue = 1.0

                if (Local_Edge_Histogram[i] <= iQuantValue):
                    break

        return Edge_HistogramElement
    

    def Apply(self, src_img):

        EDHTable = np.zeros(80)

        self.width, self.height = src_img.size

        if src_img.mode == 'L':
            fmt = 'L'
        else:
            fmt = 'RGB'

        src_data = np.array(src_img.getdata(), dtype=np.uint8).reshape(self.height, self.width, len(fmt))
        self.grey_level = np.zeros((self.width, self.height))

        for y in range(self.height):
             for x in range(self.width):
                if fmt == 'L':
                    yy = src_data[y, x]
                else:
                    yy = 0.114 * src_data[y, x, 0] + 0.587 * src_data[y, x, 1] + 0.299 * src_data[y, x, 2]
                
                mean = int(219.0 * yy / 256.0 + 16.5)
                self.grey_level[x, y] = mean
        
        EDHTable = self.extractFeature()
        return EDHTable


    def getblockSize(self):
    
        if self.blockSize < 0:
        
            a = int(math.sqrt((self.width * self.height) / self.num_block))
            self.blockSize = int(math.floor((a / 2)) * 2)

            if self.blockSize == 0:
                self.blockSize = 2
        
        return self.blockSize


    def getFirstBlockAVG(self, i, j):
    
        average_brightness = 0

        if self.grey_level[i, j] != 0:

            for m in range(self.getblockSize() // 2):
            
                for n in range(self.getblockSize() // 2):
                
                    average_brightness = average_brightness + self.grey_level[i + m, j + n];
                
        else:
            pass
        
        bs = self.getblockSize() ** 2
        div = 4 / bs
        average_brightness *= div

        return average_brightness


    def getSecondBlockAVG(self, i, j):
    
        average_brightness = 0

        if self.grey_level[i, j] != 0:

            for m in range(self.getblockSize()//2, self.getblockSize()):
                for n in range(self.getblockSize()//2):
                    average_brightness += self.grey_level[i + m, j + n]
        else:
            pass
        
        bs = self.getblockSize() ** 2
        div = 4 / bs
        average_brightness *= div

        return average_brightness


    def getThirdBlockAVG(self, i, j):
    
        average_brightness = 0

        if self.grey_level[i, j] != 0:

            for m in range(self.getblockSize()//2):
                for n in range(self.getblockSize()//2, self.getblockSize()):
                    average_brightness += self.grey_level[i + m, j + n]
        else:
            pass

        bs = self.getblockSize() ** 2
        div = 4 / bs
        average_brightness *= div

        return average_brightness



    def getFourthBlockAVG(self, i, j):
    
        average_brightness = 0

        for m in range(self.getblockSize() // 2, self.getblockSize()):
            for n in range(self.getblockSize() // 2, self.getblockSize()):
                average_brightness += self.grey_level[i + m, j + n]

        bs = self.getblockSize() ** 2
        div = 4 / bs
        average_brightness = average_brightness * div
        return average_brightness
    


    def getEdgeFeature(self, i, j):
    
        average = [self.getFirstBlockAVG(i, j), self.getSecondBlockAVG(i, j),
                self.getThirdBlockAVG(i, j), self.getFourthBlockAVG(i, j)]
        
        th = self.threshold

        edge_filter = np.array([[1.0, -1.0, 1.0, -1.0],
                [1.0, 1.0, -1.0, -1.0],
                [math.sqrt(2), 0.0, 0.0, -math.sqrt(2)],
                [0.0, math.sqrt(2), -math.sqrt(2), 0.0], 
                [2.0, -2.0, -2.0, 2.0]])
        
        strengths = np.zeros(5)
        e_index = None

        for e in range(5):
            for k in range(4):
                strengths[e] += average[k] * edge_filter[e, k]
            strengths[e] = abs(strengths[e])

        e_max = 0.0
        e_max = strengths[0]
        e_index = self.vertical_edge

        if strengths[1] > e_max:
            e_max = strengths[1]
            e_index = self.horizontal_edge
        
        if (strengths[2] > e_max):
            e_max = strengths[2]
            e_index = self.diagonal_45_degree_edge
        
        if (strengths[3] > e_max):
            e_max = strengths[3]
            e_index = self.diagonal_135_degree_edge
        
        if (strengths[4] > e_max):
            e_max = strengths[4]
            e_index = self.non_directional_edge

        if (e_max < th):
            e_index = self.NoEdge

        return (e_index)


    def extractFeature(self):

        sub_local_index = 0
        EdgeTypeOfBlock = 0
        count_local = np.zeros(16)

        for j in range(0, self.height - self.getblockSize() + 1, self.getblockSize()):
            for i in range(0, self.width - self.getblockSize() + 1, self.getblockSize()):
            
                sub_local_index = ((i << 2) //self. width) + ((j << 2) // self.height << 2)
                count_local[sub_local_index] += 1

                EdgeTypeOfBlock = self.getEdgeFeature(i, j)

                if EdgeTypeOfBlock == 0:
                    pass
                elif EdgeTypeOfBlock == 1:
                    self.Local_Edge_Histogram[sub_local_index * 5] += 1
                elif EdgeTypeOfBlock == 2:
                    self.Local_Edge_Histogram[sub_local_index * 5 + 1] += 1
                elif EdgeTypeOfBlock == 4:
                    self.Local_Edge_Histogram[sub_local_index * 5 + 2] += 1
                elif EdgeTypeOfBlock == 5:
                    self.Local_Edge_Histogram[sub_local_index * 5 + 3] += 1
                elif EdgeTypeOfBlock == 3:
                    self.Local_Edge_Histogram[sub_local_index * 5 + 4] += 1

        for k in range(80):
            self.Local_Edge_Histogram[k] /= count_local[k // 5]
        
        return self.Local_Edge_Histogram

