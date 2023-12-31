import cv2
import matplotlib.pyplot as plt
import numpy as np
from RGHS_runner import rghs
from contrast_n_retinex import ret,col_enh

#create image path
def enhance_image(img):
    enh_img=col_enh(img)
    ret_img=ret(enh_img)
    rghs_img=rghs(ret_img)
    b, g,r=cv2.split(rghs_img)
    enh_r = cv2.addWeighted(r, 0.50, np.zeros_like(r), 0, 0)
    final_img= cv2.merge([b,g,enh_r])
    
    #make rgb from bgr
    rghs_img_8u = cv2.convertScaleAbs(final_img)  # Convert to 8-bit image

    # Now, you can safely perform the color conversion
    img_bgr = cv2.cvtColor(rghs_img_8u, cv2.COLOR_BGR2RGB)
    # img_bgr=cv2.cvtColor(rghs_img,cv2.COLOR_BGR2RGB)
    template=cv2.imread('pool_line.png')
    template=cv2.cvtColor(template, cv2.COLOR_BGR2RGB)

    # Store width and height of template in w and h
    w=template.shape[1]
    h=template.shape[0]

    # Perform match operations.
    res = cv2.matchTemplate(img_bgr, template, cv2.TM_CCOEFF_NORMED)

    # Specify a threshold
    threshold = 0.5
    average_pixel_value = [np.mean(img_bgr[:,:,0]),np.mean(img_bgr[:,:,1]),np.mean(img_bgr[:,:,2])]
    # Store the coordinates of matched area in a numpy array
    loc = np.where(res >= threshold)

    # Draw a rectangle around the matched region.
    for pt in zip(*loc[::-1]):
        img_bgr[pt[1]-3:pt[1] +h+3, pt[0]-3:pt[0] + w+3] = average_pixel_value


    sharpen_filter=np.array([[-1,-1,-1],
                    [-1,9.5,-1],
                  [-1,-1,-1]
    ])
    padded_image = cv2.copyMakeBorder(img_bgr, 2, 2, 2, 2, cv2.BORDER_WRAP)
    img_bgr=cv2.filter2D(padded_image,-1,sharpen_filter)

    blue=img_bgr[:,:,2]

    equ = cv2.equalizeHist(blue)

    inverted_equ=cv2.bitwise_not(equ)


    height, width = inverted_equ.shape
    for y in range(height):
      for x in range(width):
        #cv2.circle(edge2,(x,y),10,255,-1)
        neighborhood_size = 70
        half_size = neighborhood_size // 2
        neighborhood_x = slice(max(0, x - half_size), min(inverted_equ.shape[1], x + half_size + 1))
        neighborhood_y = slice(max(0, y - round(half_size/4)), min(inverted_equ.shape[0], round(y + half_size/4 + 1)))
        # Set the values in the neighborhood to 0
        if(inverted_equ[neighborhood_y, neighborhood_x]).sum() >= neighborhood_size*neighborhood_size/4 *200 :
          inverted_equ[neighborhood_y, neighborhood_x]=0
    #plt.imshow(inverted_equ)

    border_size = 3

    image_cleared = inverted_equ[border_size:height-border_size, border_size:width-border_size]

    return image_cleared
