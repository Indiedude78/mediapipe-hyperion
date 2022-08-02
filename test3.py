import time
import magichue
import creds

user = creds.user
password = creds.password

api = magichue.RemoteAPI.login_with_user_password(user=user, password=password)
local_devices = api.get_online_bulbs()

# loop over all the bulbs
for i, bulb in enumerate(local_devices):
    i = i + 1
    # if they are off, turn them on
    if bulb.on == False:
        bulb.on = True
        print("Bulb " + str(i) + " turned on")
        time.sleep(2)
    else:
        bulb.on = False
        print("Bulb " + str(i) + " turned off")
        time.sleep(2)

# if bulb 1 is on, set the brightness to 50
if local_devices[0].on == True:
    local_devices[0].brightness = 50
    print("Bulb 1 brightness set to 50")
    time.sleep(2)
