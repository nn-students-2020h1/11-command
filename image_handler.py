from PIL import Image, ImageDraw, ImageFilter


def get_black_white_img():
    """This function makes initial image into black and white image"""
    image = Image.open('initial.jpg')
    draw = ImageDraw.Draw(image)
    for x in range(image.size[0]):  # This is image height
        for y in range(image.size[1]):  # This is image width
            r, g, b = image.getpixel((x, y))
            sr = (r+g+b)//3  # Get average value of RGB
            draw.point((x, y), (sr, sr, sr))  # Point this pixel
    image.save('res.jpg', "JPEG")  # Save out image
