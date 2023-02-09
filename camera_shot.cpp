#include <iostream>
#include <EDSDK.h>

int main() {
  EdsError err = EDS_ERR_OK;

  // Initialize the SDK
  err = EdsInitializeSDK();
  if (err != EDS_ERR_OK) {
    std::cerr << "Error initializing SDK: 0x" << std::hex << err << std::endl;
    return 1;
  }

  // Get the first camera
  EdsCameraListRef cameraList = NULL;
  err = EdsGetCameraList(&cameraList);
  if (err != EDS_ERR_OK) {
    std::cerr << "Error getting camera list: 0x" << std::hex << err << std::endl;
    return 1;
  }
  EdsUInt32 count;
  err = EdsGetChildCount(cameraList, &count);
  if (err != EDS_ERR_OK) {
    std::cerr << "Error getting child count: 0x" << std::hex << err << std::endl;
    return 1;
  }
  if (count == 0) {
    std::cerr << "No cameras found" << std::endl;
    return 1;
  }
  EdsCameraRef camera = NULL;
  err = EdsGetChildAtIndex(cameraList, 0, &camera);
  if (err != EDS_ERR_OK) {
    std::cerr << "Error getting camera at index 0: 0x" << std::hex << err << std::endl;
    return 1;
  }

  // Open the camera
  err = EdsOpenSession(camera);
  if (err != EDS_ERR_OK) {
    std::cerr << "Error opening session: 0x" << std::hex << err << std::endl;
    return 1;
  }

  // Take a photo
  err = EdsSendCommand(camera, kEdsCameraCommand_TakePicture, 0);
  if (err != EDS_ERR_OK) {
    std::cerr << "Error taking picture: 0x" << std::hex << err << std::endl;
    return 1;
  }

  // Close the camera
  err = EdsCloseSession(camera);
  if (err != EDS_ERR_OK) {
    std::cerr << "Error closing session: 0x" << std::hex << err << std::endl;
    return 1;
  }

  // Terminate the SDK
  err = EdsTerminateSDK();
  if (err != EDS_ERR_OK) {
    std::cerr << "Error terminating SDK: 0x" << std::hex << err << std::endl;
    return 1;
  }

  return 0;
}
