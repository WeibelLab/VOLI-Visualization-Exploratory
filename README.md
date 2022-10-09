# VOLI Visualization Exploratory
This is the system demo of ASSETS'22 Poster “Towards Visualization of Time–Series Ecological Momentary Assessment (EMA) Data on Standalone Voice–First Virtual Assistants”. 

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

## Further Resources
This work is a part of [VOLI Project]() and UC San Diego [Human-Extented Lab](). 