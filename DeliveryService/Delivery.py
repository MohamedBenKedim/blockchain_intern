class Delivery:
    def __init__(self, name, location):
        self.name = name
        self.location = location

    def add_product(self, product):
        self.products.append(product)

    def __str__(self):
        return f"Manufacturer Name: {self.name}\n" \
               f"Location: {self.location}\n" \
               
#main
DeliveryService = Delivery('FEDX-Delivery','Tunis Nassr 0021 Moon space')