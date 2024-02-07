import qrcode
import json
from smart_phone import smart_phone

class Manufacturer:
    def __init__(self, name, location, products=[]):
        self.name = name
        self.location = location
        self.products=[]

    def add_product(self, product):
        self.products.append(product)

    def __str__(self):
        return f"Manufacturer Name: {self.name}\n" \
               f"Location: {self.location}\n" \
               f"Products: {', '.join(self.products)}"


def generate_qr_for_phone(unicode):

    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,  # QR code version (adjust as needed)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
        box_size=10,  # Size of each box (adjust as needed)
        border=4,  # Border size (adjust as needed)
    )

    qr.add_data(unicode)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")

    qr_img.save(unicode+".png")

#main
manifacturer = Manufacturer('ItGrow','Tunis Nassr 0021 Moon space')

with open("c:\\Users\\MSI\\Desktop\\2022-2023\\PyBlockChain\\blockchain-python-tutorial\\Manifacturer_node\\phones_database.json", 'r') as json_file:
    data = json.load(json_file)

'''products = [
            smart_phone('OPPO33',manifacturer.name,'Xmodel',["6.5-inch display", "quad-core processor", "128GB storage","8GB RAM", "dual rear cameras", "4000mAh battery","ABCDEFG"],"A11"),
            smart_phone('RedmiNote10',manifacturer.name,'Alphpamodel',["6.5-inch display", "quad-core processor", "64GB storage","8GB RAM", "dual rear cameras", "4000mAh battery"],"B11"),
            smart_phone('Iphone14Pro',manifacturer.name,'Alphpamodel', ["10-inch display", "quad-core processor", "64GB storage","4GB RAM", "quad cameras", "4000mAh battery"],"C11")
           ]'''

def generate_qr_for_phone(unicode):

    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,  # QR code version (adjust as needed)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
        box_size=10,  # Size of each box (adjust as needed)
        border=4,  # Border size (adjust as needed)
    )

    qr.add_data(unicode)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save(unicode+".png")

for product in data:
    product_name = product['product_name']
    manufacturer = product['manufacturer']
    model = product['model']
    specifications = product['specifications']
    unique_identifier = product['unique_identifier']
    product = smart_phone(product_name,manufacturer,model,specifications,unique_identifier)
    manifacturer.add_product(product)
    generate_qr_for_phone(unique_identifier)
