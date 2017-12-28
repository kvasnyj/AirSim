# In settings.json first activate computer vision mode: 
# https://github.com/Microsoft/AirSim/blob/master/docs/image_apis.md#computer-vision-mode

from AirSimClient import *

client = CarClient()
client.confirmConnection()

client.simSetSegmentationObjectID("[\w]*", 0, True);
client.simSetSegmentationObjectID("ground[\w]*", 1, True);
client.simSetSegmentationObjectID("road[\w]*", 2, True);
client.simSetSegmentationObjectID("sky[\w]*", 3, True);
client.simSetSegmentationObjectID("car[\w]*", 4, True);
client.simSetSegmentationObjectID("sign[\w]*", 5, True);

#get segmentation image in various formats
responses = client.simGetImages([
    ImageRequest(1, AirSimImageType.Segmentation)]) 

#save segmentation images in various formats
for idx, response in enumerate(responses):
    filename = 'c:/temp/py_seg_' + str(idx)

    if response.pixels_as_float:
        AirSimClientBase.write_pfm(os.path.normpath(filename + '.pfm'), AirSimClientBase.getPfmArray(response))
    elif response.compress: #png format
        AirSimClientBase.write_file(os.path.normpath(filename + 'py-%d-%s.png' % (response.image_type, time.strftime('%Y%m%d-%H%M%S'))), response.image_data_uint8)
    else: #uncompressed array - numpy demo
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) #get numpy array
        img_rgba = img1d.reshape(response.height, response.width, 4) #reshape array to 4 channel image array H X W X 4
        img_rgba = np.flipud(img_rgba) #original image is fliped vertically
        AirSimClientBase.write_png(os.path.normpath(filename + '.numpy.png'), img_rgba) #write to png 

print("Done")