signs = (
    ('aries', 'Овен'), 
    ('taurus', 'Телец'), 
    ('gemini', 'Близнецы'),
    ('cancer', 'Рак'),
    ('leo', 'Лев'),
    ('virgo', 'Дева'),
    ('libra', 'Весы'),
    ('scorpio', 'Скорпион'),
    ('sagittarius', 'Стрелец'), 
    ('capricorn', 'Козерог'), 
    ('aquarius', 'Водолей'),  
    ('pisces', 'Рыбы')
    )
signs_en = ('aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces')
signs_ru = ('Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева', 'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы')

zodiac_en_to_ru = dict(signs)
zodiac_ru_to_en = dict(zip(map(lambda x: x[1], signs), map(lambda x: x[0], signs)))