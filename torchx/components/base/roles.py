# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Any, Dict, List, Optional

from torchx.specs.api import Container, RetryPolicy, Role, macros


def create_torch_dist_role(
    name: str,
    container: Container,
    entrypoint: str,
    script_args: Optional[List[str]] = None,
    script_envs: Optional[Dict[str, str]] = None,
    num_replicas: int = 1,
    max_retries: int = 0,
    retry_policy: RetryPolicy = RetryPolicy.APPLICATION,
    **launch_kwargs: Any,
) -> Role:
    """
    A ``Role`` for which the user provided ``entrypoint`` is executed with the
    torchelastic agent (in the container). Note that the torchelastic agent
    invokes multiple copies of ``entrypoint``.

    For more information about torchelastic see
    `torchelastic quickstart docs <http://pytorch.org/elastic/0.2.0/quickstart.html>`__.

    .. important:: It is the responsibility of the user to ensure that the
                   container's image includes torchelastic. Since Torchx has no
                   control over the build process of the image, it cannot
                   automatically include torchelastic in the container's image.

    The following example launches 2 ``replicas`` (nodes) of an elastic ``my_train_script.py``
    that is allowed to scale between 2 to 4 nodes. Each node runs 8 workers which are allowed
    to fail and restart a maximum of 3 times.

    .. warning:: ``replicas`` MUST BE an integer between (inclusive) ``nnodes``. That is,
                   ``ElasticRole("trainer", nnodes="2:4").replicas(5)`` is invalid and will
                   result in undefined behavior.

    ::

     elastic_trainer = torch_dist_role("trainer", "my_train_script.py",
                            script_args=["--script_arg", "foo", "--another_arg", "bar"],
                            num_replicas=4, max_retries=1,
                            nproc_per_node=8, nnodes="2:4", max_restarts=3)
     # effectively runs:
     #    python -m torch.distributed.launch
     #        --nproc_per_node 8
     #        --nnodes 2:4
     #        --max_restarts 3
     #        my_train_script.py --script_arg foo --another_arg bar

    Args:
        name: Name of the role
        entrypoint: User binary or python script that will be launched.
        script_args: User provided arguments
        script_envs: Env. variables that will be set on worker process that runs entrypoint
        num_replicas: Number of role replicas to run
        max_retries: Max number of retries
        retry_policy: Retry policy that is applied to the role
        launch_kwargs: kwarg style launch arguments that will be used to launch torchelastic agent.

    Returns:
        Role object that launches user entrypoint via the torchelastic as proxy

    """
    script_args = script_args or []
    script_envs = script_envs or {}

    entrypoint_override = "python"
    args: List[str] = ["-m", "torch.distributed.launch"]

    launch_kwargs.setdefault("rdzv_backend", "etcd")
    launch_kwargs.setdefault("rdzv_id", macros.app_id)
    launch_kwargs.setdefault("role", name)

    for (arg, val) in launch_kwargs.items():
        if isinstance(val, bool):
            # treat boolean kwarg as a flag
            if val:
                args += [f"--{arg}"]
        else:
            args += [f"--{arg}", str(val)]
    if not os.path.isabs(entrypoint) and not entrypoint.startswith(macros.img_root):
        # make entrypoint relative to {img_root} ONLY if it is not an absolute path
        entrypoint = os.path.join(macros.img_root, entrypoint)

    args += [entrypoint, *script_args]
    return (
        Role(name)
        .runs(entrypoint_override, *args, **script_envs)
        .on(container)
        .replicas(num_replicas)
        .with_retry_policy(retry_policy, max_retries)
    )