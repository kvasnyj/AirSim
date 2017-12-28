from AirSimClient import *
import time

# connect to the AirSim simulator
client = CarClient()
client.confirmConnection()
client.enableApiControl(True)
car_controls = CarControls()

Kp = 0.03
Ki = 0
Kd = 0 #3.5
prev_cte = 0
int_cte = 0
frame = 0
err = 0

def UpdateError(cte):
    global prev_cte, int_cte, err
    diff_cte = cte - prev_cte
    prev_cte = cte
    int_cte += cte
    err += (1 + abs(cte)) * (1 + abs(cte))

    steer = -Kp * cte - Kd * diff_cte - Ki * int_cte
    if steer > 0.6: steer = 0.6
    if steer < -0.6: steer = -0.6

    print(cte, steer, err)

    return steer


def TotalError():
    return err / frame

while True:
    # get state of the car
    car_state = client.getCarState()
    car_kin = car_state.kinematics_true
    print("Speed %d, Gear %d" % (car_state.speed, car_state.gear))

    beta = 3
    z = 0
    pts = [np.array([0, -1, z]), np.array([130, -1, z]), np.array([130, 125, z]), np.array([0, 125, z]), np.array([0, -1, z]), np.array([130, -1, z]), np.array([130, -128, z]), np.array([0, -128, z]), np.array([0, -1, z])]
    pd = car_kin.position
    car_pt = np.array([pd.x_val, pd.y_val, pd.z_val])

    dist = 10000000
    for i in range(0, len(pts)-1):
        dist = min(dist, np.linalg.norm(np.cross((car_pt - pts[i]), (car_pt - pts[i+1])))/np.linalg.norm(pts[i]-pts[i+1]))

    cte = dist 

    # set the controls for car
    car_controls.throttle = 1
    car_controls.steering = UpdateError(cte)
    client.setCarControls(car_controls)

    # let car drive a bit
    time.sleep(1)

    # get camera images from the car
    responses = client.simGetImages([
        ImageRequest(0, AirSimImageType.Scene),
        ImageRequest(1, AirSimImageType.DepthPerspective),
        ImageRequest(2, AirSimImageType.Segmentation)
        ])

    #print('Retrieved images: %d' % len(responses))

    for response in responses:
        if response.pixels_as_float:
            #print("Type %d, size %d" % (response.image_type, len(response.image_data_float)))
            CarClient.write_pfm(os.path.normpath('c:/temp/airsim/py-%d-%s.pfm' % (response.image_type, time.strftime("%Y%m%d-%H%M%S"))), CarClient.getPfmArray(response))
        else:
            #print("Type %d, size %d" % (response.image_type, len(response.image_data_uint8)))
            CarClient.write_file(os.path.normpath("c:/temp/airsim/py-%d-%s.png" % (response.image_type, time.strftime("%Y%m%d-%H%M%S"))), response.image_data_uint8)
