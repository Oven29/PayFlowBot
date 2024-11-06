from aiogram import F


amount_filter = F.regexp(r'^([0-9]+|[0-9]+\.[0-9]+)$')  # regexp filter for integer or float

card_filter = F.regexp(r'^\d{1,16}$')
