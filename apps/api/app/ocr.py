from PIL import Image
import pytesseract
import difflib
import cv2
import numpy as np

class ocr_o:
    def __init__(self, im):
        self.__image = im
        self.__gray_im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        self._text = ""

    def prepare_im(self):
        self.__gray_im = cv2.medianBlur(self.__gray_im, 3)
        #equ = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        #self.__gray_im = equ.apply(self.__gray_im)
        self._text = pytesseract.image_to_string(Image.fromarray(self.__gray_im))
        #print(self._text)
        #cv2.imwrite("new.jpg", self.__gray_im)

    def get_back_cover_info(self):
        date = self._text.split("\n")[0].split(" ")[3].replace("_", "")
        return date

    def contains_num(self, s):
        return any(i.isdigit() for i in s)

    def get_cover_info(self):
        self._text = self._text.split("\n")
        cc = 0

        for i in self._text:
            index = self._text.index(i)
            self._text[index] = ''.join(j for j in i if 48 <= ord(j) <= 90 or ord(j) == 32)
            if self.contains_num(self._text[index]):
                self._text[index] = self._text[index].strip()
            #i = i.replace(".", "").replace(",", "")
            if self._text[index].isdigit():
                cc = self._text[index]
        #print(self._text)
        #found_w = difflib.get_close_matches('1234567890', self._text)
        #index = self._text.index(found_w[0])
        index = self._text.index(cc)
        name = self._text[index + 2]
        last_name = self._text[index + 1]
        name = ''.join(i for i in name if 65 <= ord(i) <= 90 or ord(i) == 32)
        last_name = ''.join(i for i in last_name if 65 <= ord(i) <= 90 or ord(i) == 32)
        height, width, channels = self.__image.shape
        crop_img = self.__image[int(height * 0.3):int(height * 0.8), int(width * 0.63):width]
        return cc, name, last_name, crop_img
