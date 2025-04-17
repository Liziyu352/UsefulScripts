#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import ast
import re
import sys
import pathlib

# 全局变量
data = None
x = None
y = None
fixed_xlim = None
fixed_ylim = None
k = None
b = None
rounds = 7500
custom_rounds = True # Enable rounds above

def load_data():
    """加载数据并计算坐标范围"""
    global data, x, y, fixed_xlim, fixed_ylim
    dataset = pathlib.Path('./dataset.txt')
    data_content = ast.literal_eval(dataset.read_text())

    # 转换键值对为浮点数
    temp = {}
    for k, v in data_content.items():
        temp[float(k)] = float(v)
    data = temp.copy()

    # 创建numpy数组
    x = np.array(list(data.keys()))
    y = np.array(list(data.values()))

    # 计算坐标轴范围
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    x_margin = (x_max - x_min) * 0.2
    y_margin = (y_max - y_min) * 0.2
    fixed_xlim = (x_min - x_margin, x_max + x_margin)
    fixed_ylim = (y_min - y_margin, y_max + y_margin)

def train_model(reinit=False,wait=True):
    """训练线性回归模型"""
    global k, b, rounds
    if reinit or k is None or b is None:
        k = np.random.randn()
        b = np.random.randn()

    learning_rate = 0.01
    k_history = []
    b_history = []
    loss_history = []

    # 创建动态图表
    plt.ion()
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)

    for round in range(rounds):
        # 前向传播
        y_pred = k * x + b
        loss = ((y_pred - y) ** 2).mean()

        # 反向传播
        dk = 2 * np.mean((y_pred - y) * x)
        db = 2 * np.mean(y_pred - y)

        # 更新参数
        k -= learning_rate * dk
        b -= learning_rate * db

        # 每10轮更新一次可视化
        if round % 10 == 0:
            ax.clear()
            ax.set_xlim(fixed_xlim)
            ax.set_ylim(fixed_ylim)
            ax.scatter(x, y, label='True Value')
            ax.plot(x, k * x + b, 'r-',
                    label=f'Prediction: (k={k:.2f}, b={b:.2f})')
            ax.set_title(f'Training round: {round + 10}/{rounds} ({int((round + 10) / rounds * 100)}%) Loss: {loss:.4f}')
            ax.legend()
            if wait:
                plt.pause(0.1)

        # 记录历史数据
        k_history.append(k)
        b_history.append(b)
        loss_history.append(loss)

    plt.ioff()
    plt.show()

    # 显示训练结果
    plt.figure(figsize=(12, 5))
    plt.subplot(121)
    plt.plot(k_history, label='k')
    plt.plot(b_history, label='b')
    plt.title("Arguments")
    plt.legend()

    plt.subplot(122)
    plt.plot(loss_history)
    plt.title("Loss")
    plt.show()


# 主程序
if __name__ == "__main__":
    # 处理命令行参数
    dataset = pathlib.Path('./dataset.txt')
    data_content = ast.literal_eval(dataset.read_text())
    if custom_rounds:
        wait=False
    else:
        rounds = int(int((len(data_content.items()) ** 2.25 * 2 + 2750))/10)*10
        wait=True
    print(f"rounds={rounds}")
    if custom_rounds:
        print("Disabled waiting. MatPlotLib's windows will display as 'no responsing', please wait.")

    # 初始化系统
    load_data()
    train_model(reinit=True,wait=wait)

    # 交互式预测
    plt.figure(figsize=(10, 5))
    while True:
        try:
            cmd = input(
                "输入x值预测 | k= 修改权重 | b= 修改偏值 | reload 重载数据 | retrain 重新训练 | exit 退出: ").strip()

            if cmd.lower() == 'exit':
                break

            # 处理特殊命令
            if cmd.lower() == 'reload':
                load_data()
                train_model(reinit=True,wait=wait)
                continue

            if cmd.lower() == 'retrain':
                train_model(reinit=True,wait=wait)
                continue

            # 处理参数修改
            if re.match(r'^[kb]=', cmd):
                parts = cmd.split('=')
                if len(parts) != 2:
                    raise ValueError("TypeError: k=1.23 or b=4.56")

                new_val = float(parts[1])
                if cmd.startswith('k='):
                    k = new_val
                    print(f"set k = {k:.4f}")
                elif cmd.startswith('b='):
                    b = new_val
                    print(f"set b = {b:.4f}")
                continue

            # 处理数值预测
            x_input = float(cmd)
            y_pred = k * x_input + b

            # 可视化结果
            plt.clf()
            plt.scatter(x, y, label='True Value')
            plt.plot(x, k * x + b, 'r-',
                     label=f'Model: y = {k:.2f}x + {b:.2f}')
            plt.scatter([x_input], [y_pred], c='g', s=100,
                        label='Prediction point')

            # 显示真实值对比（如果存在）
            if x_input in data:
                y_true = data[x_input]
                error = abs(y_pred - y_true)
                plt.plot([x_input, x_input], [y_pred, y_true], 'm--',
                         label=f'Loss ({error:.2f})')
                plt.scatter(x_input, y_true, c='b', s=100, marker='X',
                            label='True value')

            # 命令行输出
            print(f"预测值: {k:.2f} * {x_input} + {y_pred:.2f} = {y_pred:.2f}")
            if x_input in data:
                print(f"真实值: {data[x_input]:.2f} | 误差: {error:.2f}")

            plt.title(f'Result: {y_pred:.2f}')
            plt.xlim(fixed_xlim)
            plt.ylim(fixed_ylim)
            plt.legend()
            plt.show(block=True)
            plt.pause(0.1)


        except Exception as e:
            print(f"e:{str(e)}")