# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import rgbmatrix
import time
import os
import board
import displayio
import framebufferio
import adafruit_mpu6050

# connect to motion sensor
i2c = board.I2C()
mpu = adafruit_mpu6050.MPU6050(i2c)

SPRITESHEET_FOLDER = "/bmps"
DEFAULT_FRAME_DURATION = 0.1  # 100ms
AUTO_ADVANCE_LOOPS = 3
FRAME_DURATION_OVERRIDES = {
    "three_rings1-sheet.bmp": 0.15,
    "hop1-sheet.bmp": 0.05,
    "firework1-sheet.bmp": 0.03,
}

# --- Display setup ---

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width=64, bit_depth=4,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh = True)
sprite_group = displayio.Group()
display.root_group = sprite_group

auto_advance = True

file_list = sorted(
    [
        f
        for f in os.listdir(SPRITESHEET_FOLDER)
        if (f.endswith(".bmp") and not f.startswith("."))
    ]
)

if len(file_list) == 0:
    raise RuntimeError("No images found")
else:
    print(file_list)

current_image = None
current_frame = 0
current_loop = 0
frame_count = 0
frame_duration = DEFAULT_FRAME_DURATION


def load_image():
    """
    Load an image as a sprite
    """
    # pylint: disable=global-statement
    global current_frame, current_loop, frame_count, frame_duration
    while sprite_group:
        sprite_group.pop()

    filename = SPRITESHEET_FOLDER + "/" + file_list[current_image]

 # CircuitPython 7+ compatible
    bitmap = displayio.OnDiskBitmap(filename)
    sprite = displayio.TileGrid(bitmap,
        pixel_shader=bitmap.pixel_shader,
        tile_width=bitmap.width,
        tile_height=32,
    )

    sprite_group.append(sprite)

    current_frame = 0
    current_loop = 0
    frame_count = int(bitmap.height / 32)
    frame_duration = DEFAULT_FRAME_DURATION
    if file_list[current_image] in FRAME_DURATION_OVERRIDES:
        frame_duration = FRAME_DURATION_OVERRIDES[file_list[current_image]]


def advance_image():
    """
    Advance to the next image in the list and loop back at the end
    """
    # pylint: disable=global-statement
    global current_image
    if current_image is not None:
        current_image += 1
    if current_image is None or current_image >= len(file_list):
        current_image = 0
    load_image()


def advance_frame():
    """
    Advance to the next frame and loop back at the end
    """
    # pylint: disable=global-statement
    global current_frame, current_loop
    current_frame = current_frame + 1
    if current_frame >= frame_count:
        current_frame = 0
        current_loop = current_loop + 1
    sprite_group[0][0] = current_frame

# LOADING IMAGES
'''
0 = thank you
1 = walking person
2 = tipsy
'''

def load_list_image(item):
    """Load the list item"""
    global current_image
    current_image = item
    load_image()

def play_walking():
    """Load the .bmp image"""
    load_list_image(1)
    while current_loop <= AUTO_ADVANCE_LOOPS:
        advance_frame()
        time.sleep(frame_duration)

def play_thankyou():
    """load the thank you image"""
    load_list_image(0)
    while current_loop <= AUTO_ADVANCE_LOOPS:
        advance_frame()
        time.sleep(frame_duration)

def load_tipsy():
    load_list_image(2)
    while current_loop <= AUTO_ADVANCE_LOOPS:
        advance_frame()
        time.sleep(frame_duration)

advance_image()

while True:
    play_walking()
    '''
    if auto_advance and current_loop >= AUTO_ADVANCE_LOOPS:
        advance_image()

    #advance_image()
    advance_frame()
    time.sleep(frame_duration)

    #print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (mpu.acceleration))
    #print("Gyro X:%.2f, Y: %.2f, Z: %.2f rad/s" % (mpu.gyro))
    #print("Temperature: %.2f C" % mpu.temperature)
    #print("")
    #time.sleep(5)
    #time.sleep(1)
    '''
