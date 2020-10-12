import cv2
import numpy as np
from pynput.mouse import Button, Controller 
import wx
mouse=Controller()
app=wx.App(False)
(sx,sy)=wx.GetDisplaySize()
(camx,camy)=(420,340)


lower_bound=np.array([33,80,40])
upper_bound=np.array([102,255,255])

cam=cv2.VideoCapture(0)
cam.set(3,camx)
cam.set(4,camy)

kernel_open=np.ones((5,5))
kernel_close=np.ones((20,20))

mouseOldLoc=np.array([0,0])
mouseCurrentLoc=np.array([0,0])
DampingFactor=3 #for making mouse smoother

pinchflag=0
openx,openy,openw,openh=(0,0,0,0)


while True:
    ret,img=cam.read()
#    img=cv2.resize(img,(340,220))

    imgHSV=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    mask=cv2.inRange(imgHSV,lower_bound,upper_bound)

    maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel_open)
    maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernel_close)
    maskFinal=maskClose
    conts,h=cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    #cv2.drawContours(img,conts,-1,(255,0,0),2)

    # for i in range(len(conts)):
    #     x,y,w,h=cv2.boundingRect(conts[i])
    #     cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
    #     cv2.putText(img,str(i+1),(x,y+h),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2 )

    if(len(conts)==2):
        if(pinchflag==1):
            pinchflag=0
            mouse.release(Button.left)

        x1,y1,w1,h1=cv2.boundingRect(conts[0])
        x2,y2,w2,h2=cv2.boundingRect(conts[1])
      
        cv2.rectangle(img,(x1,y1),(x1+w1,y1+h1),(0,0,255),2)
        cv2.rectangle(img,(x2,y2),(x2+w2,y2+h2),(0,0,255),2)
        cx1=int((x1+w1/2))
        cy1=int((y1+h1/2))
        cx2=int((x2+w2/2))
        cy2=int((y2+h2/2))
        cx=int((cx1+cx2)/2)
        cy=int((cy1+cy2)/2)
        cv2.line(img,(cx1,cy1),(cx2,cy2),(255,0,0),2)
        cv2.circle(img,(cx,cy),2,(0,255,0),2)

        mouseCurrentLoc=mouseOldLoc+((cx,cy)-mouseOldLoc)/DampingFactor
        mouse.position=(sx-int(mouseCurrentLoc[0]*sx/camx),int(mouseCurrentLoc[1]*sy/camy))

        while mouse.position!=(sx-int(mouseCurrentLoc[0]*sx/camx),int(mouseCurrentLoc[1]*sy/camy)):
                pass
        mouseOldLoc=mouseCurrentLoc
        
        # bigcont=np.array([[[x1,y1],[x1+w1,y1+h1],[x2+y2],[x2+w2,y2+h2]]])
        points = np.array([[x1,y1],[x1+w1,y1+h1],[x2,y2],[x2+w2,y2+h2]])
        openx,openy,openw,openh=cv2.boundingRect(points)
        # cv2.rectangle(img,(openx,openy),(openx+openw,openy+openh),(255,0,0),2)
        # cv2.drawContours(img,[points],0,(0,0,0),2)

    elif(len(conts)==1):
        x,y,w,h=cv2.boundingRect(conts[0])
        if(pinchflag==0):
            if(abs((w*h-openw*openh)*100/(w*h))<30):
                pinchflag=1
                mouse.press(Button.left)

                openx,openy,openw,openh=(0,0,0,0)

        else:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
            cx=int(x+w/2)
            cy=int(y+h/2)
            cv2.circle(img,(cx,cy),int((w+h)/4),(0,255,0),2)

            mouseCurrentLoc=mouseOldLoc+((cx,cy)-mouseOldLoc)/DampingFactor
            mouse.position=(sx-int(mouseCurrentLoc[0]*sx/camx),int(mouseCurrentLoc[1]*sy/camy))

            while mouse.position!=(sx-int(mouseCurrentLoc[0]*sx/camx),int(mouseCurrentLoc[1]*sy/camy)):
                pass
            mouseOldLoc=mouseCurrentLoc
            



    cv2.imshow("original_image",img)
    # cv2.imshow("mask",mask)
    # # cv2.imshow("res",res)
    
    # cv2.imshow("maskopen",maskOpen)
    # cv2.imshow("maskclose",maskClose) 
    

    
    k=cv2.waitKey(1) & 0xff
    
    if k==27:
        break

cam.release()
cv2.destroyAllWindows()