import os

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V2
import time

from data.plot import Plot
from presentation.observer import Observer

SCREEN_HEIGHT = epd2in13_V2.EPD_WIDTH  # 122
SCREEN_WIDTH = epd2in13_V2.EPD_HEIGHT  # 250

current_dir = os.path.dirname(__file__)
two_dirs_up = os.path.abspath(os.path.join(current_dir, '..', '..'))

FONT_SMALL = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), os.pardir, 'Roses.ttf'), 8)
FONT_LARGE = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), os.pardir, 'PixelSplitter-Bold.ttf'), 26)

class Epd2in13v2(Observer):

    def __init__(self, observable, mode):
        super().__init__(observable=observable)
        self.epd = epd2in13_V2.EPD()
        self.screen_image = self._init_display(self.epd)
        self.screen_draw = ImageDraw.Draw(self.screen_image)
        self.mode = mode

    def draw_loading(self, currency):
        img = Image.new('1', (SCREEN_WIDTH, SCREEN_HEIGHT), 255)
        d = ImageDraw.Draw(img)
        d.text((30,50), "Loadin %s..." % currency, outline=(50), font=FONT_LARGE)
        self.epd.displayPartial(self.epd.getbuffer(img.rotate(180)))

    @staticmethod
    def _init_display(epd):
        epd.init(epd.FULL_UPDATE)
        epd.Clear(0xFF)
        screen_image = Image.new('1', (SCREEN_WIDTH, SCREEN_HEIGHT), 255)
        epd.displayPartBaseImage(epd.getbuffer(screen_image))
        epd.init(epd.PART_UPDATE)
        return screen_image

    def form_image(self, prices, current_price, screen_draw, currency):
        screen_draw.rectangle((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), fill="#ffffff")
        screen_draw = self.screen_draw
        if self.mode == "candle":
            Plot.candle(prices, size=(SCREEN_WIDTH - 45, 93), position=(41, 0), draw=screen_draw)
        else:
            last_prices = [x[3] for x in prices]
            Plot.line(last_prices, size=(SCREEN_WIDTH - 42, 93), position=(42, 0), draw=screen_draw)

        flatten_prices = [item for sublist in prices for item in sublist]
        Plot.y_axis_labels(flatten_prices, FONT_SMALL, (0, 0), (38, 89), draw=screen_draw)
        screen_draw.line([(10, 98), (240, 98)])
        screen_draw.line([(39, 4), (39, 94)])
        screen_draw.line([(60, 102), (60, 119)])
        Plot.caption(current_price, 95, SCREEN_WIDTH, FONT_LARGE, screen_draw, currency)

    def update(self, data, current_data, currency):
        if(data == None or len(data) == 0):
          self.draw_loading(currency)
        else:
          self.form_image(data, current_data, self.screen_draw, currency)
          screen_image_rotated = self.screen_image.rotate(180)
          # TODO: add a way to switch bewen partial and full update
          # epd.presentation(epd.getbuffer(screen_image_rotated))
          self.epd.displayPartial(self.epd.getbuffer(screen_image_rotated))

    def showImage(self):
        img = Image.new('1', (SCREEN_WIDTH, SCREEN_HEIGHT), 255)
        image_path = os.path.join(two_dirs_up, 'qr_code.png')
        imagepng = Image.open(image_path)
        img.paste(imagepng, (70,2)) 
        self.epd.displayPartial(self.epd.getbuffer(img))
        time.sleep(10)

    @staticmethod
    def close():
        epd2in13_V2.epdconfig.module_exit()
