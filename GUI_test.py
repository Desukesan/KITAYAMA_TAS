import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QFileDialog, QSizePolicy, QToolBar
from PyQt5.QtGui import QPixmap
import json
import os

class DataGraphApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("データグラフ作成")

        # メインウィジェットとレイアウト
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # ツールバーの設定
        self.toolbar = QToolBar("ツールバー")
        self.addToolBar(self.toolbar)

        # ツールバーにボタンを追加
        plot_button = QPushButton("グラフを描く")
        plot_button.clicked.connect(self.plot_graph)
        self.toolbar.addWidget(plot_button)

        save_button = QPushButton("データを保存")
        save_button.clicked.connect(self.save_data)
        self.toolbar.addWidget(save_button)

        load_button = QPushButton("データを読み込む")
        load_button.clicked.connect(self.load_data)
        self.toolbar.addWidget(load_button)

        # 左側のレイアウト (ダークデータ)
        dark_layout = QVBoxLayout()
        self.text_boxes = {}
        self.graph_widgets = {}
        self.text_boxes['DARK_ref'], self.graph_widgets['DARK_ref'] = self.create_text_box_with_graph('DARK_ref', dark_layout)
        self.text_boxes['DARK_sig'], self.graph_widgets['DARK_sig'] = self.create_text_box_with_graph('DARK_sig', dark_layout)

        # 右側のレイアウト (残りのデータ)
        remaining_layout = QVBoxLayout()
        self.text_boxes['ref'], self.graph_widgets['ref'] = self.create_text_box_with_graph('ref', remaining_layout)
        self.text_boxes['sig'], self.graph_widgets['sig'] = self.create_text_box_with_graph('sig', remaining_layout)
        self.text_boxes['ref_p'], self.graph_widgets['ref_p'] = self.create_text_box_with_graph('ref_p', remaining_layout)
        self.text_boxes['sig_p'], self.graph_widgets['sig_p'] = self.create_text_box_with_graph('sig_p', remaining_layout)

        # 左側と右側のレイアウトをメインレイアウトに追加
        main_layout.addLayout(dark_layout)
        main_layout.addLayout(remaining_layout)

        self.setCentralWidget(main_widget)

        # テキストボックスの内容が変更されたときにプレビューを更新する
        for text_box in self.text_boxes.values():
            text_box.textChanged.connect(self.update_graphs)

    def create_text_box_with_graph(self, label, layout):
        h_layout = QHBoxLayout()
        lbl = QLabel(f'データ {label}:')
        h_layout.addWidget(lbl)
        
        text_box = QPlainTextEdit()
        text_box.setFixedSize(150, 80)
        text_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        h_layout.addWidget(text_box)

        graph_widget = QLabel()
        graph_widget.setFixedSize(100, 80)
        h_layout.addWidget(graph_widget)

        layout.addLayout(h_layout)
        return text_box, graph_widget

    def update_graphs(self):
        for label, text_box in self.text_boxes.items():
            data = text_box.toPlainText()
            self.update_graph(self.graph_widgets[label], data)

    def update_graph(self, graph_widget, data):
        plt.clf()
        if data.strip():
            x_values, y_values = self.parse_data(data)
            plt.figure(figsize=(1.5, 1))
            plt.plot(x_values, y_values, color='blue')
            plt.axis('off')
            plt.xlim(min(x_values), max(x_values) if x_values else 1)
            plt.ylim(min(y_values), max(y_values) if y_values else 1)

            temp_file_path = 'temp.png'
            plt.savefig(temp_file_path, bbox_inches='tight', pad_inches=0)
            plt.close()

            graph_widget.setPixmap(QPixmap(temp_file_path))
            os.remove(temp_file_path)

    def parse_data(self, data):
        x_values, y_values = [], []
        for line in data.splitlines():
            if line.strip():
                parts = line.split()
                x_values.append(float(parts[0]))
                y_values.append(float(parts[1]))
        return x_values, y_values

    def plot_graph(self):
        # 各テキストボックスからデータを取得
        x_dark_ref, y_dark_ref = self.parse_data(self.text_boxes['DARK_ref'].toPlainText())
        _, y_dark_sig = self.parse_data(self.text_boxes['DARK_sig'].toPlainText())
        _, y_ref = self.parse_data(self.text_boxes['ref'].toPlainText())
        _, y_sig = self.parse_data(self.text_boxes['sig'].toPlainText())
        _, y_ref_p = self.parse_data(self.text_boxes['ref_p'].toPlainText())
        _, y_sig_p = self.parse_data(self.text_boxes['sig_p'].toPlainText())

        # 計算
        results = {
            'ref - DARK_ref': [ref - dark_ref for dark_ref, ref in zip(y_dark_ref, y_ref)],
            'sig - DARK_sig': [sig - dark_sig for dark_sig, sig in zip(y_dark_sig, y_sig)],
            'ref_p - DARK_ref': [ref_p - dark_ref for dark_ref, ref_p in zip(y_dark_ref, y_ref_p)],
            'sig_p - DARK_sig': [sig_p - dark_sig for dark_sig, sig_p in zip(y_dark_sig, y_sig_p)],
        }

        # LOG計算
        log_values = []
        for ref_p_dark, sig_dark, sig_p_dark, ref_dark in zip(
                results['ref_p - DARK_ref'], results['sig - DARK_sig'], results['sig_p - DARK_sig'], results['ref - DARK_ref']):
            if ref_dark != 0 and sig_p_dark != 0:
                log_value = np.log((ref_p_dark * sig_dark) / (sig_p_dark * ref_dark))
                log_values.append(log_value)
            else:
                log_values.append(np.nan)

        # LOG計算結果グラフを別ウィンドウで表示
        log_fig = plt.figure(figsize=(6, 4))
        plt.plot(x_dark_ref, log_values, color='black', linestyle='-',
                 label='LOG((ref_p - DARK_ref) * (sig - DARK_sig) / (sig_p - DARK_sig) / (ref - DARK_ref))')
        plt.axhline(0.01, color='red', linestyle='--')
        plt.axhline(-0.01, color='red', linestyle='--')
        plt.title('LOG計算結果グラフ')
        plt.xlabel('DARK_ref 1列目 (X軸)')
        plt.ylabel('LOG値')
        plt.legend()
        plt.grid()
        plt.get_current_fig_manager().window.setGeometry(100, 100, 600, 400)
        plt.show()

        # ref と DARK_ref、sig と DARK_sig のグラフを同じウィンドウで表示
        combined_fig = plt.figure(figsize=(6, 8))

        # 上部 (ref と DARK_ref および ref_p と DARK_ref のグラフ)
        plt.subplot(2, 1, 1)
        plt.plot(x_dark_ref, results['ref - DARK_ref'], color='black', linestyle='-', label='ref - DARK_ref')
        plt.plot(x_dark_ref, results['ref_p - DARK_ref'], color='gray', linestyle='--', label='ref_p - DARK_ref')
        plt.title('ref と ref_p の計算結果グラフ')
        plt.xlabel('DARK_ref 1列目 (X軸)')
        plt.ylabel('値の差')
        plt.legend()
        plt.grid()

        # 下部 (sig と DARK_sig および sig_p と DARK_sig のグラフ)
        plt.subplot(2, 1, 2)
        plt.plot(x_dark_ref, results['sig - DARK_sig'], color='black', linestyle='-', label='sig - DARK_sig')
        plt.plot(x_dark_ref, results['sig_p - DARK_sig'], color='gray', linestyle='--', label='sig_p - DARK_sig')
        plt.title('sig と sig_p の計算結果グラフ')
        plt.xlabel('DARK_ref 1列目 (X軸)')
        plt.ylabel('値の差')
        plt.legend()
        plt.grid()

        plt.tight_layout()
        plt.get_current_fig_manager().window.setGeometry(800, 100, 600, 800)
        plt.show()

    def save_data(self):
        data = {label: self.text_boxes[label].toPlainText() for label in self.text_boxes}
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "データを保存", "", "JSON Files (*.json);;All Files (*)", options=options)
        
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(data, f)
            print("データが保存されました:", file_path)

    def load_data(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "データを読み込む", "", "JSON Files (*.json);;All Files (*)", options=options)
        
        if file_path:
            with open(file_path, 'r') as f:
                data = json.load(f)
            for label, content in data.items():
                if label in self.text_boxes:
                    self.text_boxes[label].setPlainText(content)
            print("データが読み込まれました:", file_path)

# アプリケーションの起動
app = QApplication(sys.argv)
window = DataGraphApp()
window.show()
sys.exit(app.exec_())
