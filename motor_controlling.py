import RPi.GPIO as gp

gp.setmode(gp.BCM)

mlc=[15,18]
mls=14

mrc=[16,20]
mrs=21
print(mlc)
gp.setup(mlc+[mls], gp.OUT)

gp.setup(mrc+[mrs], gp.OUT)

gp.output((mlc[0],mrc[0]),gp.HIGH)
gp.output((mlc[1],mrc[1]),gp.LOW)

pw1=gp.PWM(mls,50)
pw2=gp.PWM(mrs,50)

pw1.start(20)
pw2.start(20)

z=input()

pw1.stop()
pw2.stop()



