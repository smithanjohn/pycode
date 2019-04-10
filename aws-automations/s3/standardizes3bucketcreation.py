import boto3
import argparse
import botocore
import bcolors

def parseCmdLineArgs():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-a", "--app",
                        action="store",
                        dest="aws_value_app",
                        required=True,
                        help=bcolors.HELP + "Name of the application for which you want to create the S3 bucket" + bcolors.ENDC)
    parser.add_argument("-r", "--target-region",
                        action="store",
                        dest="aws_value_target_region",
                        required=False,
                        default="default",
                        help=bcolors.HELP + "Use this if you need a region specific tag added to your bucket name: ['us-east-1', 'us-west-2']" + bcolors.ENDC)
    parser.add_argument("-e", "--app-env",
                        action="store",
                        dest="aws_value_app_env",
                        required=False,
                        default="default",
                        help=bcolors.HELP + "Use this if you need a environment specific tag added to your bucket name eg: qa, e2e, prf, prd" + bcolors.ENDC)
    parser.add_argument("-p", "--profile",
                        action="store",
                        dest="aws_profile",
                        required=True,
                        help=bcolors.HELP + "AWS Profile Name in ~/.aws/credentials" + bcolors.ENDC)
    args = vars(parser.parse_args())
    return args

def main(args):
    tar_app_name=args['aws_value_app']
    tar_region=args['aws_value_target_region']
    tar_env=args['aws_value_app_env']
    session = boto3.Session(profile_name=args['aws_profile'])
    bucket_conn=session.client('s3')
    acc_conn = session.client('sts')
    account_id = acc_conn.get_caller_identity()["Account"]

    bucket_name=tar_app_name + "-" + tar_env + "-" + tar_region + "-" + account_id

    print (bcolors.WAITMSG + "Creating S3 Bucket: " + bcolors.ENDC + bcolors.BOLD + "{}".format(
        bucket_name) + bcolors.ENDC)

    create_bucket = bucket_conn.create_bucket(
        ACL='private',
        Bucket=bucket_name,
    )
    print (bcolors.OK + "Created S3 Bucket: " + bcolors.ENDC + bcolors.BOLD + "{}".format(bucket_name) + bcolors.ENDC)

if __name__ == "__main__":
    args = parseCmdLineArgs()
    try:
        main(args)
    except KeyboardInterrupt:
        print ("")
        print (bcolors.ERR + 'User Interruption received. Exiting...' + bcolors.ENDC)
    except botocore.exceptions.ProfileNotFound:
        print (bcolors.ERR + 'Profile {} not found.'.format(args['aws_profile']) + bcolors.ENDC)
    except botocore.exceptions.ClientError as errObj:
        print (bcolors.ERR + str(errObj) + bcolors.ENDC)

