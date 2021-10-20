# Copyright (c) 2021 Emanuele Bellocchia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

#
# Imports
#
import logging
from typing import Dict
from telegram_payment_bot.config import ConfigTypes, Config
from telegram_payment_bot.config_loader import ConfigCfgType
from telegram_payment_bot.payment_types import PaymentTypes
from telegram_payment_bot.utils import Utils


#
# Classes
#

# Configuration data type converter class
class _ConfigDataTypeConverter:
    # String to payment type
    STR_TO_PAYMENT_TYPE: Dict[str, PaymentTypes] = {
        "EXCEL_FILE": PaymentTypes.EXCEL_FILE,
        "GOOGLE_SHEET": PaymentTypes.GOOGLE_SHEET,
    }

    # String to log level
    STR_TO_LOG_LEVEL: Dict[str, int] = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    # Convert string to payment type
    @staticmethod
    def StrToPaymentType(payment_type: str) -> PaymentTypes:
        return _ConfigDataTypeConverter.STR_TO_PAYMENT_TYPE[payment_type]

    # Convert string to log level
    @staticmethod
    def StrToLogLevel(log_level: str) -> int:
        return (_ConfigDataTypeConverter.STR_TO_LOG_LEVEL[log_level]
                if log_level in _ConfigDataTypeConverter.STR_TO_LOG_LEVEL
                else logging.INFO)

    # Convert log level to string
    @staticmethod
    def LogLevelToStr(log_level: int) -> str:
        idx = list(_ConfigDataTypeConverter.STR_TO_LOG_LEVEL.values()).index(log_level)
        return list(_ConfigDataTypeConverter.STR_TO_LOG_LEVEL.keys())[idx]


# Utility functions for configuration data class
class _ConfigDataUtils:
    # Minimum/maximum column values
    COL_MIN_VAL: str = "A"
    COL_MAX_VAL: str = "Z"

    # Read file
    @staticmethod
    def ReadFile(file_name: str) -> str:
        with open(file_name, "r", encoding="utf-8") as fin:
            file_data = fin.read()
        return file_data

    # Get if column indexes are valid
    @staticmethod
    def AreColumnIndexesValid(config: Config,
                              curr_col: str) -> bool:
        # Check value of current column
        if (len(curr_col) != 1 or
                curr_col < _ConfigDataUtils.COL_MIN_VAL or
                curr_col > _ConfigDataUtils.COL_MAX_VAL):
            return False

        # Get other indexes that are already available
        col_idxs = []
        for col_idx in (ConfigTypes.PAYMENT_EMAIL_COL,
                        ConfigTypes.PAYMENT_USERNAME_COL,
                        ConfigTypes.PAYMENT_EXPIRATION_COL):
            if config.IsValueSet(col_idx):
                col_idxs.append(config.GetValue(col_idx))

        # All possible cases
        if len(col_idxs) == 0:
            res = True
        elif len(col_idxs) == 1:
            res = curr_col != col_idxs[0]
        elif len(col_idxs) == 2:
            res = (curr_col != col_idxs[0] and
                   curr_col != col_idxs[1] and
                   col_idxs[0] != col_idxs[1])
        else:
            res = False
        return res


# Payment bot configuration
PaymentBotConfigCfg: ConfigCfgType = {
    # Pyrogram
    "pyrogram": [
        {
            "type": ConfigTypes.SESSION_NAME,
            "name": "session_name",
        },
    ],
    # App
    "app": [
        {
            "type": ConfigTypes.APP_TEST_MODE,
            "name": "app_test_mode",
            "conv_fct": Utils.StrToBool,
        },
        {
            "type": ConfigTypes.APP_LANG_FILE,
            "name": "app_lang_file",
            "def_val": None,
        },
    ],
    # Users
    "users": [
        {
            "type": ConfigTypes.AUTHORIZED_USERS,
            "name": "authorized_users",
            "conv_fct": lambda val: val.split(","),
        },
    ],
    # Support
    "support": [
        {
            "type": ConfigTypes.SUPPORT_EMAIL,
            "name": "support_email",
            "def_val": "",
        },
        {
            "type": ConfigTypes.SUPPORT_TELEGRAM,
            "name": "support_telegram",
            "def_val": "",
        },
    ],
    # Payment
    "payment": [
        {
            "type": ConfigTypes.PAYMENT_WEBSITE,
            "name": "payment_website",
            "def_val": "",
        },
        {
            "type": ConfigTypes.PAYMENT_CHECK_ON_JOIN,
            "name": "payment_check_on_join",
            "conv_fct": Utils.StrToBool,
            "def_val": True,
        },
        {
            "type": ConfigTypes.PAYMENT_TYPE,
            "name": "payment_type",
            "conv_fct": _ConfigDataTypeConverter.StrToPaymentType,
        },
        {
            "type": ConfigTypes.PAYMENT_EXCEL_FILE,
            "name": "payment_excel_file",
            "load_if": lambda cfg: cfg.GetValue(ConfigTypes.PAYMENT_TYPE) == PaymentTypes.EXCEL_FILE,
        },
        {
            "type": ConfigTypes.PAYMENT_GOOGLE_SHEET_ID,
            "name": "payment_google_sheet_id",
            "load_if": lambda cfg: cfg.GetValue(ConfigTypes.PAYMENT_TYPE) == PaymentTypes.GOOGLE_SHEET,
        },
        {
            "type": ConfigTypes.PAYMENT_GOOGLE_CRED,
            "name": "payment_google_cred",
            "load_if": lambda cfg: cfg.GetValue(ConfigTypes.PAYMENT_TYPE) == PaymentTypes.GOOGLE_SHEET,
        },
        {
            "type": ConfigTypes.PAYMENT_GOOGLE_CRED_PATH,
            "name": "payment_google_cred_path",
            "load_if": lambda cfg: cfg.GetValue(ConfigTypes.PAYMENT_TYPE) == PaymentTypes.GOOGLE_SHEET,
        },
        {
            "type": ConfigTypes.PAYMENT_EMAIL_COL,
            "name": "payment_email_col",
            "conv_fct": lambda val: val.upper(),
            "def_val": "A",
            "valid_if": _ConfigDataUtils.AreColumnIndexesValid
        },
        {
            "type": ConfigTypes.PAYMENT_USERNAME_COL,
            "name": "payment_username_col",
            "conv_fct": lambda val: val.upper(),
            "def_val": "B",
            "valid_if": _ConfigDataUtils.AreColumnIndexesValid
        },
        {
            "type": ConfigTypes.PAYMENT_EXPIRATION_COL,
            "name": "payment_expiration_col",
            "conv_fct": lambda val: val.upper(),
            "def_val": "C",
            "valid_if": _ConfigDataUtils.AreColumnIndexesValid
        },
        {
            "type": ConfigTypes.PAYMENT_DATE_FORMAT,
            "name": "payment_date_format",
            "def_val": "%d/%m/%Y",
        },
    ],
    # Email
    "email": [
        {
            "type": ConfigTypes.EMAIL_ENABLED,
            "name": "email_enabled",
            "conv_fct": Utils.StrToBool,
            "def_val": False,
        },
        {
            "type": ConfigTypes.EMAIL_FROM,
            "name": "email_from",
            "load_if": lambda cfg: cfg.GetValue(ConfigTypes.EMAIL_ENABLED),
        },
        {
            "type": ConfigTypes.EMAIL_REPLY_TO,
            "name": "email_reply_to",
            "load_if": lambda cfg: cfg.GetValue(ConfigTypes.EMAIL_ENABLED),
        },
        {
            "type": ConfigTypes.EMAIL_HOST,
            "name": "email_host",
            "load_if": lambda cfg: cfg.GetValue(ConfigTypes.EMAIL_ENABLED),
        },
        {
            "type": ConfigTypes.EMAIL_USER,
            "name": "email_user",
            "load_if": lambda cfg: cfg.GetValue(ConfigTypes.EMAIL_ENABLED),
        },
        {
            "type": ConfigTypes.EMAIL_PASSWORD,
            "name": "email_password",
            "load_if": lambda cfg: cfg.GetValue(ConfigTypes.EMAIL_ENABLED),
        },
        {
            "type": ConfigTypes.EMAIL_SUBJECT,
            "name": "email_subject",
            "load_if": lambda cfg: cfg.GetValue(ConfigTypes.EMAIL_ENABLED),
        },
        {
            "type": ConfigTypes.EMAIL_ALT_BODY,
            "name": "email_alt_body",
            "conv_fct": _ConfigDataUtils.ReadFile,
            "print_fct": lambda val: "file successfully loaded",
            "load_if": lambda cfg: cfg.GetValue(ConfigTypes.EMAIL_ENABLED),
        },
        {
            "type": ConfigTypes.EMAIL_HTML_BODY,
            "name": "email_html_body",
            "conv_fct": _ConfigDataUtils.ReadFile,
            "print_fct": lambda val: "file successfully loaded",
            "load_if": lambda cfg: cfg.GetValue(ConfigTypes.EMAIL_ENABLED),
        },
    ],
    # Logging
    "logging": [
        {
            "type": ConfigTypes.LOG_LEVEL,
            "name": "log_level",
            "conv_fct": _ConfigDataTypeConverter.StrToLogLevel,
            "print_fct": _ConfigDataTypeConverter.LogLevelToStr,
            "def_val": True,
        },
        {
            "type": ConfigTypes.LOG_CONSOLE_ENABLED,
            "name": "log_console_enabled",
            "conv_fct": Utils.StrToBool,
            "def_val": True,
        },
        {
            "type": ConfigTypes.LOG_FILE_ENABLED,
            "name": "log_file_enabled",
            "conv_fct": Utils.StrToBool,
            "def_val": False,
        },
        {
            "type": ConfigTypes.LOG_FILE_NAME,
            "name": "log_file_name",
            "load_if": lambda cfg: cfg.GetValue(ConfigTypes.LOG_FILE_ENABLED),
        },
        {
            "type": ConfigTypes.LOG_FILE_USE_ROTATING,
            "name": "log_file_use_rotating",
            "conv_fct": Utils.StrToBool,
            "load_if": lambda cfg: cfg.GetValue(ConfigTypes.LOG_FILE_ENABLED),
        },
        {
            "type": ConfigTypes.LOG_FILE_APPEND,
            "name": "log_file_append",
            "conv_fct": Utils.StrToBool,
            "load_if": lambda cfg: (cfg.GetValue(ConfigTypes.LOG_FILE_ENABLED) and
                                    not cfg.GetValue(ConfigTypes.LOG_FILE_USE_ROTATING)),
        },
        {
            "type": ConfigTypes.LOG_FILE_MAX_BYTES,
            "name": "log_file_max_bytes",
            "conv_fct": Utils.StrToInt,
            "load_if": lambda cfg: (cfg.GetValue(ConfigTypes.LOG_FILE_ENABLED) and
                                    cfg.GetValue(ConfigTypes.LOG_FILE_USE_ROTATING)),
        },
        {
            "type": ConfigTypes.LOG_FILE_BACKUP_CNT,
            "name": "log_file_backup_cnt",
            "conv_fct": Utils.StrToInt,
            "load_if": lambda cfg: (cfg.GetValue(ConfigTypes.LOG_FILE_ENABLED) and
                                    cfg.GetValue(ConfigTypes.LOG_FILE_USE_ROTATING)),
        },
    ],
}
