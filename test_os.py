import os

mod = 10

os.mkdir("data")
for i in range(mod):
    os.mkdir(f"data/{i}")