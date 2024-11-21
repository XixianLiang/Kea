import json
import os
import re
import functools
from datetime import datetime
import time
import warnings
import pkg_resources
import yaml
# logcat regex, which will match the log message generated by `adb logcat -v threadtime`
LOGCAT_THREADTIME_RE = re.compile(
    '^(?P<date>\S+)\s+(?P<time>\S+)\s+(?P<pid>[0-9]+)\s+(?P<tid>[0-9]+)\s+'
    '(?P<level>[VDIWEFS])\s+(?P<tag>[^:]*):\s+(?P<content>.*)$'
)


def lazy_property(func):
    attribute = '_lazy_' + func.__name__

    @property
    @functools.wraps(func)
    def wrapper(self):
        if not hasattr(self, attribute):
            setattr(self, attribute, func(self))
        return getattr(self, attribute)

    return wrapper


def parse_log(log_msg):
    """
    parse a logcat message
    the log should be in threadtime format
    @param log_msg:
    @return:
    """
    m = LOGCAT_THREADTIME_RE.match(log_msg)
    if not m:
        return None
    log_dict = {}
    date = m.group('date')
    time = m.group('time')
    log_dict['pid'] = m.group('pid')
    log_dict['tid'] = m.group('tid')
    log_dict['level'] = m.group('level')
    log_dict['tag'] = m.group('tag')
    log_dict['content'] = m.group('content')
    datetime_str = "%s-%s %s" % (datetime.today().year, date, time)
    log_dict['datetime'] = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")

    return log_dict


def get_available_devices():
    """
    Get a list of device serials connected via adb
    :return: list of str, each str is a device serial number
    """
    import subprocess

    r = subprocess.check_output(["adb", "devices"])
    if not isinstance(r, str):
        r = r.decode()
    devices = []
    for line in r.splitlines():
        segs = line.strip().split()
        if len(segs) == 2 and segs[1] == "device":
            devices.append(segs[0])
    return devices


def weighted_choice(choices):
    import random

    total = sum(choices[c] for c in list(choices.keys()))
    r = random.uniform(0, total)
    upto = 0
    for c in list(choices.keys()):
        if upto + choices[c] > r:
            return c
        upto += choices[c]


def safe_re_match(regex, content):
    if not regex or not content:
        return None
    else:
        return regex.match(content)


def md5(input_str):
    import hashlib

    return hashlib.md5(input_str.encode('utf-8')).hexdigest()


def safe_get_dict(view_dict, key, default=None):
    return view_dict[key] if (key in view_dict) else default


def generate_report(img_path, html_path, bug_information=None):
    '''Generate report for the test based on the executed events'''
    line_list = []
    
    bug_link_list = []
    # user can click to jump to the corresponding event, contains the event index of each bug
    bug_set = set()
    json_dir = os.path.join(html_path, "report_screenshot.json")
    with open(json_dir, 'r') as json_file:
        report_screens = json.load(json_file)
    if bug_information is not None:
        for bug in bug_information:
            property_name = "<p>" + bug[2] + "</p>"
            interaction_end = str(bug[0]) + ".1"
            for report_screen in report_screens:
                if str(bug[0]) + "." in report_screen['event_index']:
                    interaction_end = report_screen['event_index']
            bug_link = ("<tr><td>" + property_name + "</td>" +
                        "<td><a href=\"#"+str(bug[0])+"\">"+str(bug[0])+"</a></td>" +
                        "<td><a href=\"#"+str(bug[0]) + ".1" + "\">"+str(bug[0])+ ".1 ~ " + interaction_end + "</a></td>" +
                        "<td><a href=\"#"+str(bug[0] + 1) + "\">"+str(bug[0] + 1)+"</a></td></tr>")
            bug_link_list.append(bug_link)
            bug_set.add(str(bug[0]))
            bug_set.add(str(bug[0] + 0.1))
            bug_set.add(str(bug[0] + 1))
    f_html = open(
        os.path.join(html_path,  "bug_report.html"), 'w', encoding='utf-8'
    )
    f_style = pkg_resources.resource_filename(
                "kea", "resources/style/style.html"
            )
    f_style = open(f_style, 'r', encoding='utf-8')
    # f_style = open("droidbot/resources/style/style.html", 'r', encoding='utf-8')
    new_str = "<ul id=\"menu\">" + '\n'
    new_bug_str = ""
    for report_screen in report_screens:
        action_count = report_screen['event_index']
        event_name = report_screen['event']
        img_name = report_screen['screen_shoot']
        img_file = os.path.join("all_states", img_name)
        line = (
            "      <li><img src=\""
            + img_file
            + "\" class=\"img\"><p>"
            + action_count+ " " + event_name
            + "</p></li>"
            + '\n'
        )
        if bug_information is not None:
            if action_count in bug_set:
                line = (
                    "      <li><img src=\""
                    + img_file
                    + "\" class=\"img\""
                    + " id=\""
                    + action_count
                    + "\">"
                    +"<p>"
                    + action_count+ " " + event_name
                    + "</p></li>"
                    + '\n'
                )
        line_list.append(line)
    for item in line_list:
        new_str = new_str + item
    for item in bug_link_list:
        new_bug_str = new_bug_str + item
    new_str = new_str + "   </ul>"
    old_str = "<ul id=\"menu\"></ul>"
    old_bug_str = "<tr><td>bug_link</td><td>bug_link</td><td>bug_link</td><td>bug_link</td></tr>"
    for line in f_style:
        if bug_information is not None and old_bug_str in line:
            f_html.write(line.replace(old_bug_str, new_bug_str))
            continue
        f_html.write(line.replace(old_str, new_str))
        
def get_yml_config()->dict[str,str]:
    if not any(os.path.exists(ymal_path := os.path.join(os.getcwd(), _)) for _ in ["config.yml", "config.yaml"]):
        raise "config.yml not found"

    with open(ymal_path, "r") as fp:
        config_dir:dict[str, str] = yaml.safe_load(fp)
    
    return config_dir

def deprecated(reason):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(f"Function '{func.__name__}' is deprecated: {reason}", DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator

class Time(object):
    def __init__(self):
        self.start_time = time.time()

    def get_time_duration(self):
        return str(int(time.time() - self.start_time))

class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]