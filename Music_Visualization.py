'''
Arcaea Music Visualizer
Product by Zaid_J
'''
import subprocess
import numpy as np
import os

from scipy.io import wavfile
from scipy.fftpack import fft

# 初始化
buffer = np.arange(0,16)
sound_chunk_idx = 0
chunk_size = 1470

# 更新函数，每一帧调用一次
def update():
    ydata = buffer
    ydata = ydata/4000
    data = []
    for i in ydata:
        i=int(i)
        if i>300:
            i=300
        data.append(i)
    return data

# 音频流回调函数
def callback():
    global sound_chunk_idx

    # 曲子播放完毕返回False
    if (music_data[chunk_size*sound_chunk_idx:chunk_size*(sound_chunk_idx+1), 0].size < chunk_size):
        return False
    
    outdata = music_data[chunk_size*sound_chunk_idx:chunk_size*(sound_chunk_idx+1), :]
    sound_chunk_idx += 1
    buffer[:] = np.abs(fft(outdata[0:1024,0]))[:128:8]
    return True

# arcaea生成波频图
def draw(x,time_start,time_end,data):
    old_h=0
    time=time_start
    with open("./output/"+filename+".aff","a") as file:
        file.writelines("timinggroup(){\n")
        file.writelines("  timing(0,100.00,4.00);\n")
        file.writelines("  timing({},999999.00,4.00);\n".format(time_start+1))
        file.writelines("  timing({},100.00,4.00);\n".format(time_start+2))
        for i in data[int(time_start/100):]:
            h=i
            d_h=old_h-h
            bpm=d_h/(300/(2*100))
            time+=100
            if -0.01<bpm<0:
                bpm=-0.01
            elif 0.00<=bpm<0.01:
                bpm=0.01
            file.writelines("  timing({},{:.2f},4.00);\n".format(time,bpm))
            old_h=h
        file.writelines("  timing({},-100.00,4.00);\n".format(time_end+1))
        file.writelines("  scenecontrol({},hidegroup,0.00,1);\n".format(time_end+x))
        if x < 8:
            for i in range(0,6):
                start = 0.48 - 6*0.03*(7-x)
                file.writelines("  arc({},{},{:.2f},{:.2f},s,4.00,4.00,0,none,true);\n".format(time_end+1,time_end+501,start-i*0.03,start-i*0.03))
        else :
            for i in range(0,6):
                start = 0.52 + 6*0.03*(x-8)
                file.writelines("  arc({},{},{:.2f},{:.2f},s,4.00,4.00,0,none,true);\n".format(time_end+1,time_end+501,start+i*0.03,start+i*0.03))
        file.writelines("};\n")

if __name__ == '__main__':

    # 用于存储波频图
    all_data=[]
    for i in range(16):
        all_data.append([])
    
    filename = str(input("输入音频文件名(包括后缀): "))
    if subprocess.call(['ffmpeg','-i',"./input/"+filename,'./input/running.wav']) == 1:
        print("输入文件不存在或不是音频文件!")
        os.remove("./input/running.wav")
        exit(0)
    sr, music_data = wavfile.read('./input/running.wav')
    time_start = int(input("输入开始时间(ms): "))
    time_end = int(input("输入结束时间(ms): "))

    # 存储波频图
    while callback() and sound_chunk_idx*100/3 <= time_end:
        if sound_chunk_idx%3 == 0:#1秒30帧，此处除以3表示在arcaea中一秒10帧
            data=update()
            for i in range(0,16):
                all_data[i].append(data[i])
    
    # 绘画波频图
    file = open("./output/"+filename+".aff",'w').close()
    for i in range(0,16):
        draw(i,time_start,time_end,all_data[i])
    
    os.remove("./input/running.wav")