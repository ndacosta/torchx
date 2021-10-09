#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# Follows PEP-0440 version scheme guidelines
# https://www.python.org/dev/peps/pep-0440/#version-scheme
#
# Examples:
# 0.1.0.devN # Developmental release
# 0.1.0aN  # Alpha release
# 0.1.0bN  # Beta release
# 0.1.0rcN  # Release Candidate
# 0.1.0  # Final release
__version__ = "0.1.0rc1"

# Use the github container registry images corresponding to the current package
# version.
# pyre-fixme[5]: Global expression must be annotated.
TORCHX_IMAGE = f"ghcr.io/pytorch/torchx:{__version__}"
# pyre-fixme[5]: Global expression must be annotated.
EXAMPLES_IMAGE = f"ghcr.io/pytorch/torchx-examples:{__version__}"