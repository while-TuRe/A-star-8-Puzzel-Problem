import time
import copy
import os
import glob
import cv2
import numpy as np

from tkinter import *
root = Tk()

num_path = "images2/"
num_images = []
open_list = []
close_list = []#存储board G已确定
target_state = [[1,2,3,],
            [8,0,4],
            [6,5,7]]
is_auto = 1
def PrintState(state):
    for i in range(len(state)):
        print(state[i])
    print()
def DrawState(state,merge_img):
    small_h, small_w = num_images[0].shape[:2]
    for i in range(3):
        for j in range(3):
            merge_img[i*small_h:(i+1)*small_h,j*small_w:(j+1)*small_w] = num_images[state[i][j]]
    cv2.imshow("merge", merge_img)
    

def Draw(current_board):
    #找到所需绘制的游戏路径
    best_path = []
    while(current_board):
        best_path.append(current_board.state)
        current_board = current_board.parent
    best_path.reverse()
    print("检索得最短路径%d步" % len(best_path))
    # for state in best_path:
    #     PrintState(state)
    #提取出9张图片数字
    for i in range(0,9):
        img = cv2.imread(os.path.join(num_path,str(i)+'.png'))
        num_images.append(img)
    #print(num_images[0].shape,img.dtype,num_images[0].dtype)
    merge_shape = [num_images[0].shape[0]*3+10,num_images[0].shape[1]*3+10]
    for i in range(2, len(num_images[0].shape)):
        merge_shape.append(num_images[0].shape[i])
    merge_img = np.zeros(tuple(merge_shape),num_images[0].dtype)
    #merge_img = np.zeros(tuple(shape), images[0].dtype)
    #print(merge_img.shape)
    cv2.namedWindow("merge")
    
    for state in best_path:
        DrawState(state,merge_img)
        ret = cv2.waitKey(100*is_auto)
        if(ret == -1 and not is_auto):
            break


class Board:
    parent = []
    state = []
    G = 0
    H = 0
    def GetNumPos(self,num):
        for i in range(len(self.state)):
            for j in range(len(self.state)):
                if self.state[i][j] == num:
                    return i,j

    def __init__(self , current_state , prt = []):
        if(prt):
            self.SetParent(prt)
        self.state = current_state
        for i in range (len(current_state)):
            for j in range (len(current_state[i])):
                x,y = self.GetNumPos(target_state[i][j])
                self.H = self.H + abs(x - i) + abs(y - j)
    
    def SetParent(self,prt):
        self.parent = prt
        self.G = prt.G + 1
    def GetPosExchange(self,x0,y0,x1,y1):
        new_state = copy.deepcopy(self.state)
        tmp = new_state[x0][y0]
        new_state[x0][y0] = new_state[x1][y1]
        new_state[x1][y1] = tmp
        return new_state

    def __eq__(self,state):
        if self and state:
            return self.state == state
    def GetF(self):
        return self.G+10*self.H

def GetStInList(alist,state):
    for i in range(len(alist)):
        if alist[i].state == state:
            return i
    return -1

def DealPuzzle(start_state):
    open_list.append(Board(start_state))
    loop=0
    while(open_list != []):
        loop=loop+1
        current_board = open_list[0]
        #print(loop)
        #DrawState(current_board.state)
        open_list.remove(current_board)
        close_list.append(current_board)
        if(current_board == target_state):
            print("成功找到解")
            print("检索%d轮" % loop,end=",")
            Draw(current_board)
            return
        #add new reachable board into open_list
        
        x0,y0 = current_board.GetNumPos(0)
        for [x1,y1] in [[x0-1,y0],[x0+1,y0],[x0,y0-1],[x0,y0+1]]: 
            if x1>=0 and x1<len(start_state) and y1>=0 and y1<len(start_state[x1]):
                new_state = current_board.GetPosExchange(x0, y0, x1, y1)
                if GetStInList(close_list, new_state) == -1:#close中没有，bd未确定
                    pos = GetStInList(open_list, new_state)
                    if  pos== -1:#新探索到的点
                        open_list.append(Board(new_state,prt=current_board))
                    if current_board.G + 1 < open_list[pos].G:#需更新的点
                        open_list[pos].SetParent(current_board)       
        # for i in range(len(open_list)):
        #     print("open_list")
        #     DrawState(open_list[i].state)
        open_list.sort(key=lambda elem : elem.GetF())

#判断目标是否可达
def IsRevND(state):
    sum = 0
    for i in range(0, len(state), 1):
        for j in range(0, len(state[i]), 1):
            for ii in range(0, i, 1):
                for jj in range(0, len(state[i]), 1):
                    if state[ii][jj] != 0 and state[i][j] != 0 and state[ii][jj] < state[i][j]:
                        sum += 1
            for jj in range(0, j, 1):
                if state[i][jj] != 0 and state[i][j] != 0 and state[i][jj] < state[i][j]:
                    sum += 1
    if sum % 2 == 0:
        return True
    else:
        return False

def selection():  
   global is_auto 
   is_auto = radio.get() 

def buttonclick():
   root.destroy()


if __name__ == "__main__":
    start_state =[[2,8,3],
                [1,6,4],
                [7,0,5]]
    #DrawState(start_state)
    # Draw(Board(start_state))
    # time.sleep(100)
    #判断是否可达
    if(IsRevND(target_state) != IsRevND(start_state)):
        print("目标不可达！")
        exit(1)
    else:
        print('目标可达，开始求解')
    #输入弹窗
    root.title("input")
    root.geometry('300x300')#是x 不是*
    TypeAhead = Label(root, text="您希望自动演示还是手动演示？",
        font=("Arial", 12))
    TypeAhead.pack(side=TOP)  #这里的side可以赋值为LEFT  RTGHT TOP  BOTTOM
    #添加单选框
    radio = IntVar()
    radio.set(is_auto)  
    rad1 = Radiobutton(root, variable=radio,text="自动演示",value=1,command=selection)
    rad2 = Radiobutton(root, variable=radio,text="手动演示",value=0,command=selection)
    rad1.pack()
    rad2.pack()
    #确认键
    button = Button(root, text ="确认", command = buttonclick)
    button.pack()
    root.mainloop()
    #is_auto = int(input("您希望自动演示还是手动演示（按任意键后移动）？自动演示请输入1，手动演示请输入0:"))
    #print(is_auto)
    DealPuzzle(start_state)
    
    cv2.destroyWindow("merge")