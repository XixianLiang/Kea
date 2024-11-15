from .input_manager import DEFAULT_DEVICE_SERIAL, DEFAULT_POLICY, DEFAULT_TIMEOUT
from .main import Kea, Setting, start_kea
from .utils import get_yml_config

import importlib
import os
import argparse
import sys
def parse_args():
    parser = argparse.ArgumentParser(description="Start kea to test app.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f",nargs="+", action="store",dest="files", help="The python files to be tested.")
    parser.add_argument("-d", "--device_serial", action="store", dest="device_serial", default=DEFAULT_DEVICE_SERIAL,
                        help="The serial number of target device (use `adb devices` to find)")
    parser.add_argument("-a","--apk", action="store", dest="apk_path", required=True,
                        help="The file path to target APK")
    parser.add_argument("-o","--output", action="store", dest="output_dir", default="output",
                        help="directory of output")
    parser.add_argument("-p","--policy", action="store", dest="policy",choices=["random", "mutate"], default=DEFAULT_POLICY,
                        help='Policy to use for test input generation. ')
    parser.add_argument("-t", "--timeout", action="store", dest="timeout", default=DEFAULT_TIMEOUT, type=int,
                        help="Timeout in seconds. Default: %d" % DEFAULT_TIMEOUT)
    parser.add_argument("-n","--number_of_events_that_restart_app", action="store", dest="number_of_events_that_restart_app", default=100, type=int,
                        help="Every xx number of events, then restart the app. Default: 100")
    parser.add_argument("-debug", action="store_true", dest="debug_mode",
                        help="Run in debug mode (dump debug messages).")
    parser.add_argument("-keep_app", action="store_true", dest="keep_app",
                        help="Keep the app on the device after testing.")
    options = parser.parse_args()
    return options

def parse_ymal_args(opts):
    config_dict = get_yml_config()
    for key, value in config_dict.items():
        if key.lower() == "system" and value:
            opts.is_harmonyos = value.lower() == "harmonyos"
        elif key.lower() == "app_path" and value:
            opts.apk_path = value
        elif key.lower() == "policy" and value:
            opts.input_policy = value
        elif key.lower() == "output_dir" and value:
            opts.output_dir = value
        elif key.lower() == "count" and value:
            opts.count = value
        elif key.lower() in ["target", "device", "device_serial"] and value:
            opts.device_serial = value
        elif key.lower() in ["property", "properties", "file", "files"] and value:
            opts.files = value
    
    return opts


def import_and_instantiate_classes(files, settings="Setting"):
    droidcheck_instance = []
    current_path = os.path.abspath(os.getcwd())
    
    d = get_mobile_driver(settings)
    settings.d = d

    for file in files:
        module_path = os.path.join(current_path, file)
        module_dir = os.path.dirname(module_path)
        
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)  # 确保当前路径在 sys.path 中

        module_name = os.path.splitext(os.path.relpath(file, start=current_path))[0]
        module_name = module_name.replace("/", ".").replace("\\", ".")
        


        try:
            module = importlib.import_module(module_name)
            module.d = d

            # Find all classes in the module and attempt to instantiate them.
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Kea) and attr is not Kea:
                    instance = attr()  # 实例化子类
                    droidcheck_instance.append(instance)
        except ModuleNotFoundError as e:
            print(f"Error importing module {module_name}: {e}")
    return droidcheck_instance

def get_mobile_driver(settings:"Setting"):
    # initialize the dsl according to the system
    if not settings.is_harmonyos:
        from kea.dsl import Mobile
        return Mobile()
    else:
        from kea.dsl_hm import Mobile
        return Mobile(serial=settings.device_serial)

def main():
    options = parse_args()
    options = parse_ymal_args(options)
    test_classes = []
    settings =  Setting(apk_path=options.apk_path,
                       device_serial=options.device_serial,
                       output_dir=options.output_dir,
                       timeout=options.timeout,
                       policy_name=options.policy,
                       number_of_events_that_restart_app=options.number_of_events_that_restart_app,
                       debug_mode=options.debug_mode,
                       keep_app=options.keep_app,
                       is_harmonyos=options.is_harmonyos
                       )
    if options.files is not None:
        test_classes = import_and_instantiate_classes(options.files, settings)
    print(Kea._all_testCase)
    start_kea(test_classes[0], settings)

if __name__ == "__main__":
    main()
    

    