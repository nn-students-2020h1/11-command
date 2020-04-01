from PIL import Image, ImageDraw, ImageFilter, ImageEnhance


def get_black_white_img():
    """This function makes initial image into black and white image"""
    image = Image.open('initial_user_images/initial.jpg')
    draw = ImageDraw.Draw(image)
    for x in range(image.size[0]):  # This is image height
        for y in range(image.size[1]):  # This is image width
            r, g, b = image.getpixel((x, y))
            sr = (r+g+b)//3  # Get average value of RGB
            draw.point((x, y), (sr, sr, sr))  # Point this pixel
    image.save('result_user_images/res.jpg', "JPEG")  # Save out image


def get_contrast_img(factor, base_img, res_img):
    im = Image.open(base_img)
    enhancer = ImageEnhance.Contrast(im)
    enhanced_im = enhancer.enhance(1.0 + factor)
    enhanced_im.save(res_img)
