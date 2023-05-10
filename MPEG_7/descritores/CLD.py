import numpy as np 
from PIL import Image
import math


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
        self.colorLayoutImage = np.null
        self.extract()

    def Apply(self, srcImg):

        self.srcImg = Image.load(srcImg)
        self._xSize, self._ySize = self.srcImg.size
        self.init()


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
        


        self.YCoeff[0] = self.quant_ydc(self.shape[0, 0] >> 3) >> 1
        self.CbCoeff[0] = self.quant_cdc(self.shape[1, 0] >> 3)
        self.CrCoeff[0] = self.quant_cdc(self.shape[2, 0] >> 3)

        #quantization and zig-zagging
        for i in range(64):
        
            self.YCoeff[i] = self.quant_ac((self.shape[0, (self.arrayZigZag[i])]) >> 1) >> 3
            self.CbCoeff[i] = self.quant_ac(self.shape[1, (self.arrayZigZag[i])]) >> 3
            self.CrCoeff[i] = self.quant_ac(self.shape[2, (self.arrayZigZag[i])]) >> 3
        


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
        

        if self.srcImg.PixelFormat == PixelFormat.Format8bppIndexed:
            fmt = PixelFormat.Format8bppIndexed
        else:
            fmt = PixelFormat.Format24bppRgb

        srcData = srcImg.LockBits(Rectangle(0, 0, _xSize, _ySize), ImageLockMode.ReadOnly, fmt)

        offset = srcData.Stride - srcData.Width * 3



        for yi in range(self._ySize):
                for xi in range(self._xSize):

                    R = src[2]
                    G = src[1]
                    B = src[0]

                    y_axis = (int)(yi / (self._ySize / 8.0))
                    x_axis = (int)(xi / (self._xSize / 8.0))

                    k = (y_axis << 3) + x_axis

                    #RGB to YCbCr, partition and average-calculation
                    yy = (0.299 * R + 0.587 * G + 0.114 * B) / 256.0
                    sum[0, k] += (int)(219.0 * yy + 16.5); # Y
                    sum[1, k] += (int)(224.0 * 0.564 * (B / 256.0 * 1.0 - yy) + 128.5); # Cb
                    sum[2, k] += (int)(224.0 * 0.713 * (R / 256.0 * 1.0 - yy) + 128.5); # Cr
                    cnt[k] += 1

                src += offset



        self.srcImg.UnlockBits(srcData)


        for i in range(8):
            for j in range(8):
                for k in range(3):
                    if (cnt[(i << 3) + j] != 0):
                        self.shape[k, (i << 3) + j] = (int)(sum[k, (i << 3) + j] / cnt[(i << 3) + j])
                    else:
                        self.shape[k, (i << 3) + j] = 0


    def Fdct(self, shapes):

        dct = np.array(64)

        #calculation of the cos-values of the second sum
        for i in range(8):
        
            for j in range(8):
            
                s = 0.0
                for k in range(8):
                    s += self.arrayCosin[j, k] * shapes[8 * i + k]
                dct[8 * i + j] = s

        for j in range(8):
            for i in range(8):

                s = 0.0
                for k in range(8):
                    s += self.arrayCosin[i, k] * dct[8 * k + j];
                shapes[8 * i + j] = int(math.Floor(s + 0.499999))


    def quant_ydc(self, i):

        if (i > 192):
            j = 112 + ((i - 192) >> 2)
        elif (i > 160):
            j = 96 + ((i - 160) >> 1)
        elif (i > 96):
            j = 32 + (i - 96)
        elif (i > 64):
            j = 16 + ((i - 64) >> 1)
        else:
            j = i >> 2

        return j


    def quant_cdc(self, i):

        if (i > 191):
            j = 63
        elif (i > 160):
            j = 56 + ((i - 160) >> 2)
        elif (i > 144):
            j = 48 + ((i - 144) >> 1)
        elif (i > 112):
            j = 16 + (i - 112)
        elif (i > 96):
            j = 8 + ((i - 96) >> 1)
        elif (i > 64):
            j = (i - 64) >> 2
        else:
            j = 0

        return j
    

    def quant_ac(i):

        if (i > 255):
            i = 255

        if (i < -256):
            i = -256

        if ((abs(i)) > 127):
            j = 64 + ((abs(i)) >> 2)

        elif ((abs(i)) > 63):
            j = 32 + ((abs(i)) >> 1)

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






    private static Bitmap YCrCb2RGB(int[,] rgbSmallImage)
    {
        Bitmap br = new Bitmap(240, 240, PixelFormat.Format24bppRgb);

        double rImage, gImage, bImage;

        ///
        BitmapData srcData = br.LockBits(new Rectangle(0, 0, 240, 240),
        ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);

        int offset = srcData.Stride - srcData.Width * 3;


        unsafe
        {
            byte* src = (byte*)srcData.Scan0.ToPointer();

            int i = 0;
            for (int y = 1; y <= 240; y++)
            {
                i = 0;
                if (y >= 30) i = 8;
                if (y >= 60) i = 16;
                if (y >= 90) i = 24;
                if (y >= 120) i = 32;
                if (y >= 150) i = 40;
                if (y >= 180) i = 48;
                if (y >= 210) i = 56;

                for (int x = 0; x < 8; x++)
                {

                    for (int j = 0; j < 30; j++)
                    {
                        rImage = ((rgbSmallImage[0, i] - 16.0) * 256.0) / 219.0;
                        gImage = ((rgbSmallImage[1, i] - 128.0) * 256.0) / 224.0;
                        bImage = ((rgbSmallImage[2, i] - 128.0) * 256.0) / 224.0;

                        src[2] = (byte)Math.Max(0, (int)((rImage) + (1.402 * bImage) + 0.5)); //R
                        src[1] = (byte)Math.Max(0, (int)((rImage) + (-0.34413 * gImage) + (-0.71414 * bImage) + 0.5));  //G
                        src[0] = (byte)Math.Max(0, (int)((rImage) + (1.772 * gImage) + 0.5)); //B
                        src += 3;
                    }
                    i++;

                }

                src += offset;


            }

        }

        br.UnlockBits(srcData);

        ////


        return br;
    }

    public Bitmap getColorLayoutImage()
    {
        if (colorLayoutImage != null)
            return colorLayoutImage;
        else
        {
            int[,] smallReImage = new int[3, 64];

            // inverse quantization and zig-zagging
            smallReImage[0, 0] = IquantYdc((YCoeff[0]));
            smallReImage[1, 0] = IquantCdc((CbCoeff[0]));
            smallReImage[2, 0] = IquantCdc((CrCoeff[0]));

            for (int i = 1; i < 64; i++)
            {
                smallReImage[0, (arrayZigZag[i])] = IquantYac((YCoeff[i]));
                smallReImage[1, (arrayZigZag[i])] = IquantCac((CbCoeff[i]));
                smallReImage[2, (arrayZigZag[i])] = IquantCac((CrCoeff[i]));
            }

            // inverse Discrete Cosine Transform

            int[] Temp1 = new int[64];
            int[] Temp2 = new int[64];
            int[] Temp3 = new int[64];

            for (int i = 0; i < 64; i++)
            {
                Temp1[i] = smallReImage[0, i];
                Temp2[i] = smallReImage[1, i];
                Temp3[i] = smallReImage[2, i];

            }

            Idct(Temp1);
            Idct(Temp2);
            Idct(Temp3);

            for (int i = 0; i < 64; i++)
            {
                smallReImage[0, i] = Temp1[i];
                smallReImage[1, i] = Temp2[i];
                smallReImage[2, i] = Temp3[i];
            }


            // YCrCb to RGB
            colorLayoutImage = YCrCb2RGB(smallReImage);
            return colorLayoutImage;
        }
    }

    def Idct(self, iShapes):


        dct = np.array(64);

        #calculation of the cos-values of the second sum
        for u in range(8):
            for v in range(8):

                s = 0.0
                for k in range(8):
                    s += self.arrayCosin[k, v] * iShapes[8 * u + k];
                dct[8 * u + v] = s;

        for v in range(8):
            for u in range(8):

                s = 0.0;
                for k in range(8):
                    s += self.arrayCosin[k, u] * dct[8 * k + v];
                iShapes[8 * u + v] = int(math.floor(s + 0.499999))



    def IquantYdc(self, i):

        i = i << 1
        if (i > 112):
            j = 194 + ((i - 112) << 2);
        elif (i > 96):
            j = 162 + ((i - 96) << 1);
        elif (i > 32):
            j = 96 + (i - 32);
        elif (i > 16):
            j = 66 + ((i - 16) << 1);

        else:
            j = i << 2;

        return j << 3;

    def IquantCdc(self, i):

        if (i > 63):
            j = 192
        elif (i > 56):
            j = 162 + ((i - 56) << 2)
        elif (i > 48):
            j = 145 + ((i - 48) << 1)
        elif (i > 16):
            j = 112 + (i - 16)
        elif (i > 8):
            j = 97 + ((i - 8) << 1)
        elif (i > 0):
            j = 66 + (i << 2)
        else:
            j = 64
            
        return j << 3;

    def IquantYac(self, i):

        i = i << 3;
        i -= 128;
        if (i > 128):
            i = 128
        if (i < -128):
            i = -128
        if ((math.Abs(i)) > 96):
            j = ((math.Abs(i)) << 2) - 256
        elif ((math.Abs(i)) > 64):
            j = ((math.Abs(i)) << 1) - 64
        else:
            j = math.Abs(i)

        if i < 0:
            j = -j
        else:
            j = j

        return j << 1;

    def IquantCac(self, i):
        i = i << 3;
        i -= 128;
        if (i > 128):
            i = 128
        if (i < -128):
            i = -128;
        if ((math.Abs(i)) > 96):
            j = ((math.Abs(i) << 2) - 256)
        elif ((math.Abs(i)) > 64):
            j = ((math.Abs(i) << 1) - 64)
        else:
            j = math.Abs(i)

        if i < 0:
            j = -j
        else:
            j = j

        return j
