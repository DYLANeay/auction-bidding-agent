"""The part that plays: brain, airbag, dashboard, phone line (think: a car)

config.py               the settings, in their factory position

strategy/               the brain, one file per step
    values.py           how much an auction is worth
    market.py           how much a point costs right now
    planning.py         how much to keep at the bank and how much to spend
    bidding.py          which auctions to bid on, and how much
    brain.py            the buyer who uses all of the above each round

safety/                 the airbag, around the brain
    conversion.py       turns any value into a safe number
    game_round.py       one round whose data has all been checked
    incoming.py         reads the server message, keeps what makes sense
    outgoing.py         cleans the bids before they leave
    airbag.py           keeps the agent alive whatever happens
"""
