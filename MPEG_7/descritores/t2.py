import math
import numpy as np
from PIL import Image

class CLD_Descriptor:
    def __init__(self):
        self.shape = np.zeros((3, 64), dtype=int)
        self.YCoeff = np.zeros(64, dtype=int)
        self.CbCoeff = np.zeros(64, dtype=int)
        self.CrCoeff = np.zeros(64, dtype=int)
        self.colorLayoutImage = None
        self._ySize = 0
        self._xSize = 0

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

    def apply(self, srcImg):
        self.srcImg = srcImg
        self._ySize = srcImg.height
        self._xSize = srcImg.width
        self.init()

    def init(self):
        self.shape = np.zeros((3, 64), dtype=int)
        self.YCoeff = np.zeros(64, dtype=int)
        self.CbCoeff = np.zeros(64, dtype=int)
        self.CrCoeff = np.zeros(64, dtype=int)
        self.colorLayoutImage = None
        self.extract()

    def extract(self):
        self.createShape()

        Temp1 = self.shape[0, :].copy()
        Temp2 = self.shape[1, :].copy()
        Temp3 = self.shape[2, :].copy()

        self.Fdct(Temp1)
        self.Fdct(Temp2)
        self.Fdct(Temp3)

        self.YCoeff[0] = self.quant_ydc(self.shape[0, 0] // 8) // 2
        self.CbCoeff[0] = self.quant_cdc(self.shape[1, 0] // 8)
        self.CrCoeff[0] = self.quant_cdc(self.shape[2, 0] // 8)

        for i in range(1, 64):
            self.YCoeff[i] = self.quant_ac((self.shape[0, self.arrayZigZag[i]]) // 2) // 8
            self.CbCoeff[i] = self.quant_ac(self.shape[1, self.arrayZigZag[i]]) // 8
            self.CrCoeff[i] = self.quant_ac(self.shape[2, self.arrayZigZag[i]]) // 8

    def createShape(self):
        sum_ = np.zeros((3, 64), dtype=int)
        cnt = np.zeros(64, dtype=int)
        yy = 0.0

        for yi in range(self._ySize):
            for xi in range(self._xSize):
                R, G, B = self.srcImg.getpixel((xi, yi))

                y_axis = int(yi / (self._ySize / 8.0))
                x_axis = int(xi / (self._xSize / 8.0))
                k = (y_axis << 3) + x_axis

                yy = (0.299 * R + 0.587 * G + 0.114 * B) / 256.0
                sum_[0, k] += int(219.0 * yy + 16.5)  # Y
                sum_[1, k] += int(224.0 * 0.564 * (B / 256.0 * 1.0 - yy) + 128.5)  # Cb
                sum_[2, k] += int(224.0 * 0.713 * (R / 256.0 * 1.0 - yy) + 128.5)  # Cr
                cnt[k] += 1

        for i in range(64):
            if cnt[i] != 0:
                self.shape[0, i] = sum_[0, i] / cnt[i]
                self.shape[1, i] = sum_[1, i] / cnt[i]
                self.shape[2, i] = sum_[2, i] / cnt[i]

    def Fdct(self, data):
        N = len(data)

        for k in range(N):
            sum_ = 0.0
            for n in range(N):
                sum_ += data[n] * math.cos(math.pi / N * (n + 0.5) * k)
            data[k] = sum_

    def quant_ydc(self, value):
        if value == 0:
            return 0
        elif value < 0:
            return int(value / 7.0)
        else:
            return int(value / 6.0 + 0.5)

    def quant_cdc(self, value):
        if value == 0:
            return 0
        elif value < 0:
            return int(value / 3.0)
        else:
            return int(value / 2.0 + 0.5)

    def quant_ac(self, value):
        if value < 0:
            return int(value / 4.0)
        else:
            return int(value / 3.0 + 0.5)

