PAYMENTS = (
    ('MPESA', 'MPESA', ),
    ('CARD', 'Visa/Mastercard Card',),
)

MEDICATION_TYPE = (
    ('OTC', 'Over the Counter '),
    ('PO', 'Pharmacy Only',),
    ('P', 'Prescription', ),
)

STATUSES = (('Received', 'Received'), ('Packaged', 'Packaged'), ('On Transit', 'On Transit'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'))

USER_TYPES = (('customer', 'customer'), ('rider', 'rider'), ('pharmacist', 'pharmacist'))
CUSTOMER = 'customer'
PHARMACIST = 'pharmacist'
RIDER = 'rider'
