import cv2
import numpy as np

img=cv2.imread('/mural1_bwnoise.jpg')
cv2.imshow('src',img)
dst=cv2.bilateralFilter(img,9,175,75)
cv2.imshow('res',dst)
dst1=cv2.GaussianBlur(dst,(3,3),0)
cv2.imshow('mid',dst1)
kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
res = cv2.filter2D(dst1, -1, kernel=1.4)
cv2.imshow('fin',res)
cv2.imwrite('output3.jpg',res)
cv2.waitKey(0)
cv2.destroyAllWindows()
