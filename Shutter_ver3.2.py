import serial
import serial.tools.list_ports
import time
import tkinter as tk
from tkinter import messagebox, StringVar, ttk

def list_serial_ports():
    """接続されているシリアルポートのリストを取得します。"""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def send_command(arduino, motor_num, steps, delay_time, direction):
    command = f"{motor_num},{steps},{delay_time},{direction}\n"
    arduino.write(command.encode())
    time.sleep(delay_time)

def operate_motor(arduino, motor_num, steps, direction):
    try:
        send_command(arduino, motor_num, steps, 2, direction)
    except Exception as e:
        messagebox.showerror("エラー", f"モーターの操作中にエラーが発生しました: {str(e)}")

def connect_serial_port(port):
    """Arduinoに接続します。"""
    return serial.Serial(port, 9600, timeout=1)

def angle_to_steps(angle):
    """角度をステップ数に変換します。"""
    steps_per_degree = 512 / 360
    return int(angle * steps_per_degree)

def on_run_motor():
    try:
        angle = float(steps_entry.get())  # 角度を浮動小数点数として取得
        steps = angle_to_steps(angle)  # 角度をステップ数に変換
        direction = direction_var.get()
        motor_num = motor_var.get()  # モーターの選択
        operate_motor(arduino, motor_num, steps, direction)
    except ValueError:
        messagebox.showerror("エラー", "モーターの角度は数値で入力してください。")

def connect_to_selected_port():
    global arduino
    try:
        if 'arduino' in globals():
            arduino.close()  # 以前の接続を閉じる
        selected_port = port_var.get()  # ドロップダウンからポートを取得
        arduino = connect_serial_port(selected_port)
        
        # 接続が成功したらテキストボックスに初期値50を設定
        steps_entry.delete(0, tk.END)  # 現在のテキストを削除
        steps_entry.insert(0, "50")  # 初期値として50を設定
    except Exception as e:
        messagebox.showerror("接続エラー", str(e))

# シャッタースイッチの設定 (モーター1)
def shutter_switch_motor1():
    global shutter_state_motor1, direction_var_motor1

    # 50度の回転
    angle = 50
    steps = angle_to_steps(angle)
    motor_num = "1"  # モーター1

    # 方向を切り替え
    direction = direction_var_motor1.get()
    operate_motor(arduino, motor_num, steps, direction)
    
    # 次の操作のために方向を切り替え
    direction_var_motor1.set("-1" if direction == "1" else "1")

    # シャッター状態を切り替え
    if shutter_state_motor1.get() == "CLOSE":
        shutter_state_motor1.set("OPEN !!")
        shutter_state_label_motor1.config(fg="red", font=("", 12, "bold"))
    else:
        shutter_state_motor1.set("CLOSE")
        shutter_state_label_motor1.config(fg="blue", font=("", 12, "bold"))
    
    shutter_state_label_motor1.config(text=f"Shutter Motor 1 : {shutter_state_motor1.get()}")

# シャッタースイッチの設定 (モーター2)
def shutter_switch_motor2():
    global shutter_state_motor2, direction_var_motor2

    # 50度の回転
    angle = 50
    steps = angle_to_steps(angle)
    motor_num = "2"  # モーター2

    # 方向を切り替え
    direction = direction_var_motor2.get()
    operate_motor(arduino, motor_num, steps, direction)
    
    # 次の操作のために方向を切り替え
    direction_var_motor2.set("1" if direction == "-1" else "-1")

    # シャッター状態を切り替え
    if shutter_state_motor2.get() == "CLOSE":
        shutter_state_motor2.set("OPEN !!")
        shutter_state_label_motor2.config(fg="red", font=("", 12, "bold"))
    else:
        shutter_state_motor2.set("CLOSE")
        shutter_state_label_motor2.config(fg="blue", font=("", 12, "bold"))
    
    shutter_state_label_motor2.config(text=f"Shutter Motor 2 : {shutter_state_motor2.get()}")

# GUIの設定
root = tk.Tk()
root.title("Shutter Control")

# シリアルポートのリストを取得
ports = list_serial_ports()
selected_port = ports[0] if ports else None

# シリアルポートの選択
port_var = StringVar(value=selected_port)
port_label = tk.Label(root, text="シリアルポート:")
port_label.grid(row=0, column=0)

port_dropdown = ttk.Combobox(root, textvariable=port_var, values=ports)
port_dropdown.grid(row=0, column=1)

connect_button = tk.Button(root, text="接続", command=connect_to_selected_port)
connect_button.grid(row=0, column=2)

# モーターの選択
motor_var = StringVar(value="1")  # 初期値をモーター1に設定
tk.Label(root, text="モーター番号:").grid(row=1, column=0)
tk.Radiobutton(root, text="Motor 1", variable=motor_var, value="1").grid(row=1, column=1)
tk.Radiobutton(root, text="Motor 2", variable=motor_var, value="2").grid(row=1, column=2)

# モーターの入力フィールド
tk.Label(root, text="角度:").grid(row=2, column=0)
steps_entry = tk.Entry(root)  # 角度入力用エントリ
steps_entry.grid(row=2, column=1)

direction_var = StringVar(value="1")  # 初期値をCWに設定
direction_var_motor1 = StringVar(value="-1")
direction_var_motor2 = StringVar(value="1")

tk.Label(root, text="方向:").grid(row=3, column=0)
tk.Radiobutton(root, text="CW", variable=direction_var, value="1").grid(row=3, column=1)
tk.Radiobutton(root, text="CCW", variable=direction_var, value="-1").grid(row=3, column=2)

run_button = tk.Button(root, text="Run", command=on_run_motor)
run_button.grid(row=2, column=2)

# シャッタースイッチボタン (モーター1)
shutter_button_motor1 = tk.Button(root, text="Shutter Switch Motor 1", command=shutter_switch_motor1)
shutter_button_motor1.grid(row=4, column=0)

# シャッター状態表示ラベル (モーター1)
shutter_state_motor1 = StringVar(value="CLOSE")
shutter_state_label_motor1 = tk.Label(root, text=f"Shutter Motor 1 : {shutter_state_motor1.get()}")
shutter_state_label_motor1.grid(row=5, column=0)

# シャッタースイッチボタン (モーター2)
shutter_button_motor2 = tk.Button(root, text="Shutter Switch Motor 2", command=shutter_switch_motor2)
shutter_button_motor2.grid(row=4, column=1)

# シャッター状態表示ラベル (モーター2)
shutter_state_motor2 = StringVar(value="CLOSE")
shutter_state_label_motor2 = tk.Label(root, text=f"Shutter Motor 2 : {shutter_state_motor2.get()}")
shutter_state_label_motor2.grid(row=5, column=1)

# GUIのメインループを開始
root.mainloop()

# プログラム終了時にシリアルポートを閉じる
if 'arduino' in globals():
    arduino.close()
