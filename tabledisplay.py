#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import ast
import re
import sys
import pathlib

dataset = pathlib.Path('./dataset.txt')
data = ast.literal_eval(dataset.read_text())
temp={}
for k, v in data.items():
    temp[float(k)] = float(v)
data = temp.copy()

x = np.array(list(data.keys()))
y = np.array(list(data.values()))

#hotfix:直接随机参数得了  懒得写底值筛选
k = np.random.randn()
b = np.random.randn()
learning_rate = 0.01
try:
    rounds=sys.argv[1]
except:
    rounds=1000


#控制坐标轴 免得坐标乱飞
x_min, x_max = x.min(), x.max()
y_min, y_max = y.min(), y.max()
x_margin = (x_max - x_min) * 0.2  
y_margin = (y_max - y_min) * 0.2
fixed_xlim = (x_min - x_margin, x_max + x_margin)
fixed_ylim = (y_min - y_margin, y_max + y_margin)

k_history = []
b_history = []
loss_history = []
plt.ion()
fig = plt.figure(figsize=(10, 5))
ax = fig.add_subplot(111)
for round in range(rounds):
    y_pred = k * x + b
    loss = ((y_pred - y)**2).mean()
    
    # 计算梯度
    dk = 2 * np.mean((y_pred - y) * x)
    db = 2 * np.mean(y_pred - y)
    
    # 更新参数
    k -= learning_rate * dk
    b -= learning_rate * db
    
    if round % 10 == 0: #hotfix:减轻可视化压力
        ax.clear()
        ax.set_xlim(fixed_xlim)
        ax.set_ylim(fixed_ylim)
        ax.scatter(x, y, label='True Value')
        ax.plot(x, k*x + b, 'r-', label=f'Prediction (k={k:.2f}, b={b:.2f})')
        ax.set_title(f'Training Round: {round+10}/{rounds} {int((round+10)/rounds*100)}% Loss: {loss:.4f}')
        ax.legend()
        plt.pause(0.1)
    k_history.append(k)
    b_history.append(b)
    loss_history.append(loss)

plt.ioff()
plt.show()

plt.figure(figsize=(12,5))
plt.subplot(121)
plt.plot(k_history, label='k')
plt.plot(b_history, label='b')
plt.title("Arguments")
plt.legend()

plt.subplot(122)
plt.plot(loss_history)
plt.title("Loss")
plt.show()

# 交互预测系统
plt.figure(figsize=(10, 5))
while True:
    try:
        input_x = input("输入x值预测或 k=?/b=?改参数，exit退出: ").strip()
        
        if input_x.lower() == 'exit': #特判exit防止下面数字处理出错
            break
            
        # 参数修改功能
        if re.match(r'^[kb]=', input_x):
            parts = input_x.split('=')
            if len(parts) != 2:
                raise ValueError
            new_val = float(parts[1])
            
            if input_x.startswith('k='):
                k = new_val
                print(f"权重k=: {k:.4f}")
            elif input_x.startswith('b='):
                b = new_val
                print(f"偏值b=: {b:.4f}")
            continue
            
        x_testarg = float(input_x)
        y_testarg = k * x_testarg + b
        
        plt.clf()
        plt.scatter(x, y, label='True Value')
        plt.plot(x, k*x + b, 'r-', label=f'This Model: y={k:.2f}x+{b:.2f}')
        
        #连线 方便展示差值
        plt.scatter([x_testarg], [y_testarg], c='g', s=100, label='Prediction point')
        
        if x_testarg in data: #刷题刷到了同款 但还是得预测
            y_true = data[x_testarg]
            error = abs(y_testarg - y_true)
            plt.plot([x_testarg, x_testarg], [y_testarg, y_true], 'm--', 
                    label=f'loss ({error:.2f})')
            plt.scatter(x_testarg, y_true, c='b', s=100, marker='X', 
                       label='True Value')
            
        plt.title(f'result: y = {y_testarg:.2f}')
        plt.legend()
        plt.show(block=False)
        plt.pause(0.1)
        
        print(f"预测: {k:.2f}*{x_testarg} + {b:.2f} = {y_testarg:.2f}")
        if x_testarg in data:
            print(f"实际: {data[x_testarg]:.2f} | 误差: {error:.2f}")
            
    except Exception as e:
        print(str(e))

