#!/usr/bin/env python
#
# // SPDX-License-Identifier: BSD-3-CLAUSE
#
# (C) Copyright 2018, Xilinx, Inc.
#
import xdnn
import json
import os, sys

def _fixQuantJsonLayerNames(quantFile):
  obj = None
  with open(quantFile) as data:
      obj = json.load(data)

  for l in obj['network']:
    if "/Conv2D" not in l['name']:
      l['name'] = l['name']+"/Conv2D"

  with open(quantFile + "_fixed", "w") as outfile:
    json.dump(obj, outfile, sort_keys=True, indent=4, separators=(',', ': '))

class xdnn_env(object):
    def __init__(self, xclbin=None, quant_info=None, quant_cfgfile=None, isxdnnv3=False, **kwargs):
        self._xdnnParams = {}
        self._xdnnParams['xclbin'] = xclbin
        self._xdnnParams['isXdnnv3'] = isxdnnv3
        self._xdnnParams['lib_path'] = os.environ["LIBXDNN_PATH"]
        self._xdnnParams['lib_path'] = kwargs['lib_path'] if 'lib_path' in kwargs else os.environ["LIBXDNN_PATH"]
        self._xdnnParams['api'] = xdnn.XDNNManager(self._xdnnParams['lib_path'])
        self._xdnnParams['quantDB'] = None
        self._xdnnParams['scaleA'] = 10000
        self._xdnnParams['scaleB'] = 30
        self._xdnnParams['useGlobalScale'] = False

        if quant_cfgfile:
          extension = quant_cfgfile.rsplit('.', 1)[-1]
          if extension == 'json':
            self._xdnnParams['quantize_json'] = quant_cfgfile
            with open(quant_cfgfile) as data:
              try:
                obj = json.load(data)
              except:
                raise TypeError('expected a json quantization config file, received {}'.format(quant_cfgfile))
          elif extension == 'txt':
            self._xdnnParams['quantize_json'] = None  ## to be determined in fpga_pydot_layer.forward_exec()
            if quant_info is None:
              raise RuntimeError('quant_info cannot be \"None\"')
            obj = quant_info

          # make a map of { layerName -> data }
          # FIXME: need to only include layers exisitng in the partition NOT ALL LAYERS in graph
          self._xdnnParams['quantDB'] = {}
          for l in obj['network']:
            layerName = l['name']
            self._xdnnParams['quantDB'][layerName] = l
        else:
          self._xdnnParams['useGlobalScale'] = True

    def get_params(self):
        return self._xdnnParams


class xdnn_fpga_env(xdnn_env):
    def __init__(self, xclbin, quant_info=None, quant_cfgfile=None, isxdnnv3=False):
        xdnn_env.__init__(self, xclbin, quant_info=quant_info, quant_cfgfile=quant_cfgfile,
                          isxdnnv3=isxdnnv3)

        if isxdnnv3 and 'v3' not in os.environ['LIBXDNN_PATH']:
          os.environ['LIBXDNN_PATH'] += '.v3'

        if "XDNN_COMPILER_FILE" in os.environ:
          self._xdnnParams['compiler_file'] = os.environ["XDNN_COMPILER_FILE"]

    def createHandle(self):
        (ret, handles) = xdnn.createHandle(self._xdnnParams['xclbin'])

        if ret != 0:
          raise RuntimeError("Could not init FPGA: xclbin %s lib_path %s" % (self._xdnnParams['xclbin'], self._xdnnParams['lib_path']))
          sys.exit(1)

        self._xdnnParams['handles'] = handles
