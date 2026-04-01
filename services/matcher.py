def get_compatible_donors(recipient_blood_group):
    """
    Returns a list of blood groups that can donate to the given recipient blood group.
    """
    rules = {
        'O-': ['O-'],
        'O+': ['O-', 'O+'],
        'A-': ['O-', 'A-'],
        'A+': ['O-', 'O+', 'A-', 'A+'],
        'B-': ['O-', 'B-'],
        'B+': ['O-', 'O+', 'B-', 'B+'],
        'AB-': ['O-', 'A-', 'B-', 'AB-'],
        'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']
    }
    return rules.get(recipient_blood_group, [])

def can_donate_to(donor_blood_group, recipient_blood_group):
    """
    Checks if a donor's blood group can be donated to a recipient's blood group.
    """
    compatible_types = get_compatible_donors(recipient_blood_group)
    return donor_blood_group in compatible_types
