# Multisite Photometry Image Processing Application
## Description
This application takes raw image files produced by the Multisite Photometry System and processes those images into 1-dimensional traces representing flourescence signal. This application is capable of processing up to 5 seperate recording regions, as well as a "correction" signal fiber that is submerged in a flourophore solution. Additionally, this application can process an unlimited number of interpolated "channels", each with a different excitation wavelength, this enables use of isosbestic correction or even the use of multiple flourphores (provided they possess distinct flourescence excitation frequencies) in the same fiber/brain region.

This application also allows for performance of signal regression steps to produce deltaF/F or z-score traces, as well as alignment with behavioral data/events.

Specifications and guides to the hardware are provided in **docs**, and a basic script for arduino for camera and laser control is provided in **hardwarecontrol**.

## Deployment
This code can be run either using the provided conda enviroment or using the executable release (generated with pyinstaller). You may generate your own executable using the pyinstaller command below.
```
pyinstaller start.spec
```
It is NOT recommended to run the MSPhotom application from within a jupyter notebook or Spyder, as asynchronous image loading will be disabled to prevent conflict with the jupyter/spyder eventloop
