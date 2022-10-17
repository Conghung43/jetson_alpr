There are 5 parts:

1. ALPR
-Training AI model
-Build up AI main program with clean code.
-Archieve 24~25 FPS. Target is 35~40 FPS.

2. GPS module
-NEO GPS using ARDUINO because this module can not directly connect with JETSON NANO (can not found any library)
-Query in formation from ARDUINO: latitude, longtitude, speed

3. ZED camera. 
-Directly use ZED because it available now (no need to buy==> Decrease R&D cost). Potential camera will be listed bellow
-Tested with JETSON NANO and it consume less resoure with depth mode = NONE


4. Program optimize.
-Thread vs Queue tested (save temp image in memory, drive)

5. SQL
-read write to sqlite3

6. File management.
-Ken design






Next step:
Current: 20 FPS after training 
setup ARDUINO and communicate with python program via USB: GPS device not work
