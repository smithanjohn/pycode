# S3 Automations

This is my humble effort to start pushing code on the public gitrepo. Over the years I have made many code contributions
as a part of my day job and will start publishing the general automations which may be used over various cloud platforms.

## Standardize S3 Bucket Creation

######  Create a virtual env : https://help.dreamhost.com/hc/en-us/articles/115000695551-Installing-and-using-virtualenv-with-Python-3

######  Switch to Virtual Env and install packages


      $ pip3.6 install -r requirements.txt 
            
            
###### Run the Automation

      $   python3 standardizes3bucketcreation.py -h
            usage: standardizes3bucketcreation.py [-h] -a AWS_VALUE_APP
                                      [-r AWS_VALUE_TARGET_REGION]
                                      [-e AWS_VALUE_APP_ENV] -p AWS_PROFILE

            optional arguments:
            -h, --help            show this help message and exit
             -a AWS_VALUE_APP, --app AWS_VALUE_APP
                        Name of the application for which you want to create the S3 bucket
            -r AWS_VALUE_TARGET_REGION, --target-region AWS_VALUE_TARGET_REGION
                        Use this if you need a region specific tag added to your bucket name: ['us-east-1', 'us-west-2']
            -e AWS_VALUE_APP_ENV, --app-env AWS_VALUE_APP_ENV
                        Use this if you need a environment specific tag added to your bucket name eg: qa, e2e, prf, prd
            -p AWS_PROFILE, --profile AWS_PROFILE
                        AWS Profile Name in ~/.aws/credentials
      
      $  python3 standardizes3bucketcreation.py -a testsjohn4 -r us-west-2 -e test -p gw-ppd
      ⌛  Creating S3 Bucket: testsjohn4-test-us-west-2-301532132469
         Created S3 Bucket: testsjohn4-test-us-west-2-301532132469

PS: Please feel free to add PR's in case you would want to see some changes. Also raise an issue if you want to see some 
additional features.