'''
# Original Code Given

class House:
    def __init__(self, ssn, name, email, address):
        self.ssn = ssn
        self.name = name
        self.email = email
        self.address = address

    def __str__(self):
        return f"House(id={self.ssn}, name={self.name}, email={self.email}, address={self.address})"
'''

class Tenant:
    def __init__(self, ssn, name, email, unit_number):
        self.ssn = ssn
        self.name = name
        self.email = email
        self.unit_number = unit_number

    def __str__(self):
        return f"Tenant(ssn={self.ssn}, name={self.name}, email={self.email}, unit={self.unit_number})"

class Apartment:
    def __init__(self, building_number, address, units):
        self.building_number = building_number
        self.address = address
        self.units = list(units) # available units
        self.tenants = []  # lists the tenants

    def __str__(self):
        return (
            f"Apartment(building={self.building_number}, "
            f"address={self.address}, "
            f"units={self.units}, "
            f"tenants={len(self.tenants)})"
        )
    
