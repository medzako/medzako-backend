PAYMENTS = (
    ('MPESA', 'MPESA', ),
    ('CARD', 'Visa/Mastercard Card',),
)

MEDICATION_TYPE = (
    ('OTC', 'Over the Counter '),
    ('PO', 'Pharmacy Only',),
    ('P', 'Prescription', ),
)

RECEIVED = 'received'
ACCEPTED = 'accepted'
DISPATCHED = 'dispatched'
DELIVERED = 'delivered'
CANCELED = 'canceled'
REJECTED = 'rejected'

STATUSES = ((RECEIVED, RECEIVED), (ACCEPTED, ACCEPTED), (DISPATCHED, DISPATCHED), (DELIVERED, DELIVERED), (CANCELED, CANCELED), (REJECTED, REJECTED),)

USER_TYPES = (('customer', 'customer'), ('rider', 'rider'), ('pharmacist', 'pharmacist'))
CUSTOMER = 'customer'
PHARMACIST = 'pharmacist'
RIDER = 'rider'
