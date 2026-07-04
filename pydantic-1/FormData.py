class FormData():
    def __init__(self, name, email, message,pincode:int, city:str="Mumbai"):
        self.name:str = name
        self.email:str = email
        self.message:str = message
        self.pincode:int=pincode
        self.city:str = city


form1=FormData("John Doe", "john.doe@example.com", "Hello, this is a test message.", 1234, "Delhi")
print(form1.name)  # Output: John Doe
print(form1.pincode)  # Output: 1234
print(form1.city)  # Output: Delhi