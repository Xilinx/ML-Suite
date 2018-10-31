#!/usr/bin/env bash
#
# // SPDX-License-Identifier: BSD-3-CLAUSE
#
# (C) Copyright 2018, Xilinx, Inc.
#
#!/bin/bash

for DSP_WIDTH in 28 56; do
    python $MLSUITE_ROOT/xfdnn/tools/compile/bin/xfdnn_compiler_caffe.py \
        -n $MLSUITE_ROOT/models/caffe/inception_v3/fp32/inception_v3_without_bn_deploy.prototxt \
        -g $MLSUITE_ROOT/examples/compile/work/caffe/inception_v3/fp32/inception_v3_without_bn_deploy_${DSP_WIDTH}.cmds \
        -w $MLSUITE_ROOT/models/caffe/inception_v3/fp32/inception_v3_without_bn.caffemodel \
        -s all \
        -i ${DSP_WIDTH} \
        -m 4 \
        -d 16
done

