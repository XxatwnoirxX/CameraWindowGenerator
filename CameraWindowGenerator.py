# !/usr/bin/env python
# -*- coding: utf-8 -*-

#----------------------------------------------
#   ScriptName  : CameraWindowGenerator
#   Author      : Atsushi Hirata
#   Since       : 2022/10
#   Update      : 2022/10/25 : 細かい修正を行いました。
#                 2022/11/04 : ビューモード、シェーダーモードの変更機能を追加しました。
#                 2022/11/09 : バグの修正、一部変数名の変更を行いました。
#----------------------------------------------


from asyncio.windows_events import NULL
from cProfile import label
import maya.cmds as cmds
from maya.common.ui import LayoutManager
import os,functools


#各定数、変数の定義
CWG_WINDOW_NAME = 'CamWinGenerator'         #UIの名前
CWG_CAM_WINDOW_WIDTH = 600                  #カメラウインドウサイズ
CWG_CAM_WINDOW_HEIGHT = 500
CWG_GUI_WINDOW_WIDTH = 230                  #GUIウインドウサイズ
CWG_GUI_WINDOW_HEIGHT = 450
CWG_BUTTON_HEIGHT = 90                      #ボタンサイズ
CWG_TEXTBOX_WIDTH = CWG_GUI_WINDOW_WIDTH/5  #テキストボックスの幅

cwg_cam_list = []                           #カメラのリスト
cwg_cam_name_list = []                      #カメラ名のリスト
cwg_cam_btn_list = []                       #ボタン用リスト
cwg_btn_layout = None                       #ボタンのレイアウト
cwg_window_name_strings = 'presp'           #オープンするウィンドウ名
cwg_exclude_flag = False                    #初期カメラの除去フラグ
cwg_max_window = 3                          #最大ウインドウ数
cwg_view_mode_flag = 'points'               #ビューモードの指定フラグ


#カメラノードを検出
def cwg_detec_cam(self):
    global cwg_cam_list
    global cwg_cam_name_list
    global cwg_view_mode_flag
    cwg_cam_list = cmds.ls(ca=True)
    cwg_cam_name_list = cmds.listCameras()
    if cwg_cam_list is None:
        print("detection error : No Cameras")
        return
    return(cwg_cam_name_list)


#デフォルトのカメラを除外
def cwg_exclude_default_cam(self, cwg_cam_list):
    cwg_cam_list.remove('top')
    cwg_cam_list.remove('side')
    cwg_cam_list.remove('front')
    cwg_cam_list.remove('persp')
    return(cwg_cam_list)


#ウインドウを開く処理
def cwg_open_window(self, camName):
    camWindowName = camName

    #既にGUIが存在する時に古いほうを消す処理
    if cmds.window(camWindowName, ex=1):
        cmds.deleteUI(camWindowName)
    
    #新しいウインドウを開く
    cmds.window(camWindowName, title=camWindowName, w=CWG_CAM_WINDOW_WIDTH, h=CWG_CAM_WINDOW_HEIGHT, rtf=True)
    cmds.paneLayout()
    editor = cmds.modelEditor()
    cmds.modelPanel()
    cmds.modelEditor(editor, edit=True, camera=camName )
    
    if cwg_view_mode_flag == 'wireframe':
        cmds.modelEditor(editor, edit=True, displayAppearance='wireframe')
    elif cwg_view_mode_flag == 'points':
        cmds.modelEditor(editor, edit=True, displayAppearance='points')
    elif cwg_view_mode_flag == 'boundingBox':
        cmds.modelEditor(editor, edit=True, displayAppearance='boundingBox')
    elif cwg_view_mode_flag == 'flatShaded':
        cmds.modelEditor(editor, edit=True, displayAppearance='flatShaded')
    else:
        print("View mode flag error!")
        return()

    cmds.showWindow(camWindowName)


#ウインドウを開く(全て)
def cwg_all_camwin_open(self):
    global cwg_max_window
    cwg_max_window = cmds.textField('maxWin', q=True, text=True)
    winCount = (int(cwg_max_window))
    cwg_cam_list = cwg_detec_cam(self)
    if cwg_exclude_flag == True:
        cwg_cam_list = cwg_exclude_default_cam(self, cwg_cam_list)
    elif cwg_exclude_flag == False:
        pass

    if cwg_cam_list == NULL:
        print("=>Detection Error : No camera!")
        return(self)

    print("=>Open all winow!")
    for camName in cwg_cam_list:
        winCount = winCount -1
        if winCount >= 0:
            print(camName + " is opened!")
            cwg_open_window(self, camName)

        
#ウインドウを開く(単体)
def cwg_camwin_open(self, cwg_cam_name_list, *args,**kwargs):
    print("=>Open " + cwg_cam_name_list + " winow!")
    cwg_cam_list = cwg_detec_cam(self)
    for camName in cwg_cam_list:
        if(camName == cwg_cam_name_list):
            cwg_open_window(self, camName)
        else:
            pass


#GUIボタンの追加
def cwg_add_btn(self, cwg_btn_layout, cwg_cam_list):
    for winName in cwg_cam_list:
        global cwg_window_name_strings
        cwg_window_name_strings = ''.join(winName)
        cwg_cam_btn_list.append(cmds.button(l=winName, c=functools.partial(cwg_camwin_open , "self", cwg_window_name_strings), p=cwg_btn_layout))


#GUIの表示処理
def cwg_gui():
    global cwg_max_window
    global cwg_view_mode_flag
    #既にGUIが存在する時に古いほうを消す処理
    if cmds.window(CWG_WINDOW_NAME, ex=1):
        cmds.deleteUI(CWG_WINDOW_NAME)
    cmds.window(CWG_WINDOW_NAME, title=CWG_WINDOW_NAME, rtf=True, h=CWG_GUI_WINDOW_HEIGHT, w=CWG_GUI_WINDOW_WIDTH)

    #GUIを作成
    with LayoutManager(cmds.formLayout()) as form:
        with LayoutManager(cmds.columnLayout()):
            cmds.scrollLayout(cr=True, w=CWG_GUI_WINDOW_WIDTH, h=CWG_GUI_WINDOW_HEIGHT-CWG_BUTTON_HEIGHT)
            cwg_btn_layout  = cmds.columnLayout(adj=True, rowSpacing=3)

    with LayoutManager(cmds.columnLayout(adjustableColumn=True, rowSpacing=10)):
        with LayoutManager(cmds.frameLayout( label='ViewMode' )):
            with LayoutManager(cmds.columnLayout( w=CWG_GUI_WINDOW_WIDTH)):
                rbc = cmds.radioCollection()
                rb1 = cmds.radioButton( label='wireframe', onc="cwg_view_mode_flag = 'wireframe' ")
                rb2 = cmds.radioButton( label='points', onc="cwg_view_mode_flag = 'points' ")
                rb3 = cmds.radioButton( label='boundingBox',onc="cwg_view_mode_flag = 'boundingBox' ")
                rb4 = cmds.radioButton( label='flatShaded',onc="cwg_view_mode_flag = 'flatShaded' ")
    cmds.radioCollection( rbc, edit=True, select=rb1 )

    with LayoutManager(cmds.columnLayout(adjustableColumn=True, rowSpacing=10)):
        with LayoutManager(cmds.frameLayout( label='Option' )):
            with LayoutManager(cmds.rowColumnLayout( numberOfColumns=2, columnAttach=(1, 'right', 10), columnWidth=[(1, CWG_GUI_WINDOW_WIDTH - 30), (2, 20)] )):
                cmds.text("Exclude default camera")
                cmds.checkBox( label='', ed= True, onc="cwg_exclude_flag = True", ofc="cwg_exclude_flag = False")
            
            with LayoutManager(cmds.rowColumnLayout( numberOfColumns=2, columnAttach=(1, 'right', 10), columnWidth=[(1, CWG_GUI_WINDOW_WIDTH - CWG_TEXTBOX_WIDTH), (2, CWG_TEXTBOX_WIDTH)] )):
                cmds.text("Max Window")
                cmds.textField('maxWin', tx="4", ed=True)

    cmds.button(l="AllCamOpen", w=CWG_GUI_WINDOW_WIDTH, h= 35, c=cwg_all_camwin_open, bgc=(0.5,0.5,1))   
    cmds.formLayout(form, edit=1)

    #GUIを表示
    cmds.showWindow(CWG_WINDOW_NAME)
    return(cwg_btn_layout)


def cwg_camera_window_generator():
    cwg_btn_layout = cwg_gui()
    cwg_cam_name_list = cwg_detec_cam("self")
    #検知したカメラをヒストリに表示
    print("=>Detection Camera")
    print("     CamList : " + str(cwg_cam_list))
    print("     CamNameList : " + str(cwg_cam_name_list))
    cwg_add_btn("self", cwg_btn_layout, cwg_cam_name_list)


if __name__ == '__main__':  
    cwg_camera_window_generator()