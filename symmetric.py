import numpy as np
import cv2

img = cv2.imread('/s.png')
h,w,c=img.shape
roi1 = img[0:h,w/2:w]
roi2=cv2.flip(roi1,1)
final=np.concatenate((roi2,roi1),1)
cv2.imshow('src',img)
cv2.imshow('ROI1',roi1)
cv2.imshow('roi2',roi2)
cv2.imshow('result',final)
cv2.imwrite('o3.jpg',final)
cv2.waitKey(0)
cv2.destroyAllWindows()
