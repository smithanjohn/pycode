import time
import argparse
import boto3
import bcolors
__author__ = 'sjohn4'
__version__ = "1.0.0"


def description():
 """
 This automation is to remove an Availability Zone from the Active ASG

 """


def parseCmdLineArgs():
    """Command Line Arguments for Program"""
    parser = argparse.ArgumentParser(description=description.__doc__, version=__version__,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-e", "--environment",
                        action="store",
                        dest="env",
                        required=True,
                        choices = ['qa','prf','e2e', 'prd'],
                        help=bcolors.BHELP + "[REQUIRED]:" + bcolors.HELP + "Provide the environment" + bcolors.ENDC)
    parser.add_argument("-s", "--swimlane",
                        action="store",
                        dest="swimlane",
                        choices=['devops', 'test', 'sw1', 'sw2', 'sw3', 'sw4', 'sw5', 'sw6', 'sw10'],
                        required=True,
                        help=bcolors.BHELP + "[REQUIRED]:" + bcolors.HELP + "Provide the DC name to disable" + bcolors.ENDC)
    parser.add_argument("-a", "--action",
                        action="store",
                        dest="action",
                        choices=['remove', 'add'],
                        required=True,
                        help=bcolors.BHELP + "[REQUIRED]:" + bcolors.HELP + "Provide the action that needs to be performed on the GTM WIP's [enabble/disable]" + bcolors.ENDC)
    parser.add_argument("-z", "--az",
                        action="store",
                        dest="az",
                        required=True,
                        help=bcolors.BHELP + "[REQUIRED]:" + bcolors.HELP + "Provide the action that needs to be performed on the GTM WIP's [enabble/disable]" + bcolors.ENDC)
    parser.add_argument("-r", "--region-name",
                        action="store",
                        dest="region",
                        required=True,
                        help=bcolors.BHELP + "[REQUIRED]:" + bcolors.HELP + "Memcache Cluster Region. Valid: us-west-2, us-east-1" + bcolors.ENDC)
    parser.add_argument("-p", "--profile",
                        action="store",
                        dest="aws_profile",
                        required=True,
                        help=bcolors.BHELP + "[REQUIRED]:" + bcolors.HELP + "AWS Profile Name as in ~/.aws/credentials" + bcolors.ENDC)
    args = vars(parser.parse_args())

    return args


def get_asg_name(asg_session, lb_name):
    asg_details = {}
    asg_paginator = asg_session.get_paginator("describe_auto_scaling_groups")
    asg_response = asg_paginator.paginate()

    for parse_asg_1 in asg_response:
        asg_page = parse_asg_1["AutoScalingGroups"]

        for parse_asg_2 in asg_page:
            try:
                if parse_asg_2["LoadBalancerNames"][0] == lb_name:
                    asg_details_key = parse_asg_2["AutoScalingGroupName"]
                    asg_details_value = [parse_asg_2["Instances"], parse_asg_2["VPCZoneIdentifier"]]
                    asg_details[asg_details_key] = asg_details_value
            except IndexError:
                continue

    return asg_details


def check_asg_instances_health(instances_state_list):
    instances_number = len(instances_state_list)
    health_score = 0
    for instance_iterator in instances_state_list:
        if instance_iterator["HealthStatus"] == "Healthy" and instance_iterator["LifecycleState"] == "InService":
            health_score = health_score + 1
    health_percentage = (health_score/instances_number)*100
    if health_percentage > 50:
        return True
    else:
        return False


def modify_asg(asg_session, asg_name, vpc_identifier):
    print bcolors.BOLD + "Modifying ASG: {}. Following are the updated list of Subnets: {}".format(asg_name, vpc_identifier)
    modify_response = asg_session.update_auto_scaling_group(AutoScalingGroupName=asg_name, VPCZoneIdentifier=vpc_identifier)


def update_vpc_identifier(ec2_session, vpc_identifier_list, action_az):
    for vpc_identifier_iterator in vpc_identifier_list:
        sub_response = ec2_session.describe_subnets(SubnetIds=[vpc_identifier_iterator])
        if sub_response["Subnets"][0]["AvailabilityZone"] == action_az:
            action_subnet = sub_response["Subnets"][0]["SubnetId"]

    print bcolors.BMSG + "The following Subnet: {} associated with Region: {} will be removed from the list of Subnets: {}".format(action_subnet, action_az, vpc_identifier_list) + bcolors.ENDC
    vpc_identifier_list.remove(action_subnet)
    vpc_identifier_tup = tuple(vpc_identifier_list)
    seq = ","
    vpc_identifier = seq.join(vpc_identifier_tup)
    return vpc_identifier


def validate_az(ec2_session, az):
    az_names = []
    response_desc_az = ec2_session.describe_availability_zones()
    for parse_desc_az_1 in response_desc_az["AvailabilityZones"]:
        az_zone = parse_desc_az_1["ZoneName"]
        az_names.append(az_zone)
    print bcolors.BOLD + "Valid list of AZ's: {}".format(az_names) + bcolors.ENDC

    if az in az_names:
        print bcolors.OKGREEN + "AZ {} found in list of valid az's {}".format(az, az_names) + bcolors.ENDC
    else:
        print bcolors.ERR + "AZ {} NOT found in list of valid az's {}".format(az, az_names) + bcolors.ENDC
        exit(0)



def main(args):
    environment = args["env"]
    swimlane = args["swimlane"]
    action = args["action"]
    action_az = args["az"]
    region = args["region"]
    tier = ["app", "web"]

    session = boto3.Session(profile_name=args['aws_profile'], region_name=region)
    asg_session = session.client('autoscaling')
    ec2_session = session.client('ec2')

    validate_az(ec2_session, action_az)

    print  bcolors.OKGREEN + "You have selected the following properties:" + bcolors.ENDC
    print  bcolors.OKGREEN + "Environment       : {}".format(environment) + bcolors.ENDC
    print  bcolors.OKGREEN + "Swimlane          : {} ".format(swimlane) + bcolors.ENDC
    print  bcolors.OKGREEN + "Availability Zone : {} ".format(action_az) + bcolors.ENDC
    print  bcolors.OKGREEN + "Region            : {}".format(region) + bcolors.ENDC

    if action == "remove":
        for tier_name in tier:
            lb_name = swimlane + environment + tier_name + "blue" + "elb"
            print bcolors.WAIT + "Fetching ASG details for ELB : {}. Please hold on, this might take a while ..".format(lb_name) + bcolors.ENDC
            asg_details = get_asg_name(asg_session, lb_name)

            if bool(asg_details) ==True:
                print bcolors.OKGREEN + "The following ASG's : {} are associated with the Active ELB's : {}".format(asg_details.keys(), lb_name) + bcolors.ENDC
                for asg_details_iterator in asg_details.keys():
                    vpc_identifier_string = asg_details[asg_details_iterator][1]
                    vpc_identifier_list = vpc_identifier_string.split(",")
                    print bcolors.BOLD + "The following Subnets : {} are associated with the ASG : {}".format(vpc_identifier_list, asg_details_iterator) + bcolors.ENDC

                    instances_state_list = asg_details[asg_details_iterator][0]
                    check = check_asg_instances_health(instances_state_list)
                    if check == True and len(vpc_identifier_list) > 1:
                        vpc_identifier = update_vpc_identifier(ec2_session, vpc_identifier_list, action_az)
                        modify_asg(asg_session, asg_details_iterator, vpc_identifier)
                    else:
                        print check
                        print vpc_identifier_list
                        print len(vpc_identifier_list)
                        print "No action. Health Check failed"



if __name__ == '__main__':
    start_time = time.time()
    args = parseCmdLineArgs()
    try:
        main(args)
    except KeyboardInterrupt:
        print ""
        print bcolors.ERR + 'User Interruption received. Exiting...' + bcolors.ENDC
    except ValueError:
        print bcolors.ERR + "Invalid Value Type are passed." + bcolors.ENDC
    print bcolors.BOLD + "Total Script Execution Time: {0:.2f} seconds".format(time.time() - start_time) + bcolors.ENDC


