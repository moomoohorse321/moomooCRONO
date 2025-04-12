#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

import argparse
import json
import logging
import re
import subprocess
import tempfile
from builtins import range
from pprint import pprint
from accuracy import get_gt, compute_similarity, parse_pr_data


import opentuner
from opentuner import (ConfigurationManipulator,
                        IntegerParameter,
                        LogIntegerParameter,
                        SwitchParameter)

from opentuner import MeasurementInterface
from opentuner.measurement.inputmanager import FixedInputManager
from opentuner.search.objective import ThresholdAccuracyMinimizeTime

log = logging.getLogger("pbtuner")

parser = argparse.ArgumentParser(parents=opentuner.argparsers())
parser.add_argument('program',
                    help='PetaBricks binary program to autotune')
parser.add_argument('--program-cfg-default',
                    help="override default program config exemplar location")
parser.add_argument('--program-cfg-output',
                    help="location final autotuned configuration is written")
parser.add_argument('--program-settings',
                    help="override default program settings file location")
parser.add_argument('--program-input',
                    help="use only a given input for autotuning")
parser.add_argument('--upper-limit', type=float, default=30,
                    help="time limit to apply to initial test")
parser.add_argument('--test-config', action='store_true')


class PetaBricksInterface(MeasurementInterface):
    def __init__(self, args):
        """
            Scope: internal to auto-tuner
        """
        self.program_settings = json.load(open(args.program_settings))
        objective = ThresholdAccuracyMinimizeTime(self.program_settings['accuracy'])
        input_manager = FixedInputManager()
        # pass many settings to parent constructor
        super(PetaBricksInterface, self).__init__(
            args, program_name=args.program, objective=objective, input_manager=input_manager)

    def build_config(self, cfg):
        """
            Scope: internal to auto-tuner
        """
        r = []
        # direct copy
        for k, v in list(cfg.items()):
            if k[0] != '.' and k != 'worker_threads':
                r.append('-D' + k + '=' + str(v))
        return r

    def run(self, desired_result, input, limit):
        """
            Scope: environment dependent
        """
        limit = min(limit, self.args.upper_limit)
        configs = self.build_config(desired_result.configuration.data)
        print(configs)

        gcc_cmd = ['g++', '-g', '--std=c++0x', '-O3', '-Wall', '-Werror', 'pagerank.cc'] + configs + \
            ['-o', 'pagerank', '-lpthread', '-lrt']
            
        compile_result = self.call_program(gcc_cmd)
        # print(gcc_cmd)
        assert compile_result['returncode'] == 0
               
        cmd = ['./pagerank',
                '1',
                str(desired_result.configuration.data['worker_threads']),
                './sample.txt'] 
        
        
        run_result = self.call_program(cmd)

        result = opentuner.resultsdb.models.Result()
        try:
            output  = run_result['stdout'].decode('utf-8')
            # print(output)
            time, out = parse_pr_data(output)
            result.time = time
            result.accuracy = compute_similarity(get_gt(), out)
            if result.time < limit + 3600:
                result.state = 'OK'
            else:
                # time will be 2**31 if timeout
                result.state = 'TIMEOUT'
        except:
            log.warning("program crash, out = %s / err = %s", out, err)
            result.state = 'ERROR'
            result.time = float('inf')
            result.accuracy = float('-inf')
        return result

    def save_final_config(self, configuration):
        """
        called at the end of autotuning with the best
        resultsdb.models.Configuration
        
        Scope: internal to auto-tuner
        """
        self.manipulator().save_to_file(configuration.data,
                                        'approx_config.json')

    def manipulator(self):
        """
            create the configuration manipulator, from example config
            
            Scope: internal to auto-tuner
        """
        cfg = open(self.args.program_cfg_default).read()
        manipulator = ConfigurationManipulator()
        # print(manipulator().random())
        self.choice_sites = dict()

        for m in re.finditer(r" *([a-zA-Z0-9_-]+)[ =]+([0-9e.+-]+) *"
                             r"[#] *([a-z]+).* ([0-9]+) to ([0-9]+)", cfg):
            k, v, valtype, minval, maxval = m.group(1, 2, 3, 4, 5)
            minval = float(minval)
            maxval = float(maxval)
            assert valtype == 'int'
            # log.debug("param %s %f %f", k, minval, maxval)

            if k == 'worker_threads':
                manipulator.add_parameter(IntegerParameter(k, 1, 16))
            elif k == 'distributedcutoff':
                pass
            elif minval == 0 and maxval < 64:
                manipulator.add_parameter(SwitchParameter(k, maxval))
            else:
                manipulator.add_parameter(LogIntegerParameter(k, minval, maxval))

        return manipulator

    def test_config(self):
        pprint(self.manipulator.random())


if __name__ == '__main__':
    args = parser.parse_args()
    if not args.program_cfg_default:
        args.program_cfg_default = args.program + '.cfg.default'
    if not args.program_cfg_output:
        args.program_cfg_output = args.program + '.cfg'
    if not args.program_settings:
        args.program_settings = args.program + '.settings'
    if args.test_config:
        PetaBricksInterface(args).test_config()
    else:
        PetaBricksInterface.main(args)
