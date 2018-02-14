import cv2
import numpy as np
from matplotlib import pyplot as plt

img=cv2.imread('/mural1_scratches.jpg',cv2.IMREAD_GRAYSCALE)
src=cv2.imread('/mural1_scratches.jpg')
cv2.imshow('src',src)
img2=cv2.medianBlur(img,31)
cv2.imshow('mb',img2)
img3=cv2.absdiff(img2,img)
cv2.imshow('diff',img3)
ret,img4=cv2.threshold(img3,50,255,cv2.THRESH_BINARY)
cv2.imshow('bin',img4)
dst = cv2.inpaint(src,img4,27,cv2.INPAINT_TELEA)
cv2.imshow('res',dst)
kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
im = cv2.filter2D(dst, -1, kernel=1.5)
cv2.imshow('final',im)
cv2.imwrite('result.jpg',im)
cv2.waitKey(0)
cv2.destroyAllWindows()
