# !/usr/bin/env python
# -*- coding: utf-8 -*-

#----------------------------------------------
#   ScriptName  : CameraWindowGenerator
#   Author      : Atsushi Hirata
#   Since       : 2022/10
#   Update      : 2022/10/25 : 細かい修正を行いました。
#                 2022/11/04 : ビューモード、シェーダーモードの変更機能を追加しました。
#                 2022/11/08 : バグの修正を行いました。
#----------------------------------------------


from asyncio.windows_events import NULL
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
window_width = 230              #ウインドウサイズ
window_height = 450
button_height = 90              #ボタンサイズ
textbox_width = window_width/5  #テキストボックスの幅
btnLayout = None                #ボタンのレイアウト
winNameStrings = 'presp'        #ウィンドウ名
excludeFlag = False             #初期カメラの除去フラグ
maxWindow = 3                   #最大ウインドウ数
ViewModeFlag = 'points'         #ビューモードの指定フラグ


#カメラノードを検出
def CWG_detecCam(self):
    global camList
    global camNameList
    global ViewModeFlag
    camList = cmds.ls(ca=True)
    camNameList = cmds.listCameras()
    if camList is None:
        print("detection error : No Cameras")
        return
    return(camNameList)


#デフォルトのカメラを除外
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
    
    if ViewModeFlag == 'wireframe':
        cmds.modelEditor(editor, edit=True, displayAppearance='wireframe')
    elif ViewModeFlag == 'points':
        cmds.modelEditor(editor, edit=True, displayAppearance='points')
    elif ViewModeFlag == 'boundingBox':
        cmds.modelEditor(editor, edit=True, displayAppearance='boundingBox')
    elif ViewModeFlag == 'flatShaded':
        cmds.modelEditor(editor, edit=True, displayAppearance='flatShaded')
    else:
        print("viewModeFlag error!")
        return()

    cmds.showWindow(camWindowName)


#ウインドウを開く(全て)
def CWG_AllOpen(self):
    global maxWindow
    maxWindow = cmds.textField('maxWin', q=True, text=True)
    winCount = (int(maxWindow))
    camList = CWG_detecCam(self)
    if excludeFlag == True:
        camList = CWG_excludeDefCam(self, camList)
    elif excludeFlag == False:
        pass

    if camList == NULL:
        print("=>Detection Error : No camera!")
        return(self)

    print("=>open All Winow!")
    for camName in camList:
        winCount = winCount -1
        if winCount >= 0:
            print(camName + " is Opened!")
            CWG_openWindow(self, camName)

        
#ウインドウを開く(単体)
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
    global maxWindow
    global ViewModeFlag
    #既にGUIが存在する時に古いほうを消す処理
    if cmds.window(windowName, ex=1):
        cmds.deleteUI(windowName)
    cmds.window(windowName, title=windowName, rtf=True, h=window_height, w=window_width)

    #GUIを作成
    with LayoutManager(cmds.formLayout()) as form:
        with LayoutManager(cmds.columnLayout()):
            cmds.scrollLayout(cr=True, w=window_width, h=window_height-button_height)
            btnLayout  = cmds.columnLayout(adj=True, rowSpacing=3)

    with LayoutManager(cmds.columnLayout(adjustableColumn=True, rowSpacing=10)):
        with LayoutManager(cmds.frameLayout( label='ViewMode' )):
            with LayoutManager(cmds.columnLayout( w=window_width)):
                rbc = cmds.radioCollection()
                rb1 = cmds.radioButton( label='wireframe', onc="ViewModeFlag = 'wireframe' ")
                rb2 = cmds.radioButton( label='points', onc="ViewModeFlag = 'points' ")
                rb3 = cmds.radioButton( label='boundingBox',onc="ViewModeFlag = 'boundingBox' ")
                rb4 = cmds.radioButton( label='flatShaded',onc="ViewModeFlag = 'flatShaded' ")
    cmds.radioCollection( rbc, edit=True, select=rb1 )

    with LayoutManager(cmds.columnLayout(adjustableColumn=True, rowSpacing=10)):
        with LayoutManager(cmds.frameLayout( label='Option' )):
            with LayoutManager(cmds.rowColumnLayout( numberOfColumns=2, columnAttach=(1, 'right', 10), columnWidth=[(1, window_width - 30), (2, 20)] )):
                cmds.text("Exclude default camera")
                cmds.checkBox( label='', ed= True, onc="excludeFlag = True", ofc="excludeFlag = False")
            
            with LayoutManager(cmds.rowColumnLayout( numberOfColumns=2, columnAttach=(1, 'right', 10), columnWidth=[(1, window_width - textbox_width), (2, textbox_width)] )):
                cmds.text("Max Window")
                cmds.textField('maxWin', tx="4", ed=True)

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