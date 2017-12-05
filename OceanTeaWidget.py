#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
from maya import cmds
import pymel.core as pm
from maya import OpenMayaUI
import random
import imp
try:
    imp.find_module('PySide2')
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except ImportError:
    from PySide.QtGui import *
    from PySide.QtCore import *
try:
    import shiboken
except:
    import shiboken2 as shiboken

from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
ptr = OpenMayaUI.MQtUtil.mainWindow()

#おしゃれミキシンを定義
class OceanTeaBaseMixin(MayaQWidgetBaseMixin, QMainWindow):
    round_a=10
    round_b=10
    col_l = [64]*3
    col_c = [64]*3
    col_r = [64]*3
    at_l = 0.0
    at_c = 0.5
    at_r = 1.0
    def __init__(self, *args, **kwargs):
        super(OceanTeaBaseMixin, self).__init__(*args, **kwargs)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.installEventFilter(self)
        
    def eventFilter(self, obj, event):
        set_cursor_icon(self, event)
        
    def mouseReleaseEvent(self, pos):
        mouse_released(self, pos)
        
    def mousePressEvent(self, pos):
        mouse_pressed(self, pos)
        
    def mouseMoveEvent(self, pos):
        mouse_moved(self, pos, self.round_a, self.round_b)
        self.call_palette()
                        
    def showEvent(self, e):
        self.call_palette()
        
    def opacity(self, opacity=1.0):
        self.setWindowOpacity(opacity)
        
    def gradient(self, col_l=62, col_c=62, col_r=62, at_l=0.0, at_c=0.5, at_r=1.0):
        self.col_l = col_l
        self.col_c = col_c
        self.col_r = col_r
        self.at_l = at_l
        self.at_c = at_c
        self.at_r = at_r
        
    def round_rect(self, a, b):
        self.round_a = a
        self.round_b = b
        
    def call_palette(self):
        paletteUI(self, round_a=self.round_a,  round_b=self.round_b,
                        col_l=self.col_l, col_c=self.col_c, col_r=self.col_r, at_l=self.at_l, 
                        at_c=self.at_c, at_r=self.at_r)
        
#他のクラスでも使えるようにグローバル関数でUI処理する
def paletteUI(widget=None, round_a=10, round_b=10, col_l=62, col_c=62, col_r=62, at_l=0.0, at_c=0.5, at_r=1.0):
    col_l = to_3_list(col_l)
    left = convert_2_hex(col_l)
    col_c = to_3_list(col_c)
    center = convert_2_hex(col_c)
    col_r = to_3_list(col_r)
    right = convert_2_hex(col_r)
    
    Palette = QPalette()
    gradient = QLinearGradient(QRectF(
            widget.rect()).topLeft(),
            QRectF(widget.rect()).topRight()
        )
    gradient.setColorAt(at_l, left)
    gradient.setColorAt(at_c, center)
    gradient.setColorAt(at_r, right)
    Palette.setBrush(QPalette.Background, QBrush(gradient))
        
    widget.setPalette(Palette)
    path = QPainterPath()
    path.addRoundedRect(widget.rect(), round_a, round_b)
    region = QRegion(path.toFillPolygon().toPolygon())
    widget.setMask(region)
    
def mouse_released(widget, pos):
    widget.mc_x = pos.x()
    widget.mc_y = pos.y()

def mouse_pressed(widget, pos, set_value=True):
    hit_size = 10
    pre_size_x = widget.size().width()
    pre_size_y = widget.size().height()
    mc_x = pos.x()
    mc_y = pos.y()
    size_x = widget.size().width()
    size_y = widget.size().height()
    sub_x = size_x-mc_x
    sub_y = size_y-mc_y
    resize_mode = None
    if mc_x < hit_size:
        resize_mode = 'left'
    if mc_y < hit_size:
        resize_mode = 'top'
    if sub_y < hit_size:
        resize_mode = 'bottom'
    if sub_x < hit_size:
        resize_mode = 'right'
    if mc_x < hit_size and mc_y < hit_size:
        resize_mode = 'top_left'
    if sub_x < hit_size and sub_y < hit_size:
        resize_mode = 'bottom_right'
    if sub_x < hit_size and mc_y < hit_size:
        resize_mode = 'top_right'
    if mc_x < hit_size and sub_y < hit_size:
        resize_mode = 'bottom_left'
    if set_value:
        widget.pre_size_x = pre_size_x
        widget.pre_size_y = pre_size_y
        widget.mc_x = mc_x
        widget.mc_y = mc_y 
        widget.size_x = size_x
        widget.size_y = size_y
        widget.sub_x = sub_x
        widget.sub_y = sub_y
        widget.resize_mode = resize_mode
    return resize_mode

def mouse_moved(widget, pos, a=10, b=10):
    winX = pos.globalX() - widget.mc_x
    winY = pos.globalY() - widget.mc_y
    if widget.resize_mode is None:
        widget.move(winX, winY)
    else:
        w_x = widget.size().width()
        w_y = widget.size().height()
        if 'right' in widget.resize_mode:
            w_x = pos.x() + widget.sub_x
            widget.resize(w_x, w_y)
        if 'bottom' in widget.resize_mode:
            w_y = pos.y() + widget.sub_y
            widget.resize(w_x, w_y)
        if 'left' in widget.resize_mode:
            sub_x = pos.x() - widget.mc_x
            w_x = w_x - sub_x
            widget.resize(w_x, w_y)
            if widget.size().width() != widget.pre_size_x:
                winX = pos.globalX() - widget.mc_x
                widget.move(winX, widget.pos().y())
            widget.pre_size_x = widget.size().width() 
        if 'top' in widget.resize_mode:
            sub_y = pos.y() - widget.mc_y
            w_y = w_y - sub_y
            widget.resize(w_x, w_y)
            if widget.size().height() != widget.pre_size_y:
                winY = pos.globalY() - widget.mc_y
                widget.move(widget.pos().x(), winY)
            widget.pre_size_y = widget.size().height() 
        
#ウィンドウサイズ切り替え位置でカーソル変更する
def set_cursor_icon(widget, event):
    if event.type() == QEvent.Type.Enter:
        QApplication.setOverrideCursor(Qt.ArrowCursor)
    if event.type() == QEvent.Type.HoverMove:
        pos = event.pos()
        resize_mode = mouse_pressed(widget, pos, set_value=False)
        cur_dict = {
                        'right':Qt.SizeHorCursor,
                         'left':Qt.SizeHorCursor,
                         'top':Qt.SizeVerCursor,
                         'bottom':Qt.SizeVerCursor,
                         'top_left':Qt.SizeFDiagCursor,
                         'bottom_right':Qt.SizeFDiagCursor,
                         'top_right':Qt.SizeBDiagCursor,
                         'bottom_left':Qt.SizeBDiagCursor,
                         None:Qt.ArrowCursor
                            }
        cur = cur_dict[resize_mode] 
        current_cur = QApplication.overrideCursor().shape()
        if cur != current_cur:
            QApplication.changeOverrideCursor(cur_dict[resize_mode])
    #UI外に出たときは元のMaya標準カーソルに戻す
    if event.type() == QEvent.Type.Leave:
        QApplication.restoreOverrideCursor()

def convert_2_hex(color):
    hex = '#'
    for var in color:
        var = format(var, 'x')
        if  len(var) == 1:
            hex = hex+'0'+str(var)
        else:
            hex = hex+str(var)
    return hex
    
def to_3_list(item):
    if not isinstance(item, list):
        item = [item]*3
    return item
    
#オシャレクラスを継承してUIを構築する
class OsyareMain(OceanTeaBaseMixin):
    def __init__(self):
        super(OsyareMain, self).__init__()
        self._initUI()

    def _initUI(self):
        sq_widget = QScrollArea(self)
        sq_widget.setWidgetResizable(True)
        sq_widget.setFocusPolicy(Qt.NoFocus)
        sq_widget.setMinimumHeight(1)
        self.setCentralWidget(sq_widget)
        
        self.opacity(0.85)
        self.gradient(col_l=[64, 225, 225], col_c=[128, 128, 255], col_r=[255, 128, 255])
        
        self.setGeometry(300, 300, 800, 100)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        main_layout = QVBoxLayout()
        sq_widget.setLayout(main_layout)
        hist_layout = QHBoxLayout()
        comment_layout = QHBoxLayout()
        main_layout.addLayout(hist_layout)
        main_layout.addLayout(comment_layout)
        self.init_face()
        self.hist_label = self.set_label('History :', x=20, y=5)
        self.info_label = self.set_label('Undo Info', x=115, y=5)
        hist_layout.addWidget(self.hist_label)
        hist_layout.addWidget(self.info_label)
        self.face_label = self.set_label(self.face_list[0], x=20, y=50)
        #print self.face_label.width()
        self.comment_label = self.set_label(u'まあもちつけ', x=180, y=50)
        comment_layout.addWidget(self.face_label )
        comment_layout.addWidget(self.comment_label)
        self.create_job()
        self.setButton()
        #左に詰める
        hist_layout.addStretch(0)
        comment_layout.addStretch(0)
        
        self.move(400, 820)
        
    def set_label(self, string, x, y):
        label = QLabel(string)
        label.setScaledContents(True)
        label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)#縮小できるポリシー
        label.move(x, y)
        
        label.setFont(QFont("Arial", 18))
        palette = QPalette()
        palette.setColor(QPalette.WindowText, QColor(*[255]*3))
        label.setPalette(palette)
        
        return label
        
    def setButton(self):
        btn = QPushButton(u"×", self)
        w = self.width()-30
        btn.move(w,5)
        btn.setMaximumWidth(20)
        btn.setMaximumHeight(20)
        change_widget_color(btn, textColor=250, bgColor=[255, 64, 64], mode='button')
        btn.clicked.connect(self.close)
        
        path = QPainterPath()
        path.addRoundedRect(btn.rect(), 10, 10)
        region = QRegion(path.toFillPolygon().toPolygon())
        btn.setMask(region)
        
    def closeEvent(self,e):
        cmds.scriptJob(k=self.select_job)
        
    def create_job(self):
        self.select_job = cmds.scriptJob(cu=True, e=("idle", self.undo_info_getter))
        
    pre_info = ''
    def undo_info_getter(self):
        try:
            undo_info = cmds.undoInfo(q=True, un=True)
            if undo_info == self.pre_info:
                return
            print 'get undo info, ', undo_info
            self.info_label.setText(undo_info)
            info_list = undo_info.split(' ')
            srt_mode = info_list[0]
            self.pre_info = undo_info
            if srt_mode == 'scale':
                axis_val_list = [float(i) for i in info_list[-4:-1]]
                if reduce(lambda a, b:a*b, axis_val_list) > 1.0:
                    self.face_label.setText(self.face_list[6])
                    self.comment_label.setText(u'膨らむ～')
                if reduce(lambda a, b:a*b, axis_val_list) < 1.0:
                    self.face_label.setText(self.face_list[7])
                    self.comment_label.setText(u'縮むー')
            elif srt_mode == 'rotate':
                self.face_label.setText(self.face_list[11])
                self.comment_label.setText(u'目が回る～～')
            elif srt_mode == 'move':
                self.face_label.setText(self.face_list[12])
                self.comment_label.setText(u'ブーン')
            elif srt_mode == 'select':
                sel_count = len(cmds.ls(sl=True, fl=True))
                print 'select mode', sel_count
                if sel_count == 0:
                    self.face_label.setText(self.face_list[2])
                    self.comment_label.setText(u'選択解除であります。')
                elif sel_count < 50:
                    self.face_label.setText(self.face_list[1])
                    self.comment_label.setText(str(sel_count)+u'個選択したお')
                elif sel_count > 1000:
                    self.face_label.setText(self.face_list[5])
                    self.comment_label.setText(u'アワワワワワワワワワ')
                elif sel_count > 100:
                    self.face_label.setText(self.face_list[4])
                    self.comment_label.setText(u'めっちゃ選択した！！')
            elif srt_mode.startswith('Create'):
                self.face_label.setText(self.face_list[8])
                self.comment_label.setText(u'Dag仲間が増えたお')
            elif srt_mode.startswith('Duplicate'):
                self.face_label.setText(self.face_list[9])
                self.comment_label.setText(u'ﾌﾞﾝｼｰﾝ!!')
            elif srt_mode== 'doDelete':
                self.face_label.setText(self.face_list[10])
                self.comment_label.setText(u'アディオスアミーゴ…')
                
            else:
                self.face_label.setText(self.face_list[0])
                self.comment_label.setText(u'まあもちつけ')
                return
            return
        except Exception as e:
            print e.message
            return 
            
    def init_face(self):
        self.face_list = [
        u'( ´・ω・｀)_且 {',
        u'(*´・∀・) {', 
        u'（　･`ω･´) {', 
        u'c(・ω・`c⌒っ {', 
        u'(((；ﾟДﾟ))) {', 
        u'Σ(ﾟДﾟ；≡；ﾟдﾟ) {', #5
        u'(　´)Д(｀ ) {', 
        u'(›´ω`‹ ) {', 
        u'(｡>ω<)ﾉ {', 
        u'(・(・(・(・д・)・)・)・) {', 
        u'(´ ; Δ ; )／ {', #10
        u'（；°Д。） {', 
        u'(((((((((((っ･ω･)っ {', 
        u' {'
        ]
        
    
def change_widget_color(button, textColor=200, bgColor=68, hiColor=68, hiText=255, hiBg=[97, 132, 167], dsColor=[255, 128, 128],
                                        mode='common', toggle=False, hover=True, destroy=False, dsWidth=1):
    textColor = to_3_list(textColor)
    bgColor = to_3_list(bgColor)
    hiColor = to_3_list(hiColor)
    hiText = to_3_list(hiText)
    hiBg = to_3_list(hiBg)
    dsColor = to_3_list(dsColor)
    if toggle and button.isChecked():
        bgColor = hiColor
    if hover:
        hvColor = map(lambda a:a+20, bgColor)
    else:
        hvColor = bgColor
    textHex =  convert_2_hex(textColor)
    bgHex = convert_2_hex(bgColor)
    hvHex = convert_2_hex(hvColor)
    hiHex = convert_2_hex(hiColor)
    htHex = convert_2_hex(hiText)
    hbHex = convert_2_hex(hiBg)
    dsHex = convert_2_hex(dsColor)
    if mode == 'common':
        button.setStyleSheet('color: '+textHex+' ; background-color: '+bgHex)
    if mode == 'button':
        if not destroy:
            button. setStyleSheet('QPushButton{background-color: '+bgHex+'; color:  '+textHex+' ; border: black 0px}' +\
                                'QPushButton:hover{background-color: '+hvHex+'; color:  '+textHex+' ; border: black 0px}'+\
                                'QPushButton:pressed{background-color: '+hiHex+'; color: '+textHex+'; border: black 2px}')
        if destroy:
            button. setStyleSheet('QPushButton{background-color: '+bgHex+'; color:  '+textHex+'; border-style:solid; border-width: '+str(dsWidth)+'px; border-color:'+dsHex+'; border-radius: 0px;}' +\
                                'QPushButton:hover{background-color: '+hvHex+'; color:  '+textHex+'; border-style:solid; border-width: '+str(dsWidth)+'px; border-color:'+dsHex+'; border-radius: 0px;}'+\
                                'QPushButton:pressed{background-color: '+hiHex+'; color: '+textHex+'; border-style:solid; border-width: '+str(dsWidth)+'px; border-color:'+dsHex+'; border-radius: 0px;}')
    if mode == 'window':
        button. setStyleSheet('color: '+textHex+';'+\
                        'background-color: '+bgHex+';'+\
                        'selection-color: '+htHex+';'+\
                        'selection-background-color: '+hbHex+';')
                        
def main():
    global window
    try:
        window.close()
        del window
    except:
        pass
    window = OsyareMain()
    window.show()
    