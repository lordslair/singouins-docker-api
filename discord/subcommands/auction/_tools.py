# -*- coding: utf8 -*-

import datetime


def auction_time_left(creation_date):
    from mongo.models.Auction import AuctionDocument

    # Access the underlying pymongo collection
    collection = AuctionDocument._get_collection()
    # Retrieve the index information
    index_info = collection.index_information()

    # Find and return the expireAfterSeconds value
    for index in index_info.values():
        if 'expireAfterSeconds' in index:
            expiration = index['expireAfterSeconds']
            # Convert to dt object
            expiration_duration = datetime.timedelta(seconds=expiration)

    expiration_time = creation_date + expiration_duration
    remaining_time = expiration_time - datetime.datetime.utcnow()
    # Extract hours, minutes, and seconds from timedelta
    remaining_h = remaining_time.days * 24 + remaining_time.seconds // 3600
    remaining_m = (remaining_time.seconds % 3600) // 60
    remaining_s = remaining_time.seconds % 60

    return f"{remaining_h}:{remaining_m}:{remaining_s}"
