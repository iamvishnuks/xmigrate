from model.project import Project
from pkg.aws import ami
from pkg.aws import ec2
from pkg.aws.network import create_nw as aws_create_nw
from pkg.azure import compute
from pkg.azure import disk
from pkg.azure.network import create_nw as azure_create_nw
from pkg.common.cloning import clone
from pkg.common.vm_preparation import prepare
from pkg.gcp import compute as gcp_compute
from pkg.gcp import disk as gcpdisk
from pkg.gcp.network import create_nw as gcp_create_nw
from services.project import get_project_by_name
from utils.logger import *
import asyncio


async def call_start_vm_preparation(user, project, hostname, db) -> None:
    await asyncio.create_task(start_vm_preparation(user, project, hostname, db))


async def start_vm_preparation(user, project, hostname, db) -> None:
    logger("VM preparation started","info")
    print("****************VM preparation awaiting*****************")
    preparation_completed = await prepare(user, project, hostname, db)
    if preparation_completed:
        print("****************VM preparation completed*****************")
        logger("VM preparation completed", "info")
    else:
        print("VM preparation failed")
        logger("VM preparation failed", "error")


async def call_start_clone(user, project, hostname, db) -> None:
    await asyncio.create_task(start_cloning(user, project,hostname, db))


async def start_cloning(user, project, hostname, db) -> None:
    logger("Cloning started","info")
    print("****************Cloning awaiting*****************")
    cloning_completed = await clone(user, project, hostname, db)
    if cloning_completed:
        print("****************Cloning completed*****************")
        logger("Cloning completed","info")
    else:
        print("Disk cloning failed")
        logger("Disk cloning failed", "error")


async def call_start_convert(user, project, hostname, db):
    await asyncio.create_task(start_convert(user, project, hostname, db))


async def start_convert(user, project, hostname, db):
    provider = get_project_by_name(user, project, hostname, db)

    if provider == "azure":
        logger("Download started","info")
        print("****************Download started*****************")
        image_downloaded = await disk.start_downloading(project, hostname, db)
        if image_downloaded:
            print("****************Download completed*****************")
            logger("Image Download completed","info")
            print("****************Conversion awaiting*****************")
            logger("Conversion started","info")
            converted =  await disk.start_conversion(project, hostname, db)
            if converted:
                print("****************Conversion completed*****************")
                logger("Disk Conversion completed","info")
            else:
                print("Disk Conversion failed")
                logger("Disk Conversion failed","error")
        else:
            print("Image Download failed\nDisk Conversion failed")
            logger("Image Download faied", "error")
            logger("Disk Conversion failed", "error")
    elif provider == "aws":
        logger("Conversion started","info")
        print("****************Conversion awaiting*****************")
        logger("AMI creation started","info")
        ami_created = await ami.start_ami_creation(user, project, hostname, db)
        if ami_created:
            print("****************Conversion completed*****************")
            logger("Conversion completed","info")
            logger("AMI creation completed:"+str(ami_created),"info")
        else:
            print("Disk Conversion failed")
            logger("Disk Conversion failed","error")
    elif provider == "gcp":
        logger("Download started","info")
        print("****************Download started*****************")
        image_downloaded = await gcpdisk.start_downloading(project, hostname, db)
        print("****************Conversion awaiting*****************")
        logger("Conversion started","info")
        if image_downloaded:
            converted =  await gcpdisk.start_conversion(project,hostname, db)
            if converted:
                print("****************Conversion completed*****************")
                logger("Disk Conversion completed","info")
            else:
                print("Disk Conversion failed")
                logger("Disk Conversion failed","error")


async def call_build_network(user, project, db):
    await asyncio.create_task(start_network_build(user, project, db))


async def start_network_build(user, project, db):
    provider = get_project_by_name(user, project, db).provider
    network_created = False
    logger("Network build started", "info")
    print("****************Network build awaiting*****************")

    if provider == "azure":
        network_created = await azure_create_nw(project, db)
    elif provider == "aws":
        network_created = await aws_create_nw(user, project, db)
    elif provider == "gcp":
        network_created = await gcp_create_nw(user, project, db)
    if network_created:
        logger("Network creation completed","info")
    else:
        print("Network creation failed")
        logger("Network creation failed","error")


async def call_build_host(project, hostname, db):
    await asyncio.create_task(start_host_build(project, hostname, db))

async def start_host_build(project, hostname, db):
    provider = (db.query(Project).filter(Project.name==project).first()).provider

    if provider == "azure":
        logger("Host build started","info")
        print("****************Host build awaiting*****************")
        disk_created = await disk.create_disk(project, hostname, db)
        if disk_created:
            vm_created = await compute.create_vm(project, hostname, db)
        else:
            logger("Disk creation failed","error")
    elif provider == "aws":
        logger("ec2 creation started","info")
        ec2_created = await ec2.build_ec2(project, hostname, db)
        if ec2_created:
            logger("ec2 creation completed","info")
        else:
            print("ec2 creation failed")
            logger("ec2 creation failed","error")
    elif provider == "gcp":
        logger("gcp vm creation started","info")
        disk_created = await gcpdisk.start_image_creation(project, hostname, db)
        if disk_created:
            vm_created = await gcp_compute.build_compute(project, hostname, db)
            if vm_created:
                logger("gcp vm creation completed","info")
            else:
                print("gcp vm creation failed")
                logger("gcp vm creation failed","error")
        else:
            print("gcp disk creation failed")
            logger("gcp disk creation failed","error")
