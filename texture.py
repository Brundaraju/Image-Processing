import cv2
import sys
import numpy as np
from random import randint

img_sample = cv2.imread('/p4.jpg')
img_height=35
img_width  = 300
sample_width = img_sample.shape[1]
sample_height = img_sample.shape[0]
img = np.zeros((img_height,img_width,3), np.uint8)
PatchSize = 30
OverlapWidth = 30
InitialThresConstant = 78


randomPatchHeight = randint(0, sample_height - PatchSize)
randomPatchWidth = randint(0, sample_width - PatchSize)
for i in range(PatchSize):
    for j in range(PatchSize):
        img[i, j] = img_sample[randomPatchHeight + i, randomPatchWidth + j]
        
GrowPatchLocation = (0,PatchSize)
def OverlapErrorVertical( imgPx, samplePx ):
    iLeft,jLeft = imgPx
    iRight,jRight = samplePx
    OverlapErr = 0
    diff = np.zeros((3))
    for i in range( PatchSize ):
        for j in range( OverlapWidth ):
            diff[0] =  int(img[i + iLeft, j+ jLeft][0]) - int(img_sample[i + iRight, j + jRight][0])
            diff[1] =  int(img[i + iLeft, j+ jLeft][1]) - int(img_sample[i + iRight, j + jRight][1])
            diff[2] =  int(img[i + iLeft, j+ jLeft][2]) - int(img_sample[i + iRight, j + jRight][2])
            OverlapErr += (diff[0]**2 + diff[1]**2 + diff[2]**2)**0.5
    return OverlapErr

def OverlapErrorHorizntl( leftPx, rightPx ):
    iLeft,jLeft = leftPx
    iRight,jRight = rightPx
    OverlapErr = 0
    diff = np.zeros((3))
    for i in range( OverlapWidth ):
        for j in range( PatchSize ):
            diff[0] =  int(img[i + iLeft, j+ jLeft][0]) - int(img_sample[i + iRight, j + jRight][0])
            diff[1] =  int(img[i + iLeft, j+ jLeft][1]) - int(img_sample[i + iRight, j + jRight][1])
            diff[2] =  int(img[i + iLeft, j+ jLeft][2]) - int(img_sample[i + iRight, j + jRight][2])
            OverlapErr += (diff[0]**2 + diff[1]**2 + diff[2]**2)**0.5
    return OverlapErr

def GetBestPatches( px ):
    PixelList = []
    if px[0] == 0:
        for i in range(sample_height - PatchSize):
            for j in range(OverlapWidth, sample_width - PatchSize ):
                error = OverlapErrorVertical( (px[0], px[1] - OverlapWidth), (i, j - OverlapWidth)  )
                if error  < ThresholdOverlapError:
                    PixelList.append((i,j))
                elif error < ThresholdOverlapError/2:
                    return [(i,j)]
    #check for leftmost layer
    elif px[1] == 0:
        for i in range(OverlapWidth, sample_height - PatchSize ):
            for j in range(sample_width - PatchSize):
                error = OverlapErrorHorizntl( (px[0] - OverlapWidth, px[1]), (i - OverlapWidth, j)  )
                if error  < ThresholdOverlapError:
                    PixelList.append((i,j))
                elif error < ThresholdOverlapError/2:
                    return [(i,j)]
    
    else:
        for i in range(OverlapWidth, sample_height - PatchSize):
            for j in range(OverlapWidth, sample_width - PatchSize):
                error_Vertical   = OverlapErrorVertical( (px[0], px[1] - OverlapWidth), (i,j - OverlapWidth)  )
                error_Horizntl   = OverlapErrorHorizntl( (px[0] - OverlapWidth, px[1]), (i - OverlapWidth,j) )
                if error_Vertical  < ThresholdOverlapError and error_Horizntl < ThresholdOverlapError:
                    PixelList.append((i,j))
                elif error_Vertical < ThresholdOverlapError/2 and error_Horizntl < ThresholdOverlapError/2:
                    return [(i,j)]
    return PixelList

def SSD_Error( offset, imgPx, samplePx ):
    err_r = int(img[imgPx[0] + offset[0], imgPx[1] + offset[1]][0]) -int(img_sample[samplePx[0] + offset[0], samplePx[1] + offset[1]][0])
    err_g = int(img[imgPx[0] + offset[0], imgPx[1] + offset[1]][1]) - int(img_sample[samplePx[0] + offset[0], samplePx[1] + offset[1]][1])
    err_b = int(img[imgPx[0] + offset[0], imgPx[1] + offset[1]][2]) - int(img_sample[samplePx[0] + offset[0], samplePx[1] + offset[1]][2])
    return (err_r**2 + err_g**2 + err_b**2)/3.0


def GetCostVertical(imgPx, samplePx):
    Cost = np.zeros((PatchSize, OverlapWidth))
    for j in range(OverlapWidth):
        for i in range(PatchSize):
            if i == PatchSize - 1:
                Cost[i,j] = SSD_Error((i ,j - OverlapWidth), imgPx, samplePx)
            else:
                if j == 0 :
                    Cost[i,j] = SSD_Error((i , j - OverlapWidth), imgPx, samplePx) + min( SSD_Error((i + 1, j - OverlapWidth), imgPx, samplePx),SSD_Error((i + 1,j + 1 - OverlapWidth), imgPx, samplePx) )
                elif j == OverlapWidth - 1:
                    Cost[i,j] = SSD_Error((i, j - OverlapWidth), imgPx, samplePx) + min( SSD_Error((i + 1, j - OverlapWidth), imgPx, samplePx), SSD_Error((i + 1, j - 1 - OverlapWidth), imgPx, samplePx) )
                else:
                    Cost[i,j] = SSD_Error((i, j -OverlapWidth), imgPx, samplePx) + min(SSD_Error((i + 1, j - OverlapWidth), imgPx, samplePx),SSD_Error((i + 1, j + 1 - OverlapWidth), imgPx, samplePx),SSD_Error((i + 1, j - 1 - OverlapWidth), imgPx, samplePx))
    return Cost

def GetCostHorizntl(imgPx, samplePx):
    Cost = np.zeros((OverlapWidth, PatchSize))
    for i in range( OverlapWidth ):
        for j in range( PatchSize ):
            if j == PatchSize - 1:
                Cost[i,j] = SSD_Error((i - OverlapWidth, j), imgPx, samplePx)
            elif i == 0:
                Cost[i,j] = SSD_Error((i - OverlapWidth, j), imgPx, samplePx) + min(SSD_Error((i - OverlapWidth, j + 1), imgPx, samplePx), SSD_Error((i + 1 - OverlapWidth, j + 1), imgPx, samplePx))
            elif i == OverlapWidth - 1:
                Cost[i,j] = SSD_Error((i - OverlapWidth, j), imgPx, samplePx) + min(SSD_Error((i - OverlapWidth, j + 1), imgPx, samplePx), SSD_Error((i - 1 - OverlapWidth, j + 1), imgPx, samplePx))
            else:
                Cost[i,j] = SSD_Error((i - OverlapWidth, j), imgPx, samplePx) + min(SSD_Error((i - OverlapWidth, j + 1), imgPx, samplePx), SSD_Error((i + 1 - OverlapWidth, j + 1), imgPx, samplePx), SSD_Error((i - 1 - OverlapWidth, j + 1), imgPx, samplePx))
    return Cost

def FindMinCostPathVertical(Cost):
    Boundary = np.zeros((PatchSize),np.int)
    ParentMatrix = np.zeros((PatchSize, OverlapWidth),np.int)
    for i in range(1, PatchSize):
        for j in range(OverlapWidth):
            if j == 0:
                ParentMatrix[i,j] = j if Cost[i-1,j] < Cost[i-1,j+1] else j+1
            elif j == OverlapWidth - 1:
                ParentMatrix[i,j] = j if Cost[i-1,j] < Cost[i-1,j-1] else j-1
            else:
                curr_min = j if Cost[i-1,j] < Cost[i-1,j-1] else j-1
                ParentMatrix[i,j] = curr_min if Cost[i-1,curr_min] < Cost[i-1,j+1] else j+1
            Cost[i,j] += Cost[i-1, ParentMatrix[i,j]]
    minIndex = 0
    for j in range(1,OverlapWidth):
        minIndex = minIndex if Cost[PatchSize - 1, minIndex] < Cost[PatchSize - 1, j] else j
    Boundary[PatchSize-1] = minIndex
    for i in range(PatchSize - 1,0,-1):
        Boundary[i - 1] = ParentMatrix[i,Boundary[i]]
    return Boundary

def FindMinCostPathHorizntl(Cost):
    Boundary = np.zeros(( PatchSize),np.int)
    ParentMatrix = np.zeros((OverlapWidth, PatchSize),np.int)
    for j in range(1, PatchSize):
        for i in range(OverlapWidth):
            if i == 0:
                ParentMatrix[i,j] = i if Cost[i,j-1] < Cost[i+1,j-1] else i + 1
            elif i == OverlapWidth - 1:
                ParentMatrix[i,j] = i if Cost[i,j-1] < Cost[i-1,j-1] else i - 1
            else:
                curr_min = i if Cost[i,j-1] < Cost[i-1,j-1] else i - 1
                ParentMatrix[i,j] = curr_min if Cost[curr_min,j-1] < Cost[i-1,j-1] else i + 1
            Cost[i,j] += Cost[ParentMatrix[i,j], j-1]
    minIndex = 0
    for i in range(1,OverlapWidth):
        minIndex = minIndex if Cost[minIndex, PatchSize - 1] < Cost[i, PatchSize - 1] else i
    Boundary[PatchSize-1] = minIndex
    for j in range(PatchSize - 1,0,-1):
        Boundary[j - 1] = ParentMatrix[Boundary[j],j]
    return Boundary

def QuiltVertical(Boundary, imgPx, samplePx):
    for i in range(PatchSize):
        for j in range(Boundary[i], 0, -1):
            img[imgPx[0] + i, imgPx[1] - j] = img_sample[ samplePx[0] + i, samplePx[1] - j ]
def QuiltHorizntl(Boundary, imgPx, samplePx):
    for j in range(PatchSize):
        for i in range(Boundary[j], 0, -1):
            img[imgPx[0] - i, imgPx[1] + j] = img_sample[samplePx[0] - i, samplePx[1] + j]

def QuiltPatches( imgPx, samplePx ):
    if imgPx[0] == 0:
        Cost = GetCostVertical(imgPx, samplePx)
        Boundary = FindMinCostPathVertical(Cost)
        QuiltVertical(Boundary, imgPx, samplePx)
    elif imgPx[1] == 0:
        Cost = GetCostHorizntl(imgPx, samplePx)
        Boundary = FindMinCostPathHorizntl(Cost)
        QuiltHorizntl(Boundary, imgPx, samplePx)
    else:
        CostVertical = GetCostVertical(imgPx, samplePx)
        CostHorizntl = GetCostHorizntl(imgPx, samplePx)
        BoundaryVertical = FindMinCostPathVertical(CostVertical)
        BoundaryHorizntl = FindMinCostPathHorizntl(CostHorizntl)
        QuiltVertical(BoundaryVertical, imgPx, samplePx)
        QuiltHorizntl(BoundaryHorizntl, imgPx, samplePx)


def FillImage( imgPx, samplePx ):
    for i in range(PatchSize):
        for j in range(PatchSize):
            img[ imgPx[0] + i, imgPx[1] + j ] = img_sample[ samplePx[0] + i, samplePx[1] + j ]

pixelsCompleted = 0
TotalPatches = ( (img_height - 1 )/ PatchSize )*((img_width)/ PatchSize) - 1
sys.stdout.write("Progress : [%-20s] %d%% | PixelsCompleted: %d | ThresholdConstant: --.------" % ('='*(pixelsCompleted*20/TotalPatches), (100*pixelsCompleted)/TotalPatches, pixelsCompleted))
sys.stdout.flush()
while GrowPatchLocation[0] + PatchSize < img_height:
    pixelsCompleted += 1
    ThresholdConstant = InitialThresConstant
    #set progress to zer0
    progress = 0
    while progress == 0:
        ThresholdOverlapError = ThresholdConstant * PatchSize * OverlapWidth
        List = GetBestPatches(GrowPatchLocation)
        if len(List) > 0:
            progress = 1
            sampleMatch = List[ randint(0, len(List) - 1) ]
            FillImage( GrowPatchLocation, sampleMatch )
            QuiltPatches( GrowPatchLocation, sampleMatch )
            GrowPatchLocation = (GrowPatchLocation[0], GrowPatchLocation[1] + PatchSize)
            if GrowPatchLocation[1] + PatchSize > img_width:
                GrowPatchLocation = (GrowPatchLocation[0] + PatchSize, 0)
        else:
            ThresholdConstant *= 1.1
    sys.stdout.write('\r')
    sys.stdout.write("Progress : [%-20s] %d%% | PixelsCompleted: %d | ThresholdConstant: %f" % ('='*(pixelsCompleted*20/TotalPatches), (100*pixelsCompleted)/TotalPatches, pixelsCompleted, ThresholdConstant))
    sys.stdout.flush()

cv2.imshow('Sample Texture',img_sample)
cv2.imshow('Generated Image',img)
cv2.imwrite('o2.jpg',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
