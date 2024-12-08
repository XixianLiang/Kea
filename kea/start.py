from .input_manager import DEFAULT_POLICY, DEFAULT_TIMEOUT
from .core import Kea, Setting, start_kea
from .utils import get_yml_config, sanitize_args

import argparse

def parse_args():
    """Parse, load and sanitize the args from the command line and the config file `config.yml`.

    The args are better to be either specified via the command line or the config file `config.yml`.
    The design purpose of config.yml is to ease specifying the args via a config file.
    """
    parser = argparse.ArgumentParser(description="Start kea to test app.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", nargs="+", action="store",dest="property_files", help="The app properties to be tested.")
    parser.add_argument("-d", "--device_serial", action="store", dest="device_serial", default=None,
                        help="The serial number of target device (use `adb devices` to find)")
    parser.add_argument("-a","--apk", action="store", dest="apk_path",
                        help="The file path to target APK")
    parser.add_argument("-o","--output", action="store", dest="output_dir", default="output",
                        help="directory of output")
    parser.add_argument("-p","--policy", action="store", dest="policy",choices=["random", "guided", "llm"], default=DEFAULT_POLICY,  # tingsu: can we change "mutate" to "guided"?
                        help='Policy used for input event generation. ')
    parser.add_argument("-t", "--timeout", action="store", dest="timeout", default=DEFAULT_TIMEOUT, type=int,
                        help="Timeout in seconds. Default: %d" % DEFAULT_TIMEOUT)
    parser.add_argument("-n","--number_of_events_that_restart_app", action="store", dest="number_of_events_that_restart_app", default=100, type=int,
                        help="Restart the app when this number of events has been executed. Default: 100")
    parser.add_argument("-debug", action="store_true", dest="debug_mode",
                        help="Run in debug mode (dump debug messages).")
    parser.add_argument("-keep_app", action="store_true", dest="keep_app",
                        help="Keep the app on the device after testing.")
    parser.add_argument("-grant_perm", action="store_true", dest="grant_perm",
                        help="Grant all permissions while installing. Useful for Android 6.0+.")
    parser.add_argument("-is_emulator", action="store_true", dest="is_emulator",default=True,
                        help="Declare the target device to be an emulator, which would be treated specially.")
    parser.add_argument("-is_harmonyos", action="store_true", dest="is_harmonyos", default=False,
                        help="use harmonyos devices")
    parser.add_argument("-load_config", action="store_true", dest="load_config", default=False,
                        help="load the args from config.yml. The args in config.yml will overwrite the args in the command line.")
    parser.add_argument("-utg", action="store_true", dest="generate_utg", default=False,
                        help="Generate UI transition graph")
    options = parser.parse_args()

    # load the args from the config file `config.yml`
    if options.load_config:
        options = load_ymal_args(options)

    # sanitize these args
    sanitize_args(options) 

    return options

def load_ymal_args(opts):
    """Load the args from the config.yml. 

    The design purpose of config.yml is to ease specifying the args via a config file.
    Note that the values of the args in config.yml would overwrite those of the same set of 
    args specified via the command line.
    """
    config_dict = get_yml_config()
    for key, value in config_dict.items():
        if key.lower() == "system" and value:
            opts.is_harmonyos = value.lower() == "harmonyos"
        elif key.lower() in ["app_path", "package", "package_name"] and value:
            opts.apk_path = value
        elif key.lower() == "policy" and value:
            opts.policy = value
        elif key.lower() == "output_dir" and value:
            opts.output_dir = value
        elif key.lower() == "count" and value:
            opts.count = value
        elif key.lower() in ["target", "device", "device_serial"] and value:
            opts.device_serial = value
        elif key.lower() in ["property", "properties", "file", "files"] and value:
            opts.property_files = value
    
    return opts


def main():
    """the main entry of Kea.
    """
    # parse the args
    options = parse_args()
    # load the properties to be tested
    Kea.load_properties(options.property_files)
    kea = Kea()
    print(f"Test cases: {kea._all_testCases}")

    # setup the setting
    settings =  Setting(apk_path=options.apk_path,
                       device_serial=options.device_serial,
                       output_dir=options.output_dir,
                       timeout=options.timeout,
                       policy_name=options.policy,
                       number_of_events_that_restart_app=options.number_of_events_that_restart_app,  # tingsu: do we need a better name?
                       debug_mode=options.debug_mode,
                       keep_app=options.keep_app,
                       is_harmonyos=options.is_harmonyos,
                       grant_perm=options.grant_perm,
                       is_emulator=options.is_emulator,
                       generate_utg=options.generate_utg,
                       is_package = options.is_package
                       )
    
    # start Kea
    start_kea(kea, settings) 

if __name__ == "__main__":
    main()
    

    
