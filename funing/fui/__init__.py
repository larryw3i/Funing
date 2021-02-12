

from flocale.locale import _, lang_code

date_str_regex = '^(?:(?!0000)[0-9]{4}([-/.]?)(?:(?:0?[1-9]|1[0-2])([-/.]?)'+\
'(?:0?[1-9]|1[0-9]|2[0-8])|(?:0?[13-9]|1[0-2])([-/.]?)(?:29|30)|(?:0?[13578]'+\
'|1[02])([-/.]?)31)|(?:[0-9]{2}(?:0[48]|[2468][048]|[13579][26])|(?:0[48]|'+\
'[2468][048]|[13579][26])00)([-/.]?)0?2([-/.]?)29)$'

# data string regex
dregex_dict = {
    'str':  ['',_('string')],
    'int':  ['^\d+$',_('integer')],
    'float':['^\d+.\d+$',_('float')],
    'bool': ['^[0|1]$',_('boolean')],
    'date': [date_str_regex,_('Date')],
    'Time': ['^([01]?[0-9]|2[0-3]):[0-5][0-9]$', _('Time')],
    'Time_s': ['^([01]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$', \
        _('Time(With second)')]
}
dregex_dict_ks =[ k for k,v in dregex_dict.items() ]
dregex_dict_v_regs =[ v[0] for k,v in dregex_dict.items() ]
dregex_dict_v_ts =[ v[1] for k,v in dregex_dict.items() ]