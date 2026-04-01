from datetime import datetime, timedelta

def check_eligibility(donor):
    return is_donor_eligible(donor)

def is_donor_eligible(donor):
    """
    Check if a donor is eligible to donate blood based on several criteria.
    - Age must be at least 18.
    - Weight must be at least 50 kg.
    - At least 90 days must have passed since the last donation.
    """
    if donor.age is None or donor.weight is None:
        return False, "Profile incomplete. Please update your age and weight in the profile section."

    if donor.age < 18:
        return False, "Donor must be at least 18 years old."
    
    if donor.weight < 50:
        return False, "Donor must weigh at least 50 kg."
    
    if donor.last_donation_date:
        days_since_last = (datetime.utcnow() - donor.last_donation_date).days
        if days_since_last < 90:
            remaining_days = 90 - days_since_last
            return False, f"At least 90 days must pass since last donation. Please wait {remaining_days} more days."
            
    return True, "Donor is eligible."
