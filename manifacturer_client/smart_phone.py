class smart_phone:
    def __init__(self, product_name, manufacturer, model, specifications,unique_identifier):
        self.product_name = product_name
        self.manufacturer = manufacturer
        self.model = model
        self.specifications = specifications
        self.unique_identifier = unique_identifier
        
    
    def __str__(self):
        return f"Product Name: {self.product_name}\n" \
            f"Manufacturer: {self.manufacturer}\n" \
            f"Model: {self.model}\n" \
            f"Specifications: {', '.join(self.specifications)}\n" \
            f"Unique Identifier: {self.unique_identifier}"    