# Towards Visualization of Time-Series Ecological Momentary Assessment (EMA) Data on Standalone Voice-First Virtual Assistants
Yichen Han, Christopher Bo Han, Chen Chen, Peng Wei Lee, Michael Hogarth, Alison A. Moore, Nadir Weibel, Emilia Farcas

![A user's past sleep quality presented on an Amazon Echo Show](documentation/sleepquality.jpg)

This work is a part of [VOLI Project](http://voli.ucsd.edu/) at UC San Diego [Human-Centered Extented Intelligence Lab](https://hxi.ucsd.edu/). You may read the full [Paper]() and watch the [Video Presentation](https://drive.google.com/file/d/1VW-CC7GzLiob--P1NYOe89nwbE7B3i1s/view?usp=sharing).


## Motivation

## System Design

## Quick Start
You may deploy the system in a simplified way with only Alexa Skill and AWS Lambda, or make a full deployment with AWS EC2 server as well.

## Prerequisites
+ An Amazon developer account and its ```IAM user name``` and ```access key``` ([Reference](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html)).
+ ```AWS CLI``` is configured with credentials.

## Simple Deployment
### 1. Deploy Alexa Skill:

### 2. Deploy AWS Lambda:
Enter the ```lambda``` folder, then run these commands (replace contents in <> with your owns'):

```
$ aws lambda create-function --function-name voli-visualization-exploratory --zip-file fileb://system-demo.zip --handler index.handler --runtime nodejs16.x --role arn:aws:iam::<ID>:role/<Role name>

$ aws lambda update-function-code --function-name voli-visualization-exploratory --zip-file fileb://system-demo.zip
```

By this time, you are able to see a Function in AWS Lambda named ```voli-visualization-exploratory```. Open it, click ```Add trigger```, select ```Alexa```, and enter the ```Skill ID``` in Part 1.

## Server Deployment

## Citation
```
@inproceedings{han2022towards,
author = {Han, Yichen and Han, Christopher Bo and Chen, Chen and Lee, Peng Wei and Hogarth, Michael and Moore, Alison A. and Weibel, Nadir and Farcas, Emilia},
title = {Towards Visualization of Time-Series Ecological Momentary Assessment (EMA) Data on Standalone Voice-First Virtual Assistants},
year = (2022),
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = (https://doi.org/10.1145/3517428.3550398)
doi = {10.1145/3517428.3550398},
keywords = {Gerontechnology, Accessibility, Health – Well-being, User Experience Design, Older Adults, Voice User Interfaces, EMA},
location = {Athens, Greece},
series = {ASSETS '22}
}
```

## Further Resources
