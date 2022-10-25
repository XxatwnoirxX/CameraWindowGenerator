# !/usr/bin/env python
# -*- coding: utf-8 -*-

#----------------------------------------------
#   ScriptName  : CameraWindowGenerator
#   Author      : Atsushi Hirata
#   Since       : 2022/10
#   Update      : None
#----------------------------------------------


from cProfile import label
import maya.cmds as cmds
from maya.common.ui import LayoutManager
import os,functools


#各変数の定義
windowName = 'CamWinGenerator'  #UIの名前
camWindow_width = 600           #カメラウインドウサイズ
camWindow_height = 500
camWindowName = 'camWindowName' #カメラウインドウの名前
camName = 'camName'             #カメラの名前
camList = []                    #カメラのリスト
camNameList = []                #カメラ名のリスト
cambtnList = []                 #ボタン用リスト
window_width = 230              #GUIのウインドウサイズ
window_height = 370
button_height = 90                  #ボタンサイズ
textbox_width = window_width / 5    #テキストボックスの幅
btnLayout = None                    #ボタンのレイアウト
winNameStrings = 'presp'
maxWin = 3                          #最大ウインドウ数
excludeFlag = False


#カメラノードを検出
def CWG_detecCam(self):
    global camList
    global camNameList
    camList = cmds.ls(ca=True)
    camNameList = cmds.listCameras()
    if camList is None:
        print("detection error : No Cameras")
        return
    return(camNameList)


def CWG_excludeDefCam(self, camList):
    camList.remove('top')
    camList.remove('side')
    camList.remove('front')
    camList.remove('persp')
    return(camList)


#ウインドウを開く処理
def CWG_openWindow(self, camName):
    camWindowName = camName
    #既にGUIが存在する時に古いほうを消す処理
    if cmds.window(camWindowName, ex=1):
        cmds.deleteUI(camWindowName)
    #新しいウインドウを開く
    cmds.window(camWindowName, title=camWindowName, w=camWindow_width, h=camWindow_height, rtf=True)
    cmds.paneLayout()
    editor = cmds.modelEditor()
    cmds.modelPanel()
    cmds.modelEditor(editor, edit=True, camera=camName )
    cmds.showWindow(camWindowName)


#ウインドウを開く(全て)
def CWG_AllOpen(self):
    print("=>open All Winow!")
    camList = CWG_detecCam(self)
    if excludeFlag == True:
        camList = CWG_excludeDefCam(self, camList)
    elif excludeFlag == False:
        pass
    for camName in camList:
        print(camName + " is Opened!")
        CWG_openWindow(self, camName)

        
#ウインドウを開く(一つ)
def CWG_Open(self, camNameList, *args,**kwargs):
    print("=>open " + camNameList + " Winow!")
    camList = CWG_detecCam(self)
    for camName in camList:
        if(camName == camNameList):
            CWG_openWindow(self, camName)
        else:
            pass


#GUIボタンの追加
def CWG_addBtn(self, btnLayout, camList):
    for winName in camList:
        global winNameStrings
        winNameStrings = ''.join(winName)
        cambtnList.append(cmds.button(l=winName, c=functools.partial(CWG_Open , "self", winNameStrings), p=btnLayout))
    

#GUIの表示処理
def CWG_gui():
    #既にGUIが存在する時に古いほうを消す処理
    if cmds.window(windowName, ex=1):
        cmds.deleteUI(windowName)
    cmds.window(windowName, title=windowName, rtf=True, h=window_height, w=window_width)
    #GUIを作成
    with LayoutManager(cmds.formLayout()) as form:
        with LayoutManager(cmds.columnLayout()):
            cmds.scrollLayout(cr=True, w=window_width, h=window_height-button_height)
            btnLayout  = cmds.columnLayout(adj=True, rowSpacing=3, w=window_width,h=window_height-button_height)
    with LayoutManager(cmds.rowColumnLayout( numberOfColumns=2, columnAttach=(1, 'right', 10), columnWidth=[(1, window_width - 30), (2, 20)] )):
        cmds.text("Exclude default camera")
        cmds.checkBox( label='', ed= True, onc="excludeFlag = True", ofc="excludeFlag = False")

    with LayoutManager(cmds.rowColumnLayout( numberOfColumns=2, columnAttach=(1, 'right', 10), columnWidth=[(1, window_width - textbox_width), (2, textbox_width)] )):
        cmds.text("Max Window")
        cmds.textField(tx="3", cc="maxWin = 3")

    cmds.button(l="AllCamOpen", w=window_width, h= 35, c=CWG_AllOpen, bgc=(0.5,0.5,1))   
    cmds.formLayout(form, edit=1)
    #GUIを表示
    cmds.showWindow(windowName)
    return(btnLayout)


def CameraWindowGenerator():
    btnLayout = CWG_gui()
    camNameList = CWG_detecCam("self")
    #検知したカメラをヒストリに表示
    print("=>Detection Camera")
    print("     CamList : " + str(camList))
    print("     CamNameList : " + str(camNameList))
    CWG_addBtn("self", btnLayout, camNameList)


if __name__ == '__main__':  
    CameraWindowGenerator()