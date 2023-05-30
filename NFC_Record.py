print("Startup...")
# init
import tkinter as tk
from datetime import datetime as dt
import nfc
from threading import Thread as th
from time import sleep
from pygame import mixer as mx
from csv import reader as rdr
from csv import writer as wtr
from os import path as pt

tx_title="電算研出席"
tx_ver="v1.08"

gray="#444444"
white="#ffffff"
great="#008a00"
info="#0070f0"
warn="#807500"
ftal="#cc0000"

# flag [main,]
FLAG=[True]
N_UPD=set(); D_UPD=set(); E_UPD=set(); A_NUM=0;
RPTNUM=[0,0]; EXT=[dict()]

class mCardReader(object):
    def on_connect(self, tag):
        global A_NUM
        #touched
        stat_update(info,"読み込み中...","\uf16a")

        # Load Student No. from IC CARD
        try:
            tag.polling(system_code=0x93B1)
            sc = nfc.tag.tt3.ServiceCode(64, 0x0b)
            bc = nfc.tag.tt3.BlockCode(0, service=0)
            data = tag.read_without_encryption([sc], [bc])

            stid = data.decode('utf-8').lstrip('0').rstrip()[:-2]
            if stid in EXT[0]:
                if stid in N_UPD or stid in D_UPD:
                    mplay("snd/special.mp3")
                    stat_update(warn,"{} さん 既に出席済みです".format(EXT[0][stid]),"\ue762")
                elif stid in E_UPD:
                    mplay("snd/great.mp3")
                    stat_update(great,"{} さん 出席に変更しました".format(EXT[0][stid]),"\ue10b")
                    N_UPD.add(stid)
                else:
                    mplay("snd/great.mp3")
                    stat_update(great,"{} さん こんにちは".format(EXT[0][stid]),"\ue10b")
                    N_UPD.add(stid)
                    A_NUM += 1
            else:
                if RPTNUM[1]:
                    mplay("snd/fatal.mp3")
                    stat_update(ftal,"[E20] {} さん 未登録者です".format(stid),"\uee57")
                else:
                    mplay("snd/great.mp3")
                    stat_update(great,"{} さん こんにちは".format(stid),"\ue10b")
                    N_UPD.add(stid)
                

        except AttributeError:
            mplay("snd/warn2.mp3")
            stat_update(warn,"[E10] KIT学生証ではありません","\ue1e0")
        except nfc.tag.tt3.Type3TagCommandError:
            mplay("snd/warn1.mp3")
            stat_update(warn,"[E11] もう一度やり直してください","\uea6a")
        return True

    def read_id(self):
        try:
            stat_update(info,"KIT学生証をかざしてください","\ued5c")
            clf = nfc.ContactlessFrontend('usb')
            try:
                clf.connect(rdwr={'on-connect': self.on_connect})
            finally:
                clf.close()
        except Exception as e:
            print("Err:",e)
            mplay("snd/fatal.mp3")
            for i in range(4,-1,-1):
                stat_update(ftal,"[E01] カードリーダー未接続 ({}s)".format(i),"\ueb55")
                slp(1)
        slp(.3)

#tkinterを起動
root = tk.Tk()
#タイトルの設定
root.title((tx_title,tx_ver))
#画面サイズの指定
root.geometry("520x640")
#音の設定
mx.init(frequency= 44100)

def mplay(addr):
    mx.music.load(addr)
    mx.music.play()
		 
def readNFC():
    while FLAG[0]:
        stat_update(info,"カードリーダ準備中...","\uf16a")
        mCardReader().read_id()

def slp(time):
	sleep(time if FLAG[0] else 0)

def upload():
    global A_NUM
    # 前処理
    try:
        # 名簿読み込み
        upld_update("(1/4) List Loading...")
        with open("list.csv") as f:
            for row in rdr(f):
                EXT[0] = {**EXT[0], row[0]:row[1]}
        RPTNUM[1] = len(EXT[0])
        print("F: List Load OK")
        
        # 出席済み記録を確認
        upld_update("(2/4) Checking list...")
        if pt.isfile("checked.csv"):
            with open("checked.csv") as f:
                for row in rdr(f):
                    if len(row)!=0:
                        D_UPD.add(row[0])
            print("F: Additional check OK")
        else:
            print("F: No list file")
        

        # 事前報告記録を確認
        upld_update("(3/4) Checking external...")
        if pt.isfile("external.csv"):
            with open("external.csv") as f:
                for row in rdr(f):
                    if len(row)!=0:
                        E_UPD.add(row[0])
            print("F: External check OK")
        else:
            print("F: No external file")

        # 出席が必要な人数の計算
        upld_update("(4/4) Restoring...")
        for i in D_UPD:
            if not(i in E_UPD): A_NUM+=1
        print("F: Status restore OK")
    except Exception as e:
        ex="W: "+str(e)
        print(ex)
        for i in range(len(ex)+1):
            upld_update(ex[i:i+40])
            slp(3 if i == 0 else .3)
    finally:
        print("F: Ready")
    
    # メインループ
    while FLAG[0] or len(N_UPD):
        if len(N_UPD):
            try:
                tmp = list(N_UPD)
                upld_update("Writing...")
                with open("checked.csv",mode="a",encoding="cp932",newline="") as f:
                    for i in tmp:
                        wtr(f).writerow([i,EXT[0][i] if RPTNUM[1] else None,dt.now().strftime('%Y/%m/%d %H:%M:%S'),"出席"])
                        D_UPD.add(i);N_UPD.remove(i)
                        print("R: Recorded {}({}) at {}".format(i,EXT[0][i] if RPTNUM[1] else None,dt.now().strftime('%Y/%m/%d %H:%M:%S')))
                upld_update("Write OK")
                slp(3)
            except Exception as e:
                ex="E51: "+str(e)
                print(ex)
                for i in range(len(ex)+1):
                    upld_update(ex[i:i+40])
                    slp(3 if i == 0 else .3)
        else:
            upld_update("Standby...")
            slp(3) 
    
        
#tk 常時更新
def alway_update():
    global A_NUM
    RPTNUM[0]=len(D_UPD)
    dateS.config(text=dt.now().strftime('%Y/%m/%d %H:%M:%S'))
    upldSR.config(text="{}/{} ({}/{})".format(A_NUM,RPTNUM[1]-len(E_UPD),RPTNUM[0],RPTNUM[1]))
    root.after(100,alway_update)

def stat_update(color,mes,icon):
    if not(FLAG[0]) : return
    statS.config(text=mes,bg=color)
    statF.config(bg=color)
    mainS.config(text=icon,bg=color)
    mainF.config(bg=color)
	
def upld_update(p1):
	if not(FLAG[0]) : return
	upldSL.config(text=p1)

titleF = tk.Frame(root)
titleF.pack(fill=tk.X)

dateF = tk.Frame(root,bg=gray)
dateF.pack(side= tk.BOTTOM,fill=tk.X)

upldF = tk.Frame(root)
upldF.pack(side= tk.BOTTOM,fill=tk.X)
upldFR =tk.Frame(upldF,bg=gray)
upldFR.pack(side=tk.RIGHT)
upldFL =tk.Frame(upldF,bg=gray)
upldFL.pack(fill=tk.X)

statF = tk.Frame(root,bg=info)
statF.pack(side= tk.BOTTOM,fill=tk.X)

mainF = tk.Frame(root,bg=info)
mainF.pack(fill=tk.BOTH,expand=True)

# ラベル表示
titleS = tk.Label(titleF, text=(tx_title,tx_ver),
    font=("Segoe UI", "32"))
titleS.pack(side=tk.LEFT)

dateS = tk.Label(dateF, text="Date",
    font=("Consolas", "14"),
    fg=white,bg=gray)
dateS.pack(expand=True)

upldSL = tk.Label(upldFL, text="Startup...",
    font=("Consolas","14"),
    fg=white,bg=gray)
upldSL.pack(side=tk.LEFT)
upldSR = tk.Label(upldFR, text="---/---",
    font=("Consolas","14"),
    fg=white,bg=gray)
upldSR.pack(side=tk.RIGHT)


statS = tk.Label(statF, text="起動中",
    font=("Segoe UI","24"),
    fg=white,bg=info)
statS.pack(expand=True)

mainS = tk.Label(mainF,text="\uf16a",
    font=("Segoe MDL2 Assets",220),
    fg=white,bg=info,
)
mainS.pack(expand=True)

# NFC start
thr1 = th(target=readNFC)
thr1.start()
# Record start
thr2 = th(target=upload)
thr2.start()
# alway start
alway_update()

print("----------------\n")

# Disp start
root.mainloop()

# shutdown
print("\n----------------")
print("Shutdown...")
print("Please disconnect NFC reader.")
FLAG[0] = False
thr2.join()
print(" - Record shutdown OK")
thr1.join()
print(" - NFC shutdown OK")
mx.quit()

# 後処理
print("----------------\n")
# 出席
tmp = list(D_UPD)
for i in tmp:
    del EXT[0][i]
# 4年、事前報告
tmp = list(E_UPD)
for i in tmp:
    if i in EXT[0] : del EXT[0][i]

# 無断欠席の演算
with open("absent_{}.log".format(dt.now().strftime("%y%m")),mode="w",encoding="cp932",newline="") as f:
    for k,v in EXT[0].items():
        print("[無断欠席] {} / {}".format(k,v))
        wtr(f).writerow([k,v])
print("\n")