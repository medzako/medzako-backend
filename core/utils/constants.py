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

BUSINESS_PERMIT = 'business_permit'
ANNUAL_PRACTICE_LICENSE = 'annual_practice_license'
PREMISES_REGISTRATION_LICENSE = 'premises_registration_license'

PHARMACY_LICENSES = ((BUSINESS_PERMIT, BUSINESS_PERMIT),
 (ANNUAL_PRACTICE_LICENSE, ANNUAL_PRACTICE_LICENSE), 
 (PREMISES_REGISTRATION_LICENSE, PREMISES_REGISTRATION_LICENSE))

DRIVING_LICENSE = "driving_license"
ID_FRONT = "id_front"
ID_BACK = "id_back"

RIDER_LICENSES = (
    (DRIVING_LICENSE, DRIVING_LICENSE),
    (ID_FRONT, ID_FRONT),
    (ID_BACK, ID_BACK)
)

