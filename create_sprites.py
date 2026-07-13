import os
from PIL import Image

player = [
    "     **     ",
    "  ********  ",
    "************",
    "************"
]

red = [
    "  ****  ",
    "* **** *",
    "** ** **",
    " ****** ",
    "*  **  *",
    " *    * "
]

yellow = [
    " *    * ",
    "  *  *  ",
    "********",
    "** ** **",
    " **  ** ",
    " *    * "
]

green = [
    "  ****  ",
    "** ** **",
    " ****** ",
    "  *  *  ",
    " **  ** ",
    "   **   "
]

extra = [
    "  ****  ",
    " ****** ",
    "********",
    "  *  *  "
]


sprites = {
    "images/player": {"data": player, "colors": {' ': (0, 0, 0, 0), '*': (0, 0, 255, 255)}},
    "images/red": {"data": red, "colors": {' ': (0, 0, 0, 0), '*': (255, 0, 0 ,255)}},
    "images/yellow": {"data": yellow, "colors": {' ': (0, 0, 0, 0), '*': (255, 255, 0, 255)}},
    "images/green": {"data": green, "colors": {' ': (0, 0, 0, 0), '*': (0, 255, 0, 255)}},
    "images/extra": {"data": extra, "colors": {' ': (0, 0, 0, 0), '*': (0, 255, 255, 255)}}
}

os.makedirs('images', exist_ok=True)

for name, sprite in sprites.items():
    sprite_data = sprite["data"]
    color_map = sprite["colors"]
    
    height = len(sprite_data)
    width = len(sprite_data[0])
    
    pixel_data = []
    for row in sprite_data:
        for char in row:
            pixel_data.append(color_map.get(char, (0, 0, 0, 0)))

    img = Image.new('RGBA', (width, height))
    img.putdata(pixel_data)
    
    img_resized = img.resize((width * 8, height * 8), Image.Resampling.NEAREST)
    img_resized.save(f'{name}.png')
    print(f"Saved {name}.png ({width*8}x{height*8})")