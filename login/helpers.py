"""Helpers for login functions."""

def fill_models_from_sso(user_profile, user, profile_json):
    """Fill models from SSO data."""

    # Fill in data into the profile from SSO
    for response_key, data_key in {
            'first_name': 'name',
            'email': 'email',
            'mobile': 'contact_no',
            'roll_number': 'roll_no',
            'username': 'ldap_id'}.items():

        if response_key in profile_json and profile_json[response_key] is not None:
            setattr(user_profile, data_key, profile_json[response_key])

    # Fill in some special parameters
    if 'first_name' in profile_json and 'last_name' in profile_json:
        if profile_json['first_name'] is not None and profile_json['last_name'] is not None:
            user_profile.name = profile_json['first_name'] + ' ' + profile_json['last_name']
            user.first_name = profile_json['first_name']
            user.last_name = profile_json['last_name']

    if 'email' in profile_json:
        if profile_json['email'] is not None:
            user.email = profile_json['email']

    if 'contacts' in profile_json and profile_json['contacts']:
        user_profile.contact_no = profile_json['contacts'][0]['number']

    if 'profile_picture' in profile_json:
        if profile_json['profile_picture'] is not None:
            user_profile.profile_pic = 'https://gymkhana.iitb.ac.in' + profile_json['profile_picture']

    # Fill in program details
    if 'program' in profile_json:
        for field in [
            'join_year',
            'department',
            'department_name',
            'degree',
            'degree_name',
            'graduation_year']:

            if profile_json['program'][field] is not None:
                setattr(user_profile, field, profile_json['program'][field])
                                
    if 'insti_address' in profile_json:
        if profile_json['insti_address']['room'] is not None and profile_json['insti_address']['hostel'] is not None:
            user_profile.hostel = profile_json['insti_address']['hostel']
            user_profile.room = (profile_json['insti_address']['room'])



    # Save the profile
    user.save()
    user_profile.save()
