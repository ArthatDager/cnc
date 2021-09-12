#!/usr/bin/env python
"CNC GUI basic page switching"
import sys
import os
import pygame 
import pigpio
import socket
import linecache 
from pygame import *
from pygame.transform import scale
from pygame.locals import *
import math
pygame.warn_unwanted_files
main_dir = os.path.dirname(os.path.abspath("__file__"))

#            R    G    B
WHITE    = (255, 255, 255)
DARKGRAY = (150, 150, 150)
BLACK    = (  0,   0,   0)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
ABLUE    = ( 50,  50, 100)
COLOR_ON = (100, 100, 200)
COLOR_OFF= (255, 255, 255)
dstx = 0
dsty = 0
dscale= 1

def main():
    init()
    global DISPLAYSURF, FPSCLOCK, WINDOWWIDTH, WINDOWHEIGHT, XINV, YINV 
    global Font
    global FDMAR
    global dstx,dsty,dscale
    dstx,dsty,dscale=getscale(590,540)
    get_stpz(dstx,dsty,dscale)

    #global gsetting[5]
    Font = font.Font(None, 34)
    # if image_file is None:
    image_file = os.path.join(main_dir, 'data', 'home.png')
    margin = 80
    view_size = (500, 500)
    zoom_view_size = (500, 500)
    win_size = (800, 600)
    background_color = Color('beige')
    WINDOWWIDTH, WINDOWHEIGHT = 800, 600
    #XINV, YINV = True, True #@TODO
    XINV, YINV = False, False #@TODO
    FDMAR = False 
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    #DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT),pygame.FULLSCREEN, 32)
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
    # set up key repeating so we can hold down the key to scroll.
    #old_k_delay, old_k_interval = pygame.key.get_repeat ()
    #pygame.key.set_repeat (500, 30)

    try:
        #screen = pygame.display.set_mode(win_size,pygame.FULLSCREEN)
        screen = pygame.display.set_mode(win_size)
        screen.fill(background_color)
        pygame.display.flip()

        image = pygame.image.load(image_file).convert()
        image_w, image_h = image.get_size()

        if image_w < view_size[0] or image_h < view_size[1]:
            print ("The source image is too small for this example.")
            print ("A %i by %i or larger image is required." % zoom_view_size)
            return

        regions = pygame.Surface(win_size, 0, 24)
        pygame.display.flip()

        #screen.set_clip((margin, margin, zoom_view_size[0], zoom_view_size[1]))

        view_rect = Rect(0, 0, view_size[0], view_size[1])

        #scale(image.subsurface(view_rect), zoom_view_size,
        #      screen.subsurface(screen.get_clip()))
        #pygame.display.flip()
	#pygame.mouse.set_visible(False) #@TODO
        screenHome()

        # the direction we will scroll in.
        direction = None

        clock = pygame.time.Clock()
        clock.tick()

        going = True
    finally:
        #pygame.key.set_repeat (old_k_delay, old_k_interval)
        print 'GOOD BYE'

def showtext(win, pos, text, color, bgcolor):
    #Render Font line
    if(bgcolor=='NO'):
        textimg = Font.render(text, 1, color)
    else:
        textimg = Font.render(text, 1, color, bgcolor)
    win.blit(textimg, pos)
    return pos[0] + textimg.get_width() + 5, pos[1]

def showtextr(win, pos, angle, text, color, bgcolor):
    #Render Font line
    if(bgcolor=='NO'):
        textimg = Font.render(text, 1, color)
    else:
        textimg = Font.render(text, 1, color, bgcolor)
    textimg=pygame.transform.rotate(textimg, angle) 
    win.blit(textimg, pos)
    return pos[0] + textimg.get_width() + 5, pos[1]

def getset():
    #read setting from file and return setting array
    fo = open("setting.txt", "r")
    sett=["12","4","3","2","0"]
    count=0;
    for line in fo:
        sett[count]=line[:-1]
        count+=1
    fo.close()
    return sett

def getshset(setfile):
    #read setting from file and return setting array
    fo = open(setfile, "r")
    sett=["12","4","3","2","0"]
    count=1;
    for line in fo:
        sett[count]=line[:-1]
        count+=1
    sett[0]=str(count)
    fo.close()
    return sett

def filelines(x, y, nfile, line_off, line_count, line_length, line_selected):
    fo = open(nfile, "r")
    i=y
    lines=1
    liner=' '	
    for line in fo:
        line=line[0:(line_length+1)]
	if (lines > line_off) and (lines< (line_off + line_count + 1))  :
            if (lines == line_selected + line_off):
                showtextr(DISPLAYSURF, (x,i),0,line[:-1], COLOR_OFF, ABLUE)
                liner=line[:-1]
            else: 
                showtextr(DISPLAYSURF, (x,i),0,line[:-1], COLOR_OFF,'NO')
            i=i+25
        lines+=1
    fo.close() 
    return liner  

def wline(nfile, line_str):
    with open(nfile, "a" ) as fo:
        fo.write(line_str)
    fo.close() 

def printset(s):
    #Printing setting to file 
    fo = open("setting.txt", "w+")
    gcon = open("gconfig1.h", "w+")
    for i in range(len(s)):
        fo.write(s[i]+'\n')
    gcon.write("/*\n* gconfig.h\n*  Created by: Adros Systems\n*  Author: sdagar\n*/\n")
    gcon.write("#ifndef GCONFIG_H_\n")
    gcon.write("#define GCONFIG_H_\n")
    gcon.write("#define FINE 100\n")
    gcon.write("#define SPEED_R 12\n")
    gcon.write("#define SPEED_N 6\n")
    gcon.write("#define SPEED_DIF_X "+str(float(s[2])/10)+"\n")
    gcon.write("#define SPEED_DIF_Y "+str(float(s[3])/10)+"\n")
    gcon.write("#define SX 1\n")
    gcon.write("#define SY 1\n")
    gcon.write("#define KX 5\n")
    gcon.write("#define KY 5\n")
    gcon.write("#define NX (SPEED_R*(KX+1)/(2*SPEED_DIF_X))+1\n")
    gcon.write("#define NY (SPEED_R*(KX+1)/(2*SPEED_DIF_X))+1\n")
    gcon.write("#define FL (int)(NX>NY?NX:NY)\n")
    gcon.write("#define MAXT 5\n")
    gcon.write("#endif")

def getscale(L,H):
    #Generating Scale and starting point for gcode
    L=float(L)
    H=float(H)
    stp_file=os.path.join(main_dir, 'motion' ,'step1.txt')
    g = open(stp_file, "r")
    sx=1.176
    sy=1
    x=0
    y=0
    xMx=1.0
    xMn=-1.0
    yMx=1.0
    yMn=-1.0
    for line in g:
        if (line=='3\n'):
            y=y+sy
        elif (line=='4\n'):
            x=x-sx
            y=y+sy
        elif (line=='7\n'):	
            y=y-sy
        elif (line=='8\n'):	
            x=x+sx
            y=y-sy
        elif (line=='1\n'):
            x=x+sx
        elif (line=='2\n'):	
            x=x+sx
            y=y+sy
        elif (line=='5\n'):
            x=x-sx
        elif (line=='6\n'):
            x=x-sx
            y=y-sy
            #pygame.draw.line(DISPLAYSURF,BLACK,(xb,yb),(x,y),2)
        if (x>xMx):
            xMx=x
        if (x<xMn):
            xMn=x
        if (y>yMx):
            yMx=y
        if (y<yMn):
            yMn=y

    scx = L/(xMx-xMn)
    scy = H/(yMx-yMn)
    scale = scx
    if (scx>scy):
        scale = scy
    if (scale>0.756):
        scale = 0.756 
    stx = int(-xMn*L/(xMx-xMn))
    sty = int(-yMn*H/(yMx-yMn))
    g.close()
    return [stx,sty,scale]

def gdraw(stx,sty,scale,col):
    #Draw Gcode on screen
    #sc=getscale(590,540)
    sclx=1.176
    scly=1
    xoff=10.0;
    yoff=550.0;
    togg=False;
    #print (sc[0],sc[1],sc[2])
    stp_file=os.path.join(main_dir, 'motion' ,'step1.txt')
    g = open(stp_file, "r")
    sx=scale*sclx
    sy=scale*scly
    x=stx+xoff
    y=yoff-sty
    xb=stx+xoff
    yb=yoff-sty
    for line in g:
        if (line=='3\n'):
            y=y-sy
        elif (line=='4\n'):
            x=x-sx
            y=y-sy
        elif (line=='7\n'):	
            y=y+sy
        elif (line=='8\n'):	
            x=x+sx
            y=y+sy
        elif (line=='1\n'):
            x=x+sx
        elif (line=='2\n'):	
            x=x+sx
            y=y-sy
        elif (line=='5\n'):
            x=x-sx
        elif (line=='6\n'):
            x=x-sx
            y=y+sy
        elif (line=='9\n'):
            togg=True       
        elif (line=='0\n'):
            togg=False       
        if (togg==True):  
            colo = col  
        else:
            colo = DARKGRAY  
        if not ((int(xb)==int(x)) and (int(yb)==int(y))):
            pygame.draw.line(DISPLAYSURF,colo,(int(xb),int(yb)),(int(x),int(y)),3)
        xb=x
        yb=y
    pygame.display.update()
    g.close()

def get_stpz(stx,sty,scale):
    #Draw Gcode on screen
    #sc=getscale(590,540)
    sclx=1.176
    scly=1
    xoff=10.0;
    yoff=550.0;
    togg=False;
    count=0;
    #print (sc[0],sc[1],sc[2])
    stp_file=os.path.join(main_dir, 'motion' ,'step1.txt')
    stz_file=os.path.join(main_dir, 'motion' ,'stepz.txt')
    g = open(stp_file, "r")
    gz = open(stz_file, "w")
    sx=scale*sclx
    sy=scale*scly
    x=stx+xoff
    y=yoff-sty
    xb=stx+xoff
    yb=yoff-sty
    print "sx = "+str(sx)+"sy =" + str(sy)
    for line in g:
        if (line=='3\n'):
            y=y-sy
        elif (line=='4\n'):
            x=x-sx
            y=y-sy
        elif (line=='7\n'):	
            y=y+sy
        elif (line=='8\n'):	
            x=x+sx
            y=y+sy
        elif (line=='1\n'):
            x=x+sx
        elif (line=='2\n'):	
            x=x+sx
            y=y-sy
        elif (line=='5\n'):
            x=x-sx
        elif (line=='6\n'):
            x=x-sx
            y=y+sy
        elif (line=='9\n'):
            gz.write('9 0\n')
        elif (line=='0\n'):
            gz.write('0 0\n')

        if ((int(xb)==(int(x)+1)) and (int(yb)==(int(y)))):
            gz.write('1 ')
            gz.write(str(count))
            gz.write('\n')
        if ((int(xb)==(int(x)+1)) and (int(yb)==(int(y)+1))):
            gz.write('2 ')
            gz.write(str(count))
            gz.write('\n')
        if ((int(xb)==(int(x))) and (int(yb)==(int(y)+1))):
            gz.write('3 ')
            gz.write(str(count))
            gz.write('\n')
        if ((int(xb)==(int(x)-1)) and (int(yb)==(int(y)+1))):
            gz.write('4 ')
            gz.write(str(count))
            gz.write('\n')
        if ((int(xb)==(int(x)-1)) and (int(yb)==(int(y)))):
            gz.write('5 ')
            gz.write(str(count))
            gz.write('\n')
        if ((int(xb)==(int(x)-1)) and (int(yb)==(int(y)-1))):
            gz.write('6 ')
            gz.write(str(count))
            gz.write('\n')
        if ((int(xb)==(int(x))) and (int(yb)==(int(y)-1))):
            gz.write('7 ')
            gz.write(str(count))
            gz.write('\n')
        if ((int(xb)==(int(x)+1)) and (int(yb)==(int(y)-1))):
            gz.write('8 ')
            gz.write(str(count))
            gz.write('\n')
        count=count+1
        xb=x
        yb=y
    #pygame.display.update()
    g.close()
    gz.close()

def gdraw2(stx,sty,scale,col):
    #Draw Gcode on screen
    #sc=getscale(590,540)
    sclx=1.176
    scly=1
    xoff=10.0;
    yoff=550.0;
    togg=False;
    #print (sc[0],sc[1],sc[2])
    stp_file=os.path.join(main_dir, 'motion' ,'stepz.txt')
    g = open(stp_file, "r")
    #sx=scale*sclx
    sx=-1
    #sy=scale*scly
    sy=1
    x=stx+xoff
    y=yoff-sty
    xb=stx+xoff
    yb=yoff-sty
    for line1 in g:
        line,lineC = line1.split()
        if (line=='3'):
            y=y-sy
        elif (line=='4'):
            x=x-sx
            y=y-sy
        elif (line=='7'):	
            y=y+sy
        elif (line=='8'):	
            x=x+sx
            y=y+sy
        elif (line=='1'):
            x=x+sx
        elif (line=='2'):	
            x=x+sx
            y=y-sy
        elif (line=='5'):
            x=x-sx
        elif (line=='6'):
            x=x-sx
            y=y+sy
        elif (line=='9'):
            togg=True       
        elif (line=='0'):
            togg=False       
        if (togg==True):  
            colo = col  
        else:
            colo = DARKGRAY  
        if not ((int(xb)==int(x)) and (int(yb)==int(y))):
            pygame.draw.line(DISPLAYSURF,colo,(int(xb),int(yb)),(int(x),int(y)),3)
        xb=x
        yb=y
    pygame.display.update()
    g.close()


def dgdraw(stx,sty,scale,linS,linE):
    #Draw Diffrential Gcode on screen
    sclx=1.176
    scly=1
    togg=False
    stp_file=os.path.join(main_dir, 'motion' ,'stepd.txt')
    sx=scale*sclx
    sy=scale*scly
    x=stx+dgdraw.xoff
    y=dgdraw.yoff-sty
    xb=stx+dgdraw.xoff
    yb=dgdraw.yoff-sty
    #linecache.checkcache(stp_file)
    if linE == (-1) :
	end_tourch(stx,sty,scale)
        return
    for ln in range(linS,linE):
        line = linecache.getline(stp_file, ln)

        if (line=='3\n'):
            y=y-sy
        elif (line=='4\n'):
            x=x-sx
            y=y-sy
        elif (line=='7\n'):	
            y=y+sy
        elif (line=='8\n'):	
            x=x+sx
            y=y+sy
        elif (line=='1\n'):
            x=x+sx
        elif (line=='2\n'):	
            x=x+sx
            y=y-sy
        elif (line=='5\n'):
            x=x-sx
        elif (line=='6\n'):
            x=x-sx
            y=y+sy
        elif (line=='9\n'):
            togg=True       
        elif (line=='0\n'):
            togg=False       
        if (togg==True):  
            colo = BLUE  
        else:
            colo = YELLOW  
            
        if not ((int(xb)==int(x)) and (int(yb)==int(y))):
            pygame.draw.line(DISPLAYSURF,colo,(int(xb),int(yb)),(int(x),int(y)),3)
        xb=x
        yb=y
    pygame.display.update()
    dgdraw.xoff=xb-stx;
    dgdraw.yoff=yb+sty;

def dgdraw2(stx,sty,scale,linS,linE):
    #Draw Diffrential Gcode on screen
    sclx=1.176
    scly=1
    togg=False
    stp_file=os.path.join(main_dir, 'motion' ,'stepz.txt')
    sx=-1#scale*sclx
    sy=1#scale*scly
    x=stx+dgdraw2.xoff
    y=dgdraw2.yoff-sty
    xb=stx+dgdraw2.xoff
    yb=dgdraw2.yoff-sty
    
    
    #linecache.checkcache(stp_file)
    if linE == (-1) :
	end_tourch(stx,sty,scale)
        return
    for ln in range(linS,linE):
        line = linecache.getline(stp_file, ln)
        if not line: break 
        line1,line2 = line.split()
        
           
        dgdraw2.line_n = int(line2)
        if(int(line2)>linE):
            break 
  
        if (line1=='3'):
            y=y-sy
        elif (line1=='4'):
            x=x-sx
            y=y-sy
        elif (line1=='7'):	
            y=y+sy
        elif (line1=='8'):	
            x=x+sx
            y=y+sy
        elif (line1=='1'):
            x=x+sx
        elif (line1=='2'):	
            x=x+sx
            y=y-sy
        elif (line1=='5'):
            x=x-sx
        elif (line1=='6'):
            x=x-sx
            y=y+sy
        elif (line1=='9'):
            togg=True       
        elif (line1=='0'):
            togg=False       
        if (togg==True):  
            colo = BLUE  
        else:
            colo = YELLOW  
            
        if not ((int(xb)==int(x)) and (int(yb)==int(y))):
            pygame.draw.line(DISPLAYSURF,colo,(int(xb),int(yb)),(int(x),int(y)),3)
        xb=x
        yb=y
    pygame.display.update()
    dgdraw2.xoff=xb-stx;
    dgdraw2.yoff=yb+sty;
    linecache.clearcache()

def update_tourch(stx,sty,scale):
    update_tourch.ls.sendall('1')
    linN =update_tourch.ls.recv(8)
    update_tourch.ls.sendall('0')
    #print 'line No from Server:',(linN.strip('\0'))
    #print 'line No from Server:',int(linN.strip('\0'))
    #dgdraw.xoff=10.0;
    #dgdraw.yoff=550.0;
    #dgdraw(stx,sty,scale,1,int(linN.strip('\0')))
    dgdraw2.xoff=10.0;
    dgdraw2.yoff=550.0;
    dgdraw2.line_n=0;
    line_c = int(linN.strip('\0'))
    if (line_c >= dgdraw2.line_n) or line_c == -1 :
        dgdraw2(stx,sty,scale,1,line_c)
    if ( int(linN.strip('\0'))==(-1)):
        return False
    else:
        return True	
def pause_tourch():
    update_tourch.ls.sendall('2')
    linN =update_tourch.ls.recv(8)
    print 'Status:'+linN
    if linN.strip('\0') == 'RESUME':
        print 'YES'
        return True
    if linN.strip('\0') == 'PAUSE':
        return False 
def stop_tourch():
    update_tourch.ls.sendall('16')
    linN =update_tourch.ls.recv(8)
    print 'Status:'+linN

def end_tourch(dstx,dsty,dscale):
    update_tourch.ls.sendall('16')
    gdraw2(dstx,dsty,dscale,BLUE)
    print 'Status: END'

def circle2g(setting):
    #Radius
    fo = open(os.path.join("gcode" ,"circle.txt"), "w+")
    print "GCODE Written"
    fo.write('G%d X%d Y%d I%d J%d\n' % (2,setting[0],0,setting[0]/2,0))
    fo.write('G%d X%d Y%d I%d J%d\n' % (2,-setting[0],0,-setting[0]/2,0))
    fo.write('END')
    # Close opend file
    fo.close()    

def rectangle2g(setting):
    #Length, Hieght
    fo = open(os.path.join("gcode" ,"rect.txt"), "w+")
    print "GCODE Written"
    fo.write('G%d X%d Y%d\n' % (1,setting[0],0))
    fo.write('G%d X%d Y%d\n' % (1,0,setting[1]))
    fo.write('G%d X%d Y%d\n' % (1,-setting[0],0))
    fo.write('G%d X%d Y%d\n' % (1,0,-setting[1]))
    fo.write('END')
    # Close opend file
    fo.close()

def rhombus2g(setting):
    #Diagonal_x,Diagonal_y
    fo = open(os.path.join("gcode" ,"rhom.txt"), "w+")
    print "GCODE Written"
    fo.write('G%d X%d Y%d\n' % (1,setting[0]/2,setting[1]/2))
    fo.write('G%d X%d Y%d\n' % (1,-setting[0]/2,setting[1]/2))
    fo.write('G%d X%d Y%d\n' % (1,-setting[0]/2,-setting[1]/2))
    fo.write('G%d X%d Y%d\n' % (1,setting[0]/2,-setting[1]/2))
    fo.write('END')
    # Close opend file
    fo.close()

def triangle2g(setting):
    #Base,Hieght,vertex_x
    fo = open(os.path.join("gcode" ,"tri.txt"), "w+")
    print "GCODE Written"
    fo.write('G%d X%d Y%d\n' % (1,setting[0],0))
    fo.write('G%d X%d Y%d\n' % (1,setting[2]-setting[0],setting[1]))
    fo.write('G%d X%d Y%d\n' % (1,-setting[2],-setting[1]))
    fo.write('END')
    # Close opend file
    fo.close()

def polygon2g(setting):
    #N,Radius
    fo = open(os.path.join("gcode" ,"poly.txt"), "w+")
    print "GCODE Written"
    angle = 0
    for i  in range(setting[0]):
        d = [setting[1]*(math.cos(angle+2*math.pi/setting[0])-math.cos(angle)),setting[1]*(math.sin(angle+2*math.pi/setting[0])-math.sin(angle))]
        fo.write('G%d X%f Y%f\n' % (1,d[0],d[1]))
        angle += 2*math.pi/setting[0]  
    fo.write('END')
    # Close opend file
    fo.close()

def star2g(setting):
    #N,Inner_R,Outer_R
    fo = open(os.path.join("gcode" ,"star.txt"), "w+")
    print "GCODE Written"
    angle = 0
    R1 = setting[1]
    R2 = setting[2]
    for i  in range(2*setting[0]):
        d = [R1*math.cos(angle+math.pi/setting[0])-R2*math.cos(angle),R1*math.sin(angle+math.pi/setting[0])-R2*math.sin(angle)]
        fo.write('G%d X%f Y%f\n' % (1,d[0],d[1]))
        angle += math.pi/setting[0]  
        R=R1
        R1=R2
        R2=R
    fo.write('END')
    # Close opend file
    fo.close()

def screenCali():
    #Home screen to salect basic options
    image_arr = [os.path.join(main_dir, 'data', 'cr.png'), os.path.join(main_dir, 'data', 'cl.png'), os.path.join(main_dir, 'data', 'ct.png'), os.path.join(main_dir, 'data', 'cb.png')]
    for i in range(4):
        SIMAGE = pygame.image.load(image_arr[i])
        DISPLAYSURF.blit(SIMAGE, (0, 0))
        loop = True
        pygame.display.update()
        while loop :
            event = pygame.event.wait()
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == MOUSEBUTTONUP:
                screenNeedsRedraw = True # screen should be redrawn
                loop=False
    dstx,dsty,dscale=getscale(590,540)
    get_stpz(dstx,dsty,dscale)
    gdraw2(dstx,dsty,dscale,WHITE)

    screenHome()

def screenHome():
    #Home screen to salect basic options
    global dstx,dsty,dscale
    image_file = os.path.join(main_dir, 'data', 'home.png')
    SIMAGE = pygame.image.load(image_file)
    DISPLAYSURF.blit(SIMAGE, (0, 0))

    BUTTON1 = (630,0,170,114)
    BUTTON1s = [630,0,170,114]

    BUTTON2 = (630,121,170,114)
    BUTTON2s = [630,121,170,114]

    BUTTON3 = (630,242,170,114)
    BUTTON3s = [630,242,170,114]

    BUTTON4 = (630,366,170,114)
    BUTTON4s = [630,366,170,114]

    BUTTON5 = (630,488,170,114)
    BUTTON5s = [630,488,170,114]

    screenNeedsRedraw = True 
    
    if XINV == True:
        BUTTON1s[0] = WINDOWWIDTH - BUTTON1s[0] - BUTTON1s[2]
        BUTTON2s[0] = WINDOWWIDTH - BUTTON2s[0] - BUTTON2s[2]
        BUTTON3s[0] = WINDOWWIDTH - BUTTON3s[0] - BUTTON3s[2]
        BUTTON4s[0] = WINDOWWIDTH - BUTTON4s[0] - BUTTON4s[2]
        BUTTON5s[0] = WINDOWWIDTH - BUTTON5s[0] - BUTTON5s[2]
    if YINV == True:
        BUTTON1s[1] = WINDOWHEIGHT - BUTTON1s[1] - BUTTON1s[3]
        BUTTON2s[1] = WINDOWHEIGHT - BUTTON2s[1] - BUTTON2s[3]
        BUTTON3s[1] = WINDOWHEIGHT - BUTTON3s[1] - BUTTON3s[3]
        BUTTON4s[1] = WINDOWHEIGHT - BUTTON4s[1] - BUTTON4s[3]
        BUTTON5s[1] = WINDOWHEIGHT - BUTTON5s[1] - BUTTON5s[3]
    #dstx,dsty,dscale=getscale(590,540)
    #get_stpz(dstx,dsty,dscale)
    print str(dstx)+", "+str(dsty)+", "+str(dscale)
    gdraw2(dstx,dsty,dscale,WHITE)
    while True:
        if screenNeedsRedraw:
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON1,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON2,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON3,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON4,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON5,2)
            pygame.display.update()
            FPSCLOCK.tick(300)

        screenNeedsRedraw = False # by default, don't redraw the screen
        event = pygame.event.wait()
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYUP:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == MOUSEBUTTONUP:
            screenNeedsRedraw = True # screen should be redrawn
            mousex, mousey = event.pos # syntactic sugar

            # check for clicks on the difficulty buttons
            if pygame.Rect((BUTTON1s)).collidepoint(mousex, mousey):
                print 'HOME RUN'
                screenRun()
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON1,2)
            elif pygame.Rect((BUTTON2s)).collidepoint(mousex, mousey):
                print 'HOME SHAPES'
                screenShapes()
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON2,2)
            elif pygame.Rect((BUTTON3s)).collidepoint(mousex, mousey):
                print 'HOME SETUP'
                screenSetup()
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON3,2)
            elif pygame.Rect((BUTTON4s)).collidepoint(mousex, mousey):
                print 'HOME GCODE'
                screenGcode()
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON4,2)
            elif pygame.Rect((BUTTON5s)).collidepoint(mousex, mousey):
                print 'HOME USB'
                screenUsb()
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON5,2)
            pygame.display.update()

def screenRun():
    #Run screen to run Gcode
    global difficulty, boxSize, boardWidth, boardHeight, maxLife, paletteColors, bgColor
    global FDMAR
    image_file = os.path.join(main_dir, 'data', 'run.png')
    SIMAGE = pygame.image.load(image_file)
    DISPLAYSURF.blit(SIMAGE, (0, 0))

    BUTTON1 = (630,0,170,114)
    BUTTON1s = [630,0,170,114]

    BUTTON2 = (630,121,170,114)
    BUTTON2s = [630,121,170,114]

    BUTTON3 = (630,242,170,114)
    BUTTON3s = [630,242,170,114]

    BUTTON4 = (630,366,170,114)
    BUTTON4s = [630,366,170,114]

    BUTTON5 = (630,488,170,114)
    BUTTON5s = [630,488,170,114]
    
    screenNeedsRedraw = True
    
    
    if XINV == True:
        BUTTON1s[0] = WINDOWWIDTH - BUTTON1s[0] - BUTTON1s[2]
        BUTTON2s[0] = WINDOWWIDTH - BUTTON2s[0] - BUTTON2s[2]
        BUTTON3s[0] = WINDOWWIDTH - BUTTON3s[0] - BUTTON3s[2]
        BUTTON4s[0] = WINDOWWIDTH - BUTTON4s[0] - BUTTON4s[2]
        BUTTON5s[0] = WINDOWWIDTH - BUTTON5s[0] - BUTTON5s[2]
    if YINV == True:
        BUTTON1s[1] = WINDOWHEIGHT - BUTTON1s[1] - BUTTON1s[3]
        BUTTON2s[1] = WINDOWHEIGHT - BUTTON2s[1] - BUTTON2s[3]
        BUTTON3s[1] = WINDOWHEIGHT - BUTTON3s[1] - BUTTON3s[3]
        BUTTON4s[1] = WINDOWHEIGHT - BUTTON4s[1] - BUTTON4s[3]
        BUTTON5s[1] = WINDOWHEIGHT - BUTTON5s[1] - BUTTON5s[3]

    gdraw2(dstx,dsty,dscale,WHITE)
    spath = os.path.join(main_dir, "motion", "step1.txt" )
    dpath = os.path.join(main_dir, "motion", "stepd.txt" )
    cpsd = 'cp -f '+ spath + ' ' + dpath 
    os.system(cpsd)
    linecache.checkcache(dpath)

    while True:
        if screenNeedsRedraw:
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON1,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON2,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON3,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON4,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON5,2)
            pygame.display.update()
            FPSCLOCK.tick(300)

        screenNeedsRedraw = False # by default, don't redraw the screen
        if (FDMAR == True):
           for num in range(1,10):
               event = pygame.event.poll()
               if event.type == MOUSEBUTTONUP:
                   break    
               time.delay(10)     
        else:
            event = pygame.event.wait()

        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYUP:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == MOUSEBUTTONUP:
            screenNeedsRedraw = True # screen should be redrawn
            mousex, mousey = event.pos # syntactic sugar

            # check for clicks on the difficulty buttons
            if pygame.Rect((BUTTON1s)).collidepoint(mousex, mousey):
                print 'RUN HOME'
                screenHome()
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON1,2)

            elif pygame.Rect((BUTTON2s)).collidepoint(mousex, mousey):
                print 'RUN PLACE'
                screenPlace()
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON2,2)

            elif pygame.Rect((BUTTON3s)).collidepoint(mousex, mousey):
                dgdraw2.xoff=10.0;
                dgdraw2.yoff=550.0;
                print 'RUN START'
		os.system("./intr_fdma.exe 8989&")
                os.system('sudo ./fdma.exe 10000&') #TODO
                FDMAR = True
		time.delay(100)
                update_tourch.ls=socket.socket()
                update_tourch.ls.connect(('localhost',8989))
                update_tourch.ls.sendall('Communication Start')

                print 'fdma.exe is executed'
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON3,2)

            elif pygame.Rect((BUTTON4s)).collidepoint(mousex, mousey):
                FDMAR = False 
		FDMAR=pause_tourch()
                print 'RUN PAUSE'
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON4,2)
                
            elif pygame.Rect((BUTTON5s)).collidepoint(mousex, mousey):
                #stop_tourch()
                print 'RUN STOP'
                time.delay(200)     
                update_tourch.ls.close()
                time.delay(200)     
                os.system('sudo pkill fdma.exe') #TODO
                os.system('sudo pkill intr_fdma.exe') #TODO
                FDMAR = False
                #update_tourch.ls.shutdown(socket.SHUT_RDWR)
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON5,2)
                screenHome()
            pygame.display.update()
        else:
	    if FDMAR == True :
                FDMAR=update_tourch(dstx,dsty,dscale)
                if (FDMAR == False): 
                    update_tourch.ls.close()

def screenPlace():
    #Place screen to place tourch
    global difficulty, boxSize, boardWidth, boardHeight, maxLife, paletteColors, bgColor
    image_file = os.path.join(main_dir, 'data', 'place.png')
    SIMAGE = pygame.image.load(image_file)
    DISPLAYSURF.blit(SIMAGE, (0, 0))
    os.system('sudo ./place.exe&')
    os.system("./intrcon.exe 8899 &")
    time.delay(200)
    #pi=pigpio.pi()
    #os.system('sudo pigs m 18 w')
    #pi.set_mode(18,pigpio.OUTPUT)
    #pi.set_mode(23,pigpio.OUTPUT)
    #pi.set_mode(24,pigpio.OUTPUT)
    #pi.set_mode(25,pigpio.OUTPUT)
    #os.system('sudo pigs m 23 w')
    #os.system('sudo pigs m 24 w')
    #os.system('sudo pigs m 25 w')
    BUTTON1 = (630,0,170,114)
    BUTTON1s = [630,0,170,114]

    BUTTON2 = (630,121,170,114)
    BUTTON2s = [630,121,170,114]

    BUTTON3 = (630,242,170,114)
    BUTTON3s = [630,242,170,114]

    BUTTON4 = (630,366,170,114)
    BUTTON4s = [630,366,170,114]

    BUTTON5 = (630,488,170,114)
    BUTTON5s = [630,488,170,114]

    screenNeedsRedraw = True 
   
    
    if XINV == True:
        BUTTON1s[0] = WINDOWWIDTH - BUTTON1s[0] - BUTTON1s[2]
        BUTTON2s[0] = WINDOWWIDTH - BUTTON2s[0] - BUTTON2s[2]
        BUTTON3s[0] = WINDOWWIDTH - BUTTON3s[0] - BUTTON3s[2]
        BUTTON4s[0] = WINDOWWIDTH - BUTTON4s[0] - BUTTON4s[2]
        BUTTON5s[0] = WINDOWWIDTH - BUTTON5s[0] - BUTTON5s[2]
    if YINV == True:
        BUTTON1s[1] = WINDOWHEIGHT - BUTTON1s[1] - BUTTON1s[3]
        BUTTON2s[1] = WINDOWHEIGHT - BUTTON2s[1] - BUTTON2s[3]
        BUTTON3s[1] = WINDOWHEIGHT - BUTTON3s[1] - BUTTON3s[3]
        BUTTON4s[1] = WINDOWHEIGHT - BUTTON4s[1] - BUTTON4s[3]
        BUTTON5s[1] = WINDOWHEIGHT - BUTTON5s[1] - BUTTON5s[3]
    ls=socket.socket()
    ls.connect(('localhost',8899))
    ls.sendall('Communication Start')

    while True:
        if screenNeedsRedraw:
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON1,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON2,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON3,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON4,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON5,2)
            pygame.display.update()
            FPSCLOCK.tick(300)
        screenNeedsRedraw = False # by default, don't redraw the screen
        event = pygame.event.wait()
        if event.type == QUIT:
            print 'QUIT'
            pygame.quit()
            sys.exit()
        elif event.type == KEYUP:
            if event.key == K_ESCAPE:
                print 'QUIT'
                pygame.quit()
                sys.exit()
        elif event.type == MOUSEBUTTONUP :
            screenNeedsRedraw = True # screen should be redrawn
            mousex, mousey = event.pos # syntactic sugar
            #print pygame.mouse.get_pressed()
            # check for clicks on the difficulty buttons
            if pygame.Rect((BUTTON1s)).collidepoint(mousex, mousey):

                ls.sendall('16')
                time.delay(200)
                ls.close()
                print 'PLACE BACK'
                screenRun()
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON1,2)
        elif  pygame.mouse.get_pressed() == (1,0,0):
            mousex, mousey = event.pos # syntactic sugar
            if pygame.Rect((BUTTON2s)).collidepoint(mousex, mousey):
                ls.sendall('1')
		msg=ls.recv(2);
                print 'CLIENT:' + msg
                print 'PLACE UP'
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON2,2)
            elif pygame.Rect((BUTTON3s)).collidepoint(mousex, mousey):
                ls.sendall('4')
		msg=ls.recv(2);
                print 'CLIENT:' + msg

                print 'PLACE RIGHT'
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON3,2)
            elif pygame.Rect((BUTTON4s)).collidepoint(mousex, mousey):
                ls.sendall('8')
		msg=ls.recv(2);
                print 'CLIENT:' + msg
                print 'PLACE LEFT'
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON4,2)
            elif pygame.Rect((BUTTON5s)).collidepoint(mousex, mousey):
                ls.sendall('2')
		msg=ls.recv(2);
                print 'CLIENT:' + msg
                print 'PLACE DOWN'
                pygame.draw.rect(DISPLAYSURF,COLOR_ON,BUTTON5,2)
            else:
                ls.sendall('0')
                print 'PLACE DOWN'
            pygame.display.update()

def screenShapes():
    #Shapes screen to salect predefined shapes
    global difficulty, boxSize, boardWidth, boardHeight, maxLife, paletteColors, bgColor
    image_file = os.path.join(main_dir, 'data', 'shapes.png')
    SIMAGE = pygame.image.load(image_file)
    DISPLAYSURF.blit(SIMAGE, (0, 0))

    #Circle
    BUTTON1 = (19,18,142,142)
    BUTTON1s = [19,18,142,142]
    #Rectangle
    BUTTON2 = (225,18,142,142)
    BUTTON2s = [225,18,142,142]
    #Star
    BUTTON3 = (433,18,142,142)
    BUTTON3s = [433,18,142,142]
    #Blank
    BUTTON4 = (638,18,142,142)
    BUTTON4s = [638,18,142,142]
    #Rhombus
    BUTTON5 = (19,218,142,142)
    BUTTON5s = [19,218,142,142]
    #Triangle
    BUTTON6 = (225,218,142,142)
    BUTTON6s = [225,218,142,142]
    #Polygon
    BUTTON7 = (433,218,142,142)
    BUTTON7s = [433,218,142,142]    
    #Blank
    BUTTON8 = (638,218,142,142)
    BUTTON8s = [638,218,142,142]
    #Blank
    BUTTON9 = (19,418,142,142)
    BUTTON9s = [19,418,142,142]
    #Blank
    BUTTON10 = (225,418,142,142)
    BUTTON10s = [225,418,142,142]
    #Blank
    BUTTON11 = (433,418,142,142)
    BUTTON11s = [433,418,142,142]
    #Cancel
    BUTTON12 = (638,418,142,142)
    BUTTON12s = [638,418,142,142]

    screenNeedsRedraw = True 
    
    
    if XINV == True:
        BUTTON1s[0] = WINDOWWIDTH - BUTTON1s[0] - BUTTON1s[2]
        BUTTON2s[0] = WINDOWWIDTH - BUTTON2s[0] - BUTTON2s[2]
        BUTTON3s[0] = WINDOWWIDTH - BUTTON3s[0] - BUTTON3s[2]
        BUTTON4s[0] = WINDOWWIDTH - BUTTON4s[0] - BUTTON4s[2]
        BUTTON5s[0] = WINDOWWIDTH - BUTTON5s[0] - BUTTON5s[2]
        BUTTON6s[0] = WINDOWWIDTH - BUTTON6s[0] - BUTTON6s[2]
        BUTTON7s[0] = WINDOWWIDTH - BUTTON7s[0] - BUTTON7s[2]
        BUTTON8s[0] = WINDOWWIDTH - BUTTON8s[0] - BUTTON8s[2]
        BUTTON9s[0] = WINDOWWIDTH - BUTTON9s[0] - BUTTON9s[2]
        BUTTON10s[0] = WINDOWWIDTH - BUTTON10s[0] - BUTTON10s[2]
        BUTTON11s[0] = WINDOWWIDTH - BUTTON11s[0] - BUTTON11s[2]
        BUTTON12s[0] = WINDOWWIDTH - BUTTON12s[0] - BUTTON12s[2]
    if YINV == True:
        BUTTON1s[1] = WINDOWHEIGHT - BUTTON1s[1] - BUTTON1s[3]
        BUTTON2s[1] = WINDOWHEIGHT - BUTTON2s[1] - BUTTON2s[3]
        BUTTON3s[1] = WINDOWHEIGHT - BUTTON3s[1] - BUTTON3s[3]
        BUTTON4s[1] = WINDOWHEIGHT - BUTTON4s[1] - BUTTON4s[3]
        BUTTON5s[1] = WINDOWHEIGHT - BUTTON5s[1] - BUTTON5s[3]
        BUTTON6s[1] = WINDOWHEIGHT - BUTTON6s[1] - BUTTON6s[3]
        BUTTON7s[1] = WINDOWHEIGHT - BUTTON7s[1] - BUTTON7s[3]
        BUTTON8s[1] = WINDOWHEIGHT - BUTTON8s[1] - BUTTON8s[3]
        BUTTON9s[1] = WINDOWHEIGHT - BUTTON9s[1] - BUTTON9s[3]
        BUTTON10s[1] = WINDOWHEIGHT - BUTTON10s[1] - BUTTON10s[3]
        BUTTON11s[1] = WINDOWHEIGHT - BUTTON11s[1] - BUTTON11s[3]
        BUTTON12s[1] = WINDOWHEIGHT - BUTTON12s[1] - BUTTON12s[3]
    
    while True:
        if screenNeedsRedraw:
            pygame.display.update()
            FPSCLOCK.tick(300)

        screenNeedsRedraw = False # by default, don't redraw the screen
        event = pygame.event.wait()
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYUP:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == MOUSEBUTTONUP:
            screenNeedsRedraw = True # screen should be redrawn
            mousex, mousey = event.pos # syntactic sugar

            # check for clicks on the difficulty buttons
            if pygame.Rect((BUTTON1s)).collidepoint(mousex, mousey):
                print 'SHAPES CIRCLE'
                screenSetsh('cir')
            elif pygame.Rect((BUTTON2s)).collidepoint(mousex, mousey):
                print 'SHAPES RECTANGLE'
                screenSetsh('rec')
            elif pygame.Rect((BUTTON3s)).collidepoint(mousex, mousey):
                print 'SHAPES STAR'
                screenSetsh('sta')
            elif pygame.Rect((BUTTON4s)).collidepoint(mousex, mousey):
                print 'SHAPES BLANK'
            elif pygame.Rect((BUTTON5s)).collidepoint(mousex, mousey):
                print 'SHAPES RHOMBUS'
                screenSetsh('rho')
            elif pygame.Rect((BUTTON6s)).collidepoint(mousex, mousey):
                print 'SHAPES TRIANGLE'
                screenSetsh('tri')
            elif pygame.Rect((BUTTON7s)).collidepoint(mousex, mousey):
                print 'SHAPES POLYGON'
                screenSetsh('pol')
            elif pygame.Rect((BUTTON8s)).collidepoint(mousex, mousey):
                print 'SHAPES BLANK'
            elif pygame.Rect((BUTTON9s)).collidepoint(mousex, mousey):
                print 'SHAPES BLANK'
            elif pygame.Rect((BUTTON10s)).collidepoint(mousex, mousey):
                print 'SHAPES BLANK'
            elif pygame.Rect((BUTTON11s)).collidepoint(mousex, mousey):
                print 'SHAPES BLANK'
            elif pygame.Rect((BUTTON12s)).collidepoint(mousex, mousey):
                print 'SHAPES CANCEL'
                screenHome()
            pygame.display.update()

def screenSetup():
    #Setup screen change settings
    global difficulty, boxSize, boardWidth, boardHeight, maxLife, paletteColors, bgColor
    image_file = os.path.join(main_dir, 'data', 'setup.png')
    SIMAGE = pygame.image.load(image_file)
    DISPLAYSURF.blit(SIMAGE, (0, 0))

    BUTTON1 = (630,0,170,114)
    BUTTON1s = [630,0,170,114]

    BUTTON2 = (630,121,170,114)
    BUTTON2s = [630,121,170,114]

    BUTTON3 = (630,242,170,114)
    BUTTON3s = [630,242,170,114]

    BUTTON4 = (630,366,170,114)
    BUTTON4s = [630,366,170,114]

    BUTTON5 = (630,488,170,114)
    BUTTON5s = [630,488,170,114]

    screenNeedsRedraw = True 
    
    
    if XINV == True:
        BUTTON1s[0] = WINDOWWIDTH - BUTTON1s[0] - BUTTON1s[2]
        BUTTON2s[0] = WINDOWWIDTH - BUTTON2s[0] - BUTTON2s[2]
        BUTTON3s[0] = WINDOWWIDTH - BUTTON3s[0] - BUTTON3s[2]
        BUTTON4s[0] = WINDOWWIDTH - BUTTON4s[0] - BUTTON4s[2]
        BUTTON5s[0] = WINDOWWIDTH - BUTTON5s[0] - BUTTON5s[2]
    if YINV == True:
        BUTTON1s[1] = WINDOWHEIGHT - BUTTON1s[1] - BUTTON1s[3]
        BUTTON2s[1] = WINDOWHEIGHT - BUTTON2s[1] - BUTTON2s[3]
        BUTTON3s[1] = WINDOWHEIGHT - BUTTON3s[1] - BUTTON3s[3]
        BUTTON4s[1] = WINDOWHEIGHT - BUTTON4s[1] - BUTTON4s[3]
        BUTTON5s[1] = WINDOWHEIGHT - BUTTON5s[1] - BUTTON5s[3]
   
    setting = getset()
    set4 = ['mm', 'inch']
    colbac=[ABLUE, 'NO', 'NO', 'NO', 'NO']
    selset = 0
    setrMx=[23, 23, 15, 15, 1]
    setrMn=[0, 0,  0,  0, 0]
    showtext(DISPLAYSURF, (440, 30), setting[0], COLOR_OFF, 'NO')
    showtext(DISPLAYSURF, (440,100), setting[1], COLOR_OFF, colbac[1])
    showtext(DISPLAYSURF, (440,170), setting[2], COLOR_OFF, colbac[2])
    showtext(DISPLAYSURF, (440,240), setting[3], COLOR_OFF, colbac[3])
    showtext(DISPLAYSURF, (440,310), set4[int(setting[4])], COLOR_OFF, colbac[4])
    while True:
        if screenNeedsRedraw:
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON1,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON2,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON3,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON4,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON5,2)
            pygame.display.update()
            FPSCLOCK.tick(300)

        screenNeedsRedraw = False # by default, don't redraw the screen
        event = pygame.event.wait()
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYUP:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == MOUSEBUTTONUP:
            screenNeedsRedraw = True # screen should be redrawn
            mousex, mousey = event.pos # syntactic sugar

            # check for clicks on the difficulty buttons
            if pygame.Rect((BUTTON1s)).collidepoint(mousex, mousey):
                colbac[selset]='NO'
                if(selset==0):
                    selset=5
                selset-=1;
                colbac[selset]=ABLUE
                DISPLAYSURF.blit(SIMAGE, (0, 0))
                print 'SETUP UP'
            elif pygame.Rect((BUTTON2s)).collidepoint(mousex, mousey):
                if(int(setting[selset])<setrMx[selset]):
                    setting[selset]=str(int(setting[selset])+1);
                print 'SETUP ADD'
            elif pygame.Rect((BUTTON3s)).collidepoint(mousex, mousey):
                if(int(setting[selset])>setrMn[selset]):
                    setting[selset]=str(int(setting[selset])-1);
                print 'SETUP SUB'
            elif pygame.Rect((BUTTON4s)).collidepoint(mousex, mousey):
                colbac[selset]='NO'
                if(selset==4):
                    selset=-1
                selset+=1;
                colbac[selset]=ABLUE
                DISPLAYSURF.blit(SIMAGE, (0, 0))
                print 'SETUP DOWN'
            elif pygame.Rect((BUTTON5s)).collidepoint(mousex, mousey):
                printset(setting)
                os.system('g++ -I . gdecode.cpp -o gdecode.exe')
                print 'SETUP DONE'
                screenHome()

            #setting[0]=str(int(setting[0])+1);
            
            pygame.draw.rect(DISPLAYSURF,ABLUE,(362,21+71*selset,243,36),0)
            showtext(DISPLAYSURF, (440, 30), setting[0], COLOR_OFF, colbac[0])
            showtext(DISPLAYSURF, (440,100), setting[1], COLOR_OFF, colbac[1])
            showtext(DISPLAYSURF, (440,170), setting[2], COLOR_OFF, colbac[2])
            showtext(DISPLAYSURF, (440,240), setting[3], COLOR_OFF, colbac[3])
            showtext(DISPLAYSURF, (440,310), set4[int(setting[4])], COLOR_OFF, colbac[4])
            pygame.display.update()

def screenGcode():
    #Gcode screen to creat custom gcode
    global difficulty, boxSize, boardWidth, boardHeight, maxLife, paletteColors, bgColor
    image_file = os.path.join(main_dir, 'data', 'gcode.png')
    SIMAGE = pygame.image.load(image_file)
    DISPLAYSURF.blit(SIMAGE, (0, 0))

    #X
    BUTTON1s = [9,365,96,74]
    #I
    BUTTON2s = [112,365,96,74]
    #1
    BUTTON3s = [216,365,96,74]
    #2
    BUTTON4s = [320,365,96,74]
    #3
    BUTTON5s = [423,365,96,74]
    #0
    BUTTON6s = [527,365,96,74]
    #Y
    BUTTON7s = [9,446,96,74]
    #J
    BUTTON8s = [112,446,96,74]
    #4
    BUTTON9s = [216,446,96,74]
    #5
    BUTTON10s = [320,446,96,74]
    #6
    BUTTON11s = [423,446,96,74]
    #.
    BUTTON12s = [527,446,96,74]
    #Z
    BUTTON13s = [9,525,96,74]
    #K
    BUTTON14s = [112,525,96,74]
    #7
    BUTTON15s = [216,525,96,74]
    #8
    BUTTON16s = [320,525,96,74]
    #9
    BUTTON17s = [423,525,96,74]
    #-
    BUTTON18s = [527,525,96,74]
    #Next
    BUTTON19s = [630,365,170,114]
    #Done
    BUTTON20s = [630,487,170,114]    
    screenNeedsRedraw = True 
    
    if XINV == True:
        BUTTON1s[0] = WINDOWWIDTH - BUTTON1s[0] - BUTTON1s[2]
        BUTTON2s[0] = WINDOWWIDTH - BUTTON2s[0] - BUTTON2s[2]
        BUTTON3s[0] = WINDOWWIDTH - BUTTON3s[0] - BUTTON3s[2]
        BUTTON4s[0] = WINDOWWIDTH - BUTTON4s[0] - BUTTON4s[2]
        BUTTON5s[0] = WINDOWWIDTH - BUTTON5s[0] - BUTTON5s[2]
        BUTTON6s[0] = WINDOWWIDTH - BUTTON6s[0] - BUTTON6s[2]
        BUTTON7s[0] = WINDOWWIDTH - BUTTON7s[0] - BUTTON7s[2]
        BUTTON8s[0] = WINDOWWIDTH - BUTTON8s[0] - BUTTON8s[2]
        BUTTON9s[0] = WINDOWWIDTH - BUTTON9s[0] - BUTTON9s[2]
        BUTTON10s[0] = WINDOWWIDTH - BUTTON10s[0] - BUTTON10s[2]
        BUTTON11s[0] = WINDOWWIDTH - BUTTON11s[0] - BUTTON11s[2]
        BUTTON12s[0] = WINDOWWIDTH - BUTTON12s[0] - BUTTON12s[2]
        BUTTON13s[0] = WINDOWWIDTH - BUTTON13s[0] - BUTTON13s[2]
        BUTTON14s[0] = WINDOWWIDTH - BUTTON14s[0] - BUTTON14s[2]
        BUTTON15s[0] = WINDOWWIDTH - BUTTON15s[0] - BUTTON15s[2]
        BUTTON16s[0] = WINDOWWIDTH - BUTTON16s[0] - BUTTON16s[2]
        BUTTON17s[0] = WINDOWWIDTH - BUTTON17s[0] - BUTTON17s[2]
        BUTTON18s[0] = WINDOWWIDTH - BUTTON18s[0] - BUTTON18s[2]
        BUTTON19s[0] = WINDOWWIDTH - BUTTON19s[0] - BUTTON19s[2]
        BUTTON20s[0] = WINDOWWIDTH - BUTTON20s[0] - BUTTON20s[2]

    if YINV == True:
        BUTTON1s[1] = WINDOWHEIGHT - BUTTON1s[1] - BUTTON1s[3]
        BUTTON2s[1] = WINDOWHEIGHT - BUTTON2s[1] - BUTTON2s[3]
        BUTTON3s[1] = WINDOWHEIGHT - BUTTON3s[1] - BUTTON3s[3]
        BUTTON4s[1] = WINDOWHEIGHT - BUTTON4s[1] - BUTTON4s[3]
        BUTTON5s[1] = WINDOWHEIGHT - BUTTON5s[1] - BUTTON5s[3]
        BUTTON6s[1] = WINDOWHEIGHT - BUTTON6s[1] - BUTTON6s[3]
        BUTTON7s[1] = WINDOWHEIGHT - BUTTON7s[1] - BUTTON7s[3]
        BUTTON8s[1] = WINDOWHEIGHT - BUTTON8s[1] - BUTTON8s[3]
        BUTTON9s[1] = WINDOWHEIGHT - BUTTON9s[1] - BUTTON9s[3]
        BUTTON10s[1] = WINDOWHEIGHT - BUTTON10s[1] - BUTTON10s[3]
        BUTTON11s[1] = WINDOWHEIGHT - BUTTON11s[1] - BUTTON11s[3]
        BUTTON12s[1] = WINDOWHEIGHT - BUTTON12s[1] - BUTTON12s[3]
        BUTTON13s[1] = WINDOWHEIGHT - BUTTON13s[1] - BUTTON13s[3]
        BUTTON14s[1] = WINDOWHEIGHT - BUTTON14s[1] - BUTTON14s[3]
        BUTTON15s[1] = WINDOWHEIGHT - BUTTON15s[1] - BUTTON15s[3]
        BUTTON16s[1] = WINDOWHEIGHT - BUTTON16s[1] - BUTTON16s[3]
        BUTTON17s[1] = WINDOWHEIGHT - BUTTON17s[1] - BUTTON17s[3]
        BUTTON18s[1] = WINDOWHEIGHT - BUTTON18s[1] - BUTTON18s[3]
        BUTTON19s[1] = WINDOWHEIGHT - BUTTON19s[1] - BUTTON19s[3]
        BUTTON20s[1] = WINDOWHEIGHT - BUTTON20s[1] - BUTTON20s[3]
    wpath = os.path.join(main_dir, "gcode", "wgcode.txt" )
    gpath = os.path.join(main_dir, "gcode", "gcode.txt" )
    cpwg = 'cp '+ wpath + ' ' + gpath 
    os.system("rm -f ./gcode/wgcode.txt")   
    gline="G"
    showtextr(DISPLAYSURF, (30, 300), 0, gline, COLOR_OFF, ABLUE)
    while True:
        if screenNeedsRedraw:
            pygame.display.update()
            FPSCLOCK.tick(300)

        screenNeedsRedraw = False # by default, don't redraw the screen
        event = pygame.event.wait()
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYUP:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == MOUSEBUTTONUP:
            screenNeedsRedraw = True # screen should be redrawn
            mousex, mousey = event.pos # syntactic sugar

            # check for clicks on the difficulty buttons
            if pygame.Rect((BUTTON1s)).collidepoint(mousex, mousey):
                gline+=' X'                
                print 'GCODE X'
            elif pygame.Rect((BUTTON2s)).collidepoint(mousex, mousey):
                gline+=' I'                
                print 'GCODE I'
            elif pygame.Rect((BUTTON3s)).collidepoint(mousex, mousey):
                gline+='1'                
                print 'GCODE 1'
            elif pygame.Rect((BUTTON4s)).collidepoint(mousex, mousey):
                gline+='2'                
                print 'GCODE 2'
            elif pygame.Rect((BUTTON5s)).collidepoint(mousex, mousey):
                gline+='3'                
                print 'GCODE 3'
            elif pygame.Rect((BUTTON6s)).collidepoint(mousex, mousey):
                gline+='0'                
                print 'GCODE 0'
            elif pygame.Rect((BUTTON7s)).collidepoint(mousex, mousey):
                gline+=' Y'                
                print 'GCODE Y'
            elif pygame.Rect((BUTTON8s)).collidepoint(mousex, mousey):
                gline+=' J'                
                print 'GCODE J'
            elif pygame.Rect((BUTTON9s)).collidepoint(mousex, mousey):
                gline+='4'                
                print 'GCODE 4'
            elif pygame.Rect((BUTTON10s)).collidepoint(mousex, mousey):
                gline+='5'                
                print 'GCODE 5'
            elif pygame.Rect((BUTTON11s)).collidepoint(mousex, mousey):
                gline+='6'                
                print 'GCODE 6'
            elif pygame.Rect((BUTTON12s)).collidepoint(mousex, mousey):
                gline+='.'                
                print 'GCODE .'
            elif pygame.Rect((BUTTON13s)).collidepoint(mousex, mousey):
                gline+=' Z'                
                print 'GCODE Z'
            elif pygame.Rect((BUTTON14s)).collidepoint(mousex, mousey):
                gline+=' K'                
                print 'GCODE K'
            elif pygame.Rect((BUTTON15s)).collidepoint(mousex, mousey):
                gline+='7'                
                print 'GCODE 7'
            elif pygame.Rect((BUTTON16s)).collidepoint(mousex, mousey):
                gline+='8'                
                print 'GCODE 8'
            elif pygame.Rect((BUTTON17s)).collidepoint(mousex, mousey):
                gline+='9'                
                print 'GCODE 9'
            elif pygame.Rect((BUTTON18s)).collidepoint(mousex, mousey):
                gline+='-'                
                print 'GCODE -'
            elif pygame.Rect((BUTTON19s)).collidepoint(mousex, mousey):
                gline+='\n'
		wline(wpath, gline)
                gline="G" 
                filelines(30, 50, wpath, 0, 10, 45, 0)
                showtextr(DISPLAYSURF, (30, 300), 0, "                                                                                                    ", COLOR_OFF, ABLUE)
                print 'GCODE NEXT'
            elif pygame.Rect((BUTTON20s)).collidepoint(mousex, mousey):
		wline(wpath, "END")
                os.system(cpwg)
    		gdc_file = os.path.join(main_dir,'gdecode.exe' )
                os.system(gdc_file)
                dstx,dsty,dscale=getscale(590,540)
                get_stpz(dstx,dsty,dscale)

                print 'GCODE DONE'                    
                screenHome()
            showtextr(DISPLAYSURF, (30, 300), 0, gline, COLOR_OFF, ABLUE)
            pygame.display.update()

def screenSetsh(shape):
    #Screen for Setting each shape
    global difficulty, boxSize, boardWidth, boardHeight, maxLife, paletteColors, bgColor
    global dstx,dsty,dscale
    
    if shape == 'cir':
        image_file = os.path.join(main_dir, 'data', 'setcir.png')
        setting = getshset(os.path.join('gcode' ,'circle.set'))
        setrMx  = getshset(os.path.join('gcode' ,'circleMx.set'))
        setrMn  = getshset(os.path.join('gcode' ,'circleMn.set'))
        pos = [(230, 250)]
        rot = [0]
    elif shape == 'rec':
        image_file = os.path.join(main_dir, 'data', 'setrec.png')
        setting = getshset(os.path.join('gcode' ,'rect.set'))
        setrMx  = getshset(os.path.join('gcode' ,'rectMx.set'))
        setrMn  = getshset(os.path.join('gcode' ,'rectMn.set'))
        pos = [(240, 412), (50, 250)]
        rot = [0, 90]
    elif shape == 'sta':
        image_file = os.path.join(main_dir, 'data', 'setsta.png')
        setting = getshset(os.path.join('gcode' ,'star.set'))
        setrMx  = getshset(os.path.join('gcode' ,'starMx.set'))
        setrMn  = getshset(os.path.join('gcode' ,'starMn.set'))
        pos = [(50, 90), (265, 254),(190, 200)]
        rot = [0, 0, -45]        
    elif shape == 'rho':
        image_file = os.path.join(main_dir, 'data', 'setrho.png')
        setting = getshset(os.path.join('gcode' ,'rhom.set'))
        setrMx  = getshset(os.path.join('gcode' ,'rhomMx.set'))
        setrMn  = getshset(os.path.join('gcode' ,'rhomMn.set'))
        pos = [(225, 412), (255, 250)]
        rot = [0, 90]
    elif shape == 'tri':
        image_file = os.path.join(main_dir, 'data', 'settri.png')
        setting = getshset(os.path.join('gcode' ,'tri.set'))
        setrMx  = getshset(os.path.join('gcode' ,'triMx.set'))
        setrMn  = getshset(os.path.join('gcode' ,'triMn.set'))
        pos = [(230, 417), (266, 250), (180, 350) ]
        rot = [0, 90, 0]
    elif shape == 'pol':
        image_file = os.path.join(main_dir, 'data', 'setpol.png')        
        setting = getshset(os.path.join('gcode' ,'poly.set'))
        setrMx  = getshset(os.path.join('gcode' ,'polyMx.set'))
        setrMn  = getshset(os.path.join('gcode' ,'polyMn.set'))
        pos = [(50, 90), (165, 170)]
        rot = [0, -45] 
    SIMAGE = pygame.image.load(image_file)
    DISPLAYSURF.blit(SIMAGE, (0, 0))

    #1
    BUTTON1s = [515,46,92,74]
    #2
    BUTTON2s = [610,46,92,74]
    #3
    BUTTON3s = [704,46,92,74]
    #4
    BUTTON4s = [515,123,92,75]
    #5
    BUTTON5s = [610,123,92,75]
    #6
    BUTTON6s = [704,123,92,75]
    #7
    BUTTON7s = [515,201,92,74]
    #8
    BUTTON8s = [610,201,92,74]
    #9
    BUTTON9s = [704,201,92,74]
    #0
    BUTTON10s = [610,277,92,74]
    #.
    BUTTON11s = [704,277,92,74]
    #DEC
    BUTTON12s = [515,355,136,159]
    #INC
    BUTTON13s = [654,355,142,159]
    #PREVIOUS
    BUTTON14s = [7,518,254,77]
    #NEXT
    BUTTON15s = [267,518,243,77]
    #DONE
    BUTTON16s = [514,517,281,78]

    screenNeedsRedraw = True 
    
    if XINV == True:
        BUTTON1s[0] = WINDOWWIDTH - BUTTON1s[0] - BUTTON1s[2]
        BUTTON2s[0] = WINDOWWIDTH - BUTTON2s[0] - BUTTON2s[2]
        BUTTON3s[0] = WINDOWWIDTH - BUTTON3s[0] - BUTTON3s[2]
        BUTTON4s[0] = WINDOWWIDTH - BUTTON4s[0] - BUTTON4s[2]
        BUTTON5s[0] = WINDOWWIDTH - BUTTON5s[0] - BUTTON5s[2]
        BUTTON6s[0] = WINDOWWIDTH - BUTTON6s[0] - BUTTON6s[2]
        BUTTON7s[0] = WINDOWWIDTH - BUTTON7s[0] - BUTTON7s[2]
        BUTTON8s[0] = WINDOWWIDTH - BUTTON8s[0] - BUTTON8s[2]
        BUTTON9s[0] = WINDOWWIDTH - BUTTON9s[0] - BUTTON9s[2]
        BUTTON10s[0] = WINDOWWIDTH - BUTTON10s[0] - BUTTON10s[2]
        BUTTON11s[0] = WINDOWWIDTH - BUTTON11s[0] - BUTTON11s[2]
        BUTTON12s[0] = WINDOWWIDTH - BUTTON12s[0] - BUTTON12s[2]
        BUTTON13s[0] = WINDOWWIDTH - BUTTON13s[0] - BUTTON13s[2]
        BUTTON14s[0] = WINDOWWIDTH - BUTTON14s[0] - BUTTON14s[2]
        BUTTON15s[0] = WINDOWWIDTH - BUTTON15s[0] - BUTTON15s[2]
        BUTTON16s[0] = WINDOWWIDTH - BUTTON16s[0] - BUTTON16s[2]

    if YINV == True:
        BUTTON1s[1] = WINDOWHEIGHT - BUTTON1s[1] - BUTTON1s[3]
        BUTTON2s[1] = WINDOWHEIGHT - BUTTON2s[1] - BUTTON2s[3]
        BUTTON3s[1] = WINDOWHEIGHT - BUTTON3s[1] - BUTTON3s[3]
        BUTTON4s[1] = WINDOWHEIGHT - BUTTON4s[1] - BUTTON4s[3]
        BUTTON5s[1] = WINDOWHEIGHT - BUTTON5s[1] - BUTTON5s[3]
        BUTTON6s[1] = WINDOWHEIGHT - BUTTON6s[1] - BUTTON6s[3]
        BUTTON7s[1] = WINDOWHEIGHT - BUTTON7s[1] - BUTTON7s[3]
        BUTTON8s[1] = WINDOWHEIGHT - BUTTON8s[1] - BUTTON8s[3]
        BUTTON9s[1] = WINDOWHEIGHT - BUTTON9s[1] - BUTTON9s[3]
        BUTTON10s[1] = WINDOWHEIGHT - BUTTON10s[1] - BUTTON10s[3]
        BUTTON11s[1] = WINDOWHEIGHT - BUTTON11s[1] - BUTTON11s[3]
        BUTTON12s[1] = WINDOWHEIGHT - BUTTON12s[1] - BUTTON12s[3]
        BUTTON13s[1] = WINDOWHEIGHT - BUTTON13s[1] - BUTTON13s[3]
        BUTTON14s[1] = WINDOWHEIGHT - BUTTON14s[1] - BUTTON14s[3]
        BUTTON15s[1] = WINDOWHEIGHT - BUTTON15s[1] - BUTTON15s[3]
        BUTTON16s[1] = WINDOWHEIGHT - BUTTON16s[1] - BUTTON16s[3]
    loopb = True 

    count = int(setting[0])-1;
    setting[0:count] = setting[1:count]
    setrMx[0:count]  = setrMx[1:count]
    setrMn[0:count]  = setrMn[1:count]
    print count
    colbac=['NO','NO', 'NO', 'NO', 'NO', 'NO']
    selset = 0
    mode = 0
    setint=[0]*count
    for k in range(count): 
        showtextr(DISPLAYSURF, pos[k], rot[k], str(int(setting[k])), COLOR_OFF, colbac[k])
        setint[k]=int(setting[k])
    while loopb:
        if screenNeedsRedraw:
            pygame.display.update()
            FPSCLOCK.tick(300)

        screenNeedsRedraw = False # by default, don't redraw the screen
        event = pygame.event.wait()
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYUP:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == MOUSEBUTTONUP:
            screenNeedsRedraw = True # screen should be redrawn
            mousex, mousey = event.pos # syntactic sugar
            
            # check for clicks on the difficulty buttons
            if pygame.Rect((BUTTON1s)).collidepoint(mousex, mousey):
                showtextr(DISPLAYSURF, pos[selset], rot[selset], setting[selset], ABLUE, ABLUE)
                if(mode==0):
                    setting[selset]='1'
                    mode=1
                else:
                    setting[selset]=setting[selset]+'1'

                print 'SETSH 1'
            elif pygame.Rect((BUTTON2s)).collidepoint(mousex, mousey):
                showtextr(DISPLAYSURF, pos[selset], rot[selset], setting[selset], ABLUE, ABLUE)
                if(mode==0):
                    setting[selset]='2'
                    mode=1
                else:
                    setting[selset]=setting[selset]+'2'

                print 'SETSH 2'
            elif pygame.Rect((BUTTON3s)).collidepoint(mousex, mousey):
                showtextr(DISPLAYSURF, pos[selset], rot[selset], setting[selset], ABLUE, ABLUE)
                if(mode==0):
                    setting[selset]='3'
                    mode=1
                else:
                    setting[selset]=setting[selset]+'3'

                print 'SETSH 3'
            elif pygame.Rect((BUTTON4s)).collidepoint(mousex, mousey):
                showtextr(DISPLAYSURF, pos[selset], rot[selset], setting[selset], ABLUE, ABLUE)
                if(mode==0):
                    setting[selset]='4'
                    mode=1
                else:
                    setting[selset]=setting[selset]+'4'

                print 'SETSH 4'
            elif pygame.Rect((BUTTON5s)).collidepoint(mousex, mousey):
                showtextr(DISPLAYSURF, pos[selset], rot[selset], setting[selset], ABLUE, ABLUE)
                if(mode==0):
                    setting[selset]='5'
                    mode=1
                else:
                    setting[selset]=setting[selset]+'5'

                print 'SETSH 5'
            elif pygame.Rect((BUTTON6s)).collidepoint(mousex, mousey):
                showtextr(DISPLAYSURF, pos[selset], rot[selset], setting[selset], ABLUE, ABLUE)
                if(mode==0):
                    setting[selset]='6'
                    mode=1
                else:
                    setting[selset]=setting[selset]+'6'

                print 'SETSH 6'
            elif pygame.Rect((BUTTON7s)).collidepoint(mousex, mousey):
                showtextr(DISPLAYSURF, pos[selset], rot[selset], setting[selset], ABLUE, ABLUE)
                if(mode==0):
                    setting[selset]='7'
                    mode=1
                else:
                    setting[selset]=setting[selset]+'7'

                print 'SETSH 7'
            elif pygame.Rect((BUTTON8s)).collidepoint(mousex, mousey):
                showtextr(DISPLAYSURF, pos[selset], rot[selset], setting[selset], ABLUE, ABLUE)
                if(mode==0):
                    setting[selset]='8'
                    mode=1
                else:
                    setting[selset]=setting[selset]+'8'

                print 'SETSH 8'
            elif pygame.Rect((BUTTON9s)).collidepoint(mousex, mousey):
                showtextr(DISPLAYSURF, pos[selset], rot[selset], setting[selset], ABLUE, ABLUE)
                if(mode==0):
                    setting[selset]='9'
                    mode=1
                else:
                    setting[selset]=setting[selset]+'9'

                print 'SETSH 9'
            elif pygame.Rect((BUTTON10s)).collidepoint(mousex, mousey):
                showtextr(DISPLAYSURF, pos[selset], rot[selset], setting[selset], ABLUE, ABLUE)
                if(mode==0):
                    setting[selset]='0'
                    mode=1
                else:
                    setting[selset]=setting[selset]+'0'

                print 'SETSH 0'
            elif pygame.Rect((BUTTON11s)).collidepoint(mousex, mousey):
                showtextr(DISPLAYSURF, pos[selset], rot[selset], setting[selset], ABLUE, ABLUE)
                setting[selset]= str(-1*int(setting[selset]))
                print 'SETSH .'
            elif pygame.Rect((BUTTON12s)).collidepoint(mousex, mousey):
                showtextr(DISPLAYSURF, pos[selset], rot[selset], setting[selset], ABLUE, ABLUE)
                mode=0
                if(int(setting[selset])>int(setrMn[selset])):
                    setting[selset]=str(int(setting[selset])-1);
                colbac[selset]=ABLUE
                print 'SETSH DEC'
            elif pygame.Rect((BUTTON13s)).collidepoint(mousex, mousey):
                showtextr(DISPLAYSURF, pos[selset], rot[selset], setting[selset], ABLUE, ABLUE)
                mode=0
                if(int(setting[selset])<int(setrMx[selset])):
                    setting[selset]=str(int(setting[selset])+1);
                colbac[selset]=ABLUE
                print 'SETSH INC'
            elif pygame.Rect((BUTTON14s)).collidepoint(mousex, mousey):
                colbac[selset]='NO'
                mode=0
                if(selset==0):
                    selset=count
                selset-=1;
                colbac[selset]=ABLUE
                DISPLAYSURF.blit(SIMAGE, (0, 0))
                print 'SETSH PREVIOUS'
            elif pygame.Rect((BUTTON15s)).collidepoint(mousex, mousey):
                colbac[selset]='NO'
                mode=0
                if(selset==count-1):
                    selset=-1
                selset+=1;
                colbac[selset]=ABLUE
                DISPLAYSURF.blit(SIMAGE, (0, 0))
                print 'SETSH NEXT'
            elif pygame.Rect((BUTTON16s)).collidepoint(mousex, mousey):
                print 'SETSH OK'
                loopb = False
            if((int(setting[selset])<int(setrMn[selset])) and (mode == 0)):
                setting[selset]=setrMn[selset]
            if(int(setting[selset])>int(setrMx[selset])):
                setting[selset]=setrMx[selset]
                mode=0
            print setting[selset]
            for k in range(count): 
                showtextr(DISPLAYSURF, pos[k], rot[k], str(int(setting[k])), COLOR_OFF, colbac[k])
                setint[k]=int(setting[k])
            pygame.display.update()
    
    d_file = os.path.join(main_dir, 'gcode', 'gcode.txt')

    if shape == 'cir':
        s_file = os.path.join(main_dir, 'gcode', 'circle.txt')
        circle2g(setint)
    elif shape == 'rec':
        rectangle2g(setint)
        s_file = os.path.join(main_dir, 'gcode', 'rect.txt')
    elif shape == 'sta':
        star2g(setint)
        s_file = os.path.join(main_dir, 'gcode', 'star.txt')
    elif shape == 'rho':
        rhombus2g(setint)
        s_file = os.path.join(main_dir, 'gcode', 'rhom.txt')
    elif shape == 'tri':
        triangle2g(setint)
        s_file = os.path.join(main_dir, 'gcode', 'tri.txt')
    elif shape == 'pol':
        polygon2g(setint)
        s_file = os.path.join(main_dir, 'gcode', 'poly.txt')        
    #TODO cp <-> copy 
    comm = 'cp '+ s_file + ' ' + d_file
    
    os.system(comm)
    gdc_file = os.path.join(main_dir,'gdecode.exe' )
    os.system(gdc_file)
    dstx,dsty,dscale=getscale(590,540)
    get_stpz(dstx,dsty,dscale)
    screenHome()

def screenUsb():
    #USB screen to get design from USB
    #global difficulty, boxSize, boardWidth, boardHeight, maxLife, paletteColors, bgColor
    global dstx,dsty,dscale
    image_file = os.path.join(main_dir, 'data', 'usb.png')
    SIMAGE = pygame.image.load(image_file)
    DISPLAYSURF.blit(SIMAGE, (0, 0))


    BUTTON1 = (630,0,170,114)
    BUTTON1s = [630,0,170,114]

    BUTTON2 = (630,121,170,114)
    BUTTON2s = [630,121,170,114]

    BUTTON3 = (630,242,170,114)
    BUTTON3s = [630,242,170,114]

    BUTTON4 = (630,366,170,114)
    BUTTON4s = [630,366,170,114]

    BUTTON5 = (630,488,170,114)
    BUTTON5s = [630,488,170,114]

    screenNeedsRedraw = True 
    
    if XINV == True:
        BUTTON1s[0] = WINDOWWIDTH - BUTTON1s[0] - BUTTON1s[2]
        BUTTON2s[0] = WINDOWWIDTH - BUTTON2s[0] - BUTTON2s[2]
        BUTTON3s[0] = WINDOWWIDTH - BUTTON3s[0] - BUTTON3s[2]
        BUTTON4s[0] = WINDOWWIDTH - BUTTON4s[0] - BUTTON4s[2]
        BUTTON5s[0] = WINDOWWIDTH - BUTTON5s[0] - BUTTON5s[2]
    if YINV == True:
        BUTTON1s[1] = WINDOWHEIGHT - BUTTON1s[1] - BUTTON1s[3]
        BUTTON2s[1] = WINDOWHEIGHT - BUTTON2s[1] - BUTTON2s[3]
        BUTTON3s[1] = WINDOWHEIGHT - BUTTON3s[1] - BUTTON3s[3]
        BUTTON4s[1] = WINDOWHEIGHT - BUTTON4s[1] - BUTTON4s[3]
        BUTTON5s[1] = WINDOWHEIGHT - BUTTON5s[1] - BUTTON5s[3]
    
    os.system('sudo sh ./mountusb.sh') 
    p_app=filelines(30, 40, "usbdata.txt", 0, 20, 45, 1)
    line_sel=1
    line_off=0
    path_usb_file=os.path.join('/media','usbstick')
    
    while True:
        if screenNeedsRedraw:
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON1,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON2,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON3,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON4,2)
            pygame.draw.rect(DISPLAYSURF,COLOR_OFF,BUTTON5,2)
            pygame.display.update()
            FPSCLOCK.tick(300)

        screenNeedsRedraw = False # by default, don't redraw the screen
        event = pygame.event.wait()
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYUP:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == MOUSEBUTTONUP:
            screenNeedsRedraw = True # screen should be redrawn
            mousex, mousey = event.pos # syntactic sugar

            # check for clicks on the difficulty buttons
            if pygame.Rect((BUTTON1s)).collidepoint(mousex, mousey):
                if(line_sel>=1):
                    line_sel-=1			
		if(line_sel==0):
                    line_sel=20
                    line_off-=20 			

    		DISPLAYSURF.blit(SIMAGE, (0, 0))
                p_app=filelines(30, 40, "usbdata.txt", line_off, 20, 45, line_sel)
                print 'USB UP'
            elif pygame.Rect((BUTTON2s)).collidepoint(mousex, mousey):
    		path_usb_file=os.path.join(path_usb_file,'..')
                os.environ['usbfp']=path_usb_file
                os.system('echo $usbfp')
                os.system('sudo sh ./file_in_dir.sh $usbfp')
    		DISPLAYSURF.blit(SIMAGE, (0, 0))
                line_off=0
                line_sel=1
                p_app=filelines(30, 40, "usbdata.txt", line_off, 20, 45, line_sel)
                print 'USB BACK'
            elif pygame.Rect((BUTTON3s)).collidepoint(mousex, mousey):
    		path_usb_file=os.path.join(path_usb_file,p_app)
                os.environ['usbfp']=path_usb_file
                os.system('echo $usbfp')
                os.system('sudo sh ./file_in_dir.sh $usbfp')
                
                DISPLAYSURF.blit(SIMAGE, (0, 0))
                line_off=0
                line_sel=1 
                p_app=filelines(30, 40, "usbdata.txt", line_off, 20, 45, line_sel)
                print 'USB ENTER'
            elif pygame.Rect((BUTTON4s)).collidepoint(mousex, mousey):
                if(line_sel<=20):
                    line_sel+=1
		if(line_sel==21):
                    line_sel=1
                    line_off+=20 			
    		DISPLAYSURF.blit(SIMAGE, (0, 0))
                p_app=filelines(30, 40, "usbdata.txt", line_off, 20, 45, line_sel)
                print 'USB DOWN'
            elif pygame.Rect((BUTTON5s)).collidepoint(mousex, mousey):
                print 'USB CANCEL'
    		gdc_file = os.path.join(main_dir,'gdecode.exe' )
                os.system(gdc_file)
                dstx,dsty,dscale=getscale(590,540)
                get_stpz(dstx,dsty,dscale)

                print str(dstx)+", "+str(dsty)+", "+str(dscale)
                gdraw2(dstx,dsty,dscale,WHITE)
                screenHome()
            pygame.display.update()

def checkForQuit():
    # Terminates the program if there are any QUIT or escape key events.
    for event in pygame.event.get(QUIT): # get all the QUIT events
        pygame.quit() # terminate if any QUIT events are present
        sys.exit()
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            pygame.quit() # terminate if the KEYUP event was for the Esc key
            sys.exit()
        pygame.event.post(event) # put the other KEYUP event objects bac

        pygame.quit()	

if __name__ == '__main__':
   main()	
