import pyvisa
import time
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

# PyVISAリソースと初期設定
axisNo = '1'  # 固定軸番号
direction = 'CCW'
mode = 0  # 初期駆動方法
rm = pyvisa.ResourceManager()
instrument = None

# 状態を更新する関数
def update_status():
    if instrument:
        try:
            status = serial_write_read(f'AXI{axisNo}:SB1?')
            lblState.config(text="動作中" if int(status) & 0x40 else "停止")
            position = serial_write_read(f'AXI{axisNo}:POS?')
            txtCurrentPosition.delete(0, tk.END)
            txtCurrentPosition.insert(tk.END, position)
        except Exception:
            lblState.config(text="エラー")
    else:
        lblState.config(text="未接続")
    root.after(500, update_status)  # 状態を定期的に更新

# コントローラへの接続処理
def comm_port_open():
    global instrument
    try:
        instrument = rm.open_resource('GPIB1::7::INSTR')
        instrument.timeout = 2000
        messagebox.showinfo("接続完了", "コントローラに接続しました。")
        lblState.config(text="接続済み")
    except Exception as e:
        messagebox.showerror("接続エラー", f"接続失敗: {e}")

# 通信を閉じる処理
def comm_port_close():
    global instrument
    if instrument:
        instrument.close()
        instrument = None
    lblState.config(text="未接続")
    messagebox.showinfo("切断完了", "コントローラとの接続を切断しました。")

# ステージの駆動
def move_stage(direction):
    global axisNo, mode
    try:
        if mode == 0:  # 連続駆動
            cmd = f'AXI{axisNo}:GO {direction}J'
        elif mode == 1:  # ステップ駆動
            steps = txtStep.get()
            cmd = f'AXI{axisNo}:PULS {steps}:GO {direction}'
        elif mode == 2:  # 原点復帰
            cmd = f'AXI{axisNo}:GO ORG'
        serial_write(cmd)

        #現在地を更新
        update_status()
    except Exception as e:
        messagebox.showerror("エラー", f"駆動失敗: {e}")

# 現在のポジションを変更する
def update_position():
    global axisNo
    try:
        new_position = txtCurrentPosition.get()
        cmd = f'AXI{axisNo}:POS {new_position}'
        serial_write(cmd)
        messagebox.showinfo("更新完了", f"ポジションを {new_position} に更新しました。")
    except Exception as e:
        messagebox.showerror("エラー", f"ポジション更新失敗: {e}")

# コマンド送信処理
def serial_write(command):
    if instrument:
        instrument.write(command)

# コマンド送受信処理
def serial_write_read(command):
    if instrument:
        serial_write(command)
        time.sleep(0.1)
        return instrument.read()

# GUIの構築
root = tk.Tk()
root.title("ステージコントローラ")
root.geometry("400x300")  # コンパクトなサイズに調整

# 通信設定フレーム
frame_connection = ttk.LabelFrame(root, text="通信設定", padding=(5, 5))
frame_connection.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

btnConnect = ttk.Button(frame_connection, text="接続", command=comm_port_open)
btnConnect.grid(row=0, column=0, padx=5, pady=5)

btnDisconnect = ttk.Button(frame_connection, text="切断", command=comm_port_close)
btnDisconnect.grid(row=0, column=1, padx=5, pady=5)

lblState = ttk.Label(frame_connection, text="未接続", width=15, anchor="center", relief="sunken")
lblState.grid(row=0, column=2, padx=5, pady=5)

# 駆動設定フレーム
frame_drive = ttk.LabelFrame(root, text="駆動設定", padding=(5, 5))
frame_drive.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

lblStep = ttk.Label(frame_drive, text="ステップ:")
lblStep.grid(row=0, column=0, padx=5, pady=5)

txtStep = ttk.Entry(frame_drive, width=8)
txtStep.insert(0, "100")
txtStep.grid(row=0, column=1, padx=5, pady=5)

# 駆動操作フレーム
frame_controls = ttk.LabelFrame(root, text="操作", padding=(5, 5))
frame_controls.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

btnCCW = ttk.Button(frame_controls, text="CCW", command=lambda: move_stage("CCW"))
btnCCW.grid(row=0, column=0, padx=5, pady=5)

btnStop = ttk.Button(frame_controls, text="停止", command=lambda: serial_write("STOP 0"))
btnStop.grid(row=0, column=1, padx=5, pady=5)

btnCW = ttk.Button(frame_controls, text="CW", command=lambda: move_stage("CW"))
btnCW.grid(row=0, column=2, padx=5, pady=5)

# ポジション表示と変更フレーム
frame_position = ttk.LabelFrame(root, text="ポジション変更", padding=(5, 5))
frame_position.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

lblCurrentPosition = ttk.Label(frame_position, text="現在位置:")
lblCurrentPosition.grid(row=0, column=0, padx=5, pady=5)

txtCurrentPosition = ttk.Entry(frame_position, width=10)
txtCurrentPosition.grid(row=0, column=1, padx=5, pady=5)

btnUpdatePosition = ttk.Button(frame_position, text="更新", command=update_position)
btnUpdatePosition.grid(row=0, column=2, padx=5, pady=5)

# 定期更新処理
update_status()

root.mainloop()
