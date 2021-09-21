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
import xlrd
from datetime import datetime
from typing import Optional, Tuple, Union
from telegram_payment_bot.config import ConfigTypes
from telegram_payment_bot.payments_loader_base import PaymentsLoaderBase
from telegram_payment_bot.payments_data import PaymentErrorTypes, SinglePayment, PaymentsData, PaymentsDataErrors


#
# Classes
#

# Constants for payment Excel loader class
class PaymentsExcelLoaderConst:
    # Sheet index
    SHEET_IDX: int = 0


# Payments Excel loader class
class PaymentsExcelLoader(PaymentsLoaderBase):
    # Load all payments
    def LoadAll(self) -> PaymentsData:
        return self.__LoadAndCheckAll()[0]

    # Load single payment by username
    def LoadSingleByUsername(self,
                             username: str) -> Optional[SinglePayment]:
        return self.LoadAll().GetByUsername(username)

    # Check for errors
    def CheckForErrors(self) -> PaymentsDataErrors:
        return self.__LoadAndCheckAll()[1]

    # Load and check all payments
    def __LoadAndCheckAll(self) -> Tuple[PaymentsData, PaymentsDataErrors]:
        # Get payment file
        payment_file = self.config.GetValue(ConfigTypes.PAYMENT_EXCEL_FILE)

        try:
            # Log
            self.logger.GetLogger().info("Loading file \"%s\"..." % payment_file)

            # Get sheet
            sheet = self.__GetSheet(payment_file)
            # Load sheet
            payments_data, payments_data_err = self.__LoadSheet(sheet)

            # Log
            self.logger.GetLogger().info("File \"%s\" successfully loaded, number of rows: %d" %
                                         (payment_file, payments_data.Count()))

            return payments_data, payments_data_err

        # Catch everything and log exception
        except Exception:
            self.logger.GetLogger().exception("An error occurred while loading file \"%s\"" % payment_file)
            raise

    # Load sheet
    def __LoadSheet(self,
                    sheet: xlrd.sheet.Sheet) -> Tuple[PaymentsData, PaymentsDataErrors]:
        payments_data = PaymentsData()
        payments_data_err = PaymentsDataErrors()

        # Get column indexes
        email_col_idx = self.config.GetValue(ConfigTypes.PAYMENT_EMAIL_COL)
        username_col_idx = self.config.GetValue(ConfigTypes.PAYMENT_USERNAME_COL)
        expiration_col_idx = self.config.GetValue(ConfigTypes.PAYMENT_EXPIRATION_COL)

        # Read each row
        for i in range(sheet.nrows):
            # Skip header (first row)
            if i > 0:
                # Get cell values
                email = str(sheet.cell_value(i, email_col_idx)).strip()
                username = str(sheet.cell_value(i, username_col_idx)).strip()
                expiration = sheet.cell_value(i, expiration_col_idx)

                # Skip empty usernames
                if username != "":
                    self.__AddPayment(i, payments_data, payments_data_err, email, username, expiration)

        return payments_data, payments_data_err

    # Add payment
    def __AddPayment(self,
                     row_idx: int,
                     payments_data: PaymentsData,
                     payments_data_err: PaymentsDataErrors,
                     email: str,
                     username: str,
                     expiration: Union[float, int, str]) -> None:
        # In Excel, a date can be a number or a string
        try:
            expiration_datetime = xlrd.xldate_as_datetime(expiration, 0)
        except TypeError:
            try:
                expiration_datetime = datetime.strptime(expiration.strip(),
                                                        self.config.GetValue(ConfigTypes.PAYMENT_DATE_FORMAT))
            except ValueError:
                self.logger.GetLogger().warning(
                    "Expiration date for username @%s at row %d is not valid (%s), skipped" % (
                        username, row_idx, expiration)
                )
                # Add error
                payments_data_err.AddPaymentError(PaymentErrorTypes.INVALID_DATE_ERR,
                                                  row_idx + 1,
                                                  username,
                                                  expiration)
                return

        # Add data
        if payments_data.AddPayment(email, username, expiration_datetime):
            self.logger.GetLogger().debug("%3d - Row %3d | %s | %s | %s" % (
                payments_data.Count(), row_idx, email, username, expiration_datetime.date()))
        else:
            self.logger.GetLogger().warning("Username @%s is present more than one time at row %d, skipped" % (
                username, row_idx))
            # Add error
            payments_data_err.AddPaymentError(PaymentErrorTypes.DUPLICATED_USERNAME_ERR,
                                              row_idx + 1,
                                              username)

    # Get sheet
    @staticmethod
    def __GetSheet(payment_file: str) -> xlrd.sheet.Sheet:
        # Open file
        wb = xlrd.open_workbook(payment_file)
        return wb.sheet_by_index(PaymentsExcelLoaderConst.SHEET_IDX)
