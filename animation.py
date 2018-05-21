import matplotlib.pyplot as plt
import matplotlib.animation as anim

fig = plt.figure()
ax1 = plt.subplot(111)



def animFunc(x):
    file = open('C:\\Users\\HP\\Desktop\\data2.txt', 'r').read()
    lines= file.split('\n')
    xs = []
    ys = []
    for line in lines:
        if len(line) > 1:
            x, y = line.split(',')
            xs.append(int(x))
            ys.append(int(y))
    ax1.clear()
    ax1.plot(xs, ys)

func = anim.FuncAnimation(fig, animFunc, interval=1000)
plt.show()




    
        
    
