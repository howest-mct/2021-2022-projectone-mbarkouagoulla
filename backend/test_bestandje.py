from datetime import datetime
# from helpers.klasse_servo import SERVO
# import time
# servo = SERVO(5)

# while True:
#     servo.open_deur()
#     print('open')
#     time.sleep(1)
#     servo.sluit_deur()
#     print('sluit')
#     time.sleep(1)

now = datetime.now()
correct_format_date = now.strftime("%d/%m/%Y %H:%M:%S")
print(correct_format_date)
