from PIL import Image, ImageDraw, ImageFilter, ImageEnhance


class ImageHandler:

    def __init__(self):
        self._initial_path = 'initial_user_images/initial.jpg'
        self._result_path = 'result_user_images/res.jpg'

    def get_black_white_img(self):
        image = Image.open(self._initial_path)
        draw = ImageDraw.Draw(image)
        for x in range(image.size[0]):  # This is image height
            for y in range(image.size[1]):  # This is image width
                r, g, b = image.getpixel((x, y))
                sr = (r + g + b) // 3  # Get average value of RGB
                draw.point((x, y), (sr, sr, sr))  # Point this pixel
        image.save(self._result_path)  # Save out image


def get_contrast_img(factor, base_img, res_img):
    im = Image.open(base_img)
    enhancer = ImageEnhance.Contrast(im)
    enhanced_im = enhancer.enhance(1.0 + factor)
    enhanced_im.save(res_img)
