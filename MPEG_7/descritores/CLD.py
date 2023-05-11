import numpy as np 
from PIL import Image
import math
import ctypes


class CLD_Descriptor:

    # static final boolean debug = true;

    def __init__(self):

        self.availableCoeffNumbers = [1, 3, 6, 10, 15, 21, 28, 64]
        self.numCCoeff = 3
        self.numYCoeff = 6

        self.arrayZigZag = np.array([0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5,
                12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7, 14, 21, 28,
                35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51,
                58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63])

        self.arrayCosin = np.array([
                [
                        3.535534e-01, 3.535534e-01, 3.535534e-01, 3.535534e-01,
                        3.535534e-01, 3.535534e-01, 3.535534e-01, 3.535534e-01
                ],
                [
                        4.903926e-01, 4.157348e-01, 2.777851e-01, 9.754516e-02,
                        -9.754516e-02, -2.777851e-01, -4.157348e-01, -4.903926e-01
                ],
                [
                        4.619398e-01, 1.913417e-01, -1.913417e-01, -4.619398e-01,
                        -4.619398e-01, -1.913417e-01, 1.913417e-01, 4.619398e-01
                ],
                [
                        4.157348e-01, -9.754516e-02, -4.903926e-01, -2.777851e-01,
                        2.777851e-01, 4.903926e-01, 9.754516e-02, -4.157348e-01
                ],
                [
                        3.535534e-01, -3.535534e-01, -3.535534e-01, 3.535534e-01,
                        3.535534e-01, -3.535534e-01, -3.535534e-01, 3.535534e-01
                ],
                [
                        2.777851e-01, -4.903926e-01, 9.754516e-02, 4.157348e-01,
                        -4.157348e-01, -9.754516e-02, 4.903926e-01, -2.777851e-01
                ],
                [
                        1.913417e-01, -4.619398e-01, 4.619398e-01, -1.913417e-01,
                        -1.913417e-01, 4.619398e-01, -4.619398e-01, 1.913417e-01
                ],
                [
                        9.754516e-02, -2.777851e-01, 4.157348e-01, -4.903926e-01,
                        4.903926e-01, -4.157348e-01, 2.777851e-01, -9.754516e-02
                ]
        ])

        self.weightMatrix = np.zeros(shape=(3,64))

        self.shape = np.zeros(shape = [3, 64])
        self.YCoeff = np.zeros(64)
        self.CbCoeff = np.zeros(64)
        self.CrCoeff = np.zeros(64)

    def apply(self, srcImg):

        self.srcImg = srcImg
        self._xSize, self._ySize = self.srcImg.size
        
        self.extract()


    def extract(self):

        self.createShape()

        Temp1 = np.zeros(64)
        Temp2 = np.zeros(64)
        Temp3 = np.zeros(64)

        for i in range(64):
        
            Temp1[i] = self.shape[0, i]
            Temp2[i] = self.shape[1, i]
            Temp3[i] = self.shape[2, i]

        self.Fdct(Temp1)
        self.Fdct(Temp2)
        self.Fdct(Temp3)


        for i in range(64):
        
            self.shape[0, i] = Temp1[i]
            self.shape[1, i] = Temp2[i]
            self.shape[2, i] = Temp3[i]
        

        
        #self.YCoeff[0] = self.quant_ydc(self.shape[0, 0] >> 3) >> 1
        self.YCoeff[0] = self.quant_ydc(self.shape[0, 0] // 8) // 2
        self.CbCoeff[0] = self.quant_cdc(self.shape[1, 0] // 8)
        self.CrCoeff[0] = self.quant_cdc(self.shape[2, 0] // 8)

        #quantization and zig-zagging
        for i in range(64):
            
            self.YCoeff[i] = self.quant_ac((self.shape[0, (self.arrayZigZag[i])]) // 2) // 8
            self.CbCoeff[i] = self.quant_ac(self.shape[1, (self.arrayZigZag[i])]) // 8
            self.CrCoeff[i] = self.quant_ac(self.shape[2, (self.arrayZigZag[i])]) // 8
        


    def createShape(self):

        sum = np.zeros(shape=(3,64))
        cnt = np.zeros(64)
        yy = 0.0

        #init of the blocks
        for i in range(64):
        
            cnt[i] = 0
            sum[0, i] = 0
            sum[1, i] = 0
            sum[2, i] = 0
            self.shape[0, i] = 0
            self.shape[1, i] = 0
            self.shape[2, i] = 0

        if self.srcImg.mode == "L":
            fmt = "L"
        else:
            fmt = "RGB"

        srcData = np.array(self.srcImg.convert(fmt))
        srcData = np.array(srcData)

        #offset = self.srcImg.size[0] * 3 - self.srcImg.width * 3

        src = srcData.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))

        for yi in range(self._ySize):
                for xi in range(self._xSize):

                    R = src[2]
                    G = src[1]
                    B = src[0]

                    y_axis = int(yi / (self._ySize / 8.0))
                    x_axis = int(xi / (self._xSize / 8.0))

                    k = (y_axis << 3) + x_axis

                    #RGB to YCbCr, partition and average-calculation
                    yy = (0.299 * R + 0.587 * G + 0.114 * B) / 256.0
                    sum[0, k] += int(219.0 * yy + 16.5) # Y
                    sum[1, k] += int(224.0 * 0.564 * (B / 256.0 * 1.0 - yy) + 128.5) # Cb
                    sum[2, k] += int(224.0 * 0.713 * (R / 256.0 * 1.0 - yy) + 128.5) # Cr
                    cnt[k] += 1

                #src += offset


        for i in range(8):
            for j in range(8):
                for k in range(3):
                    if (cnt[(i << 3) + j] != 0):
                        self.shape[k, (i << 3) + j] = int(sum[k, (i << 3) + j] / cnt[(i << 3) + j])
                    else:
                        self.shape[k, (i << 3) + j] = 0


    def Fdct(self, shapes):

        dct = np.zeros(64)

        #calculation of the cos-values of the second sum
        for i in range(8):
            for j in range(8):
            
                s = 0.0

                for k in range(8):
                    s += self.arrayCosin[j, k] * shapes[8 * i + k]

                index = 8 * i + j
                dct[index] = s

        for j in range(8):
            for i in range(8):

                s = 0.0
                for k in range(8):
                    s += self.arrayCosin[i, k] * dct[8 * k + j]
                shapes[8 * i + j] = int(math.floor(s + 0.499999))


    def quant_ydc(self, i):

        if (i > 192):
            j = 112 + ((i - 192) // 4)
        elif (i > 160):
            j = 96 + ((i - 160) // 2)
        elif (i > 96):
            j = 32 + (i - 96)
        elif (i > 64):
            j = 16 + ((i - 64) // 2)
        else:
            j = i // 4

        return j


    def quant_cdc(self, i):

        if (i > 191):
            j = 63
        elif (i > 160):
            j = 56 + ((i - 160) // 4)
        elif (i > 144):
            j = 48 + ((i - 144) // 2)
        elif (i > 112):
            j = 16 + (i - 112)
        elif (i > 96):
            j = 8 + ((i - 96) // 2)
        elif (i > 64):
            j = (i - 64) // 4
        else:
            j = 0

        return j
    

    def quant_ac(self, i):

        if (i > 255):
            i = 255

        if (i < -256):
            i = -256

        if ((abs(i)) > 127):
            j = 64 + ((abs(i)) // 4)

        elif ((abs(i)) > 63):
            j = 32 + ((abs(i)) // 2)

        else:
            j = abs(i)

        if i < 0:
            j = -j
        else:
            j = j

        j += 128

        return j



    def getRightCoeffNumber(self, num):

        val = 0
        if (num <= 1):
            val = 1
        elif (num <= 3):
            val = 3
        elif (num <= 6):
            val = 6
        elif (num <= 10):
            val = 10
        elif (num <= 15):
            val = 15
        elif (num <= 21):
            val = 21
        elif (num <= 28):
            val = 28
        elif (num > 28):
            val = 64

        return val


    def YCrCb2RGB(self, rgbSmallImage):
    
        br = Image.new("RGB", (240, 240))

        srcData = br.load()

        offset = srcData.Stride - srcData.Width * 3

        src = srcData.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))

        for y in range(1, 241):
            i = 0
            if y >= 30: 
                i = 8
            if y >= 60: 
                i = 16
            if y >= 90: 
                i = 24
            if y >= 120:
                i = 32
            if y >= 150: 
                i = 40
            if y >= 180:
                i = 48
            if y >= 210:
                i = 56

            for x in range(8):
                for j in range(30):
                
                    rImage = ((rgbSmallImage[0, i] - 16.0) * 256.0) / 219.0
                    gImage = ((rgbSmallImage[1, i] - 128.0) * 256.0) / 224.0
                    bImage = ((rgbSmallImage[2, i] - 128.0) * 256.0) / 224.0

                    src[2] = max(0, int(rImage + (1.402 * bImage) + 0.5))  # R
                    src[1] = max(0, int(rImage + (-0.34413 * gImage) + (-0.71414 * bImage) + 0.5))  # G
                    src[0] = max(0, int(rImage + (1.772 * gImage) + 0.5))  # B
                    src += 3
                
                i += 1

            src += offset

        return br
    

    def getColorLayoutImage(self):

        if self.colorLayoutImage != None:
            return self.colorLayoutImage
        else:
            smallReImage = np.array((3,64))

            smallReImage[0, 0] = self.IquantYdc((self.YCoeff[0]))
            smallReImage[1, 0] = self.IquantCdc((self.CbCoeff[0]))
            smallReImage[2, 0] = self.IquantCdc((self.CrCoeff[0]))

            for i in range(64):
                smallReImage[0, (self.arrayZigZag[i])] = self.IquantYac((self.YCoeff[i]))
                smallReImage[1, (self.arrayZigZag[i])] = self.IquantCac((self.CbCoeff[i]))
                smallReImage[2, (self.arrayZigZag[i])] = self.IquantCac((self.CrCoeff[i]))

            Temp1 = np.array(64)
            Temp2 = np.array(64)
            Temp3 = np.array(64)

            for i in range(64):
            
                Temp1[i] = smallReImage[0, i]
                Temp2[i] = smallReImage[1, i]
                Temp3[i] = smallReImage[2, i]

            self.Idct(Temp1)
            self.Idct(Temp2)
            self.Idct(Temp3)

            for i in range(64):
                smallReImage[0, i] = Temp1[i]
                smallReImage[1, i] = Temp2[i]
                smallReImage[2, i] = Temp3[i]


            self.colorLayoutImage = self.YCrCb2RGB(smallReImage)
            return self.colorLayoutImage


    def Idct(self, iShapes):

        dct = np.array(64)

        #calculation of the cos-values of the second sum
        for u in range(8):
            for v in range(8):

                s = 0.0
                for k in range(8):
                    s += self.arrayCosin[k, v] * iShapes[8 * u + k]
                dct[8 * u + v] = s

        for v in range(8):
            for u in range(8):

                s = 0.0
                for k in range(8):
                    s += self.arrayCosin[k, u] * dct[8 * k + v]
                iShapes[8 * u + v] = int(math.floor(s + 0.499999))



    def IquantYdc(self, i):

        i = i << 1
        if (i > 112):
            j = 194 + ((i - 112) // 4)
        elif (i > 96):
            j = 162 + ((i - 96) // 2)
        elif (i > 32):
            j = 96 + (i - 32)
        elif (i > 16):
            j = 66 + ((i - 16) // 2)

        else:
            j = i // 4

        return j // 8

    def IquantCdc(self, i):

        if (i > 63):
            j = 192
        elif (i > 56):
            j = 162 + ((i - 56) // 4)
        elif (i > 48):
            j = 145 + ((i - 48) // 2)
        elif (i > 16):
            j = 112 + (i - 16)
        elif (i > 8):
            j = 97 + ((i - 8) // 2)
        elif (i > 0):
            j = 66 + (i // 4)
        else:
            j = 64
            
        return j // 8

    def IquantYac(self, i):

        i = i // 8
        i -= 128
        if (i > 128):
            i = 128
        if (i < -128):
            i = -128
        if ((abs(i)) > 96):
            j = ((abs(i)) << 2) - 256
        elif ((abs(i)) > 64):
            j = ((abs(i)) << 1) - 64
        else:
            j = abs(i)

        if i < 0:
            j = -j
        else:
            j = j

        return j // 2

    def IquantCac(self, i):
        i = i // 8
        i -= 128
        if (i > 128):
            i = 128
        if (i < -128):
            i = -128
        if ((abs(i)) > 96):
            j = ((abs(i) // 4) - 256)
        elif ((abs(i)) > 64):
            j = ((abs(i) // 2) - 64)
        else:
            j = abs(i)

        if i < 0:
            j = -j
        else:
            j = j

        return j
