"""Abstraction for interactions with Docker and DockerHub."""

import subprocess
import os
import sys


def check_docker_perms():
    """Checks if the current user has permision to access Docker socket.

    Only root, a member of the docker group or a member of the group given
    to the Docker deamion with -G can work with Docker. In other words, the
    Docker socket (/var/run/docker.sock) must be owned by the user or a
    group the user belongs to.

    See: http://goo.gl/f5NvXQ

    I would raise a PermissionError here, but trying to be Python 2.7
    compatible.

    :raises IOError: Need to be root to access Docker socket

    """
    # Find gid of group that owns the Docker socket
    # TODO: Pull Docker socket path from config.yaml
    stat_info = os.stat("/var/run/docker.sock")
    sock_uid = stat_info.st_uid
    sock_gid = stat_info.st_gid

    # Get gids and uid of user running this process
    user_gids = os.getgroups()
    user_uid = os.geteuid()

    if sock_gid not in user_gids and sock_uid != user_uid:
        err_msg = "Error: You don't have permission to use the Docker socket."
        sys.stderr.write(err_msg)
        raise IOError(err_msg)


def run(image_name, cmd, detached=True):
    """Runs, using `docker run`, the given image.

    Note that the image will be pulled down from DockerHub if it isn't
    stored locally. This is handled by Docker automatically.

    TODO: Pull default image_name from config.yaml.

    :param image_name: Full name of the image to run.
    :type image_name: string
    :param cmd: Command to pass to Docker comtainer.
    :type cmd: string
    :param detached: True if container should be in detached mode (-d).
    :type detached: boolean

    """
    # Confirm that the user has permission to access the Docker socket
    check_docker_perms()

    # Build list describing the run command for the Docker process to execute
    params = ["run"]
    if detached:
        params.append("-d")
    params.append(image_name)
    params.append(cmd)

    # Spawn subprocess to execute Docker run command
    subprocess.check_call(["docker"] + params)
