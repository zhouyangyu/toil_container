"""toil_container jobs tests."""

import argparse
import pytest

from toil_container import exceptions
from toil_container import jobs

from .utils import SKIP_DOCKER
from .utils import SKIP_SINGULARITY
from .utils import DOCKER_IMAGE
from .utils import SINGULARITY_IMAGE


def test_call_uses_subprocess():
    options = argparse.Namespace()
    job = jobs.ContainerJob(options)
    assert job.call(["ls"]) == 0
    assert "bin" in job.call(["ls", "/"], check_output=True)

    # check subprocess.CalledProcessError
    with pytest.raises(exceptions.SystemCallError):
        job.call(["rm", "/bin"])

    # check OSError
    with pytest.raises(exceptions.SystemCallError):
        job.call(["florentino-ariza"])


def assert_image_call(image_attribute, image, tmpdir):
    """Get options namespace."""
    options = argparse.Namespace()
    options.workDir = tmpdir.mkdir("working_dir").strpath
    setattr(options, image_attribute, image)

    # create job and options
    # vol1 = tmpdir.mkdir("vol1")
    # options.container_volumes = [
    #     (vol1.strpath, "/vol1"),
    #     (tmpdir.mkdir("vol2").strpath, "/vol2"),
    #     ]

    # vol1.join("foo").write("bar")
    job = jobs.ContainerJob(options)

    # test volume
    # assert "bar" in job.call(["cat", "/vol1/foo"], check_output=True)
    # assert job.call(["ls"]) == 0

    # test cwd
    assert "bin" in job.call(["ls", ".."], cwd="/bin", check_output=True)

    # test env
    cmd = ["bash", "-c", "echo $FOO"]
    assert "BAR" in job.call(cmd, env={"FOO": "BAR"}, check_output=True)

    # check subprocess.CalledProcessError
    with pytest.raises(exceptions.SystemCallError):
        job.call(["rm", "/bin"])

    # check OSError
    with pytest.raises(exceptions.SystemCallError):
        job.call(["florentino-ariza"])

    # test both singularity and docker raiser error
    options = argparse.Namespace()
    options.docker_path = "foo"
    options.singularity_path = "bar"
    job = jobs.ContainerJob(options)

    with pytest.raises(exceptions.SystemCallError):
        job.call(["foo", "bar"])


@SKIP_DOCKER
def test_job_with_docker_call(tmpdir):
    assert_image_call("docker_image", DOCKER_IMAGE, tmpdir)


@SKIP_SINGULARITY
def test_job_with_singularity_call(tmpdir):
    assert_image_call("singularity_image", SINGULARITY_IMAGE, tmpdir)
