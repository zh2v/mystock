import threading

class myThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print("开始线程：" + self.name)
        if self.name == 'timn':
            myFunct.time_n()
        elif self.name == 'add':
            myFunct(3,4).add()
        print("退出线程：" + self.name)


class myFunct():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        print('self.x=', self.x)
        print('self.y=', self.y)

    def add(self):
        print(" X + Y =", self.x + self.y)
        # run_in_thread(self.name)

    def time_n():
        time_n = 5 * 6
        print(" X * Y =", time_n)
#         return time_n

t1=myThread('timn')
t1.start()

t2=myThread('add')
t2.start()