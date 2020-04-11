import json
import ntpath
import os
import traceback
from json import JSONEncoder

from common.model import *


class Persistence:
    _tmp_fn_prefix = ".tmp"

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Persistence, cls).__new__(cls)
        return cls.instance

    def save(self, obj, filename):
        tmp_filename = filename + self._tmp_fn_prefix
        try:
            with open(tmp_filename, 'w') as out_file:
                json.dump(obj, out_file, cls=self.DictEncoder)
        except Exception as e:
            print("ERROR: failed to save to file {}: {}".format(tmp_filename, e))
            traceback.print_exc()
            return
        try:
            os.remove(filename)
            os.rename(tmp_filename, filename)
        except Exception as e:
            print("ERROR: failed rename tmp file {} to {}: {}".format(tmp_filename, filename, e))
            traceback.print_exc()

    def do_load(self, filename):
        if not os.path.isfile(filename):
            print("Config file '{}' not exist".format(filename))
            return None
        with open(filename, 'r') as in_file:
            file_data = in_file.read()
            # print(file_data)
            result = json.loads(file_data, object_hook=self.decode)
            # print("Successfully loaded {}: {}".format(filename, result))
            return result

    def load(self, filename):
        try:
            return self.do_load(filename)
        except Exception as e1:
            print("ERROR: failed to load file {}: {}".format(filename, e1))
            traceback.print_exc()

            tmp_filename = filename + self._tmp_fn_prefix
            try:
                return self.do_load(tmp_filename)
            except Exception as e2:
                print("ERROR: failed to load file {}: {}".format(tmp_filename, e2))
                traceback.print_exc()

    class DictEncoder(JSONEncoder):
        def default(self, o):
            result = o.__dict__
            result['__type__'] = type(o).__name__
            return result

    @staticmethod
    def decode(obj):
        type_name = obj.get('__type__')
        if type_name == 'ProjectState':
            pipeline_states = obj.get('pipeline_states')
            if pipeline_states is None:
                pipeline_states = {}
            return ProjectState(obj['project_name'], pipeline_states)
        elif type_name == 'PipelineState':
            return PipelineState(obj['id'], obj['ref'], obj['status'], obj['url'])
        else:
            return obj

    @staticmethod
    def create_file(full_fn):
        head, tail = ntpath.split(full_fn)
        if not os.path.isdir(ntpath.basename(head)):
            os.mkdir(ntpath.basename(head))
        if not os.path.isfile(full_fn):
            f = open(full_fn, "a+")
            f.close()
