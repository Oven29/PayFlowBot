from aiogram import F


amount_filter = F.text.regexp(r'^(\d+(\.\d+)?|\d+(,\d+)?|(\.\d+)|(\,\d+))$')  # regexp filter for integer or float

number_filter = F.text.regexp(r'^[0-9]+$')

card_filter = F.text.regexp(r'^\d{1,16}$')
